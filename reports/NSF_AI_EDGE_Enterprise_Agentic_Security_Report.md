# Architecting Secure Enterprise Agentic Workflows: Mitigating Trust-Boundary Failures, Adversarial Transferability, and Data Leakage in Production LLM & RAG Pipelines
**Author:** Ty Williamson  
**Program:** 2026 National Science Foundation (NSF) AI Institute for Future Edge Networks and Distributed Intelligence (AI-EDGE) — The Ohio State University  
**Research Tracks Synthesized:** Large Language Models & Agentic AI (Track #3) and AI for Security (Track #5)

---

## Abstract
As enterprise organizations transition from single-turn conversational chatbots to autonomous, tool-calling multi-agent architectures on cloud platforms, security perimeters face a fundamental paradigm shift. While autoregressive Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) pipelines unlock high-ROI automation across customer infrastructure, they simultaneously introduce severe attack surfaces—most notably **Indirect Prompt Injection (OWASP LLM01)**, **transferable adversarial jailbreaks (GCG)**, **autonomous vulnerability exploitation**, and **cross-lifecycle data leakage**. This technical report synthesizes foundational Transformer mechanics with empirical security benchmarks to establish a production-grade architectural blueprint for securing enterprise AI deployments.

---

## 1. Mathematical & Architectural Foundations of Context Vulnerability
In modern Transformer architectures, raw text or visual modalities are tokenized and projected into a unified embedding matrix of shape $(L \times d)$, where $L$ denotes sequence length and $d$ denotes hidden dimension. Because self-attention is permutation-invariant, positional encodings are added prior to entering stacked Transformer blocks:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V, \quad \text{where } Q = XW^Q, \; K = XW^K, \; V = XW^V$$

Stabilized via pre-layer normalization ($\text{LayerNorm}(x) = \gamma \frac{x - \mu}{\sigma} + \beta$) and residual streams ($h_i = t_i + x_i$) that prevent vanishing gradients across deep layers, each token dynamically attends to every preceding token in the context window.

**The Security Implication:** When an enterprise AI agent ingests untrusted external data—such as customer emails, web pages, or unstructured vector-database chunks in a RAG pipeline—those untrusted tokens are concatenated directly into the same $(L \times d)$ input matrix $X$ as the developer's trusted system instructions. Because the scaled dot-product attention matrix $QK^T$ mixes representations across the entire sequence without hardware- or syntax-level privilege separation, untrusted data tokens can hijack the attention distribution and redirect downstream tool invocations.

---

## 2. Quantitative Threat Landscape: The Four-Pillar Enterprise Evaluation Framework
To evaluate enterprise AI deployments systematically, system architects must apply a three-part reading rule—**WHO controls the AI**, **WHAT it can touch**, and **WHICH DATA it uses**—across four operational pillars:

### 2.1 Offensive AI: Intelligence Amplification & Trust Exploitation
* **Hyper-Scaled Spear Phishing:** LLMs eliminate the human reconnaissance bottleneck in targeted social engineering. Automated pipelines ingesting unstructured public data generated personalized spear-phishing campaigns across **600+ UK Members of Parliament** at **~£0 marginal cost** per target (Hazell, 2023).
* **Deepfake Identity & Executive Fraud:** Modern voice models such as Microsoft's **VALL-E (2023)** clone human voices from just **3 seconds of audio**. In 2024, attackers combined voice and video deepfakes to impersonate a CFO and colleagues on a live video conference at **Arup**, resulting in a **$25 million ($25.6M across 15 wire transfers)** enterprise loss. Breaking this causal chain (`Public Audio -> Voice Clone -> Urgent Call -> Human Trust -> Wire Transfer`) requires out-of-band callback verification, team safe words, and two-person payment approval gates.
* **Autonomous Vulnerability Exploitation:** Equipped with tool-calling loops, document retrieval, and execution history, GPT-4 agents achieved a **73.3% pass@5** exploitation rate across 15 real-world web vulnerabilities (including SQL injection and XSS) when provided public CVE descriptions—but dropped to **7%** when CVE descriptions were withheld (Fang et al., 2024). Similarly, **PentestGPT** (Deng et al., USENIX Security 2024) decomposes penetration testing into reconnaissance, step-by-step attack planning, and reporting, outperforming baseline GPT-3 workflows by **+228%**. These benchmarks demonstrate that current LLMs act as high-velocity **intelligence amplifiers** rather than independent zero-context hackers.

### 2.2 Security of AI: Adversarial Perturbations, Transferable Jailbreaks & OWASP LLM01
* **Physical-World Vision Attacks:** Deep neural networks rely on statistical pixel correlations rather than human semantic understanding. Adding targeted physical stickers to road signs caused vision classifiers to misread **84.8% of drive-by frames** as *"Speed Limit 45"* instead of *"STOP"* (only 15.2% accuracy; Eykholt et al., CVPR 2018).
* **Universal & Transferable Jailbreak Suffixes (GCG):** Using Greedy Coordinate Gradient (GCG) optimization, attackers generate adversarial token suffixes that force safety-trained LLMs to bypass refusal training and comply with harmful requests (Zou, Carlini et al., 2023). Critically, suffixes optimized against open-weight models **transfer directly across black-box commercial models**, including ChatGPT, Claude, and Gemini.
* **Indirect Prompt Injection (OWASP LLM01):** Ranked as the **#1 risk on the OWASP Top 10 for LLM Applications (2025)**, indirect prompt injection occurs when malicious instructions hidden inside retrieved RAG documents, web pages, or emails cross the trust boundary into the control plane and trigger high-authority tools (file systems, APIs, email, or payment gateways).

### 2.3 AI for Security: Autonomous SOC Triage & Zero-Day Discovery
* **LLM-Assisted Security Operations Centers (SOCs):** Enterprise SOC teams face severe alert fatigue from thousands of daily false-positive alarms. Production security copilots—specifically **Google’s Sec-PaLM** and **Microsoft Security Copilot**—ingest raw telemetry logs, triage high-priority threats, summarize complex attack chains into plain English, and recommend analyst remediation steps (Habibzadeh et al., 2025).
* **Industrial-Scale Zero-Day Discovery:** In April 2026, Anthropic's **Claude Mythos (Project Glasswing)** demonstrated autonomous vulnerability discovery at scale—identifying **181 working Firefox exploits**, generating **595 benchmark crashes**, hijacking **10 fully-patched targets**, and matching human expert severity assessments **89% of the time** (98% within one severity tier) at a compute cost of **under $50 per OpenBSD run** (~$10,000 for FFmpeg). Deploying these capabilities defensively allows enterprise engineering teams to audit and patch internal codebases prior to production release.

### 2.4 AI & Privacy Across the Data Lifecycle
Enterprise AI systems can violate regulatory and privacy boundaries without suffering an external breach across four lifecycle stages: **1 COLLECT** (prompts, files, voice, images) $\rightarrow$ **2 STORE** (chat logs, vector embeddings, persistent agent memory) $\rightarrow$ **3 INFER** (identity, health, location, behavior) $\rightarrow$ **4 SHARE** (third-party tools, external vendors, cross-user outputs), compounded by training-data extraction attacks capable of recovering memorized PII verbatim from model weights (Carlini et al., USENIX Security 2021).

---

## 3. FDE Production Blueprint: Securing Enterprise Multi-Agent & RAG Deployments
To bridge frontier AI models with live customer infrastructure safely, Forward Deployed Engineers must implement four mandatory architectural controls aligned with the **NIST AI Risk Management Framework (AI RMF)**:

1. **Hierarchical Planner-Worker Multi-Agent Delegation:** Replace monolithic tool-calling agents with a 2-tier architecture. An **Untrusted Data-Plane Worker Agent** ingests structured metadata and unstructured RAG vector chunks with zero tool execution permissions, emitting strictly schema-validated JSON. A **Trusted Control-Plane Planner Agent** executes the **Think-Act-Observe (ReAct)** loop exclusively over sanitized state.
2. **Self-Reflection & Policy Verification Loops:** Prior to executing any state-mutating API call, the Planner Agent runs a deterministic policy check and LLM self-reflection pass verifying that the tool invocation originates from authenticated user intent rather than retrieved data-plane content.
3. **Least-Privilege Tool Scoping & Human-in-the-Loop (HITL) Gates:** Restrict agent API tokens to minimum required scopes and enforce human approval before executing outbound communications, database writes, or financial transactions.
4. **Granular Observability & Native Telemetry Tracing:** Instrument every agent step to log **accuracy/block rates, safety verdicts, end-to-end latency (ms), throughput (tokens/sec), cost-per-request ($), and persistent state diffs** across sessions.

---

## References
* Anthropic. (2026). *Claude Mythos Preview & Project Glasswing*. anthropic.com/research/mythos-preview.
* Carlini, N., et al. (2021). *Extracting Training Data from Large Language Models*. USENIX Security 2021.
* Deng, G., et al. (2024). *PentestGPT: An LLM-Empowered Automatic Penetration Testing Tool*. USENIX Security 2024 (arXiv:2308.06782).
* Eykholt, K., et al. (2018). *Robust Physical-World Attacks on Deep Learning Visual Classification*. CVPR 2018 (arXiv:1707.08945).
* Fang, R., et al. (2024). *LLM Agents Can Autonomously Hack Websites*. arXiv:2402.06664.
* Habibzadeh, M., et al. (2025). *Large Language Models for Security Operations Centers*. arXiv:2509.10858.
* Hazell, J. (2023). *Large Language Models Can Be Used To Effectively Scale Spear Phishing Campaigns*. arXiv:2305.06972.
* NIST. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. U.S. Department of Commerce.
* OWASP. (2025). *OWASP Top 10 for Large Language Model Applications (LLM01: Prompt Injection)*. genai.owasp.org.
* Zou, A., Carlini, N., et al. (2023). *Universal and Transferable Adversarial Attacks on Aligned Language Models*. arXiv:2307.15043.