import os
import argparse
from typing import Any, Dict, Tuple

import torch

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from exc


# Local imports
from model.architecture.model_transformer import TransformerModel


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def compute_vocab_size(cfg: Dict[str, Any]) -> int:
    vocab_size = cfg.get("model", {}).get("vocab_size")
    if vocab_size is not None:
        return int(vocab_size)
    mesh = cfg.get("graph_generation", {}).get("sphere_mesh", {})
    num_horizontal = int(mesh.get("num_horizontal", 0))
    num_vertical = int(mesh.get("num_vertical", 0))
    # Consistent with train.py: +2 for special tokens
    return num_horizontal * num_vertical + 2


def build_model_from_cfg(cfg: Dict[str, Any]) -> TransformerModel:
    model_cfg = cfg.get("model", {})
    vocab_size = compute_vocab_size(cfg)

    return TransformerModel(
        vocab_size=vocab_size,
        d_model=int(model_cfg.get("d_model", 64)),
        num_heads=int(model_cfg.get("num_heads", 4)),
        num_layers=int(model_cfg.get("num_layers", 6)),
        d_ff=int(model_cfg.get("d_ff", 256)),
        max_seq_length=int(model_cfg.get("max_seq_length", 128)),
        dropout=float(model_cfg.get("dropout", 0.1)),
    )


def _count_params(module: torch.nn.Module) -> Tuple[int, int]:
    total = sum(p.numel() for p in module.parameters())
    trainable = sum(p.numel() for p in module.parameters() if p.requires_grad)
    return total, trainable


def generate_simple_architecture_graph(
    model: TransformerModel,
    out_dir: str,
    filename: str = "transformer_arch_simple",
    max_depth: int = 2,
) -> str:
    try:
        from graphviz import Digraph  # type: ignore
    except Exception:
        return ""

    def add_module_nodes(dot: "Digraph", module: torch.nn.Module, name: str, depth: int) -> None:
        total, trainable = _count_params(module)
        label = f"{name}\n{module.__class__.__name__}\nparams: {total:,} ({trainable:,} trainable)"
        dot.node(name, label=label, shape="record")
        if depth >= max_depth:
            return
        for child_name, child in module.named_children():
            child_full_name = f"{name}.{child_name}"
            dot.edge(name, child_full_name)
            add_module_nodes(dot, child, child_full_name, depth + 1)

    dot = Digraph(comment="Transformer Architecture", format="png")
    dot.attr(rankdir="LR")
    add_module_nodes(dot, model, "model", 0)

    os.makedirs(out_dir, exist_ok=True)
    # normalize filename (strip .png if present)
    if filename.lower().endswith(".png"):
        filename = filename[:-4]
    out_path = os.path.join(out_dir, filename)
    try:
        dot.render(out_path, cleanup=True)
        return out_path + ".png"
    except Exception:
        return ""


def try_torchviz_graph(model: TransformerModel, max_seq_length: int, out_dir: str, filename: str = "transformer_graph") -> str:
    try:
        from torchviz import make_dot  # type: ignore
    except Exception:
        return ""  # torchviz not available

    model.eval()
    device = torch.device("cpu")
    model.to(device)

    # Use a small batch and full seq length to show positional path
    dummy_input = torch.zeros(1, max_seq_length, dtype=torch.long, device=device)
    # forward produces logits (batch, seq, vocab)
    logits = model(dummy_input)

    dot = make_dot(
        logits,
        params=dict(list(model.named_parameters())),
    )

    os.makedirs(out_dir, exist_ok=True)
    # normalize filename (strip .png if present)
    if filename.lower().endswith(".png"):
        filename = filename[:-4]
    out_path = os.path.join(out_dir, filename)
    # Produces .png by default if graphviz is installed; otherwise .pdf/.dot depending on env
    dot.format = "png"
    try:
        dot.render(out_path, cleanup=True)
        return out_path + ".png"
    except Exception:
        # Graphviz system binaries (e.g., 'dot') likely missing from PATH
        return ""


def write_text_summary(model: TransformerModel, out_dir: str, filename: str = "model_summary.txt") -> str:
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    lines = []
    lines.append("Transformer Model Summary")
    lines.append("========================\n")
    lines.append(repr(model))
    lines.append("\n")
    lines.append(f"Total parameters: {total_params:,}")
    lines.append(f"Trainable parameters: {trainable_params:,}")
    lines.append(f"Non-trainable parameters: {total_params - trainable_params:,}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize Transformer model architecture.")
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join("config", "config.yaml"),
        help="Path to YAML config (default: config/config.yaml)",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=os.path.join("model_visu", "outputs"),
        help="Output directory for visualizations and summaries",
    )
    parser.add_argument(
        "--graph-type",
        type=str,
        choices=["simple", "autograd"],
        default="simple",
        help="Type of graph to render: simple module hierarchy or detailed autograd",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Max depth for simple module hierarchy graph (default: 2)",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="Transformer_full_architecture",
        help="Base filename for the output image (default: Transformer_full_architecture)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_yaml_config(args.config)
    model = build_model_from_cfg(cfg)

    # Always write a textual summary
    summary_path = write_text_summary(model, args.outdir)

    # Generate graph
    graph_img_path = ""
    if args.graph_type == "simple":
        graph_img_path = generate_simple_architecture_graph(
            model, args.outdir, filename=args.output_name, max_depth=args.max_depth
        )
    else:
        max_seq_length = int(cfg.get("model", {}).get("max_seq_length", 128))
        graph_img_path = try_torchviz_graph(model, max_seq_length, args.outdir, filename=args.output_name)

    print(f"Summary written to: {summary_path}")
    if graph_img_path:
        print(f"Graph image written to: {graph_img_path}")
    else:
        print("Graph image skipped. For simple graph, ensure 'graphviz' Python package and Graphviz binaries are installed.\n"
              "For autograd graph, also install 'torchviz': pip install torchviz graphviz\n"
              "Graphviz binaries: https://graphviz.org/download/")


if __name__ == "__main__":
    main()


