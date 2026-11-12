# Master Operational Runbook: Cross-Platform Setup, Command Reference, Code Walkthrough & Telemetry Guide

**Repository:** `enterprise-agentic-ai-security-fde`  
**Author:** Ty Williamson | 2026 NSF AI-EDGE Summer Research Program (The Ohio State University)

This runbook is written so that any engineer, recruiter, or student—even someone starting from a brand-new laptop with zero prior setup—can configure their environment on **Windows (WSL2 or PowerShell)**, **macOS**, or **Linux**, understand what every single terminal command does, execute every pipeline, and interpret every line of output.

---

## 1. Quick-Boot Cheat Sheet (For Returning Users)

Once your virtual environment (`.venv`) is already installed, booting this project up months later requires only **3 commands**:

```bash
# 1. Navigate into the project directory
cd enterprise-agentic-ai-security-fde

# 2. Activate the isolated Python virtual environment
source .venv/bin/activate

# 3. Run the 10-Stage Multi-Agent Security Guardrail & ViT vs. CNN Benchmarks
python src/fde_multi_agent_rag_guardrail.py
python src/vit_vs_cnn_fashion_mnist_benchmark.py --dry-run --epochs 2
python src/vit_vs_cnn_fashion_mnist_benchmark.py --epochs 5
```
*(When finished, run `deactivate` to exit the `.venv` environment.)*

---

## 2. Complete First-Time Setup for Every Operating System (From Zero)

### 2.1 Windows via WSL2 + Ubuntu (Recommended Enterprise Linux Workflow)

If you are on Windows and encounter the error `HCS_E_HYPERV_NOT_INSTALLED` or `WSL2 is not supported with your current machine configuration`, complete Steps A and B once:

#### A. Enable Windows Virtual Machine Platform (Run in Windows PowerShell as Administrator)
```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
bcdedit /set hypervisorlaunchtype auto
wsl --update
```
* **`dism.exe ... VirtualMachinePlatform`:** Enables the Windows Hyper-V virtualization subsystem required by the Linux kernel in WSL2.
* **`bcdedit /set hypervisorlaunchtype auto`:** Configures the Windows boot loader to start the hypervisor automatically on system boot.
* **`wsl --update`:** Downloads the latest stable WSL2 Linux kernel from Microsoft.

#### B. Enable CPU Hardware Virtualization in BIOS/UEFI (If Disabled)
1. Reboot the machine and press `F1`, `F2`, or `Del` (on Lenovo ThinkPads, press `Enter` then `F1`) to open BIOS Setup.
2. Navigate to **Security** $\rightarrow$ **Virtualization** (or **Advanced** $\rightarrow$ **CPU Configuration**).
3. Toggle **Intel® Virtualization Technology (VT-x)** and **Intel® VT-d Feature** (or **AMD SVM Mode**) to **On / Enabled**.
4. Press `F10` to save changes and reboot into Windows.

#### C. Clone & Provision Inside Ubuntu Terminal
```bash
git clone [https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git](https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git)
cd enterprise-agentic-ai-security-fde
sudo apt update && sudo apt install -y python3-venv python3-pip
deactivate 2>/dev/null || true
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch torchvision --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
python -m pip install numpy pydantic
```

### 2.2 macOS (Apple Silicon M1/M2/M3/M4 or Intel)

Open the macOS **Terminal** app (`Cmd + Space` $\rightarrow$ type `Terminal`) and run:

```bash
git clone [https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git](https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git)
cd enterprise-agentic-ai-security-fde
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2.3 Native Windows PowerShell (Without WSL2)

Open **PowerShell** and run:

```powershell
git clone [https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git](https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git)
cd enterprise-agentic-ai-security-fde
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install torch torchvision --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
python -m pip install numpy pydantic
```

---

## 3. Dictionary of Every Terminal Command & Why We Use It

| Terminal Command | Exact Purpose & Why It Is Required |
| :--- | :--- |
| `git clone <repo-url>` | Downloads a complete local copy of the remote GitHub repository and its version history onto your machine. |
| `cd enterprise-agentic-ai-security-fde` | Changes your active shell directory into the root folder of the repository. |
| `sudo apt update && sudo apt install -y python3-venv python3-pip` | Updates Ubuntu's package list and installs `python3-venv` (creates isolated environments) and `python3-pip` (Python package installer). |
| `deactivate 2>/dev/null \|\| true` | Safely exits any currently active virtual environment without throwing an error if none is active. |
| `rm -rf .venv` | Deletes any partial or corrupted `.venv` directory created before `python3-venv` was installed. |
| `python3 -m venv .venv` | Creates an isolated Python environment inside `.venv/` so project libraries never conflict with OS packages. |
| `source .venv/bin/activate` | Activates `.venv` so `python` and `pip` point strictly inside `.venv/bin/` (indicated by `(.venv)` in your prompt). |
| `python -m pip install --upgrade pip` | Uses the active `.venv` Python binary to upgrade `pip` to the latest version, avoiding global path confusion. |
| `python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu` | Installs the lightweight (~180 MB) CPU-optimized build of PyTorch instead of the 2.5 GB NVIDIA CUDA bundle, preventing `ModuleNotFoundError: No module named 'torch'`. |
| `python -m pip install numpy pydantic` | Installs numerical array support (`numpy`) and strict data-schema validation (`pydantic`). |

---

## 4. Line-by-Line Code Architecture Walkthrough

### 4.1 `src/fde_multi_agent_rag_guardrail.py`
* **Lines 24–78 (`TraceSpan` & `ObservabilityTracer`):** Implements granular LLM observability. `estimate_tokens()` approximates subword token counts, while `record_span()` measures execution latency in milliseconds via `time.perf_counter()`, computes throughput (`tokens_per_sec`), calculates dollar cost per request using enterprise per-1M-token rates (`$0.15` input / `$0.60` output), and stores a deep-copied JSON snapshot of agent memory (`state_snapshot`).
* **Lines 85–130 (`DocumentChunk` & `LightweightVectorRAG`):** Implements a hybrid vector database supporting both **structured metadata filtering** (`metadata_filter`) and **unstructured semantic vector search**. `_embed()` hashes tokens into a 64-dimensional vector normalized to unit $L_2$ length ($\Vert{}\mathbf{v}\Vert{}_2 = 1$), and `retrieve()` ranks chunks via cosine similarity ($\mathbf{q} \cdot \mathbf{v}$).
* **Lines 137–194 (`UntrustedDataPlaneWorkerAgent`):** Operates strictly in the **Untrusted Data Plane**. It scans incoming email subjects and bodies against compiled regular expressions for **OWASP LLM01 (Indirect Prompt Injection)** payloads (`ignore previous instructions`, `archive_verification`, `CLASS{`, `forward password`, `read_write_notes`, `system override`). Because it has **zero tool bindings**, it cannot trigger external actions and outputs only a sanitized JSON dictionary.
* **Lines 197–289 (`TrustedControlPlanePlannerAgent`):** Operates in the **Trusted Control Plane** using the **Think $\rightarrow$ Act $\rightarrow$ Observe (ReAct)** loop:
  1. Delegates untrusted email ingestion to `UntrustedDataPlaneWorkerAgent`.
  2. Queries `LightweightVectorRAG` for active **NIST AI RMF** and **OWASP LLM01** security policy chunks.
  3. Executes `self_reflect_on_action()` to block any request where `owasp_llm01_detected == True` or where an external trigger attempts to access `archive_verification` (Least-Privilege Scoping).
  4. Enforces a **Human-in-the-Loop (HITL)** approval gate (`hitl_approved`) on high-privilege tools (`send_email`, `archive_verification`, `read_write_notes`).
* **Lines 296–360 (`run_10_stage_evaluation_pipeline`):** Executes the 10-stage red-team evaluation benchmark modeled on the OSU AI-EDGE Strands Mail Agent lab (`reuassign@gmail.com`) and prints the stage-by-stage telemetry table.

### 4.2 `src/vit_vs_cnn_fashion_mnist_benchmark.py`
* **Lines 31–68 (`PatchEmbedding`):** Partitions a $[B, 1, 28, 28]$ image into $L = 49$ non-overlapping $4 \times 4$ patches via a strided convolution (`Conv2d(1, 64, kernel_size=4, stride=4)`), flattens and transposes to $[B, 49, 64]$, prepends a learnable `[CLS]` classification token (`self.cls_token`) to form $[B, 50, 64]$, and adds learnable positional encodings (`self.pos_embed`).
* **Lines 71–110 (`TransformerEncoderBlock`):** Implements a pre-norm Transformer block: `LayerNorm 1` ($z$-score standardization) $\rightarrow$ `MultiheadAttention` ($h = 4$ heads) $\rightarrow$ **Residual Connection 1** (`x = x + attn_out`) $\rightarrow$ `LayerNorm 2` $\rightarrow$ **Feed-Forward Network** (`Linear(64, 128)` $\rightarrow$ `GELU()` $\rightarrow$ `Dropout(0.1)` $\rightarrow$ `Linear(128, 64)`) $\rightarrow$ **Residual Connection 2**.
* **Lines 113–149 (`VisionTransformerViT`):** Stacks 4 `TransformerEncoderBlock` layers, applies final `LayerNorm`, extracts the contextualized `[CLS]` token at index `0` (`x[:, 0]`), and projects it to 10 Fashion-MNIST class logits.
* **Lines 156–180 (`BaselineCNN`):** Implements the Week 1/3 Convolutional Neural Network baseline using two `Conv2d(3x3) + ReLU + MaxPool2d(2x2)` feature-extraction stages followed by a 2-layer fully connected classifier.
* **Lines 187–276 (`get_dataloaders`, `train_and_evaluate`, `main`):** Handles dataset loading (either fast synthetic Gaussian noise tensors via `--dry-run` or the full 60,000-image Fashion-MNIST dataset) and trains both architectures using `AdamW` and `CrossEntropyLoss`.

---

## 5. Execution & Telemetry Interpretation Guide

### 5.1 Running Pipeline #1: Multi-Agent RAG Guardrail
```bash
python src/fde_multi_agent_rag_guardrail.py
```
* **Stages 01–02 (`EXECUTED_SAFE_TOOL`):** Benign requests calling read-only discovery tools (`list_tools`, `list_inbox`) pass the Worker scan (`LLM01 Flag: False`) and execute cleanly.
* **Stages 03–08 (`BLOCKED_BY_SELF_REFLECTION`):** Six indirect prompt-injection payloads attempting to overwrite memory (`read_write_notes`), extract `CLASS{...}` (`archive_verification`), or leak passwords (`send_email`) are flagged by the Tier 1 Worker (`LLM01 Flag: True`) and blocked by the Tier 2 Planner (`100% block rate`).
* **Stage 09 vs. Stage 10 (`HELD_FOR_HITL_APPROVAL` vs. `EXECUTED_SAFE_TOOL`):** Demonstrates that even on a clean request (`LLM01 Flag: False`), high-privilege tools like `send_email` are held until explicit Human-in-the-Loop approval (`hitl_approved=True`) is provided.

### 5.2 Running Pipeline #2: Vision Transformer (ViT) vs. CNN Benchmark

#### Fast Architecture Verification (`--dry-run`)
```bash
python src/vit_vs_cnn_fashion_mnist_benchmark.py --dry-run --epochs 2
```
* **Why `--dry-run` is used:** Generates 512 random noise tensors (`torch.randn`) to verify in <2 seconds that all PyTorch layers and gradients execute without shape errors.
* **Why accuracy is `~6%–10%` and loss is `~2.30`:** On random noise across 10 classes, uniform guessing yields $1/10 = 10\%$ accuracy and theoretical cross-entropy loss of $-\ln(0.1) \approx 2.3026$.

#### Full Fashion-MNIST Benchmark (Varying `--epochs`)
```bash
python src/vit_vs_cnn_fashion_mnist_benchmark.py --epochs 5
```
* **`--epochs 1`:** CNN leads (`~85%` vs. ViT `~80%`) because $3 \times 3$ convolutions have built-in local spatial bias, whereas ViT must learn the 2D layout of its 49 patches via positional encodings.
* **`--epochs 2` to `4`:** ViT's 4 self-attention heads ($Q, K, V$) learn global cross-patch dependencies across the garment, rapidly dropping loss from `~0.46` to `~0.35`.
* **`--epochs 5`:** Both models reach high test generalization (`~89%` ViT vs. `~90.5%` CNN) in under 40 seconds of CPU runtime.
* **`--epochs 10+`:** Both models converge near `~91%` test accuracy; `Dropout(0.1)` and `AdamW` weight decay (`1e-4`) prevent overfitting.

---

## 6. Git & GitHub Maintenance Reference (How Commits & Syncs Work)

```bash
# 1. Verify modified and untracked files (Read-Only Check)
git status

# 2. Ensure virtual environments and raw datasets are ignored
grep -qxF ".venv/" .gitignore || printf "\n.venv/\n__pycache__/\ndata/\n" >> .gitignore

# 3. Stage and commit all changes with a descriptive message
git add .
git commit -m "docs: update operational runbook and evaluation documentation"

# 4. Sync with remote branch (automatically keeping local file versions on conflict) and push
git pull origin main --no-rebase -X ours --allow-unrelated-histories --no-edit
git push -u origin main
```
* **Note on GitHub Authentication:** GitHub requires a **Personal Access Token (`ghp_...`)** with `repo` scope in place of a password when pushing over HTTPS. Running `git config --global credential.helper store` caches the token after your first push.