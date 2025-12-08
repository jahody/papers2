import os
import re
from pathlib import Path

def find_datasets_in_paper(paper_dir):
    """Search for dataset mentions in all sections of a paper."""
    datasets = set()

    # Known SAT/benchmark datasets and patterns
    known_datasets = {
        'SATLIB', 'SAT Competition', 'SAT-COMP', 'SATCOMP', 'G4SATBench',
        'SR(', 'Random', 'MaxSAT', 'DIMACS', 'UNSAT', 'Industrial',
        'SATzilla', 'Circuit-SAT', 'LEC', 'Handmade', 'Crafted',
        'GSET', 'RB-', 'RB50', 'RB100', 'BIRD', 'SMTLIB', 'SMT-LIB',
        'TwitterKORE', 'TPTP', 'CNF', 'Zamkeller', 'Zankeller',
        'k-Clique', 'k-Domset', 'k-Vercov', 'k-VertexCover',
        'SAT2014', 'SAT2016', 'SAT2017', 'SAT2018', 'SAT2019', 'SAT2020',
        'uuf250', 'ForgeEDA', 'Anniversary', 'LECSAT', 'LECUNSAT'
    }

    # Patterns for dataset names
    dataset_patterns = [
        r'\b(SATLIB)\b',
        r'\b(SAT[\s-]?Competition)\b',
        r'\b(SAT[\s-]?COMP[\s-]?\d{4})\b',
        r'\b(G4SATBench)\b',
        r'\b(SR\d+)\b',
        r'\b(Random[\s-]?[\w-]*)\s+(?:dataset|benchmark|instances)',
        r'\b(Industrial)\s+(?:dataset|benchmark|instances)',
        r'\b(Max[\d]*SAT)\b',
        r'\b(DIMACS)\b',
        r'\b(GSET)\b',
        r'\b(RB[\d-]+)\b',
        r'\b(BIRD)\b',
        r'\b(SMTLIB|SMT-LIB)\b',
        r'\b(TPTP)\b',
        r'\b(k-(?:Clique|Domset|Vercov|VertexCover))\b',
        r'\b(Zamkeller|Zankeller)\b',
        r'\b(uuf\d+[\w-]*)\b',
        r'\b(ForgeEDA)\b',
        r'\b(LEC(?:SAT|UNSAT)?)\b',
        r'\b(Circuit[\s-]SAT)\b',
        r'\b(Handmade|Crafted)\s+(?:instances|benchmarks)',
        r'from\s+the\s+(\w+)\s+(?:dataset|benchmark)',
        r'(?:dataset|benchmark)[s]?\s+(?:from|called|named)\s+(\w+)',
    ]

    # Read all text files in the paper directory
    for txt_file in Path(paper_dir).glob('*.txt'):
        try:
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Search for dataset patterns
                for pattern in dataset_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if match and len(match) > 1:
                            # Clean up the match
                            cleaned = match.strip()
                            if cleaned and not cleaned.lower() in {'the', 'and', 'for', 'from', 'with', 'are', 'this'}:
                                datasets.add(cleaned)

                # Also check for known datasets directly
                for known in known_datasets:
                    if known.lower() in content.lower():
                        datasets.add(known)

        except Exception as e:
            print(f"Error reading {txt_file}: {e}")

    return sorted(list(datasets))

def main():
    input_dir = r"g:\My Drive\OSU\projects\papers\paper_sections"
    output_dir = Path(r"g:\My Drive\OSU\projects\papers\paper_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}

    # Process each paper
    for paper_folder in sorted(os.listdir(input_dir)):
        paper_path = os.path.join(input_dir, paper_folder)
        if os.path.isdir(paper_path) and '_sections' in paper_folder:
            print(f"\n{'='*80}")
            print(f"Processing: {paper_folder}")
            print('='*80)

            datasets = find_datasets_in_paper(paper_path)
            results[paper_folder] = datasets
            
            # Write to file
            clean_name = paper_folder.replace('_sections', '')
            output_file = output_dir / f"{clean_name}_datasets.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if datasets:
                    for ds in sorted(datasets):
                        f.write(f"{ds}\n")
                else:
                    f.write("No datasets found\n")

            if datasets:
                print(f"Found {len(datasets)} potential datasets:")
                for ds in sorted(datasets):
                    print(f"  - {ds}")
            else:
                print("  No datasets found")
            
            print(f"Saved to {output_file}")

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    for paper, datasets in sorted(results.items()):
        print(f"\n{paper}:")
        if datasets:
            for ds in sorted(datasets):
                print(f"  - {ds}")
        else:
            print("  (none found)")

if __name__ == "__main__":
    main()
