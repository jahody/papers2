# 3D Plot Template

**Important**: Seaborn doesn't natively support 3D plots. Combine Matplotlib's 3D functionality with Seaborn colors.

## 3D Scatter Plot

```python
from mpl_toolkits.mplot3d import Axes3D

# Create 3D figure
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

# Get Seaborn colors
colors = sns.color_palette(PALETTE, n_colors=len(unique_categories))
color_map = {cat: colors[i] for i, cat in enumerate(unique_categories)}

# Plot with Seaborn colors
for category in unique_categories:
    mask = data['category'] == category
    ax.scatter(x[mask], y[mask], z[mask],
              c=[color_map[category]],
              label=category,
              s=80,
              alpha=0.6,
              edgecolors='black',
              linewidth=0.5)

# Style 3D axes to match Seaborn
ax.xaxis.pane.fill = True
ax.yaxis.pane.fill = True
ax.zaxis.pane.fill = True
ax.xaxis.pane.set_facecolor('white')
ax.yaxis.pane.set_facecolor('white')
ax.zaxis.pane.set_facecolor('white')
ax.xaxis.pane.set_alpha(0.8)
ax.yaxis.pane.set_alpha(0.8)
ax.zaxis.pane.set_alpha(0.8)
ax.grid(True, alpha=0.3)

ax.set_xlabel('X', fontsize=11, fontweight='bold', labelpad=10)
ax.set_ylabel('Y', fontsize=11, fontweight='bold', labelpad=10)
ax.set_zlabel('Z', fontsize=11, fontweight='bold', labelpad=10)
ax.set_title('Title', fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper left')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'plot.png'), dpi=300, bbox_inches='tight')
plt.close()
```
