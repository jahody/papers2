# 2D Plot Templates

## Line Plot

```python
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=df, x='x', y='y', ax=ax)
ax.set_title('Title', fontsize=14, fontweight='bold')
ax.set_xlabel('X Label', fontsize=12, fontweight='bold')
ax.set_ylabel('Y Label', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'plot.png'), dpi=300, bbox_inches='tight')
plt.close()
```

## Scatter Plot

```python
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df, x='x', y='y', hue='category', s=80, alpha=0.6, ax=ax)
ax.set_title('Title', fontsize=14, fontweight='bold')
ax.set_xlabel('X Label', fontsize=12, fontweight='bold')
ax.set_ylabel('Y Label', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'plot.png'), dpi=300, bbox_inches='tight')
plt.close()
```

## Bar Plot

```python
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df, x='category', y='value', hue='category',
            palette=PALETTE, ax=ax, legend=False)
ax.set_title('Title', fontsize=14, fontweight='bold')
ax.set_xlabel('Category', fontsize=12, fontweight='bold')
ax.set_ylabel('Value', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'plot.png'), dpi=300, bbox_inches='tight')
plt.close()
```

## Box Plot

```python
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='category', y='value', hue='category',
            palette=PALETTE, ax=ax, legend=False)
ax.set_title('Title', fontsize=14, fontweight='bold')
ax.set_xlabel('Category', fontsize=12, fontweight='bold')
ax.set_ylabel('Value', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'plot.png'), dpi=300, bbox_inches='tight')
plt.close()
```

## Heatmap

```python
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(data, cmap=PALETTE, center=0, annot=True,
            fmt='.2f', ax=ax, cbar_kws={'shrink': 0.8})
ax.set_title('Title', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'plot.png'), dpi=300, bbox_inches='tight')
plt.close()
```
