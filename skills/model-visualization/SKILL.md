---
name: model-visualization
description: Generate visual diagrams of neural network architectures using Graphviz, including full parameter counts and hierarchical structure visualization for transformer models.
---

# Model Visualization Skill

## When to Use

Use this skill when you need to:
- Visualize neural network model architecture
- Generate diagrams showing parameter counts for each module
- Create hierarchical graphs of transformer models
- Produce publication-quality architecture diagrams
- Understand or document model structure

## Available Visualization Tools

### 1. Full Architecture Graph (Graphviz)
Creates hierarchical diagram with:
- All model modules and submodules
- Parameter counts (total and trainable) for each component
- Layer-by-layer breakdown of transformer encoder
- PNG output at high resolution

**Script**: `scripts/visualize_model_arch.py`

**Usage**:
```bash
python model_visu/visualize_model_arch.py
```

**Output**: `model_visu/outputs/Transformer_full_architecture.png`

### 2. Flexible Architecture Graph (Multi-mode)
Supports two visualization modes:
- **Simple mode**: Module hierarchy with configurable depth
- **Autograd mode**: Detailed computation graph using torchviz

**Script**: `scripts/visualize_transformer.py`

**Usage**:
```bash
# Simple hierarchical graph (default, max depth 2)
python model_visu/visualize_transformer.py

# Autograd computation graph
python model_visu/visualize_transformer.py --graph-type autograd

# Custom depth and output name
python model_visu/visualize_transformer.py --max-depth 3 --output-name CustomArch
```

**Arguments**:
- `--config`: Path to config YAML (default: `config/config.yaml`)
- `--outdir`: Output directory (default: `model_visu/outputs`)
- `--graph-type`: `simple` or `autograd` (default: `simple`)
- `--max-depth`: Max depth for simple graph (default: 2)
- `--output-name`: Base filename for output (default: `Transformer_full_architecture`)

## Requirements

### Python Packages
- `torch` - PyTorch for model instantiation
- `pyyaml` - Config file parsing
- `graphviz` - Python package for graph generation
- `torchviz` - (Optional) For autograd visualization

Install with:
```bash
pip install torch pyyaml graphviz
pip install torchviz  # Optional, for autograd mode
```

### System Dependencies
- **Graphviz binaries** must be installed and on PATH
- Download from: https://graphviz.org/download/

## Key Features

✓ Automatic parameter counting (total and trainable)
✓ Hierarchical module structure visualization
✓ Supports custom model architectures from config
✓ High-resolution PNG output (suitable for papers/presentations)
✓ Text summary generation alongside graphs
✓ Configurable depth and output names

## Output Files

Both scripts generate:
1. **Graph image**: `.png` file with architecture diagram
2. **Text summary**: `model_summary.txt` with parameter counts and model structure

## Common Use Cases

1. **Quick architecture overview**: Use default settings
2. **Detailed layer inspection**: Use `--max-depth 3` or higher
3. **Computation graph**: Use `--graph-type autograd` to see backward pass
4. **Custom model configs**: Modify `config/config.yaml` and regenerate

## Notes

- Scripts load model configuration from `config/config.yaml`
- Vocabulary size is computed from config or mesh settings
- Models are instantiated but not trained (structure visualization only)
- Output directory is created automatically if it doesn't exist
