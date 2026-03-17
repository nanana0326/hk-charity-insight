import logging
from typing import Optional

from openai import OpenAI

from . import models, schemas
from .config import get_settings


logger = logging.getLogger(__name__)

_settings = get_settings()
_client: Optional[OpenAI] = None


def _get_client() -> Optional[OpenAI]:
    """
    Lazily initialise the DeepSeek client if an API key is configured.
    """
    global _client

    if not _settings.deepseek_api_key:
        return None

    if _client is None:
        try:
            _client = OpenAI(
                api_key=_settings.deepseek_api_key,
                base_url=_settings.deepseek_base_url,
            )
        except Exception:
            logger.exception("Failed to initialise DeepSeek client")
            return None

    return _client


def generate_report_with_gemini(
    document: models.Document,
    mode: schemas.AnalysisMode,
) -> Optional[schemas.InsightReport]:
    """
    Optional DeepSeek-powered report.

    If no API key is configured or the call fails, returns None so that
    callers can fall back to the static MVP implementation.
    """
    client = _get_client()
    if client is None:
        logger.warning(
            "DeepSeek client not available (DEEPSEEK_API_KEY unset or init failed); cannot generate report"
        )
        return None

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
            model=_settings.deepseek_model or "deepseek-chat",
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
        logger.exception("DeepSeek analysis failed")
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
        title="AI-generated analysis using DeepSeek",
        summary=summary_text,
        sections=[section],
        charts=[],
        citations=[],
    )

