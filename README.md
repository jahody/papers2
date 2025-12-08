# Paper Analysis Toolset

- `sections.py`: Combines page-level text files from `batch_output_FINAL` and splits them into logical sections (saved to `paper_sections/`).
- `idea.py`: Extracts the main idea and contribution summaries from the paper abstracts.
- `references.py`: Heuristic tool to clean and format raw reference text blobs into structured lists.
- `graph.py`: Builds a citation network from the processed papers. Exports analysis to `paper_graph/` as JSON and Graphviz DOT files.
- `dataset.py`: Scans the processed text in `paper_sections/` to identify mentions of known datasets and benchmarks (e.g., SATLIB, DIMACS).
