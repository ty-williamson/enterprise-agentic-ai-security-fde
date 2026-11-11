# Operational Runbook: Environment Setup, Command Reference & Telemetry Guide

This runbook documents every terminal command required to provision the WSL/Linux environment from scratch, execute both evaluation pipelines, and interpret the resulting security and machine learning telemetry.

---

## 1. Future Quick-Boot Checklist (How to Boot This Project Up)

If the environment is already installed and you are returning to this project later, you only need **3 commands** in your (WSL/Linux) terminal:

```bash
# 1. Navigate to the repository directory
cd ~/enterprise-agentic-ai-security-fde

# 2. Activate the isolated Python virtual environment
source .venv/bin/activate

# 3. Run either pipeline
python src/fde_multi_agent_rag_guardrail.py
python src/vit_vs_cnn_fashion_mnist_benchmark.py --epochs (number)

```

`number`can range from 1 - 10+

## 2. First-Time Environment Setup: Why Each Command Is Needed

Step 2.1: Install Python Virtual Environment Tools

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip

```

Why: Refreshes Ubuntu's APT package index and installs `python3-venv` (required to create isolated Python environments) and `python3-pip`(Python's package manager).

Step 2.2: Create and Activate a Clean `.venv` Environment

```bash
deactivate 2>/dev/null || true
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

```

Purpose and function:
`deactivate 2>/dev/null || true` & `rm -rf .venv`: Safely exits any broken virtual environment and deletes incomplete `.venv` folders if a prior install was interrupted.

`python3 -m venv .venv`: Creates an isolated directory (`.venv/`) containing its own private Python binary and package site-directory so libraries installed here never conflict with Ubuntu's operating system packages.

`source .venv/bin/activate`: Points your terminal session's `python` and `pip` commands strictly inside `.venv/bin/` (indicated by (.venv) appearing at the front of your shell prompt). 

Step 2.3: Install Lightweight CPU-Only PyTorch & Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install torch torchvision --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
python -m pip install numpy pydantic

```

Why: `python -m pi`p instead of bare `pip`: Guarantees that packages are installed into the currently active `.venv` Python interpreter rather than falling back to a global system path.

Why: `--index-url https://download.pytorch.org/whl/cpu`: Standard `pip install torch` downloads ~2.5 GB of NVIDIA CUDA GPU libraries. Using the /`whl/cpu` index downloads the lightweight (~180 MB) CPU-optimized build of PyTorch, which installs in seconds and runs cleanly on standard laptop CPUs.

## Pipeline #1: Multi-Agent RAG Guardrail & 10-Stage Security Audit