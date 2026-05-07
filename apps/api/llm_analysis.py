import logging
from typing import Optional

from openai import OpenAI

from . import models, schemas
from .config import get_settings


logger = logging.getLogger(__name__)

_client: Optional[OpenAI] = None


def _get_client() -> Optional[OpenAI]:
    """Lazily initialise an OpenAI-compatible client pointing at Ollama."""
    global _client

    settings = get_settings()
    if _client is None:
        try:
            _client = OpenAI(
                api_key=settings.ollama_api_key,
                base_url=settings.ollama_base_url,
            )
        except Exception:
            logger.exception("Failed to initialise Ollama client")
            return None
    return _client


def generate_report_with_ollama(
    document: models.Document,
    mode: schemas.AnalysisMode,
) -> Optional[schemas.InsightReport]:
    """
    LLM-powered report via local Ollama (OpenAI-compatible API).

    If the client cannot start or the call fails, returns None so callers
    can return HTTP 503.
    """
    client = _get_client()
    if client is None:
        logger.warning(
            "Ollama client not available; ensure Ollama is running and "
            "OLLAMA_BASE_URL / OLLAMA_MODEL are correct"
        )
        return None

    settings = get_settings()

    # Concatenate page text (or fields) into a single prompt-friendly string.
    texts = [p.text for p in document.pages if p.text]
    full_text = (
        "\n\n".join(texts).strip()
        or "(No text could be extracted from this document.)"
    )
    # Keep prompt size under control.
    full_text = full_text[:20000]

    perspective = (
        "funder / internal"
        if mode == schemas.AnalysisMode.FUNDER
        else "public-facing"
    )

    system_prompt = (
        "You are an analyst helping a charity insights platform.\n\n"
        "The user will provide text from a charity document (annual report, "
        "funding application, or project report). Read it carefully and then "
        f"write a concise analysis from a {perspective} perspective.\n\n"
        "Focus on:\n"
        "- what the organisation/project does and who it serves\n"
        "- key activities and outcomes\n"
        "- funding needs and approximate scale (qualitative is fine)\n"
        "- any obvious risks, gaps, or opportunities\n\n"
        "Write 3–6 short paragraphs in clear, plain English. Avoid bullet points."
    )

    try:
        response = client.chat.completions.create(
            model=settings.ollama_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Here is the document text:\n\n{full_text}",
                },
            ],
            temperature=0.7,
        )
        choice = response.choices[0]
        summary_text = (choice.message.content or "").strip()
    except Exception:
        logger.exception("Ollama LLM analysis failed")
        return None

    if not summary_text:
        return None

    section = schemas.InsightSection(
        id="ai_overview",
        title="AI-generated overview",
        body=summary_text,
    )

    return schemas.InsightReport(
        mode=mode,
        document_id=document.id,
        title="AI-generated analysis using Ollama",
        summary=summary_text,
        sections=[section],
        charts=[],
        citations=[],
    )
