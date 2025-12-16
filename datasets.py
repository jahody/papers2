#!/usr/bin/env python3
"""
Extract used datasets from papers using Claude Agent SDK.
"""

import os
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

# Reduced limit to avoid crashing the SDK bridge
MAX_CHARS_PER_PAPER = 25000 

def get_weighted_score(filename):
    """
    Return a priority score for sorting files. Lower is better.
    """
    fname = filename.lower()
    if 'abstract' in fname:
        return 0
    if 'intro' in fname:
        return 1
    if 'data' in fname:
        return 2
    if 'experiment' in fname or 'evaluation' in fname:
        return 3
    if 'model' in fname or 'method' in fname:
        return 4
    return 10

def get_paper_content(papers_dir):
    """
    Read text content from each paper directory in paper_sections.
    Prioritizes important sections and limits total length.
    """
    papers_content = []
    papers_path = Path(papers_dir)

    for paper_dir in sorted(papers_path.iterdir()):
        if paper_dir.is_dir():
            paper_text_parts = []
            
            # Get all text files and sort them by priority
            all_files = list(paper_dir.glob("*.txt"))
            # Sort by priority score, then by name for stability
            sorted_files = sorted(all_files, key=lambda p: (get_weighted_score(p.name), p.name))
            
            current_length = 0
            
            for text_file in sorted_files:
                # Skip references
                if "reference" in text_file.name.lower():
                    continue
                
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            # If adding this file exceeds limit significantly, skip it or truncate
                            # We allow a little overflow if it's the first file, otherwise check
                            if current_length > MAX_CHARS_PER_PAPER:
                                break
                            
                            header = f"\n--- Section: {text_file.stem} ---\n"
                            
                            # Truncate content if needed to just fit the remainder?
                            # For simplicity, we just add files until we hit the cap.
                            # If a single file is huge, we truncate it.
                            max_chunk = MAX_CHARS_PER_PAPER - current_length
                            if len(content) > max_chunk:
                                content = content[:max_chunk] + "\n[... truncated ...]"
                            
                            paper_text_parts.append(header + content)
                            current_length += len(header) + len(content)
                            
                except Exception as e:
                    print(f"Warning: Could not read {text_file}: {e}")

            if paper_text_parts:
                paper_id = paper_dir.name.replace("_sections", "")
                full_text = "".join(paper_text_parts)
                papers_content.append({
                    "paper_id": paper_id,
                    "content": full_text
                })

    return papers_content

async def extract_datasets(papers, output_file):
    """Extract datasets from paper content using Claude Agent SDK."""

    # Configure options for the SDK
    options = ClaudeAgentOptions(
        system_prompt='''You are an expert at analyzing research papers.
Your task is to identify and list all datasets used, created, or evaluated in the paper.
Focus on extracting specific dataset names (e.g., "MNIST", "ImageNet", "Twitter15", "SAT benchmarks", "CNF datasets").
If the paper generates synthetic data, describe it briefly.
Output your answer as a concise bulleted list. If no datasets are clearly used, state "No specific datasets identified."''',
        model='haiku'  # Use haiku for faster, cheaper processing
    )

    results = []

    for i, paper_info in enumerate(papers, 1):
        paper_id = paper_info["paper_id"]
        content = paper_info["content"]

        print(f"Processing {i}/{len(papers)}: {paper_id}")
        print(f"  > Content length: {len(content)} chars")

        try:
            prompt = f"""Identify the datasets used in this paper based on the following content:

{content}

Used Datasets:"""

            # Query Claude
            response_text = ""
            async for message in query(prompt=prompt, options=options):
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            response_text += block.text

            response_text = response_text.strip()

            results.append({
                "paper_id": paper_id,
                "datasets": response_text
            })

            print(f"  [OK] Found: {response_text[:80].replace(chr(10), ' ')}...")
            
            # Small delay to prevent overwhelming the local bridge
            await asyncio.sleep(1.0)

        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({
                "paper_id": paper_id,
                "datasets": f"ERROR: {str(e)}"
            })

    # Save results to text file
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"Paper: {result['paper_id']}\n")
            f.write(f"Datasets:\n{result['datasets']}\n")
            f.write("-" * 80 + "\n\n")

    print(f"\n[OK] Results saved to {output_file}")

    return results

async def main():
    # Configuration
    papers_dir = "paper_sections"
    output_file = "paper_datasets.txt"

    print("=" * 80)
    print("Paper Dataset Extraction using Claude Agent SDK")
    print("=" * 80)
    print()

    # Find all paper content
    print(f"Scanning {papers_dir} for paper content...")
    papers = get_paper_content(papers_dir)
    print(f"Found {len(papers)} papers with content\n")

    if not papers:
        print("No papers found!")
        return

    # Extract datasets
    results = await extract_datasets(papers, output_file)

    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total papers processed: {len(results)}")
    successful = sum(1 for r in results if not r['datasets'].startswith('ERROR'))
    print(f"Successfully processed: {successful}")
    print(f"Errors: {len(results) - successful}")

if __name__ == "__main__":
    asyncio.run(main())
