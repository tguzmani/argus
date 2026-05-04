from typing import TypedDict


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
    iterations: int
    error: str | None
