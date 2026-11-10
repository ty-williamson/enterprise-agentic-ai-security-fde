# Enterprise Agentic AI Security, RAG Guardrails & Transformer Benchmarks
**NSF AI Institute for Future Edge Networks and Distributed Intelligence (AI-EDGE) — The Ohio State University (Summer 2026)**  
**Author:** Ty Williamson | B.S. in Cybersecurity Engineering, Ohio University (Expected May 2028)

---

## Executive Overview
As enterprises transition from static chatbots to autonomous, tool-calling AI agents connected to live APIs and internal data silos, **security and trust-boundary enforcement** represent the primary bottleneck to production deployment. 

Developed during the **2026 NSF AI-EDGE Summer Research Program** at The Ohio State University, this repository contains:
1. **Live Agent Red-Team Audit & Observability Pipeline (`audits/`):** A 10-stage security audit of a live tool-calling **Strands LLM Agent (Claude Sonnet 4.6)** connected to Gmail APIs and persistent memory (`list_inbox`, `read_email`, `read_write_notes`, `archive_verification`, `send_email`), evaluating **OWASP LLM01 (Indirect Prompt Injection)** trust-boundary failures.
2. **Defensive Multi-Agent & RAG Guardrail Architecture (`src/fde_multi_agent_rag_guardrail.py`):** A reusable Python security module built around **Google Cloud / Gemini API**, **Vector Databases (ChromaDB)**, **Think-Act-Observe (ReAct)** loops, **Planner-Worker hierarchical delegation**, and **self-reflection verification** aligned with the **NIST AI Risk Management Framework (AI RMF)**.
3. **Transformer & Vision Transformer (ViT) Benchmarks (`src/vit_vs_cnn_fashion_mnist_benchmark.py`):** Empirical Python implementations of **Transformer Encoders** and **Vision Transformers (ViT)** benchmarked against **Convolutional Neural Networks (CNNs)** across 60,000+ Fashion-MNIST samples.
4. **Enterprise AI Security Technical Research Report (`reports/`):** Quantitative analysis of autonomous CVE exploitation (**73.3% pass@5**), **PentestGPT (+228%)**, transferable **GCG adversarial suffixes** across Gemini/Claude/GPT, **Google Sec-PaLM** SOC alert triage, and **Claude Mythos** zero-day discovery (**89% expert severity match** at **<$50/run**).

---

## System Architecture: Isolating the Untrusted Data Plane from the Trusted Control Plane

In standard LLM agents, trusted system instructions and untrusted external data (emails, web pages, RAG documents) share a single $(L \times d)$ token sequence inside multi-head self-attention:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

To prevent untrusted data from hijacking control-plane tools (`send_email`, `archive_verification`), this repository implements a **2-Tier Hierarchical Multi-Agent Pipeline**:

```text
[Untrusted External Inputs: Emails / Unstructured Docs / Structured Metadata]
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ TIER 1: UNTRUSTED DATA-PLANE WORKER AGENT (RAG + Vector DB Isolation)     │
│ • Ingests structured metadata & unstructured text via ChromaDB Vector RAG │
│ • Zero Tool Authority (Cannot invoke send_email or mutate state memory)   │
│ • Outputs strictly schema-validated, sanitized JSON extraction payloads   │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                        Sanitized JSON Context Only
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ TIER 2: TRUSTED CONTROL-PLANE PLANNER AGENT (ReAct + Self-Reflection)     │
│ • Executes Think -> Act -> Observe (ReAct) loop over sanitized state      │
│ • Runs Self-Reflection Policy Check against NIST AI RMF & OWASP LLM01     │
│ • Enforces Least-Privilege Scoping & Human-in-the-Loop (HITL) Approval    │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
         [Authorized API Execution & Granular Telemetry Tracing]
   (Tracks Accuracy/Block Rate, Safety, Latency, Tokens/Sec, Cost/Request)
