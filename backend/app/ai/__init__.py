"""AI / LLM integration package (Phase 2+).

This package will contain:
  - client.py          — Provider-agnostic LLM client (Ollama / OpenAI / Anthropic)
  - embeddings.py      — Embedding model wrapper
  - prompts/           — Jinja2 / text prompt templates

The LLM_PROVIDER setting in config.py selects the active provider at runtime.
No AI code is active in Phase 1.
"""
