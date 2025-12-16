#!/usr/bin/env python3
"""
Extract main ideas from paper abstracts using Claude Agent SDK.
"""

import os
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

def find_abstract_files(papers_dir):
    """Find all abstract files in paper_sections directory."""
    abstracts = []
    papers_path = Path(papers_dir)

    for paper_dir in sorted(papers_path.iterdir()):
        if paper_dir.is_dir():
            # Look for abstract file (could be Abstract.txt or ABSTRACT.txt)
            abstract_files = list(paper_dir.glob("0b_*.txt"))
            if abstract_files:
                paper_id = paper_dir.name.replace("_sections", "")
                abstracts.append({
                    "paper_id": paper_id,
                    "abstract_file": abstract_files[0]
                })

    return abstracts

async def extract_main_ideas(abstracts, output_file):
    """Extract main ideas from abstracts using Claude Agent SDK."""

    # Configure options for the SDK
    options = ClaudeAgentOptions(
        system_prompt='''You are an expert at analyzing research papers and extracting key insights.
Your task is to read paper abstracts and extract the main idea in a single, clear sentence.
Focus on what problem the paper solves and the key contribution or approach.
Keep your response concise - just the main idea, no extra commentary.''',
        model='haiku'  # Use haiku for faster, cheaper processing
    )

    results = []

    for i, paper_info in enumerate(abstracts, 1):
        paper_id = paper_info["paper_id"]
        abstract_file = paper_info["abstract_file"]

        print(f"Processing {i}/{len(abstracts)}: {paper_id}")

        try:
            # Read the abstract
            with open(abstract_file, 'r', encoding='utf-8') as f:
                abstract_text = f.read().strip()

            # Create the prompt
            prompt = f"""Extract the main idea from this paper abstract in ONE clear sentence:

{abstract_text}

Main idea:"""

            # Query Claude using the simple query function
            main_idea = ""
            async for message in query(prompt=prompt, options=options):
                # Extract text from message content blocks
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            main_idea += block.text

            main_idea = main_idea.strip()

            results.append({
                "paper_id": paper_id,
                "main_idea": main_idea
            })

            print(f"  [OK] Extracted: {main_idea[:80]}...")

        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({
                "paper_id": paper_id,
                "main_idea": f"ERROR: {str(e)}"
            })

    # Save results to text file
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"Paper: {result['paper_id']}\n")
            f.write(f"Main Idea: {result['main_idea']}\n")
            f.write("-" * 80 + "\n\n")

    print(f"\n[OK] Results saved to {output_file}")

    return results

async def main():
    # Configuration
    papers_dir = "paper_sections"
    output_file = "paper_main_ideas.txt"

    print("=" * 80)
    print("Paper Main Idea Extraction using Claude Agent SDK")
    print("=" * 80)
    print()

    # Find all abstract files
    print(f"Scanning {papers_dir} for abstracts...")
    abstracts = find_abstract_files(papers_dir)
    print(f"Found {len(abstracts)} papers\n")

    if not abstracts:
        print("No abstracts found!")
        return

    # Extract main ideas
    results = await extract_main_ideas(abstracts, output_file)

    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total papers processed: {len(results)}")
    successful = sum(1 for r in results if not r['main_idea'].startswith('ERROR'))
    print(f"Successfully extracted: {successful}")
    print(f"Errors: {len(results) - successful}")

if __name__ == "__main__":
    asyncio.run(main())
