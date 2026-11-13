# Mail-Agent Runbook

This guide covers the current mail-agent checkpoint in VS Code’s Ubuntu terminal
(WSL) and ordinary Ubuntu Bash.

Run commands from the repository root unless stated otherwise. Native Windows
PowerShell uses different paths and is not covered here.

## 1. Purpose and current status

The lab reads a synthetic email, lets Gemini propose a task, and requires your
approval before saving that task locally.

Verified so far:

- Sample-email inspection works.
- The Gemini SDK installed successfully.
- All six local application tests passed with no skips.

Still awaiting verification:

- The first live Gemini API request.
- Actual model behavior on the normal and injected email fixtures.

The integration tests use mocked model responses. Passing them verifies application
behavior, not Gemini’s decisions.

## 2. Open the repository

For Ty’s existing checkout:

```bash
cd ~/personal/nsf_ai-edge_institute/enterprise-agentic-ai-security-fde
pwd
git status --short
```

| Command | Purpose | Expected result |
| --- | --- | --- |
| `cd ...` | Opens the existing repository folder. Other users substitute their checkout path. | No output on success. |
| `pwd` | Prints the current working directory. | A path ending in `enterprise-agentic-ai-security-fde`. |
| `git status --short` | Shows modified and untracked files. | Blank output means a clean working tree. `M` means modified; `??` means untracked. |

For a new checkout, run these commands from the parent folder where you want the
repository:

```bash
git clone https://github.com/ty-williamson/enterprise-agentic-ai-security-fde.git
cd enterprise-agentic-ai-security-fde
```

`git clone` downloads the tracked files and history. `cd` enters the downloaded
folder.

Use plain URLs inside terminal commands. Do not paste Markdown link syntax into
a shell command.

**Publication dependency:** A fresh clone contains only changes pushed to GitHub.
The `labs/mail_agent/` checkpoint must be published before new users can follow
this guide from a fresh clone.

## 3. Create the Python environment

Check Python:

```bash
python3 --version
```

This prints the installed Python version. Use Python 3.10 or newer.

Create the lab’s isolated environment:

```bash
python3 -m venv .venv-mail
```

`-m venv` runs Python’s environment-creation module. `.venv-mail` is the directory
it creates. Success usually produces no output.

Install the lab dependencies:

```bash
.venv-mail/bin/python -m pip install -r labs/mail_agent/requirements.txt
```

| Part | Meaning |
| --- | --- |
| `.venv-mail/bin/python` | Uses the lab’s exact Python interpreter. |
| `-m pip` | Runs pip through that interpreter. |
| `install` | Installs the requested packages. |
| `-r labs/mail_agent/requirements.txt` | Reads the package requirements from this file. |

Expect `Successfully installed ...` or `Requirement already satisfied`.

Confirm the SDK installation:

```bash
.venv-mail/bin/python -m pip show google-genai
```

This prints package metadata. The current checkpoint pins `google-genai==3.3.0`.

The explicit interpreter path works even if the terminal prompt shows another
environment, such as `(.venv)`. Activation is optional for this guide.

### If Python or venv is missing

Only if Ubuntu reports missing Python, venv, or ensurepip support:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

| Command | Purpose |
| --- | --- |
| `sudo apt update` | Refreshes Ubuntu’s package listings with administrator privileges. |
| `sudo apt install ...` | Installs Python, virtual-environment support, and pip. It may ask for confirmation. |

If Ubuntu requests a version-specific venv package, follow that package suggestion.
Then retry environment creation.

Skip these system-installation commands if the environment already works.

## 4. Inspect the sample email

```bash
.venv-mail/bin/python labs/mail_agent/lab.py
```

This runs the program without enabling live model calls.

Expected opening output:

```text
INSPECTION ONLY: no model call and no task saved.
```

The program then displays the sample email defined in `EMAILS` inside `lab.py`.

This confirms that the program loads and reads its fixture. It does not evaluate
an agent or save a task.

## 5. Run the local tests

```bash
.venv-mail/bin/python -m unittest discover -s labs/mail_agent -p 'test_*.py' -v
```

| Part | Meaning |
| --- | --- |
| `-m unittest` | Runs Python’s built-in testing framework. |
| `discover` | Finds test files automatically. |
| `-s labs/mail_agent` | Starts discovery in the lab folder. |
| `-p 'test_*.py'` | Selects matching test filenames. Quotes prevent shell expansion. |
| `-v` | Prints each test’s name and result. |

Expected final output:

```text
Ran 6 tests in ...

OK
```

The elapsed time varies. With the SDK installed, none of the six tests should
be skipped.

The tests check:

- Human approval is required before saving.
- Model arguments cannot supply approval.
- The email must be read before a task is proposed.
- Unknown tools and invalid arguments are rejected.
- Approved tasks persist across database connections.
- Exact duplicates reuse the existing task.
- The mocked tool loop returns actual application outcomes.
- Repeated model tool requests stop at the configured limit.

These tests do not make live Gemini requests.

## 6. Configure the Gemini connection

The lab loads configuration from the repository-root `.env` file for live runs.

The lab requirements file, `labs/mail_agent/requirements.txt`, must contain:

```text
google-genai==3.3.0
python-dotenv>=1.0,<2
```

Install these dependencies:

```bash
.venv-mail/bin/python -m pip install -r labs/mail_agent/requirements.txt
```

This uses the lab’s Python environment. The root `requirements.txt` belongs to
the earlier ML examples and is a separate file.

### Local configuration

Create or view a key in [Google AI Studio](https://aistudio.google.com/apikey).
Create `.env` beside the root `README.md` with:

```dotenv
GEMINI_API_KEY=your_private_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Replace the key placeholder locally. Never commit or share this file.

Check that Git ignores it:

```bash
git check-ignore -v .env
git ls-files -- .env
```

The first command should display the ignore rule. The second should produce
no output, confirming that Git is not tracking the file.

Check that the file contains a key without displaying it:

```bash
.venv-mail/bin/python -c "from dotenv import dotenv_values; print('API key present:', bool(dotenv_values('.env').get('GEMINI_API_KEY')))"
```

Expected output:

```text
API key present: True
```

### Discover model IDs

From the repository root:

```bash
.venv-mail/bin/python - <<'PY'
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(".env", override=False, interpolate=False)

with genai.Client(api_key=os.environ["GEMINI_API_KEY"]) as client:
    for model in client.models.list():
        if "generateContent" in (model.supported_actions or []):
            print(model.name)
PY
```

| Part | Purpose |
| --- | --- |
| `python - <<'PY'` | Runs the enclosed Python code. The final `PY` ends the input. |
| `load_dotenv(...)` | Loads `.env`, preserves existing environment variables, and disables variable interpolation. |
| `genai.Client(...)` | Authenticates using the configured key. |
| `client.models.list()` | Requests Google’s model catalog. |
| `supported_actions` filter | Prints models supporting content generation. Tool-calling support and usable quota still need checking. |

Expected output is a list of model IDs. This authenticates a catalog request;
it does not run the email agent or print the key.

### Model and spending controls

The initial model is `gemini-3.5-flash-lite`. Confirm availability and current
pricing when setting up the project.

The application configuration limits each model call to 1,024 output tokens.
The tool loop permits at most six model calls per run. Multiple calls resend
conversation context and therefore consume additional input tokens.

These limits do not enforce a dollar budget. Review billing settings before
live requests. For prepaid testing, disable automatic reload if you do not want
automatic purchases. Billing enforcement can be delayed.

Run one manual test first, inspect its output and account usage, and then decide
whether to continue. No model is guaranteed to complete every task correctly.

Existing terminal environment variables take precedence over `.env`. Terminal
`export` commands are unnecessary when configuration is supplied through `.env`.

## 7. Run the live workflow

```bash
.venv-mail/bin/python labs/mail_agent/lab.py --live
```

`--live` enables real Gemini API calls.

The workflow is:

1. Your trusted request asks Gemini to read the selected email.
2. Gemini can request the `read_email` tool.
3. Python returns the selected fixture.
4. Gemini can propose a task through `save_task`.
5. Python asks you to approve that task.
6. Python returns the actual result to Gemini.

If a task is proposed, you will see:

```text
Save task "..."? Type yes to approve:
```

Inspect the title before responding.

- Type `yes` to approve saving.
- Any other response declines.

The exact model response and number of tool calls can vary.

The terminal prints JSON events showing model responses, tool requests, and tool
outcomes. Provider token counts appear when available. Missing counts remain null.

The program permits at most six model calls per run. Individual requests have a
30-second timeout. SDK retries may increase total elapsed time.

There is no simulated fallback when live configuration is missing or a request
fails.

### What this checkpoint can do

- Read the selected synthetic email.
- Propose a task.
- Require terminal approval.
- Save approved tasks in SQLite.

### What remains to be built

- Real mailbox ingestion.
- Task completion and due dates.
- Telegram messaging.
- Scheduled reminder delivery.

A successful API call demonstrates a live connection. It does not establish a
production deployment or a general security guarantee.

## 8. View saved tasks

```bash
.venv-mail/bin/python labs/mail_agent/lab.py --tasks
```

`--tasks` reads the local database without contacting Gemini.

Tasks are stored in:

```text
labs/mail_agent/local/tasks.sqlite3
```

The `local/` folder is ignored by Git.

An empty task list appears as:

```json
[]
```

Saved rows contain the task ID, title, and source ID. The command creates an empty
database if one does not already exist.

An identical title from the same source reuses the existing task instead of
creating another row.

## 9. Explore the injected email

First inspect the fixture without a model call:

```bash
.venv-mail/bin/python labs/mail_agent/lab.py --sample injection
```

`--sample injection` selects the synthetic email containing a malicious
instruction. Without `--live`, it only displays the email.

To observe the actual model:

```bash
.venv-mail/bin/python labs/mail_agent/lab.py --sample injection --live
```

Watch what the model proposes and what Python actually saves.

Decline unwanted tasks. Record the observed behavior rather than assuming that
the model will resist the instruction.

The approval gate prevents new tasks from being saved without terminal approval.
It does not ensure that the model’s suggestions or textual answers are correct.

These fixtures are learning examples, not a measured security benchmark.

## 10. Resume in a new terminal

Return to the existing checkout:

```bash
cd ~/personal/nsf_ai-edge_institute/enterprise-agentic-ai-security-fde
```

Other users substitute their actual checkout path.

View saved tasks:

```bash
.venv-mail/bin/python labs/mail_agent/lab.py --tasks
```

Tasks survive terminal closure. Do not recreate the environment or reinstall
packages simply because you opened another terminal.

For a live run, repeat the credential prompts in section 6 and then use `--live`.

To remove the credentials from the current shell when finished:

```bash
unset GEMINI_API_KEY GEMINI_MODEL
```

`unset` removes these variables from the shell. It does not revoke the API key.

## 11. Troubleshooting

| Symptom | What to check |
| --- | --- |
| `No such file or directory` for a lab path | Run `pwd`. Confirm you are in the repository root and that the checkpoint files exist locally. |
| Missing `.venv-mail/bin/python` | Create the environment from the repository root using section 3. |
| `No module named google` | Install the lab requirements using `.venv-mail/bin/python -m pip`. Packages installed in another environment are separate. |
| Skipped integration tests | Confirm the SDK is installed in the interpreter used to run the tests. |
| `externally-managed-environment` | Check the interpreter path. Use `.venv-mail/bin/python -m pip` for lab dependencies. |
| Live run requires credentials/model | Set both variables in the same terminal that launches the program. |
| Provider-related exception | Check the key, model ID, account access, quota, network, and billing. The exception class alone does not identify the cause. |
| Six-model-call limit reached | Inspect the printed tool events before retrying. The run did not finish normally. |
| No task saved | Check whether Gemini proposed a task and whether you approved it. |
| API-key typing is invisible | Expected: the key prompt deliberately hides input. |
| Existing task returned instead of a new row | Exact duplicate detection reused the saved task. |

The CLI currently suppresses detailed provider error bodies. When asking for help,
share the command, exception class, and relevant output.

Exclude API keys and private message content.

## 12. Review, commit, and push yourself

The repository owner performs all file edits, commits, and pushes.

For a documentation-only change:

```bash
git status --short
git diff -- RUNBOOK.md
git diff --check
git add RUNBOOK.md
git diff --cached --name-only
git diff --cached
git commit -m "Document mail-agent setup and operation"
git push
```

Run each command separately and inspect its result before continuing.

| Command | Purpose |
| --- | --- |
| `git status --short` | Shows modified and untracked files. |
| `git diff -- RUNBOOK.md` | Displays unstaged changes to the runbook. |
| `git diff --check` | Checks unstaged edits for whitespace problems. No output means no issues found. |
| `git add RUNBOOK.md` | Stages the runbook only. |
| `git diff --cached --name-only` | Lists all staged files, including files staged earlier. |
| `git diff --cached` | Displays everything currently staged for the next commit. |
| `git commit -m "..."` | Creates a local commit containing all staged changes. |
| `git push` | Uploads commits to the configured upstream. |

If you intend to commit only the runbook, confirm that the staged file list
contains only `RUNBOOK.md`.

The remaining checkpoint files require their own review and staging before the
complete application is published.

If a push fails, inspect the actual error. Do not automatically force-push or
merge unrelated histories.

## 13. Optional: apply a checkpoint patch

Skip this section if the checkpoint already runs.

For an existing checkout missing the lab files, place
`mail-agent-checkpoint.patch` in the repository root.

Check compatibility:

```bash
git apply --check mail-agent-checkpoint.patch
```

This changes no files. No output means the check passed.

Only after that succeeds, apply the patch:

```bash
git apply mail-agent-checkpoint.patch
```

A successful apply usually produces no output. It changes local files but does
not commit or push them.

Do not reapply a patch after editing its files. An “already exists” or “patch does
not apply” error can mean it has already been applied. Inspect `git status --short`
instead of forcing the operation.

## 14. Verification record

Verified on Ty’s Windows/WSL setup through VS Code’s Ubuntu terminal:

- Fixture inspection displayed the expected synthetic email.
- `google-genai==3.3.0` installed successfully.
- All six local tests passed with no skips.
- The reported local test run completed in 0.059 seconds.
- Live Gemini authentication and the initial `read_email` tool call succeeded.
- The following API request returned `ClientError`; the complete workflow
  remains under investigation.

The live Gemini connection and actual model behavior remain unverified.

Earlier ML examples and generated reports are outside this setup path. Update
this runbook as new capabilities are implemented and tested.



## References

- [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [Google GenAI Python SDK](https://googleapis.github.io/python-genai/)