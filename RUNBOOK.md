# Operational Runbook: Environment Setup, Command Reference & Telemetry Guide

This runbook documents every terminal command required to provision the WSL/Linux environment from scratch, execute both evaluation pipelines, and interpret the resulting security and machine learning telemetry.

---

## Future Quick-Boot Checklist (How to Boot This Project Up)

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
# Comments

`number`can range from 1 - 10+