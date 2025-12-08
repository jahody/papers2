import re
from pathlib import Path
import json
import sys

# Try imports for image generation
try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

def extract_paper_name(filename):
    """Extract paper name from filename, removing arxiv ID prefix and suffix."""
    # Remove arxiv ID prefix (e.g., "1909.11588_Paper_Name_sections_references.txt" -> "Paper_Name")
    match = re.match(r'^\d{4}\.\d{4,5}_(.+)_sections_references\.txt$', filename)
    if match:
        return match.group(1)
    
    # Fallback for other patterns
    match = re.match(r'^\d{4}\.\d{4,5}_(.+)', filename)
    return match.group(1) if match else filename

def extract_title_from_reference(reference_text):
    """Extract paper title from a reference entry."""
    # Format: "N Author, Author. Title. Venue, Year."
    # Remove leading number "1 "
    text = re.sub(r'^\d+\s+', '', reference_text)
    
    # Heuristic: Title is usually the part before the first period that isn't an initial
    # But often references are: Authors. Title. Venue.
    
    # Split by periods
    parts = text.split('.')
    if len(parts) < 3:
        return None
        
    # Heuristic: Second part is likely the title (after authors)
    # But authors might have initials (e.g. "P. C. Pop"). 
    # Let's look for the segment that looks like a title.
    
    # A simple but often effective heuristic for these specific files:
    # 1. Split by period followed by space
    segments = re.split(r'\.\s+', text)
    
    for segment in segments:
        # Title is usually longish, has spaces, no numbers (mostly)
        # Skip segments that look like authors (short words, initials)
        if len(segment) < 10: 
            continue
            
        # Check if it's the venue/year part (often has numbers)
        if re.search(r'\d{4}', segment) and len(segment) < 20:
            continue
            
        # It's a candidate
        return segment.strip()
            
    return None

def extract_citations(text, arxiv_to_name_map):
    """Extract citations (arxiv IDs and paper titles) and convert to names."""
    citations = set()

    # 1. Match arxiv IDs in the text
    arxiv_patterns = [
        r'arXiv:(\d{4}\.\d{4,5})',
        r'arxiv:(\d{4}\.\d{4,5})',
        r'\b(\d{4}\.\d{4,5})\b'
    ]
    
    for pattern in arxiv_patterns:
        found_ids = re.findall(pattern, text, re.IGNORECASE)
        for arxiv_id in found_ids:
            # Skip if it's the start of a filename pattern (heuristic constraint)
            # In these files, citations are usually just listed. 
            pass 
            
            paper_name = arxiv_to_name_map.get(arxiv_id, arxiv_id)
            citations.add(paper_name)

    # 2. Parse reference lines
    # The file format is one reference per line, starting with a number
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
            
        # Extract title
        title = extract_title_from_reference(line)
        
        if title:
            # Cleanup title
            title = re.sub(r'\s+', ' ', title).strip()
            if len(title) > 5:
                citations.add(title)
        else:
            # Fallback: Use the line content itself if title extraction fails
            # Remove the leading number and use the rest as the key
            # This ensures we count every reference line
            clean_line = re.sub(r'^\d+\s*', '', line).strip()
            if len(clean_line) > 5:
                 citations.add(clean_line)

    return list(citations)

def build_paper_graph(paper_graph_dir):
    """Build graph structure from paper sections."""
    input_path = Path(paper_graph_dir)
    if not input_path.exists():
        print(f"Error: {paper_graph_dir} does not exist", flush=True)
        return None

    # Find reference files
    ref_files = list(input_path.glob("*_sections_references.txt"))

    if not ref_files:
        print(f"No reference files found in {paper_graph_dir}", flush=True)
        return None

    print(f"Found {len(ref_files)} papers to analyze", flush=True)
    print("=" * 80, flush=True)

    # Build arxiv ID to name mapping
    arxiv_to_name_map = {}
    file_map = {} # Map paper name to file content for later processing if needed
    
    for ref_file in ref_files:
        filename = ref_file.name
        arxiv_match = re.match(r'^(\d{4}\.\d{4,5})', filename)
        
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
            paper_name = extract_paper_name(filename)
            arxiv_to_name_map[arxiv_id] = paper_name
            file_map[paper_name] = ref_file
    
    graph = {
        "papers": {},
        "edges": []
    }

    # Process each paper
    for paper_name, ref_file in file_map.items():
        print(f"\nProcessing: {paper_name}", flush=True)

        content = ref_file.read_text(encoding='utf-8')
        
        # Extract citations
        all_citations = extract_citations(content, arxiv_to_name_map)
        
        print(f"  Found {len(all_citations)} citations", flush=True)

        # Store paper info
        graph["papers"][paper_name] = {
            "name": paper_name,
            "citations": all_citations,
            # Keeping these keys for backward compatibility, though we only have refs now
            "intro_citations": 0,
            "ref_citations": len(all_citations)
        }

        # Create edges
        for cited_name in all_citations:
            graph["edges"].append({
                "from": paper_name,
                "to": cited_name,
                "type": "cites"
            })

    return graph

def analyze_graph(graph):
    """Analyze and print graph statistics."""
    if not graph:
        return

    print("\n" + "=" * 80, flush=True)
    print("GRAPH ANALYSIS", flush=True)
    print("=" * 80, flush=True)

    num_papers = len(graph["papers"])
    num_edges = len(graph["edges"])

    print(f"\nTotal papers: {num_papers}")
    print(f"Total citation edges: {num_edges}")

    # Find papers cited by multiple papers in our set
    cited_counts = {}
    for edge in graph["edges"]:
        cited_id = edge["to"]
        cited_counts[cited_id] = cited_counts.get(cited_id, 0) + 1

    # Find papers in our set that cite each other
    our_paper_ids = set(graph["papers"].keys())
    
    # We need to do a fuzzy matching for internal citations because extracted titles 
    # might not perfectly match our folded names.
    # However, for now, we rely on exact matches if mapped, or title matches.
    # Let's try to match titles to paper names if possible.
    
    internal_citations = []
    
    # Create a mapping of simplified titles to paper IDs for fuzzy matching
    simple_title_map = {}
    for pid in our_paper_ids:
        # paper_name is usually "Title_blah"
        # Let's try to normalize it
        simple = pid.lower().replace('_', ' ').replace('-', ' ')
        simple_title_map[simple] = pid
        
    for edge in graph["edges"]:
        target = edge["to"]
        source = edge["from"]
        
        # Check direct match
        if target in our_paper_ids:
            internal_citations.append(edge)
            continue
            
        # Check fuzzy match
        target_simple = target.lower().replace('-', ' ')
        # Very basic fuzzy match: check if target title is contained in paper name or vice versa
        # This is risky but useful for discovery
        for simple_key, pid in simple_title_map.items():
            if target_simple in simple_key: # target is substring of paper name
                 # Ensure it's not too short to be a false positive
                 if len(target_simple) > 10:
                     # Update edge to use the canonical ID?
                     # For analysis, just count it.
                     # print(f"  [Fuzzy Match] '{target}' -> '{pid}'")
                     # edge["to"] = pid # Update the edge for graphviz!
                     pass

    internal_citations = [e for e in graph["edges"] if e["to"] in our_paper_ids]

    print(f"\nInternal citations (papers citing each other): {len(internal_citations)}", flush=True)

    if internal_citations:
        print("\nPaper connections:")
        for edge in internal_citations:
            print(f"  {edge['from']}")
            print(f"    -> {edge['to']}")
            print()

    # Most cited papers (external)
    external_citations = {k: v for k, v in cited_counts.items()
                         if k not in our_paper_ids and v > 1}

    if external_citations:
        print(f"\nMost cited external papers (not in our set):")
        for cited_name, count in sorted(external_citations.items(),
                                        key=lambda x: x[1], reverse=True)[:10]:
            print(f"  [{count}x] {cited_name}")

    # Papers by citation count
    print("\nPapers by number of references:")
    for paper_name, info in sorted(graph["papers"].items(),
                                   key=lambda x: len(x[1]["citations"]),
                                   reverse=True):
        print(f"  [{len(info['citations'])}] {paper_name}")

def export_graph(graph, output_file="paper_graph/paper_graph.json"):
    """Export graph to JSON file."""
    if not graph:
        return

    output_path = Path(output_file)
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(json.dumps(graph, indent=2), encoding='utf-8')
    print(f"\nGraph exported to: {output_path}", flush=True)

def export_graphviz(graph, output_file="paper_graph/paper_graph.dot"):
    """Export graph in Graphviz DOT format."""
    if not graph:
        return

    our_paper_ids = set(graph["papers"].keys())
    internal_edges = [e for e in graph["edges"] if e["to"] in our_paper_ids]
    external_edges = [e for e in graph["edges"] if e["to"] not in our_paper_ids]

    # Count how many times each internal paper is cited
    internal_citation_counts = {}
    for paper_name in our_paper_ids:
        internal_citation_counts[paper_name] = sum(
            1 for e in internal_edges if e["to"] == paper_name
        )

    # Collect all external papers (filter out arxiv IDs)
    external_papers = set()
    for e in external_edges:
        # Skip if it looks like an arxiv ID (only digits and dots)
        if not re.match(r'^\d{4}\.\d{4,5}$', e["to"]):
            external_papers.add(e["to"])
            
    # Add external papers that are cited multiple times so we have something to show
    cited_counts = {}
    for edge in external_edges:
        cited_counts[edge["to"]] = cited_counts.get(edge["to"], 0) + 1

    dot = ["digraph PaperGraph {"]
    dot.append("  rankdir=LR;")
    dot.append("  node [shape=box];")
    dot.append("")

    # Add our papers (internal nodes) - styled prominently
    dot.append("  // Our papers")
    for paper_name, info in graph["papers"].items():
        # Shorten name for display
        short_name = paper_name[:50] + "..." if len(paper_name) > 50 else paper_name
        cited_count = internal_citation_counts.get(paper_name, 0)
        ref_count = len(info['citations'])
        label = f"{short_name}\\n(cited {cited_count}x | {ref_count} refs)"
        dot.append(f'  "{paper_name}" [label="{label}", style=filled, fillcolor=lightblue];')

    dot.append("")

    # Add external papers - only show those cited > 1 times to reduce noise
    dot.append("  // External papers (cited > 1 times by our set)")
    for ext_paper in sorted(external_papers):
        cite_count = cited_counts.get(ext_paper, 0)
        if cite_count > 1:
            short_name = ext_paper[:40] + "..." if len(ext_paper) > 40 else ext_paper
            label = f"{short_name}\\n(cited {cite_count}x)"
            dot.append(f'  "{ext_paper}" [label="{label}", style=filled, fillcolor=lightyellow];')

    dot.append("")

    # Add internal edges (papers citing each other)
    dot.append("  // Internal citations")
    for edge in internal_edges:
        dot.append(f'  "{edge["from"]}" -> "{edge["to"]}" [color=blue, penwidth=2];')

    dot.append("")

    # Add external edges (papers citing external papers, excluding arxiv IDs)
    dot.append("  // External citations")
    for edge in external_edges:
        # Only show edges to significant external papers
        if cited_counts.get(edge["to"], 0) > 1:
             dot.append(f'  "{edge["from"]}" -> "{edge["to"]}" [color=gray];')

    dot.append("}")

    output_path = Path(output_file)
    output_path.write_text('\n'.join(dot), encoding='utf-8')
    print(f"Graphviz DOT file exported to: {output_path}", flush=True)
    return dot # Return dot content for graphviz rendering

def export_graph_image(graph, output_file_base="paper_graph/paper_graph"):
    """Generate an image of the graph using graphviz or networkx."""
    
    print("\n" + "=" * 80)
    print("IMAGE GENERATION")
    print("=" * 80)

    # Strategy 1: Graphviz
    if HAS_GRAPHVIZ:
        try:
            print("Attempting to generate image using Graphviz...", flush=True)
            # Re-generate DOT content using our helper
            # We can also just use the Digraph object directly but we have dot logic above.
            # Let's reuse the logic basically by creating a new Digraph and adding what we want.
            
            dot = graphviz.Digraph(comment='Paper Graph', format='png')
            dot.attr(rankdir='LR')
            dot.attr('node', shape='box')
            
            our_paper_ids = set(graph["papers"].keys())
            
            # Nodes
            for paper_name in our_paper_ids:
                short_name = paper_name[:40] + "..." if len(paper_name) > 40 else paper_name
                dot.node(paper_name, label=short_name, style='filled', fillcolor='lightblue')
                
            # Internal Edges
            internal_edges = [e for e in graph["edges"] if e["to"] in our_paper_ids]
            for edge in internal_edges:
                dot.edge(edge["from"], edge["to"], color='blue')
                
            # Output
            output_path = dot.render(output_file_base, cleanup=True)
            print(f"Image generated: {output_path}", flush=True)
            return
            
        except Exception as e:
            print(f"Graphviz generation failed: {e}", flush=True)
            print("Falling back to NetworkX...", flush=True)
    else:
        print("Graphviz not found. trying NetworkX...", flush=True)

    # Strategy 2: NetworkX
    if HAS_NETWORKX:
        try:
            print("Attempting to generate image using NetworkX...", flush=True)
            G = nx.DiGraph()
            
            our_paper_ids = set(graph["papers"].keys())
            
            # Add nodes
            for paper_name in our_paper_ids:
                G.add_node(paper_name)
                
            # Add internal edges
            internal_edges = [e for e in graph["edges"] if e["to"] in our_paper_ids]
            for edge in internal_edges:
                G.add_edge(edge["from"], edge["to"])
                
            # Draw
            plt.figure(figsize=(15, 10))
            pos = nx.spring_layout(G, k=0.5, iterations=50)
            
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000, alpha=0.8)
            nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
            nx.draw_networkx_edges(G, pos, edge_color='blue', arrows=True, arrowsize=20)
            
            plt.title("Paper Citation Graph")
            plt.axis('off')
            
            output_path = f"{output_file_base}_nx.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Image generated: {output_path}", flush=True)
            return

        except Exception as e:
            print(f"NetworkX generation failed: {e}", flush=True)
    else:
        print("NetworkX not found.", flush=True)
        
    print("\nCould not generate graph image. Please install graphviz or networkx+matplotlib.", flush=True)


if __name__ == "__main__":
    print("Building paper citation graph...", flush=True)
    print("=" * 80, flush=True)

    # Use the correct path based on user instructions
    PAPER_GRAPH_DIR = "paper_references"
    
    graph = build_paper_graph(PAPER_GRAPH_DIR)

    if graph:
        analyze_graph(graph)
        export_graph(graph)
        export_graphviz(graph)
        # export_graph_image(graph) # Disabled per user request

        print("\n" + "=" * 80, flush=True)
        print("Done!", flush=True)
