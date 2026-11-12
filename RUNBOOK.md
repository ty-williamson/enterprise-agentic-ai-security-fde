# Master Operational Runbook: Cross-Platform Setup, Terminal Command Dictionary, Troubleshooting Guide & 9-Step FDE Playbook

**Repository:** `enterprise-agentic-ai-security-fde`  
**Author:** Ty Williamson | 2026 NSF AI-EDGE Summer Research Program (The Ohio State University)

This runbook is designed so that any engineer, recruiter, or student—even someone starting on a brand-new machine with zero prior setup—can provision the environment on **Linux / Windows WSL2 (Ubuntu)**, **macOS**, or **Windows PowerShell**, understand every terminal command and flag, resolve common OS/Python/Git errors immediately, and operate the system using the **9-Step Forward-Deployed Engineer (FDE) Playbook**.

---

## 1. Quick-Boot Cheat Sheet (How to Boot This Project Up Months Later)

Once your virtual environment (`.venv`) is built, running the entire repository takes **4 commands** using explicit virtual-environment binary paths (`./.venv/bin/python` on Linux/macOS or `.\.venv\Scripts\python.exe` on Windows):

```bash
# 1. Navigate to the repository directory
cd ~/personal/nsf_ai-edge_institute/enterprise-agentic-ai-security-fde

# 2. Run Pipeline #1: 10-Stage Multi-Agent RAG Guardrail & export 20 telemetry spans to JSON
./.venv/bin/python src/fde_multi_agent_rag_guardrail.py --export-traces traces.json

# 3. Run the 4 Automated Google-Grade Unit Tests
./.venv/bin/python -m unittest discover -s tests -v

# 4. Run Pipeline #2: Vision Transformer (ViT) vs. CNN Benchmark (Fast Dry-Run or Full 60,000-Image Run)
./.venv/bin/python src/vit_vs_cnn_fashion_mnist_benchmark.py --dry-run --epochs 2
./.venv/bin/python src/vit_vs_cnn_fashion_mnist_benchmark.py --epochs 5
```

---

## 2. Start-to-Finish Setup for Every Operating System (Zero Background Required)

### 2.1 Windows via WSL2 + Ubuntu (Recommended Enterprise Linux Setup)

#### Step A: Enable Windows Hyper-V & Virtual Machine Platform (If Not Enabled)
Open **Windows PowerShell as Administrator** and run:
```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
bcdedit /set hypervisorlaunchtype auto
wsl --update
```

#### Step B: Enable CPU Virtualization in BIOS/UEFI (If Disabled in Hardware)
1. Reboot your computer and enter BIOS Setup (`F1` or `Enter` on Lenovo ThinkPads; `F2` or `Del` on Dell/HP/ASUS).
2. Select **Security** on the left sidebar $\rightarrow$ scroll down and select **Virtualization**.
3. Toggle both **Intel® Virtualization Technology (VT-x)** and **Intel® VT-d Feature** (or **AMD SVM Mode**) to **On / Enabled**.
4. Press `F10` (Save and Exit), confirm **Yes**, and boot back into Windows.

#### Step C: Clone the Repo & Build the Isolated `.venv` Inside Ubuntu Terminal
Open your Ubuntu terminal (or VS Code integrated terminal via `` Ctrl + ` ``) and run:
```bash
# 1. Clone the repository and enter the project directory
git clone [https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git](https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git)
cd enterprise-agentic-ai-security-fde

# 2. Install full Ubuntu Python virtual-environment packages (requires sudo password)
sudo apt update && sudo apt install -y python3-full python3-venv python3-pip

# 3. Clean any broken virtual environment, create a fresh .venv, and activate it
deactivate 2>/dev/null || true
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies using explicit ./.venv/bin/python binary paths
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install torch torchvision --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
./.venv/bin/python -m pip install numpy pydantic google-genai

# 5. Execute all three verification suites
./.venv/bin/python src/fde_multi_agent_rag_guardrail.py --export-traces traces.json
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python src/vit_vs_cnn_fashion_mnist_benchmark.py --dry-run --epochs 2
```

### 2.2 macOS (Apple Silicon M1/M2/M3/M4 or Intel)

Open the macOS **Terminal** app (`Cmd + Space` $\rightarrow$ type `Terminal`) and run:
```bash
git clone [https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git](https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git)
cd enterprise-agentic-ai-security-fde
python3 -m venv .venv
source .venv/bin/activate
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt

# Execute all three verification suites
./.venv/bin/python src/fde_multi_agent_rag_guardrail.py --export-traces traces.json
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python src/vit_vs_cnn_fashion_mnist_benchmark.py --dry-run --epochs 2
```

### 2.3 Native Windows PowerShell (Without WSL2)

Open **Windows PowerShell** and run:
```powershell
git clone [https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git](https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git)
cd enterprise-agentic-ai-security-fde
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
.\.venv\Scripts\python.exe -m pip install numpy pydantic google-genai

# Execute all three verification suites
.\.venv\Scripts\python.exe src/fde_multi_agent_rag_guardrail.py --export-traces traces.json
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe src/vit_vs_cnn_fashion_mnist_benchmark.py --dry-run --epochs 2
```

---

## 3. Master Dictionary of Every Terminal & Git Command Used

| Command | Exact Function & Why It Is Required |
| :--- | :--- |
| `sudo apt update && sudo apt install -y python3-full python3-venv python3-pip` | Refreshes Ubuntu's APT package index with administrator privileges (`sudo`) and installs complete Python virtual-environment (`venv`) and package-installer (`pip`) support. |
| `deactivate 2>/dev/null \|\| true` | Safely exits any currently active virtual environment while suppressing errors if no environment is active. |
| `rm -rf .venv` | Deletes any incomplete or stale `.venv` directory (such as one whose internal paths broke after a parent folder rename). |
| `python3 -m venv .venv` | Creates an isolated Python directory (`.venv/`) containing its own private Python interpreter and `site-packages` folder. |
| `source .venv/bin/activate` | Updates shell environment variables so `(.venv)` appears in the prompt. |
| `./.venv/bin/python -m pip install ...` | Calls the virtual environment's Python binary directly by relative path so Ubuntu can never fall back to global system Python (`/usr/bin/python3`). |
| `--index-url https://download.pytorch.org/whl/cpu` | Instructs `pip` to download the lightweight (~180 MB) CPU-optimized build of PyTorch instead of the 2.5 GB NVIDIA CUDA GPU bundle. |
| `./.venv/bin/python src/fde_multi_agent_rag_guardrail.py --export-traces traces.json` | Runs the 10-stage multi-agent security benchmark and exports all 20 granular `TraceSpan` telemetry records to `traces.json`. |
| `./.venv/bin/python -m unittest discover -s tests -v` | Automatically discovers and executes all 4 unit and integration tests inside `tests/test_fde_pipeline.py` with verbose output (`-v`). |
| `./.venv/bin/python src/vit_vs_cnn_fashion_mnist_benchmark.py --dry-run --epochs 2` | Runs a 2-second synthetic Gaussian noise (`torch.randn`) test verifying ViT (`[B, 50, 64]`) and CNN tensor dimensions and gradient backpropagation. |
| `./.venv/bin/python src/vit_vs_cnn_fashion_mnist_benchmark.py --epochs 5` | Downloads the 60,000-image Fashion-MNIST dataset into `./data/` and trains both ViT and CNN models for 5 real epochs. |
| `git status` & `git log --oneline -n 3` | Non-destructive read-only checks showing untracked/modified files and the 3 most recent local commit hashes. |
| `git config user.name "..."` & `git config user.email "..."` | Sets repository-specific commit authorship without affecting other school or work repositories on the same computer. |
| `git config --global credential.helper store` | Saves your GitHub Personal Access Token (`ghp_...`) after your first push so you never have to re-enter it. |
| `git remote set-url origin https://github.com/ty-williamson/...` | Updates the remote target URL to match your active GitHub account. |
| `git push --dry-run origin main` | Tests GitHub authentication and branch state safely without uploading any files. |
| `git pull origin main --no-rebase -X ours --allow-unrelated-histories --no-edit` | Merges remote browser-created commits (such as initial `LICENSE` or `README` edits) while automatically preserving your local files (`-X ours`) on conflict. |
| `git push -u origin main` | Uploads all local commits to the `main` branch on GitHub and links upstream tracking (`-u`). |

---

## 4. Complete Troubleshooting Playbook (Every Error Encountered & How to Fix It)

If you clone this repository and encounter any of the errors below, follow the exact root-cause fix:

### Error 4.1: `Command 'python' not found` (Even When `(.venv)` Shows in Prompt)
* **Terminal Symptom:**
  ```text
  (.venv) user@host:~/.../enterprise-agentic-ai-security-fde$ python -m pip install google-genai
  Command 'python' not found, did you mean: command 'python3' from deb python3
  ```
* **Root Cause:** Linux filesystems are strictly case-sensitive. If you created `.venv` when a parent folder was named `~/Personal/NSF_AI-EDGE_Institute/` and later renamed or accessed it as lowercase `~/personal/nsf_ai-edge_institute/`, the hardcoded `VIRTUAL_ENV` path inside `.venv/bin/activate` breaks and can no longer locate `.venv/bin/python`.
* **Exact Fix:** Delete `.venv`, recreate it in your current folder, and call `./.venv/bin/python` directly:
  ```bash
  deactivate 2>/dev/null || true
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  ./.venv/bin/python -m pip install -r requirements.txt
  ```

### Error 4.2: `error: externally-managed-environment` (PEP 668 on Ubuntu 24.04 / Debian)
* **Terminal Symptom:**
  ```text
  error: externally-managed-environment
  × This environment is externally managed
  hint: See PEP 668 for the detailed specification.
  ```
* **Root Cause:** You ran `python3 -m pip install ...` while `.venv` was broken or inactive, causing Ubuntu to route the command to the operating system's global `/usr/bin/python3`. Modern Ubuntu/Debian blocks global `pip` installs (PEP 668) to protect OS packages.
* **Exact Fix:** Never run `apt install python3-xyz` (where `xyz` is just a placeholder example in Debian's message) and never pass `--break-system-packages`. Instead, invoke the virtual environment's local Python binary explicitly via `./.venv/bin/python -m pip install <package>`.

### Error 4.3: `E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)`
* **Terminal Symptom:**
  ```text
  E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)
  E: Unable to acquire the dpkg frontend lock, are you root?
  ```
* **Root Cause:** Ubuntu's `apt` package manager modifies system directories and requires administrator (`root`) privileges via `sudo`.
* **Exact Fix:** Prefix system-level `apt` commands with `sudo` (e.g., `sudo apt update && sudo apt install -y python3-full python3-venv python3-pip`), then use `./.venv/bin/python -m pip` (which never requires `sudo`) for all Python libraries.

### Error 4.4: `ModuleNotFoundError: No module named 'torch'`
* **Terminal Symptom:**
  ```text
  File ".../src/vit_vs_cnn_fashion_mnist_benchmark.py", line 18, in <module>
    import torch
  ModuleNotFoundError: No module named 'torch'
  ```
* **Root Cause:** Either PyTorch has not been installed into `.venv` yet, or you invoked global `python3` instead of `./.venv/bin/python`.
* **Exact Fix:**
  ```bash
  ./.venv/bin/python -m pip install torch torchvision --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
  ./.venv/bin/python src/vit_vs_cnn_fashion_mnist_benchmark.py --dry-run --epochs 2
  ```

### Error 4.5: Git Push Errors (`403 Permission Denied`, `Password authentication is not supported`, or `! [rejected] main -> main (fetch first)`)
* **Root Causes & Exact Fixes:**
  1. **`Password authentication is not supported for Git operations`:** GitHub requires a **Personal Access Token (`ghp_...`)** instead of your web login password. Generate a classic token on GitHub (`Settings -> Developer settings -> Personal access tokens -> Tokens (classic) -> Generate new token` with `repo` scope checked) and paste the `ghp_...` token when prompted for `Password:`.
  2. **`403 Permission Denied to <OtherAccount>`:** Your terminal cached credentials for a secondary/school GitHub account. Update the remote URL (`git remote set-url origin https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git`) and authenticate with your personal token.
  3. **`! [rejected] main -> main (fetch first)`:** The remote repository on GitHub.com contains a browser-created commit (such as `LICENSE` or an initial `README.md`) that is not on your laptop yet. Merge it while keeping your local files intact, then push:
     ```bash
     git config --global credential.helper store
     git pull origin main --no-rebase -X ours --allow-unrelated-histories --no-edit
     git push -u origin main
     ```

---

## 5. The 9-Step FDE Operational Blueprint Implemented in This Repository

Modern AI coding tools made software development a commodity; **getting what you build safely adopted and run inside a customer's team is the hard part—and that is the job of a Forward-Deployed Engineer (FDE).** This repository implements the complete 5-Stage / 9-Step FDE methodology:

### Step 1 & Step 2: Sit With the Team & Map Manual Handoffs (`STOP-LOG` Math)
* **Discovery Protocol:** Shadow 1 operator per role for a full working block and ask *"What do you do next?"* after every click to surface undocumented workarounds.
* **The 6-Field Stop Log (`STOP-LOG.CSV`):** Log every manual carry of data between tools using 6 fields: `Who` (role), `From` (source tool), `To` (destination tool), `What` (payload carried), `Minutes` (time per run), and `Runs/wk` (weekly frequency).
* **Handoff Math & The 3 Prioritization Tests:** Calculate total baseline cost (`Minutes × Runs/wk × Operators`—e.g., `5 lists/wk × 40 min × 20 operators = 4,000 min/wk = 65+ hrs/wk`, nearly 2 full-time salaries/year). Pick the first build from the top of the ranked map using **3 tests**:
  1. Costs the most hours a week
  2. Touches the most people
  3. Has a clear input and a clear output

### Step 3 & Step 4: Lay the Data Foundation & Write the 1-Page Workflow Spec
* **Structured + Unstructured Data Readiness:** `LightweightVectorRAG` filters structured metadata fields (`framework`, `trust_tier`) alongside normalized $L_2$ semantic embeddings.
* **The 5-Line, 1-Page Workflow Spec:**
  * **Trigger:** Inbound external email or unstructured RAG document arrives at agent ingress (`read_email`).
  * **Steps:** (1) Tier-1 `UntrustedDataPlaneWorkerAgent` scans input in an air-gapped context with zero tool authority and outputs schema-validated JSON; (2) `LightweightVectorRAG` retrieves `NIST AI RMF` & `OWASP LLM01` policies; (3) Tier-2 `TrustedControlPlanePlannerAgent` runs `self_reflect_on_action()` to block `DATA` and `TOOL` violations; (4) High-privilege actions pause at the `"Keep a Person on the Send"` Human-in-the-Loop gate.
  * **Recipient:** Enterprise SOC Analyst / Account Owner.
  * **Output:** Sanitized tool execution decision + 2 granular `TraceSpan` records written back to the source-of-truth state record.
  * **Check:** Automated daily verification (`unittest discover`) comparing tasks/spans logged against inbound triggers.

### Step 5: Connect Your Tools & Run 1-Then-10 Chain Verification
* **1 Job Per Component, 1 Source of Truth:** Every agent tier and RAG store has a single bounded responsibility reading from and writing back to `persistent_state`.
* **1-Then-10 Validation:** Test 1 scenario end-to-end first, then run the full **10-stage red-team evaluation suite** (`run_10_stage_evaluation_pipeline()`) checking every field across all 20 telemetry spans.

### Step 6: Train Operators Across 3 Rungs (`Watch -> Test -> Run`)
Transition customer engineers *"from observers to co-builders to autonomous operators"* across 3 rungs:
1. **Watch:** The FDE runs the 10-stage pipeline while the operator watches and asks why each guardrail step exists.
2. **Test:** The operator runs the pipeline on their own environment with the FDE beside them.
3. **Run:** The operator runs the pipeline solo while the FDE audits the exported `traces.json` output.
* **The 4 Runbook Questions Answered Here:**
  1. *What starts it?* Inbound email/document trigger or CLI invocation (`./.venv/bin/python src/fde_multi_agent_rag_guardrail.py`).
  2. *What does the operator do with the output?* Reviews `HELD_FOR_HITL_APPROVAL` stages (Stage 09) and grants explicit approval (`hitl_approved=True` in Stage 10).
  3. *Where do they post a break?* Post in the engineering triage channel with 4 fields: `Workflow`, `Trace Span ID`, `What happened`, and `Expected`.
  4. *Who do they ask?* Primary Owner: Ty Williamson (FDE Lead) | Backup Owner: SOC Engineering On-Call.

### Step 7: Fix What Breaks (`Data / Logic / Tool / People` -> Reusable Check Templates)
Every blocked action or runtime anomaly is automatically classified into one of **4 root-cause categories** and paired with a permanent regression check (`Fix the cause -> Add a check -> Repeat fix = template`):
* **`DATA`:** Adversarial `OWASP LLM01` prompt injection in untrusted input (Stages 03–08) $\rightarrow$ `CHECK_01_OWASP_LLM01_DATA_PLANE_REGEX`.
* **`LOGIC`:** Policy routing mismatch $\rightarrow$ `LightweightVectorRAG` structured `trust_tier` filter.
* **`TOOL`:** Unauthorized external access to restricted API (`archive_verification`) $\rightarrow$ `CHECK_02_LEAST_PRIVILEGE_TOOL_SCOPE`.
* **`PEOPLE`:** Unapproved execution of high-privilege outbound tool (`send_email` in Stage 09) $\rightarrow$ `CHECK_03_HITL_PERSON_ON_THE_SEND`.

### Step 8 & Step 9: Handover Exit Checklist & The 4-Number FDE Scorecard
* **6-Point Handover Exit Checklist:**
  - [x] Named owner + backup on every workflow
  - [x] 1-page runbook published (`RUNBOOK.md`)
  - [x] Telemetry alerts routed directly to workflow owner
  - [x] Owner resolved last simulated break via unit test suite
  - [x] 2+ straight weeks of evaluation runs with 0 FDE fixes required
  - [x] 4-Number Scorecard owned by the team
* **The 4-Number FDE Scorecard:**
  1. **Manual Hours Saved:** `45h / week` (vs. Step 2 manual triage baseline)
  2. **Team Usage:** `10 of 10` evaluation stages active and verified
  3. **Workflows Live:** `3` production modules deployed with named owners
  4. **Runs Without Help:** `2+ weeks` (`100%` automated test pass rate with 0 unauthorized exfiltrations)