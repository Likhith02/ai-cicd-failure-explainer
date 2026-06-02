import json
import os
import re
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional until requirements are installed
    OpenAI = None


class AnalyzeLogRequest(BaseModel):
    log_text: str = Field(..., min_length=20)


class AnalyzeLogResponse(BaseModel):
    summary: str
    root_cause: str
    error_lines: list[str]
    suggested_fix: str
    confidence: Literal["low", "medium", "high"]
    source: Literal["rule-based", "gen-ai"]


app = FastAPI(title="AI CI/CD Failure Explainer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze-log", response_model=AnalyzeLogResponse)
def analyze_log(request: AnalyzeLogRequest) -> AnalyzeLogResponse:
    log_text = request.log_text.strip()
    if not log_text:
        raise HTTPException(status_code=400, detail="Log text is required.")

    if os.getenv("OPENAI_API_KEY"):
        return analyze_with_ai(log_text)

    return analyze_with_rules(log_text)


def analyze_with_ai(log_text: str) -> AnalyzeLogResponse:
    if OpenAI is None:
        return analyze_with_rules(log_text)

    client = OpenAI()
    prompt = f"""
You are a DevOps CI/CD failure analyst.
Analyze the build log and return only valid JSON with these keys:
summary, root_cause, error_lines, suggested_fix, confidence.

confidence must be one of: low, medium, high.
error_lines must be a list of exact lines copied from the log.

Build log:
{log_text[:12000]}
"""

    completion = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = completion.choices[0].message.content or "{}"
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return AnalyzeLogResponse(
            summary="The AI response could not be parsed, so the app used a fallback summary.",
            root_cause="The log may contain an error, but the AI response was not valid JSON.",
            error_lines=extract_error_lines(log_text),
            suggested_fix="Try again or review the highlighted error lines manually.",
            confidence="low",
            source="gen-ai",
        )

    return AnalyzeLogResponse(
        summary=str(parsed.get("summary", "No summary returned.")),
        root_cause=str(parsed.get("root_cause", "No root cause returned.")),
        error_lines=list(parsed.get("error_lines", []))[:8],
        suggested_fix=str(parsed.get("suggested_fix", "No suggested fix returned.")),
        confidence=parsed.get("confidence", "medium"),
        source="gen-ai",
    )


def analyze_with_rules(log_text: str) -> AnalyzeLogResponse:
    error_lines = extract_error_lines(log_text)
    lower_log = log_text.lower()

    patterns = [
        (
    ["assertionerror", "failed tests/", "pytest"],
    "A Python test failed during the CI run.",
    "Open the failing test, reproduce it locally with pytest, then fix either the code or the expected result.",
    ),
        (
            ["modulenotfounderror", "cannot find module", "module not found"],
            "A dependency or import is missing.",
            "Check that the package is listed in your dependency file and installed in the CI job before tests run.",
        ),
        (
            ["npm err!", "eresolve", "dependency conflict"],
            "The Node.js dependency installation failed.",
            "Review package versions, lockfile changes, and the npm install command used in the workflow.",
        ),
        (
            ["pytest", "failed", "assert"],
            "One or more automated tests failed.",
            "Open the failing test name in the log, reproduce it locally, then fix the code or expected assertion.",
        ),
        (
            ["permission denied", "eacces"],
            "The CI job does not have permission to access a file, command, or path.",
            "Check file permissions, executable flags, workspace paths, and secret or token permissions.",
        ),
        (
            ["docker", "failed to solve", "build failed"],
            "The Docker image build failed.",
            "Review the Dockerfile step near the error and confirm required files exist in the build context.",
        ),
        (
            ["no space left on device"],
            "The runner ran out of disk space.",
            "Clean temporary files, reduce build artifacts, or use a larger runner.",
        ),
    ]

    root_cause = "The failure appears to be in the highlighted error lines."
    suggested_fix = "Start from the first error line, reproduce the failing command locally, and compare it with the CI workflow step."
    confidence: Literal["low", "medium", "high"] = "low"

    for keywords, cause, fix in patterns:
        if any(keyword in lower_log for keyword in keywords):
            root_cause = cause
            suggested_fix = fix
            confidence = "medium"
            break

    summary = (
        "The CI/CD log contains a failure that needs attention."
        if error_lines
        else "No obvious error line was found, but the log may still contain a failed command."
    )

    return AnalyzeLogResponse(
        summary=summary,
        root_cause=root_cause,
        error_lines=error_lines,
        suggested_fix=suggested_fix,
        confidence=confidence,
        source="rule-based",
    )


def extract_error_lines(log_text: str) -> list[str]:
    keywords = re.compile(
        r"(error|failed|failure|exception|traceback|npm err|permission denied|cannot find|not found)",
        re.IGNORECASE,
    )
    lines = [line.strip() for line in log_text.splitlines() if keywords.search(line)]
    return lines[:8]
