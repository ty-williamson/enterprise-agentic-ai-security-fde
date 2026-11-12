"""
Vision Transformer (ViT) vs. Convolutional Neural Network (CNN) Benchmark on Fashion-MNIST
Author: Ty Williamson (2026 NSF AI-EDGE Institute — Practical Transformer Architectures)

Implements:
1. Patch Embedding: Splits 28x28 images into 4x4 patches (L=49), prepends learnable [CLS] token (L+1=50), and adds learnable Positional Encoding.
2. Transformer Encoder Block: Pre-LayerNorm -> Multi-Head Self-Attention (Q, K, V) -> Residual (+) -> LayerNorm -> FFN (Dense1 -> GELU -> Dense2 -> Dropout) -> Residual (+).
3. Baseline CNN: 2D Convolutional feature extraction + MaxPool2d dimensionality reduction + MLP Classifier.
4. Comparative Evaluation Pipeline logging Epoch Latency, Training Loss, and Test Accuracy.
"""

import argparse
import time
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

try:
    from torchvision import datasets, transforms
    TORCHVISION_AVAILABLE = True
except ImportError:
    TORCHVISION_AVAILABLE = False


# =====================================================================
# 1. VISION TRANSFORMER (ViT) ARCHITECTURE (OSU AI-EDGE WEEK 4)
# =====================================================================

class PatchEmbedding(nn.Module):
    """
    Splits a [B, C, H, W] image into flattened patches of shape [B, L, d],
    prepends a learnable [CLS] token -> [B, L+1, d], and adds Positional Encoding.
    """

    def __init__(
        self,
        img_size: int = 28,
        patch_size: int = 4,
        in_channels: int = 1,
        embed_dim: int = 64,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.num_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(
            in_channels, embed_dim, kernel_size=patch_size, stride=patch_size
        )
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(
            torch.randn(1, self.num_patches + 1, embed_dim) * 0.02
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        # [B, C, H, W] -> [B, d, H/P, W/P] -> [B, d, L] -> [B, L, d]
        x = self.proj(x).flatten(2).transpose(1, 2)
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        # Prepend [CLS] token: shape becomes [B, L+1, d]
        x = torch.cat((cls_tokens, x), dim=1)
        x = x + self.pos_embed
        return self.dropout(x)


class TransformerEncoderBlock(nn.Module):
    """
    Single Transformer Encoder Block:
    t1 = LayerNorm(x)
    t2 = MultiHeadAttention(t1)
    t3 = t2 + x                   (Residual Stream 1)
    t4 = LayerNorm(t3)
    t5 = FFN_GELU(t4)
    h  = t5 + t3                  (Residual Stream 2)
    """

    def __init__(
        self,
        embed_dim: int = 64,
        num_heads: int = 4,
        mlp_ratio: float = 2.0,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = nn.MultiheadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.norm2 = nn.LayerNorm(embed_dim)
        hidden_dim = int(embed_dim * mlp_ratio)
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        normed_1 = self.norm1(x)
        attn_out, _ = self.attn(normed_1, normed_1, normed_1)
        x = x + attn_out
        x = x + self.ffn(self.norm2(x))
        return x


class VisionTransformerViT(nn.Module):
    """Complete Vision Transformer (ViT) for Fashion-MNIST 10-Class Classification."""

    def __init__(
        self,
        img_size: int = 28,
        patch_size: int = 4,
        in_channels: int = 1,
        num_classes: int = 10,
        embed_dim: int = 64,
        depth: int = 4,
        num_heads: int = 4,
        mlp_ratio: float = 2.0,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.patch_embed = PatchEmbedding(
            img_size, patch_size, in_channels, embed_dim, dropout
        )
        self.encoder = nn.Sequential(
            *[
                TransformerEncoderBlock(embed_dim, num_heads, mlp_ratio, dropout)
                for _ in range(depth)
            ]
        )
        self.norm = nn.LayerNorm(embed_dim)
        self.head = nn.Linear(embed_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.patch_embed(x)
        x = self.encoder(x)
        x = self.norm(x)
        # Extract the [CLS] token representation at index 0 for classification
        cls_output = x[:, 0]
        return self.head(cls_output)


# =====================================================================
# 2. BASELINE CONVOLUTIONAL NEURAL NETWORK (CNN) (OSU AI-EDGE WEEK 1/3)
# =====================================================================

class BaselineCNN(nn.Module):
    """Baseline CNN using 2D Convolutions, ReLU, MaxPooling, and Fully Connected Layers."""

    def __init__(self, num_classes: int = 10) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


# =====================================================================
# 3. TRAINING & COMPARATIVE EVALUATION PIPELINE
# =====================================================================

def get_dataloaders(batch_size: int = 128, dry_run: bool = False) -> Tuple[DataLoader, DataLoader]:
    if dry_run or not TORCHVISION_AVAILABLE:
        x_train = torch.randn(512, 1, 28, 28)
        y_train = torch.randint(0, 10, (512,))
        x_test = torch.randn(128, 1, 28, 28)
        y_test = torch.randint(0, 10, (128,))
        return (
            DataLoader(TensorDataset(x_train, y_train), batch_size=batch_size, shuffle=True),
            DataLoader(TensorDataset(x_test, y_test), batch_size=batch_size, shuffle=False),
        )

    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.2860,), (0.3530,))]
    )
    train_ds = datasets.FashionMNIST(
        root="./data", train=True, download=True, transform=transform
    )
    test_ds = datasets.FashionMNIST(
        root="./data", train=False, download=True, transform=transform
    )
    return (
        DataLoader(train_ds, batch_size=batch_size, shuffle=True),
        DataLoader(test_ds, batch_size=batch_size, shuffle=False),
    )


def train_and_evaluate(
    model: nn.Module,
    model_name: str,
    train_loader: DataLoader,
    test_loader: DataLoader,
    epochs: int,
    lr: float,
    device: torch.device,
) -> List[Dict[str, float]]:
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    history: List[Dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        start_t = time.perf_counter()
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * images.size(0)

        train_loss = running_loss / len(train_loader.dataset)

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                preds = model(images).argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        test_acc = (correct / total) * 100.0
        elapsed = time.perf_counter() - start_t
        history.append(
            {"epoch": epoch, "loss": round(train_loss, 4), "acc": round(test_acc, 2), "time_s": round(elapsed, 2)}
        )
        print(
            f"[{model_name:<8}] Epoch {epoch:02d}/{epochs:02d} | "
            f"Train Loss: {train_loss:.4f} | Test Accuracy: {test_acc:.2f}% | Latency: {elapsed:.2f}s"
        )
    return history


def main() -> None:
    parser = argparse.ArgumentParser(description="ViT vs. CNN Fashion-MNIST Benchmark")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--dry-run", action="store_true", help="Run fast synthetic verification check")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running ViT vs. CNN Evaluation Pipeline on device: {device}")
    train_loader, test_loader = get_dataloaders(args.batch_size, args.dry_run)

    vit_model = VisionTransformerViT()
    cnn_model = BaselineCNN()

    print("\n--- Training Vision Transformer (ViT) ---")
    train_and_evaluate(vit_model, "ViT", train_loader, test_loader, args.epochs, args.lr, device)

    print("\n--- Training Baseline CNN ---")
    train_and_evaluate(cnn_model, "CNN", train_loader, test_loader, args.epochs, args.lr, device)


if __name__ == "__main__":
    main()