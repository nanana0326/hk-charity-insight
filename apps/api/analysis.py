from typing import Iterable, List

from . import models, schemas


def _build_common_charts(
    document: models.Document,
) -> List[schemas.ChartSpec]:
    # For MVP we use placeholder data wired to existing fields.
    amount_fields = [f for f in document.fields if f.name == models.FieldName.AMOUNT]

    pie_data = {
        "series": [
            {"name": "Programme delivery costs", "value": 60},
            {"name": "Staff costs", "value": 25},
            {"name": "Administration & other", "value": 15},
        ]
    }

    return [
        schemas.ChartSpec(
            id=f"funding_breakdown_{document.id}",
            type=schemas.ChartType.PIE,
            title="Example funding allocation breakdown",
            description="An illustrative breakdown of how funds are allocated, based on the financial narrative in the report.",
            data=pie_data,
        ),
    ]


def _citations_from_fields(
    fields: Iterable[models.DocumentField],
) -> list[schemas.InsightCitation]:
    citations: list[schemas.InsightCitation] = []
    for field in fields:
        citations.append(
            schemas.InsightCitation(
                field=schemas.FieldName(field.name.value),
                page_number=field.page_number,
            )
        )
    return citations


def generate_report_for_funder(document: models.Document) -> schemas.InsightReport:
    fields = list(document.fields)
    charts = _build_common_charts(document)
    citations = _citations_from_fields(fields)

    sections = [
        schemas.InsightSection(
            id="overview",
            title="Project overview and funding scale",
            body=(
                "This section focuses on the overall objectives of the project, its primary target groups, "
                "and the approximate funding scale. The current implementation is a placeholder; in later "
                "iterations a large language model can refine and cross-check extracted text and tables."
            ),
        ),
        schemas.InsightSection(
            id="risk_opportunity",
            title="Risks and opportunities",
            body=(
                "By looking at the funding structure and narrative, the analysis can surface potential risks "
                "(for example heavy reliance on a single funding source, unusually high staff cost ratio, or "
                "a lack of measurable KPIs) as well as opportunities (such as high-impact projects with a clear "
                "pathway for scaling)."
            ),
        ),
        schemas.InsightSection(
            id="fit_with_strategy",
            title="Fit with funder strategy",
            body=(
                "Using topic areas, target populations and geographic coverage, this section provides a "
                "qualitative view of how well the project aligns with the funder’s strategy. Future versions "
                "can model the strategy explicitly and support semi-automated scoring and time-series comparisons."
            ),
        ),
    ]

    return schemas.InsightReport(
        mode=schemas.AnalysisMode.FUNDER,
        document_id=document.id,
        title="Project analysis report from a funder perspective (MVP)",
        summary=(
            "An early prototype of funder-oriented automated insights. The current version focuses on the "
            "overall structure and illustrative charts; future iterations can use extracted fields and large "
            "language models to produce more specific findings and recommendations."
        ),
        sections=sections,
        charts=charts,
        citations=citations,
    )


def generate_report_for_public(document: models.Document) -> schemas.InsightReport:
    fields = list(document.fields)
    charts = _build_common_charts(document)
    citations = _citations_from_fields(fields)

    sections = [
        schemas.InsightSection(
            id="story",
            title="What does this organisation do?",
            body=(
                "This section tells the story in plain language: which social problems the organisation is "
                "working on, who it serves, and what core services or programmes it runs. The current "
                "implementation is a placeholder; future versions will combine extracted content with large "
                "language models to generate copy that can be used directly for external communication."
            ),
        ),
        schemas.InsightSection(
            id="impact",
            title="How well is it doing?",
            body=(
                "This part highlights the most important achievements in the last year, such as numbers of "
                "people reached, coverage of programmes, and key milestones, supported by simple charts to "
                "show trends and change over time."
            ),
        ),
        schemas.InsightSection(
            id="where_money_goes",
            title="Where does the money go?",
            body=(
                "Using the funding structure and project list, this section explains in an intuitive way "
                "which kinds of work most of the money supports, helping potential donors see how resources "
                "are turned into social value within a few minutes."
            ),
        ),
    ]

    return schemas.InsightReport(
        mode=schemas.AnalysisMode.PUBLIC,
        document_id=document.id,
        title="Public-facing organisation overview (MVP)",
        summary=(
            "An early prototype of a public-friendly organisation overview, designed to help potential donors, "
            "volunteers or media quickly understand what the organisation does, who it serves, and roughly "
            "how funds are used."
        ),
        sections=sections,
        charts=charts,
        citations=citations,
    )

