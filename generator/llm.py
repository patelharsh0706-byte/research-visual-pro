"""
llm.py — thin wrapper around the Claude CLI for non-interactive LLM calls.
Uses `~/.local/bin/claude -p` so no ANTHROPIC_API_KEY needed.
"""
from __future__ import annotations

import subprocess
import tempfile
import os

CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")

MODEL_ALIASES = {
    "claude-opus-4-8":          "opus",
    "claude-sonnet-4-6":        "sonnet",
    "claude-haiku-4-5-20251001": "haiku",
}


def call(
    user: str,
    system: str = "",
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 4000,
) -> str:
    """
    Call Claude via CLI and return the text response.
    model: accepts full model ID or 'opus'/'sonnet'/'haiku' aliases.
    max_tokens is passed through but the CLI may not honor exact token limits.
    """
    alias = MODEL_ALIASES.get(model, model)

    cmd = [CLAUDE_BIN, "-p", "--model", alias, "--no-session-persistence"]

    if system:
        cmd += ["--system-prompt", system]

    # Pass the user prompt via stdin to avoid shell quoting issues
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(user)
        tmpfile = f.name

    try:
        with open(tmpfile) as stdin_f:
            result = subprocess.run(
                cmd,
                stdin=stdin_f,
                capture_output=True,
                text=True,
                timeout=180,
            )
        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI error: {result.stderr[:500]}")
        return result.stdout.strip()
    finally:
        os.unlink(tmpfile)
