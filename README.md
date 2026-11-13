# AI security and personal assistant learning project

This repository is being rebuilt through small, runnable checkpoints in November 2026.

---

*For setup instructions, command explanations, expected output, and troubleshooting, see the [Runbook](RUNBOOK.md).*

---

## Start here

[Mail agent: first checkpoint](labs/mail_agent/README.md)

Read one synthetic email, let Gemini propose a task, and require human approval
before saving it locally. Start by inspecting the fixture without any API key:

```bash
python3 labs/mail_agent/lab.py
```

The live path calls the Gemini API. Without credentials it stops with an explicit
error. No model execution or security result is simulated as a substitute.

## Current status

- Local task storage, approval enforcement, duplicate handling, and the bounded
  tool loop have application tests, including mocked provider responses.
- A live Gemini run still requires an API key and a model available to the account.
- There is no production deployment, measured ROI, connected mailbox, or delivered
  reminder service in this checkpoint.
- This version uses the GenAI SDK directly. It does not claim ADK orchestration,
  multiple agents, enterprise RAG, or a measured attack-success rate.
- Planned later work: task completion, due dates, Telegram delivery, Outlook
  ingestion, and source retrieval when the working use case needs it.

## Earlier generated material

The files under `src/`, `tests/`, `reports/`, and `audits/` predate this checkpoint.
They include generated demonstrations and drafts whose claimed experiments and
measurements were not performed by the author. They are retained for review, not
as evidence of completed research, live model execution, mitigated vulnerabilities,
model accuracy, adoption, or production results.

In particular, the old guardrail's printed ROI figures are fixed example strings,
its Gemini client is not used for inference, and its tool-success messages do not
execute email actions. Earlier reported ViT/CNN accuracy and the mail-agent audit
must not be used as personal accomplishments.

The author's official AI-EDGE Research Fellow title is separate from the status
of individual assignments. New independent implementation work belongs to its
actual dates, not the summer program dates.

## Learning approach

Understand the input, one model call, the requested tools, the application's
permission checks, and the resulting saved state before adding more features.
Explain and test each capability before describing it on a resume.
