#!/usr/bin/env python3
"""
Extract experimental results and tables from paper sections using Claude Agent SDK.
"""

import os
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

# Limit to avoid overloading context
MAX_CHARS_PER_PAPER = 25000

def get_weighted_score(filename):
    """
    Return a priority score for sorting files. Lower is better.
    Prioritize sections likely to contain results (tables, experiments).
    """
    fname = filename.lower()
    if 'result' in fname or 'experiment' in fname or 'eval' in fname or 'perform' in fname:
        return 0
    if 'comp' in fname or 'anal' in fname: # Comparison, analysis
        return 1
    if 'model' in fname or 'method' in fname:
        return 2
    if 'intro' in fname:
        return 3
    if 'abstract' in fname: # Usually too high level, but maybe
        return 4
    return 10

def get_paper_content(paper_dir):
    """
    Read and concatenate all relevant text files from a paper directory.
    Excludes metdata, prioritizes result sections, and enforces length limit.
    """
    content_parts = []
    paper_path = Path(paper_dir)
    
    # Get all potential text files
    all_files = list(paper_path.glob("*.txt"))
    # Sort: Primary sort by content relevance, secondary by name
    sorted_files = sorted(all_files, key=lambda p: (get_weighted_score(p.name), p.name))
    
    current_length = 0
    
    for file_path in sorted_files:
        filename = file_path.name
        
        # Skip specific files that definitely don't have detailed results tables
        if any(x in filename.lower() for x in ['references', 'acknowledgment', 'related work']):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
                if text:
                    # Check limit
                    if current_length > MAX_CHARS_PER_PAPER:
                        break
                        
                    header = f"\n--- Section: {filename} ---\n"
                    
                    # Truncate if this file pushes over the edge
                    remaining_space = MAX_CHARS_PER_PAPER - current_length
                    if len(text) > remaining_space:
                        text = text[:remaining_space] + "\n[... truncated ...]"
                    
                    content_parts.append(header + text)
                    current_length += len(header) + len(text)
                    
        except Exception as e:
            print(f"  [WARN] Could not read {filename}: {e}")
            
    return "\n\n".join(content_parts)

def find_papers(papers_dir):
    """Find all paper directories."""
    papers = []
    papers_path = Path(papers_dir)

    for paper_dir in sorted(papers_path.iterdir()):
        if paper_dir.is_dir():
            papers.append(paper_dir)
            
    return papers

async def extract_results(papers, output_file):
    """Extract results from papers using Claude Agent SDK."""

    # Configure options for the SDK
    options = ClaudeAgentOptions(
        system_prompt='''You are an expert researcher tasked with extracting experimental results from scientific papers.
Your goal is to ONE THING ONLY: Extract tables containing experimental results.

Instructions:
1.  **Output ONLY the tables.** Do not include any introductory text, explanations, or conclusions.
2.  Format specific tables as Markdown tables.
3.  If a result is presented as a list of key metrics instead of a table, format it as a table with columns "Metric" and "Value".
4.  If no experimental results are found, output the string "NO_RESULTS_FOUND".
5.  Do not output "Here are the results..." or "Based on the paper...". Start directly with the Markdown table.
''',
        model='sonnet' # Use sonnet for better reasoning capabilities
    )

    all_results = []

    for i, paper_dir in enumerate(papers, 1):
        paper_id = paper_dir.name.replace("_sections", "")
        print(f"Processing {i}/{len(papers)}: {paper_id}")

        try:
            # Aggregate paper content
            paper_text = get_paper_content(paper_dir)
            
            if not paper_text:
                print(f"  [SKIP] No relevant content found for {paper_id}")
                continue

            # Create the prompt
            prompt = f"""Find and format all experimental result tables from the following content on paper '{paper_id}'.
Preserve the exact numbers.

Paper Content:
{paper_text}

Tables:"""

            # Query Claude with retries
            extracted_info = ""
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    print(f"  [BUSY] Querying Claude... (Attempt {attempt+1}/{max_retries})")
                    extracted_info = "" # Reset
                    async for message in query(prompt=prompt, options=options):
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    extracted_info += block.text
                    break # Success
                except Exception as query_error:
                    if "Claude Code not found" in str(query_error) and attempt < max_retries - 1:
                        print(f"    [WARN] SDK Error: {query_error}. Retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise query_error # Re-raise to be caught by outer try/except
            
            extracted_info = extracted_info.strip()
            
            all_results.append({
                "paper_id": paper_id,
                "results": extracted_info
            })

            print(f"  [OK] Extracted {len(extracted_info)} characters.")

        except Exception as e:
            print(f"  [ERROR] {e}")
            all_results.append({
                "paper_id": paper_id,
                "results": f"ERROR: {str(e)}"
            })

    # Save results to text file
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in all_results:
            results_text = result['results']
            # Filter out empty results to keep output clean
            if results_text == "NO_RESULTS_FOUND":
                continue
                
            f.write(f"Paper: {result['paper_id']}\n")
            f.write("=" * 80 + "\n")
            f.write(f"{results_text}\n")
            f.write("=" * 80 + "\n\n")

    print(f"\n[OK] Results saved to {output_file}")
    return all_results

async def main():
    # Configuration
    papers_dir = "paper_sections"
    output_file = "paper_results.txt"

    print("=" * 80)
    print("Paper Results Extraction (Tables Only) using Claude Agent SDK")
    print("=" * 80)
    print()

    # Find papers
    print(f"Scanning {papers_dir} for papers...")
    papers = find_papers(papers_dir)
    print(f"Found {len(papers)} papers\n")

    if not papers:
        print("No papers found!")
        return

    # Extract results
    await extract_results(papers, output_file)

if __name__ == "__main__":
    asyncio.run(main())
