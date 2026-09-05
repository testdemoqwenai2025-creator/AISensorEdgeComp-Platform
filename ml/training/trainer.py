"""Training loop with mixed precision + gradient accumulation."""
from dataclasses import dataclass
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.amp import autocast, GradScaler
from torch.optim.lr_scheduler import LambdaLR
import math
from structlog import get_logger

log = get_logger()


@dataclass
class TrainerConfig:
    output_dir: str
    epochs: int = 10
    lr: float = 3e-4
    weight_decay: float = 0.01
    warmup_steps: int = 1000
    gradient_accumulation_steps: int = 4
    fp16: bool = True
    log_interval: int = 50
    save_interval: int = 1000


class Trainer:
    def __init__(self, model, train_loader: DataLoader, config: TrainerConfig):
        self.model = model
        self.loader = train_loader
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = model.to(self.device)
        self.optimizer = AdamW(model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
        self.scaler = GradScaler(enabled=config.fp16)
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        self.global_step = 0

    def _lr_lambda(self, step: int) -> float:
        if step < self.config.warmup_steps:
            return step / self.config.warmup_steps
        return 0.5 * (1 + math.cos(math.pi * (step - self.config.warmup_steps) /
                                  (len(self.loader) * self.config.epochs - self.config.warmup_steps)))

    def train(self):
        log.info("trainer.start", device=self.device, epochs=self.config.epochs)
        scheduler = LambdaLR(self.optimizer, self._lr_lambda)

        for epoch in range(self.config.epochs):
            log.info("epoch.start", epoch=epoch)
            self.model.train()

            for batch_idx, batch in enumerate(self.loader):
                input_ids = batch["input_ids"].to(self.device)
                labels = batch["labels"].to(self.device)

                with autocast(device_type=self.device.split(":")[0], dtype=torch.float16, enabled=self.config.fp16):
                    outputs = self.model(input_ids=input_ids, labels=labels)
                    loss = outputs["loss"] / self.config.gradient_accumulation_steps

                self.scaler.scale(loss).backward()

                if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                    self.optimizer.zero_grad()
                    scheduler.step()
                    self.global_step += 1

                    if self.global_step % self.config.log_interval == 0:
                        log.info("step", step=self.global_step, loss=float(loss.item()),
                                 lr=scheduler.get_last_lr()[0])

                    if self.global_step % self.config.save_interval == 0:
                        self.save_checkpoint()

            log.info("epoch.end", epoch=epoch)
            self.save_checkpoint(f"epoch_{epoch+1}")

        log.info("trainer.done")

    def save_checkpoint(self, suffix: str = "latest"):
        path = Path(self.config.output_dir) / f"ts-fm-{suffix}.pt"
        torch.save({
            "model": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "global_step": self.global_step,
        }, path)
        log.info("checkpoint.saved", path=str(path))
