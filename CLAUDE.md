# Argus — AI Code Review Agent

Agent that analyzes GitHub Pull Requests using agentic workflows built with LangGraph. Fetches PR diffs, gathers codebase context via RAG, analyzes findings, and posts review comments to GitHub after human approval.

## Stack

- **Backend:** Django 5.x + Django REST Framework
- **Agent:** LangGraph (Python) with PostgreSQL checkpointer
- **Queue:** Celery + Redis
- **DB:** PostgreSQL 16 with pgvector
- **Observability:** Langfuse (self-hosted via Docker)
- **LLMs:** OpenRouter (multi-model per node)
- **GitHub integration:** PyGithub

## Architecture

Domain-driven. Each Django app owns one domain. Dependencies are explicit and unidirectional:

```
repositories ← pulls ← reviews ← agent
```

No MVC-style layers (no services.py, no controllers). Business logic lives in models and Celery tasks. Extract only if a task grows unmanageable.

## Project Structure

```
argus/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── celery.py
│   └── urls.py
├── apps/
│   ├── repositories/        # Domain: GitHub repositories
│   │   ├── models.py        # Repository
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   ├── pulls/               # Domain: Pull Requests
│   │   ├── models.py        # PullRequest → FK to repositories.Repository
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   ├── reviews/             # Domain: Review sessions and findings (core)
│   │   ├── models.py        # ReviewSession, ReviewFinding, AgentStep
│   │   ├── views.py         # includes approve/reject endpoints
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tasks.py         # Celery task → invokes agent/graph.py
│   │
│   └── agent/               # Infrastructure: LangGraph graph
│       ├── graph.py         # Graph definition and compilation
│       ├── state.py         # AgentState TypedDict
│       ├── nodes/           # One file per node
│       │   ├── fetch_pr.py
│       │   ├── evaluate_scope.py
│       │   ├── fetch_file_context.py
│       │   ├── analyze_code.py
│       │   ├── classify_findings.py
│       │   └── post_comments.py
│       └── tools/           # One file per tool
│           ├── github.py
│           └── codebase_search.py
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Models

**repositories/models.py**
- `Repository` — github_id, owner, name, full_name, default_branch, is_private

**pulls/models.py**
- `PullRequest` → FK Repository — github_pr_number, title, description, author, base_branch, head_branch, github_url

**reviews/models.py**
- `ReviewSession` → FK PullRequest — thread_id (UUID, links to LangGraph checkpointer), status, celery_task_id, total_tokens_used, total_cost_usd
  - Status: `pending → running → awaiting_approval → approved → posted | failed`
- `ReviewFinding` → FK ReviewSession — severity, status, file_path, line_number, comment_body, github_comment_id
  - Severity: `critical | warning | suggestion`
  - Status: `draft → approved | rejected → posted`
- `AgentStep` → FK ReviewSession — node_name, tokens_used, duration_ms, error

## Agent Graph Flow

```
START
  ↓
fetch_pr_metadata          # deterministic — no LLM
  ↓
fetch_diff                 # deterministic — no LLM
  ↓
evaluate_scope             # routing model — needs more context?
  ↓ yes                ↓ no
fetch_file_context         |
  ↓                        |
evaluate_scope ←───────────┘  (max_iterations=3)
  ↓ sufficient
analyze_code               # reasoning model
  ↓
classify_findings          # reasoning model — structured output
  ↓
prepare_comments           # reasoning model — draft per finding
  ↓
interrupt()                # ALWAYS — human approves before any GitHub write
  ↓ approved
post_comments              # deterministic — GitHub API
  ↓
END
```

## Agent State (apps/agent/state.py)

```python
class AgentState(TypedDict):
    repository_full_name: str
    pr_number: int
    session_id: int
    pr_metadata: dict
    diff: str
    fetched_files: list[dict]
    files_to_fetch: list[str]
    findings: list[dict]
    context_sufficient: bool
    iterations: int          # max=3, escape infinite context loop
    error: str | None
```

## Multi-Model Strategy (OpenRouter)

- `routing` nodes (evaluate_scope): always `google/gemini-flash-1.5`
- `reasoning` nodes (analyze_code, classify_findings, prepare_comments): `anthropic/claude-sonnet-4-5` in production, `google/gemini-flash-1.5` in development

```python
# config/settings/base.py
AGENT_MODELS = {
    "reasoning": "google/gemini-flash-1.5" if DEBUG else "anthropic/claude-sonnet-4-5",
    "routing": "google/gemini-flash-1.5",
}
```

## API Endpoints

```
POST   /api/repositories/                    # register a repo
POST   /api/pulls/                           # register a PR
POST   /api/reviews/                         # create ReviewSession, dispatch Celery task
GET    /api/reviews/{id}/                    # poll status + findings
POST   /api/reviews/{id}/approve/            # resume graph after interrupt()
POST   /api/reviews/{id}/reject/             # cancel session
```

## Human-in-the-Loop

Graph calls `interrupt()` before any GitHub write. `ReviewSession.thread_id` links Django to the LangGraph checkpointer. The `/approve/` endpoint resumes via:

```python
graph.invoke(None, {"configurable": {"thread_id": str(session.thread_id)}})
```

## Observability

Langfuse at `http://localhost:3000`. Every graph invocation passes `langfuse.callback.CallbackHandler`. Nodes also log to `AgentStep` for in-app status display without depending on Langfuse.

## Commands

```bash
docker-compose up -d
python manage.py migrate
python manage.py runserver
celery -A config worker -l info
python manage.py run_evals
python manage.py test
```

## Non-Negotiable Rules

- **Never auto-post to GitHub** — interrupt() before every write, no exceptions
- **max_iterations=3** on fetch_file_context loop
- **Structured outputs always** — use `.with_structured_output(PydanticSchema)` for all LLM calls consumed by code
- **Deterministic nodes have no LLM** — fetch_pr, fetch_diff, post_comments are pure IO
- **One tool, one responsibility** — never combine read + write in a single tool
- **No cross-domain shortcuts** — respect the dependency direction: repositories ← pulls ← reviews ← agent

## Environment Variables

```
DATABASE_URL
REDIS_URL
OPENROUTER_API_KEY
GITHUB_TOKEN
LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY
SECRET_KEY
DEBUG
```

## Environment Activation
```bash
source .venv/bin/activate
```