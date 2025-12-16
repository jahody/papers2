# Example Table with Sample Values

| Parameter | Model1 | Model2 |
|---|---|---|
| **Model Architecture** |  |  |
| Embedding dimension | 64 | 64 |
| Model layers | 6 | 6 |
| Number of heads | 4 | 4 |
| Dropout rate | 0.1 | 0.1 |
| Positional embeddings | Sinusoidal | Graph-aware positional + sequence pos |
| **Training Configuration** |  |  |
| Optimizer | AdamW | AdamW |
| Learning rate | 1e-4 | 1e-4 |
| Weight decay | 1e-5 | 1e-5 |
| Batch size | 125 | 125 |
| Epochs | 30 | 30 |
| Warmup steps | 300 | 300 |
| **Learning Rate Schedule** |  |  |
| Scheduler | Linear warmup → Cosine annealing | Linear warmup → Cosine annealing |
| Cycle length | – | – |
| Peak decay factor | – | – |
| Min LR factor | – | – |
| **Regularization** |  |  |
| EMA decay | – | – |
| Gradient clipping | 1.0 | 1.0 |
| **Special Configuration** |  |  |
| Special tokens | – | – |
