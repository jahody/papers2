import os
import sys
from typing import Any, Dict, Tuple

import torch

try:
    import yaml
except Exception as exc:
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from exc

try:
    from graphviz import Digraph  # Python package; requires Graphviz binaries installed
except Exception as exc:
    Digraph = None  # type: ignore


# Local import of model
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


def render_full_architecture_png(model: TransformerModel, out_path_png: str) -> str:
    if Digraph is None:
        print("graphviz Python package missing. Install with: pip install graphviz", file=sys.stderr)
        return ""

    dot = Digraph(comment="Transformer Full Architecture", format="png")
    dot.attr(rankdir="LR")

    # Root node
    total, trainable = _count_params(model)
    root_name = "model"
    root_label = f"{root_name}{model.__class__.__name__}\\nparams: {total:,} ({trainable:,} trainable)"
    dot.node(root_name, label=root_label, shape="box")

    # Child modules
    children = {
        "embedding": model.embedding,
        "pos_encoding": model.pos_encoding,
        "transformer": model.transformer,
        "output_projection": model.output_projection,
        "dropout": model.dropout,
    }

    for child_name, child in children.items():
        ctot, ctrain = _count_params(child)
        label = f"model.{child_name}{child.__class__.__name__}\\nparams: {ctot:,} ({ctrain:,} trainable)"
        dot.node(f"model.{child_name}", label=label, shape="box")
        dot.edge(root_name, f"model.{child_name}")

    # Expand encoder layers list
    if hasattr(model.transformer, "layers"):
        layers = list(model.transformer.layers)
        for idx, layer in enumerate(layers):
            ltot, ltrain = _count_params(layer)
            lname = f"model.transformer.layers.{idx}"
            llabel = f"{lname}{layer.__class__.__name__}\\nparams: {ltot:,} ({ltrain:,} trainable)"
            dot.node(lname, label=llabel, shape="box")
            dot.edge("model.transformer.layers", lname)

        # Add aggregate node for ModuleList similar to screenshot
        mltot, mltrain = _count_params(model.transformer.layers)
        mlname = "model.transformer.layers"
        mllabel = f"{mlname}ModuleList\\nparams: {mltot:,} ({mltrain:,} trainable)"
        dot.node(mlname, label=mllabel, shape="box")
        dot.edge("model.transformer", mlname)

    # Ensure directory and render
    os.makedirs(os.path.dirname(out_path_png), exist_ok=True)
    base, ext = os.path.splitext(out_path_png)
    try:
        dot.render(base, cleanup=True)
        return base + ".png"
    except Exception:
        return ""


def main() -> None:
    # Defaults
    config_path = os.path.join("config", "config.yaml")
    out_dir = os.path.join("model_visu", "outputs")
    out_png = os.path.join(out_dir, "Transformer_full_architecture.png")

    cfg = load_yaml_config(config_path)
    model = build_model_from_cfg(cfg)

    result = render_full_architecture_png(model, out_png)
    if result:
        print(f"Graph image written to: {result}")
    else:
        print("Failed to render image. Ensure 'graphviz' Python package and Graphviz binaries are installed and on PATH.")


if __name__ == "__main__":
    main()







