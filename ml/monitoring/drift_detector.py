"""
Model drift detection: monitors feature distribution shifts over time.

Implements Population Stability Index (PSI) and KS-test for feature drift,
plus a confidence-distribution monitor for prediction drift.
"""
import logging
from collections import deque
from dataclasses import dataclass, field

import numpy as np
from scipy import stats
from prometheus_client import Gauge

log = logging.getLogger(__name__)

DRIFT_SCORE = Gauge("ml_drift_score", "Model drift score", ["monitor", "sensor_kind"])


@dataclass
class DriftMonitor:
    """Tracks feature distribution drift via PSI + KS-test."""
    name: str
    window_size: int = 10_000
    baseline: np.ndarray | None = None
    recent: deque = field(default_factory=lambda: deque(maxlen=10_000))
    psi_threshold: float = 0.2  # PSI > 0.2 = significant drift

    def update(self, value: float):
        self.recent.append(value)
        if len(self.recent) < self.window_size:
            return None

        if self.baseline is None:
            self.baseline = np.array(self.recent)
            return None

        recent_arr = np.array(self.recent)
        psi = self._psi(self.baseline, recent_arr)
        ks_stat, ks_p = stats.ks_2samp(self.baseline, recent_arr)

        DRIFT_SCORE.labels(monitor=self.name, sensor_kind="all").set(psi)

        if psi > self.psi_threshold:
            log.warning(
                "drift.detected",
                monitor=self.name,
                psi=psi,
                ks_p=ks_p,
                threshold=self.psi_threshold,
            )
            return {"psi": float(psi), "ks_p": float(ks_p)}

        return None

    @staticmethod
    def _psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
        """Population Stability Index."""
        eps = 1e-6
        breakpoints = np.linspace(0, 100, bins + 1)
        expected_pct = np.percentile(expected, breakpoints)
        actual_pct = np.percentile(actual, breakpoints)
        expected_bins = np.histogram(expected, bins=expected_pct)[0] / len(expected) + eps
        actual_bins = np.histogram(actual, bins=actual_pct)[0] / len(actual) + eps
        return float(np.sum((actual_bins - expected_bins) * np.log(actual_bins / expected_bins)))
