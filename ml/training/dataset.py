"""Industrial time-series dataset loader."""
import glob
from pathlib import Path
import torch
from torch.utils.data import Dataset
import pyarrow.parquet as pq
import numpy as np


class IndustrialTSDataset(Dataset):
    """Loads industrial time-series from Parquet, windowed.

    Each item: dict with 'input_ids' (window of quantile tokens) and
    'labels' (next-window tokens, for forecasting objective).
    """

    def __init__(self, sources: list[str], window_size: int = 512, stride: int = 64):
        self.window_size = window_size
        self.stride = stride
        self.files = []
        for pattern in sources:
            self.files.extend(glob.glob(pattern))
        if not self.files:
            raise RuntimeError(f"No training files found matching: {sources}")
        # In production: pre-tokenize and cache
        self._cache: dict[int, np.ndarray] = {}

    def __len__(self) -> int:
        # Approximate; in production: pre-compute and cache
        return len(self.files) * 100

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        if idx not in self._cache:
            file_idx = idx % len(self.files)
            df = pq.read_table(self.files[file_idx]).to_pandas()
            # In production: tokenize via quantile tokenizer
            self._cache[idx] = df.select_dtypes(include=[np.number]).values[: self.window_size]
        window = self._cache[idx]
        input_ids = torch.tensor(window[:-1], dtype=torch.long)
        labels = torch.tensor(window[1:], dtype=torch.long)
        return {"input_ids": input_ids, "labels": labels}
