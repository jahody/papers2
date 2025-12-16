"""
Export basic graph types with consistent style and palette.
Includes: line plot, scatter plot, bar plot, box plot, and 3D scatter plot.
"""

import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import os

# Set random seed for reproducibility
np.random.seed(42)

# Configuration
OUTPUT_DIR = 'seaborn_images'
STYLE = 'whitegrid'
PALETTE = 'deep'

# Set consistent style and palette
sns.set_style(STYLE)
sns.set_palette(PALETTE)


def generate_data():
    """Generate sample data for all plots."""
    # Line plot data
    x = np.linspace(0, 10, 100)
    y_line = np.sin(x) + np.random.normal(0, 0.1, 100)

    # Scatter plot data
    n_points = 100
    x_scatter = np.random.randn(n_points)
    y_scatter = 2 * x_scatter + np.random.randn(n_points) * 0.5

    # Bar plot data
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [45, 67, 52, 78, 61]

    # Box plot data
    df_box = pd.DataFrame({
        'Category': np.repeat(['Group 1', 'Group 2', 'Group 3'], 50),
        'Value': np.concatenate([
            np.random.normal(50, 10, 50),
            np.random.normal(60, 15, 50),
            np.random.normal(55, 12, 50)
        ])
    })

    # 3D scatter plot data
    n_3d = 100
    x_3d = np.random.randn(n_3d)
    y_3d = np.random.randn(n_3d)
    z_3d = np.random.randn(n_3d)
    categories_3d = np.random.choice(['Category A', 'Category B', 'Category C'], n_3d)

    return {
        'line': (x, y_line),
        'scatter': (x_scatter, y_scatter),
        'bar': (categories, values),
        'box': df_box,
        '3d': (x_3d, y_3d, z_3d, categories_3d)
    }


def plot_line_graph(data, output_dir):
    """Create and save line plot."""
    x, y = data['line']

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, linewidth=2.5, label='sin(x) + noise')
    ax.set_xlabel('X', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y', fontsize=12, fontweight='bold')
    ax.set_title('Line Plot', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'line_plot.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  [OK] Line plot saved")


def plot_scatter_graph(data, output_dir):
    """Create and save scatter plot."""
    x, y = data['scatter']

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, y, s=80, alpha=0.6, edgecolors='black', linewidth=0.5)
    ax.set_xlabel('X', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y', fontsize=12, fontweight='bold')
    ax.set_title('Scatter Plot', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Add trend line
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(x, p(x), "r--", alpha=0.8, linewidth=2, label=f'y={z[0]:.2f}x+{z[1]:.2f}')
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'scatter_plot.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  [OK] Scatter plot saved")


def plot_bar_graph(data, output_dir):
    """Create and save bar plot."""
    categories, values = data['bar']

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, values, width=0.6, edgecolor='black', linewidth=1.2)

    # Color bars using the palette
    colors = sns.color_palette(PALETTE, n_colors=len(categories))
    for bar, color in zip(bars, colors):
        bar.set_color(color)

    ax.set_xlabel('Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Value', fontsize=12, fontweight='bold')
    ax.set_title('Bar Plot', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bar_plot.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  [OK] Bar plot saved")


def plot_box_graph(data, output_dir):
    """Create and save box plot."""
    df = data['box']

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df, x='Category', y='Value', hue='Category',
                palette=PALETTE, ax=ax, legend=False)

    ax.set_xlabel('Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Value', fontsize=12, fontweight='bold')
    ax.set_title('Box Plot', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'box_plot.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  [OK] Box plot saved")


def plot_3d_scatter_graph(data, output_dir):
    """Create and save 3D scatter plot."""
    x, y, z, categories = data['3d']

    # Apply seaborn style to 3D plot
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    # Get colors from seaborn palette
    unique_categories = np.unique(categories)
    colors = sns.color_palette(PALETTE, n_colors=len(unique_categories))
    color_map = {cat: colors[i] for i, cat in enumerate(unique_categories)}

    # Plot each category with different color
    for category in unique_categories:
        mask = categories == category
        ax.scatter(x[mask], y[mask], z[mask],
                  c=[color_map[category]],
                  label=category,
                  s=80,
                  alpha=0.6,
                  edgecolors='black',
                  linewidth=0.5)

    ax.set_xlabel('X', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_ylabel('Y', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_zlabel('Z', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_title('3D Scatter Plot', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=10)

    # Set background color to match seaborn style
    ax.xaxis.pane.fill = True
    ax.yaxis.pane.fill = True
    ax.zaxis.pane.fill = True
    ax.xaxis.pane.set_facecolor('white')
    ax.yaxis.pane.set_facecolor('white')
    ax.zaxis.pane.set_facecolor('white')
    ax.xaxis.pane.set_alpha(0.8)
    ax.yaxis.pane.set_alpha(0.8)
    ax.zaxis.pane.set_alpha(0.8)

    # Grid
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '3d_scatter_plot.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  [OK] 3D scatter plot saved")


def main():
    """Generate all basic graphs."""
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Generating basic graphs with style='{STYLE}' and palette='{PALETTE}'...")
    print(f"Output directory: {OUTPUT_DIR}\n")

    # Generate data
    data = generate_data()

    # Create all plots
    plot_line_graph(data, OUTPUT_DIR)
    plot_scatter_graph(data, OUTPUT_DIR)
    plot_bar_graph(data, OUTPUT_DIR)
    plot_box_graph(data, OUTPUT_DIR)
    plot_3d_scatter_graph(data, OUTPUT_DIR)

    print(f"\n[SUCCESS] All graphs exported successfully to '{OUTPUT_DIR}/' directory!")
    print("\nGenerated files:")
    print("  - line_plot.png")
    print("  - scatter_plot.png")
    print("  - bar_plot.png")
    print("  - box_plot.png")
    print("  - 3d_scatter_plot.png")


if __name__ == "__main__":
    main()
