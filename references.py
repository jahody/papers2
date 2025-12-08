
import os
import re

def split_blob(text):
    parts = []
    last_end = 0
    
    # 1. Bare Numbers
    bare_num_pattern = r'(?:^|\s)(\d+)\s+(?=[A-Z])'
    matches = list(re.finditer(bare_num_pattern, text))
    nums = []
    for m in matches:
        d = int(m.group(1))
        nums.append(d)
        
    is_seq = False
    if nums:
        increments = 0
        for i in range(len(nums)-1):
            if nums[i+1] == nums[i] + 1: increments += 1
        if len(nums) > 3 and increments > len(nums) * 0.5:
            is_seq = True
            
    if is_seq:
        current_start = matches[0].start()
        splits = []
        for i in range(len(matches)):
            m = matches[i]
            ref_start = m.start(1)
            if i > 0:
                splits.append(text[current_start:ref_start].strip())
            current_start = ref_start
        splits.append(text[current_start:].strip())
        return splits

    # 2. Strict Period Blob Splitting
    matches = list(re.finditer(r'\.\s+(?=[A-Z][a-z]+,)', text))
    if len(matches) < 3:
        matches = list(re.finditer(r'\.\s+(?=[A-Z]\.?\s+[A-Z][a-z]+)', text))
    
    if len(matches) > 2:
        for match in matches:
            end = match.end()
            if end - last_end > 20:
                parts.append(text[last_end:end].strip())
                last_end = end
        parts.append(text[last_end:].strip())
        return [p for p in parts if len(p) > 10]
        
    return [text]

def format_references(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        original_content = f.read()

    lines = [line.strip() for line in original_content.split('\n') if line.strip()]
    flat_content = ' '.join(lines)
    
    references = []
    
    # 1. Bracketed
    marker_pattern = r'\[(?:[A-Z][A-Z0-9+]*\d{2}|\d+|[^\]]+, \d{4})\]'
    markers = re.findall(marker_pattern, flat_content)
    if len(markers) > 2:
        clean_content = re.sub(r'^REFERENCES\s*', '', flat_content, flags=re.IGNORECASE)
        parts = re.split(f'({marker_pattern})', clean_content)
        current_ref = ""
        for part in parts:
            part = part.strip()
            if not part: continue
            if re.match(marker_pattern, part):
                if current_ref: references.append(current_ref)
                current_ref = part
            else:
                current_ref += " " + part
        if current_ref: references.append(current_ref)

    # 2. Numbered 1. 2. 
    if not references:
        num_pattern = r'(?:^|\s)(\d{1,3}\.)\s+(?=[A-Z])'
        num_matches = re.findall(num_pattern, flat_content)
        nums = []
        for m in num_matches:
            d = re.findall(r'\d+', m)
            if d: nums.append(int(d[0]))
        is_seq = False
        if nums and (nums[0] == 1 or nums[0] == 0):
             seq_count = 0
             for i in range(len(nums)-1):
                 if nums[i+1] == nums[i] + 1: seq_count += 1
             if seq_count > len(nums) * 0.7:
                 is_seq = True
        
        if len(num_matches) > 3 and is_seq:
             parts = re.split(num_pattern, flat_content)
             for i in range(1, len(parts), 2):
                 ref_num = parts[i].strip()
                 ref_text = parts[i+1].strip() if i+1 < len(parts) else ""
                 references.append(f"{ref_num} {ref_text}")

    # 3. Existing Newlines with Blob Check
    if not references:
        bare_seq_check = re.findall(r'(?:^|\s)(\d+)\s+(?=[A-Z])', flat_content)
        bare_nums = [int(x) for x in bare_seq_check]
        is_bare_seq = False
        if len(bare_nums) > 5:
            inc = 0
            for i in range(len(bare_nums)-1):
                if bare_nums[i+1] == bare_nums[i] + 1: inc += 1
            if inc > len(bare_nums) * 0.6:
                is_bare_seq = True
        
        if is_bare_seq:
            references = split_blob(flat_content)
        else:
            candidates = []
            for line in lines:
                if len(line) > 350:
                    candidates.extend(split_blob(line))
                else:
                    candidates.append(line)
            valid = [c for c in candidates if len(c) > 20 and c.lower() != "references"]
            if len(valid) > 2:
                references = valid

    # 4. Fallback
    if not references:
        references = split_blob(flat_content)

    # Post-processing: Merge lines that are likely continuations
    if references:
        merged = []
        if references:
            merged.append(references[0])
            for i in range(1, len(references)):
                curr = references[i].strip()
                prev = merged[-1]
                if len(curr) > 0 and curr[0].islower():
                    merged[-1] = prev + " " + curr
                else:
                    merged.append(curr)
        references = merged

    # Final Validation: Ensure each reference looks valid (has year or standard keywords)
    valid_refs = []
    if references:
        for ref in references:
            # 1. Length Check
            if len(ref) < 10: continue
            
            # 2. Year Check (19xx or 20xx)
            has_year = re.search(r'(?:19|20)\d{2}', ref)
            
            # 3. Keyword Check (for papers 'to appear', etc)
            is_special = "in press" in ref.lower() or "to appear" in ref.lower() or "arxiv" in ref.lower()
            
            if has_year or is_special:
                valid_refs.append(ref)
    
    references = valid_refs

    with open(output_file, 'w', encoding='utf-8') as f:
        if references:
            for ref in references:
                clean_ref = re.sub(r'\s+', ' ', ref).strip()
                f.write(clean_ref + '\n')
        else:
            f.write(original_content + '\n')

def process_all_papers(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    count = 0
    print(f"Starting processing from {input_folder}")
    for root, dirs, files in os.walk(input_folder):
        ref_filename = None
        if 'References.txt' in files: ref_filename = 'References.txt'
        elif 'REFERENCES.txt' in files: ref_filename = 'REFERENCES.txt'

        if ref_filename:
            input_file = os.path.join(root, ref_filename)
            paper_name = os.path.basename(root)
            try:
                output_file = os.path.join(output_folder, f"{paper_name}_references.txt")
                print(f"Processing: {paper_name}")
                format_references(input_file, output_file)
                count += 1
            except Exception as e:
                print(f"Error {paper_name}: {e}")
    
    print(f"Done. Processed {count} files.")
    with open('references_processing_done.txt', 'w') as f:
        f.write(f"Done. Processed {count} files.")

if __name__ == "__main__":
    input_folder = r"g:\My Drive\OSU\projects\papers\paper_sections"
    output_folder = r"g:\My Drive\OSU\projects\papers\paper_references"
    process_all_papers(input_folder, output_folder)
