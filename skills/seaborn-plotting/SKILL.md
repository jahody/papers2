---
name: seaborn-plotting
description: Standardized Seaborn plotting guidelines for creating consistent, professional visualizations using predefined styles and color palettes for 2D and 3D plots.
---

# Seaborn Plotting Skill

## When to Use

Use this skill for:
- Any data visualization (line, scatter, bar, box, violin, heatmap, 3D plots)
- Applying consistent styling across multiple plots
- Generating publication-quality figures
- Ensuring color-blind accessible visualizations

## Quick Start

Every plotting script must start with this configuration:

```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Set random seed for reproducibility
np.random.seed(42)

# Configuration
STYLE = 'whitegrid'      # Background and grid style
PALETTE = 'deep'         # Color palette
OUTPUT_DIR = 'plots'

# Apply configuration
sns.set_style(STYLE)
sns.set_palette(PALETTE)
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

## Core Styling Rules

### Style Options
Choose ONE style consistently:
- `whitegrid` (default) - White background with gray gridlines
- `darkgrid` - Gray background with white gridlines
- `white` - Clean white background, no grid
- `dark` - Gray background, no grid
- `ticks` - White with tick marks only

### Palette Options

**Categorical data**: `deep` (default), `muted`, `pastel`, `bright`, `dark`, `colorblind`
**Sequential data**: `rocket`, `mako`, `viridis`, `plasma`, `inferno`
**Diverging data**: `vlag`, `icefire`, `coolwarm`, `bwr`, `seismic`

## Formatting Standards

### Required Format
- **Figure size**: (10, 6) for 2D plots, (12, 9) for 3D plots
- **Title**: fontsize=14, fontweight='bold'
- **Axis labels**: fontsize=12, fontweight='bold'
- **Grid**: alpha=0.3
- **Save DPI**: 300
- **Always call**: `plt.tight_layout()` before saving, `plt.close()` after saving

### File Naming
- Use lowercase with underscores: `line_plot.png`, `correlation_heatmap.png`
- Include plot type in filename
- Be descriptive and specific

## Pre-Flight Checklist

Before saving any plot, verify:

✓ `sns.set_style(STYLE)` is called
✓ `sns.set_palette(PALETTE)` is called
✓ Title is bold, fontsize 14
✓ Axis labels are bold, fontsize 12
✓ Grid enabled with alpha=0.3
✓ Correct figure size (10x6 or 12x9)
✓ Saved at 300 DPI with `bbox_inches='tight'`
✓ Output directory exists
✓ `plt.tight_layout()` called before saving
✓ `plt.close()` called after saving

## Reference Files

- `references/plot_templates.md` - Complete templates for all 2D plot types
- `references/3d_plotting.md` - 3D plot template using matplotlib with Seaborn colors
- `scripts/basic_graphs_export.py` - Working example with 5 essential plot types

## Common Mistakes to Avoid

❌ Using raw matplotlib without Seaborn styling
❌ Inconsistent styles/palettes across plots
❌ Forgetting to close figures (causes memory leaks)
❌ Not setting random seed (breaks reproducibility)
❌ Mixing different font sizes across plots
❌ Saving at low DPI (<300)
❌ Creating 3D plots without applying Seaborn colors

## Key Notes

- **Reproducibility**: Always set `np.random.seed(42)` at the start
- **Memory management**: Always call `plt.close()` after saving to free memory
- **Layout**: Use `tight_layout()` to prevent label cutoff
- **3D plots**: No native Seaborn support - manually apply Seaborn colors to matplotlib 3D plots
- **Color accessibility**: Use `colorblind` palette for accessible visualizations
