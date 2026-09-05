"""
AISensorEdgeComp TS-FM training pipeline.

Pretrains a 350M-parameter time-series foundation model on industrial corpora.
See ml/README.md for full design.

Usage:
  python -m ml.training.train_ts_fm --config ml/training/config.yaml
"""
import argparse
import logging
import os
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .dataset import IndustrialTSDataset
from .model import TSFM, TSFMConfig
from .trainer import Trainer, TrainerConfig

log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="ml/training/config.yaml")
    p.add_argument("--output", default="ml/models/ts-fm-v1")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--epochs", type=int, default=10)
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # ── 1. Dataset ─────────────────────────────────────────────────────
    log.info("Loading training data...")
    train_ds = IndustrialTSDataset(
        sources=[
            "data/nasa_bearings/*.parquet",
            "data/cwru/*.parquet",
            "data/secom/*.parquet",
            "data/uci_gas_turbine/*.parquet",
            "data/arpa_e_grid/*.parquet",
        ],
        window_size=512,
        stride=64,
    )
    train_dl = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=4)

    # ── 2. Model ───────────────────────────────────────────────────────
    config = TSFMConfig(
        vocab_size=1024,         # quantile tokens
        hidden_size=1024,
        num_layers=24,
        num_heads=16,
        max_position_embeddings=512,
        dropout=0.1,
        sensor_fusion=True,      # cross-attention over multi-modal windows
        causal_aware_loss=True,  # PC algorithm validity test
    )
    model = TSFM(config).to(args.device)
    n_params = sum(p.numel() for p in model.parameters())
    log.info(f"TS-FM initialized: {n_params:,} parameters ({n_params/1e6:.1f}M)")

    # ── 3. Trainer ─────────────────────────────────────────────────────
    trainer = Trainer(
        model=model,
        train_loader=train_dl,
        config=TrainerConfig(
            output_dir=args.output,
            epochs=args.epochs,
            lr=3e-4,
            weight_decay=0.01,
            warmup_steps=1000,
            gradient_accumulation_steps=4,
            fp16=True,
        ),
    )
    trainer.train()

    # ── 4. Export to ONNX ──────────────────────────────────────────────
    onnx_path = Path(args.output) / "ts-fm-v1.onnx"
    log.info(f"Exporting to ONNX: {onnx_path}")
    model.export_onnx(onnx_path)

    log.info("Done.")


if __name__ == "__main__":
    main()
