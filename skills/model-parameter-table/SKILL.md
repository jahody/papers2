---
name: Model Parameter Table Skill
description: >-
  Standardize how model parameters are presented by using the suggested markdown
  table structure defined in references. Trigger this skill whenever model
  parameters, hyperparameters, architectures, training configs, learning rate
  schedules, regularization, or special configuration details are requested
  or displayed.
---

# Model Parameter Table Skill

## Purpose

This skill ensures consistent presentation of model parameters using a table schema with predefined sections.

## Usage

When presenting model parameters:

1. **Use the canonical table skeleton** from `references/table_example.md`
2. **Column headers**: `Parameter | Model1 | Model2`
   - Replace `Model1`/`Model2` with actual model names
   - If only one model, use single column: `Parameter | ModelName`
3. **Fill known values only** - use `-` for unknown/unspecified values
4. **Optianal parameters** - add or remove sections or parameters when desirable

## Sections (in order)

1. **Model Architecture** - embedding dim, layers, heads, dropout, positional embeddings, feed-forward dimension, max sequence length
2. **Architecture Type** - base architecture, message passing, attention mechanisms, graph structure encoding
3. **Special Features** - graph awareness, embeddings, algorithm mimicry, attention mechanisms
4. **Training Configuration** - optimizer, learning rate, weight decay, batch size, epochs, warmup
5. **Initialization** - weight initialization, bias initialization, embedding initialization, scaling
6. **Learning Rate Schedule** - scheduler type, cycle length, decay factors
7. **Regularization** - EMA decay, gradient clipping, dropout locations
8. **Special Configuration** - special tokens, causal masking, graph file paths, attention mask support, other custom settings

## Reference Files

- `references/table_example.md` - Example with sample values

## Key Rules

✓ Always use markdown table format
✓ Follow row order from example
✓ Include all sections even if values are `-`
✓ Keep formatting consistent across all tables
✓ Do not include summaries or descriptions outside the table
✓ Present only the table itself
