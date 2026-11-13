# Mail agent: first learning checkpoint

Goal: read a synthetic email, identify a commitment, and ask before saving a task.
This is a new independent learning project started in November 2026. It is not a
completed summer REU assignment, a reproduction of the instructor's Strands service,
or a deployed production system.

## Start here in WSL

From the repository root, run:

```bash
python3 labs/mail_agent/lab.py
```

You should see a sample email and `INSPECTION ONLY`. This requires no packages or
API key. It displays input data; it does not simulate Gemini or demonstrate security.
Read `EMAILS` near the top of `lab.py` to see where the message comes from.

## What the live application does

1. Your trusted request tells Gemini to read the selected email.
2. Gemini can request `read_email`. Python returns that sample's contents.
3. Gemini can request `save_task`. Python displays the proposed title and asks you
   to type `yes`. Email content and model arguments cannot supply this approval.
4. Approved tasks persist in `labs/mail_agent/local/tasks.sqlite3`, an ignored SQLite
   database. The source is assigned by Python, not by the model. Exact duplicate
   tasks from the same source reuse the existing row.
5. Python returns the actual tool result to Gemini for its final response.

The two functions are local tools. There is no mailbox connection or email sending.
This first version captures tasks; it does not yet schedule or deliver reminders.

## Live setup

Follow [Runbook section 6](../../RUNBOOK.md#6-configure-the-gemini-connection)
for dependency installation, local `.env` configuration, model discovery,
and spending controls.

Use the explicit `.venv-mail/bin/python` interpreter path for lab commands.

## Explore the security boundary

```bash
python labs/mail_agent/lab.py --sample injection
python labs/mail_agent/lab.py --sample injection --live
```

The injected email tries to make the assistant save an unrelated task and claim
approval. Observe what the model proposes and what Python actually saves. Decline
unwanted tasks at the terminal. Human approval does not guarantee that a task is
correct: you must inspect it. The assistant's textual answer can also be wrong.
The synthetic examples are learning fixtures, not a security benchmark. There are
no attack-rate, ROI, production, or model-quality claims.

The terminal prints model-call elapsed time and provider-reported token usage when
available. It also shows tool requests and outcomes. No fabricated timing offsets,
token estimates, throughput scores, or cost calculations are added. Six model calls
is the limit for one run; individual requests have a 30-second timeout.

## Local tests

```bash
python -m unittest discover -s labs/mail_agent -p 'test_*.py' -v
```

Most tests require only Python. The tool-loop integration test requires the SDK and
uses a clearly identified mocked model transport. These tests verify application
behavior; they do not establish how Gemini behaves. A real key and live run are
still needed to verify the provider connection and observe model decisions.

## Next lessons

After you can explain this file and use it successfully, add task completion and
due dates, then Telegram messaging and Outlook ingestion. Add retrieval only when
we need to recover the message or document explaining a task. Build and measure
each capability before describing it on the resume.

SDK reference: https://googleapis.github.io/python-genai/
