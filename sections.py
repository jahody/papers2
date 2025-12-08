import re
from pathlib import Path

def combine_files(folder):
    """Combine text files sorted by page number."""
    path = Path(folder)
    if not path.exists():
        print(f"Error: {folder} does not exist")
        return None, None

    files = sorted(path.glob("*.txt"),
                   key=lambda f: int(m.group(1)) if (m := re.search(r'_page_(\d+)\.txt$', str(f))) else 0)

    if not files:
        print(f"No .txt files in {folder}")
        return None, None

    print(f"Combining {len(files)} files...")
    content = []
    for f in files:
        print(f"  {f.name}")
        content.append(f.read_text(encoding='utf-8'))

    return '\n'.join(content), path.name

def extract_sections(content, name):
    """Extract sections starting with ## to separate files."""
    if not content:
        return

    sections = []
    current = {"title": "", "content": []}

    for line in content.split('\n'):
        # Check for ## section headers
        if line.strip().startswith('##'):
            if current["title"] or current["content"]:
                sections.append(current)
            current = {"title": line.strip().lstrip('#').strip(), "content": []}
        # Check for Abstract without ## marker (e.g., "Abstract." or "Abstract—" or "Abstract ")
        elif re.match(r'^Abstract[\s.\-—]', line.strip()):
            if current["title"] or current["content"]:
                sections.append(current)
            # Extract abstract content after the marker
            abstract_content = re.sub(r'^Abstract[\s.\-—]+', '', line.strip())
            current = {"title": "Abstract", "content": [abstract_content] if abstract_content else []}
        else:
            current["content"].append(line)

    if current["title"] or current["content"]:
        sections.append(current)

    out_dir = Path("paper_sections") / f"{name}_sections"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        print(f"Warning: Removing existing file {out_dir} to create directory")
        out_dir.unlink()
        out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nExtracting {len(sections)} sections to {out_dir}")

    for i, sec in enumerate(sections, 1):
        if sec["title"]:
            # Extract original section number
            num_match = re.match(r'^(\d+)\.?\s*(.+)', sec["title"])
            if num_match:
                orig_num = num_match.group(1)
                clean_title = num_match.group(2)
            else:
                clean_title = sec["title"]
                # Special numbering for common sections
                if 'abstract' in sec["title"].lower():
                    orig_num = '0b'
                else:
                    orig_num = None  # No number for other unnumbered sections

            filename = re.sub(r'[<>:"/\\|?*]', '_', clean_title)[:100]
            if orig_num:
                out_file = out_dir / f"{orig_num}_{filename}.txt"
                display = f"{orig_num}_{filename}"
            else:
                out_file = out_dir / f"{filename}.txt"
                display = filename
        else:
            out_file = out_dir / "0a_intro.txt"
            display = "0a_intro"

        text = '\n'.join(sec["content"]).strip()
        if text:
            out_file.write_text(text, encoding='utf-8')
            print(f"  {display}")

def get_all_folders(base="batch_output_FINAL"):
    """Get all paper folders in the base directory."""
    base_path = Path(base)
    if not base_path.exists():
        print(f"Error: {base} does not exist")
        return []

    folders = sorted([f for f in base_path.iterdir() if f.is_dir()])
    if not folders:
        print(f"No folders in {base}")
        return []

    return folders

if __name__ == "__main__":
    folders = get_all_folders()

    if not folders:
        print("No papers found to process")
    else:
        print(f"Found {len(folders)} papers to process\n")
        print("=" * 80)

        for idx, folder in enumerate(folders, 1):
            print(f"\n[{idx}/{len(folders)}] Processing: {folder.name}")
            print("-" * 80)

            content, name = combine_files(folder)
            if content:
                print("=" * 80)
                extract_sections(content, name)

            print()

        print("\n" + "=" * 80)
        print(f"Completed processing {len(folders)} papers")
