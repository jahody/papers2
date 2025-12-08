import os
import re
from pathlib import Path

def extract_main_idea(abstract_text):
    """Extract the main idea from an abstract.

    The main idea is typically found in:
    1. The first sentence (introduces the problem/approach)
    2. Sentences with key phrases like "we propose", "we present", "this paper"
    3. The last sentence (summarizes contribution)
    """
    if not abstract_text or not abstract_text.strip():
        return "No abstract found"

    # Clean up the text
    text = abstract_text.strip()

    # Split into sentences (simple approach)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Look for key contribution sentences
    contribution_keywords = [
        r'\bwe\s+(propose|present|introduce|develop|design|show|demonstrate|report)',
        r'\bthis\s+(paper|work|study|article)\s+(proposes|presents|introduces|develops)',
        r'\bour\s+(approach|method|system|model|framework)',
    ]

    main_ideas = []

    # First sentence often states the problem or approach
    if sentences:
        main_ideas.append(sentences[0].strip())

    # Find sentences with contribution keywords
    for sentence in sentences:
        for pattern in contribution_keywords:
            if re.search(pattern, sentence, re.IGNORECASE):
                if sentence not in main_ideas:
                    main_ideas.append(sentence.strip())
                break

    # If we found specific contribution sentences, use those
    # Otherwise use the first sentence
    if len(main_ideas) > 1:
        return ' '.join(main_ideas[:2])  # Use first + one contribution sentence
    elif main_ideas:
        return main_ideas[0]
    else:
        # Fallback: return first 200 chars
        return text[:200] + ('...' if len(text) > 200 else '')


def find_abstract_file(paper_dir):
    """Find the abstract file in a paper directory."""
    paper_path = Path(paper_dir)

    # Look for files that might contain the abstract
    abstract_patterns = ['*Abstract*.txt', '*ABSTRACT*.txt', '*abstract*.txt', '0b*.txt']

    for pattern in abstract_patterns:
        matches = list(paper_path.glob(pattern))
        if matches:
            return matches[0]

    return None


def main():
    output_dir = r"g:\My Drive\OSU\projects\papers\output"
    results = {}

    print(f"{'='*100}")
    print("MAIN IDEAS FROM PAPER ABSTRACTS")
    print(f"{'='*100}\n")

    # Process each paper
    for paper_folder in sorted(os.listdir(output_dir)):
        paper_path = os.path.join(output_dir, paper_folder)
        if os.path.isdir(paper_path) and '_sections' in paper_folder:
            # Extract paper ID and title
            paper_id = paper_folder.split('_')[0]
            paper_title = paper_folder.replace('_sections', '').replace('_', ' ')

            # Find and read abstract
            abstract_file = find_abstract_file(paper_path)

            if abstract_file:
                try:
                    with open(abstract_file, 'r', encoding='utf-8', errors='ignore') as f:
                        abstract_text = f.read()

                    main_idea = extract_main_idea(abstract_text)
                    results[paper_folder] = {
                        'id': paper_id,
                        'title': paper_title,
                        'idea': main_idea
                    }

                    print(f"Paper ID: {paper_id}")
                    print(f"Title: {paper_title}")
                    print(f"\nMain Idea:")
                    print(f"  {main_idea}")
                    print(f"\n{'-'*100}\n")

                except Exception as e:
                    print(f"Error reading abstract for {paper_folder}: {e}\n")
            else:
                print(f"No abstract found for {paper_folder}\n")

    # Save results to a file
    output_file = r"g:\My Drive\OSU\projects\papers\paper_main_ideas.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*100 + "\n")
        f.write("MAIN IDEAS FROM PAPER ABSTRACTS\n")
        f.write("="*100 + "\n\n")

        for paper_folder, info in sorted(results.items()):
            f.write(f"Paper ID: {info['id']}\n")
            f.write(f"Title: {info['title']}\n")
            f.write(f"\nMain Idea:\n")
            f.write(f"  {info['idea']}\n")
            f.write("\n" + "-"*100 + "\n\n")

    print(f"\n{'='*100}")
    print(f"Results saved to: {output_file}")
    print(f"Total papers processed: {len(results)}")
    print(f"{'='*100}")


if __name__ == "__main__":
    main()
