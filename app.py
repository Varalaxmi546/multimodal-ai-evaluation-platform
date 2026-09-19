from pathlib import Path
from io import BytesIO
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from ai_service import (
    analyze_text,
    analyze_image,
    analyze_pdf,
    evaluate_models,
    generate_and_evaluate,
)

from database import (
    initialize_database,
    save_analysis,
    get_history,
    get_analysis,
    delete_analysis,
    delete_all_history,
    get_dashboard_stats,
)


app = FastAPI(
    title="Multimodal AI Analysis & Model Evaluation Platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


initialize_database()


# =========================================================
# REQUEST MODELS
# =========================================================

class TextRequest(BaseModel):
    text: str


class ModelEvaluationRequest(BaseModel):
    prompt: str
    model_a_response: str
    model_b_response: str


class AutomaticEvaluationRequest(BaseModel):
    prompt: str


class EvaluationReportRequest(BaseModel):
    prompt: str
    model_a_scores: dict
    model_b_scores: dict
    recommendation: str
    recommendation_reason: str
    evaluation_result: str
    evaluation_latency: float | None = None


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "online",
        "message": "Platform is running",
    }


@app.get("/")
def home():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# =========================================================
# TEXT ANALYSIS
# =========================================================

@app.post("/analyze/text")
def text_analysis(
    request: TextRequest
):

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty.",
        )

    result = analyze_text(
        request.text
    )

    save_analysis(
        "Text Analysis",
        request.text,
        result["result"],
    )

    return result


# =========================================================
# IMAGE ANALYSIS
# =========================================================

@app.post("/analyze/image")
async def image_analysis(
    file: UploadFile = File(...)
):

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Image file is empty.",
        )

    result = analyze_image(
        data,
        file.content_type or "image/jpeg",
    )

    save_analysis(
        "Image Analysis",
        file.filename or "image",
        result["result"],
    )

    return result


# =========================================================
# PDF ANALYSIS
# =========================================================

@app.post("/analyze/pdf")
async def pdf_analysis(
    file: UploadFile = File(...)
):

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="PDF file is empty.",
        )

    result = analyze_pdf(
        data
    )

    save_analysis(
        "PDF Analysis",
        file.filename or "document.pdf",
        result["result"],
    )

    return result


# =========================================================
# MANUAL MODEL EVALUATION
# =========================================================

@app.post("/evaluate/models")
def model_evaluation(
    request: ModelEvaluationRequest
):

    if not request.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty.",
        )

    if (
        not request.model_a_response.strip()
        or not request.model_b_response.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="Both model responses are required.",
        )

    result = evaluate_models(
        request.prompt,
        request.model_a_response,
        request.model_b_response,
    )

    save_analysis(
        "Model Evaluation",
        request.prompt,
        result["result"],
    )

    return result


# =========================================================
# AUTOMATIC MODEL EVALUATION
# =========================================================

@app.post("/evaluate/automatic")
def automatic_evaluation(
    request: AutomaticEvaluationRequest
):

    if not request.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty.",
        )

    result = generate_and_evaluate(
        request.prompt
    )

    save_analysis(
        "Automatic Model Evaluation",
        request.prompt,
        result["evaluation"]["result"],
    )

    return result


# =========================================================
# EVALUATION REPORT
# =========================================================

@app.post("/report/evaluation")
def create_evaluation_report(
    request: EvaluationReportRequest
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="AI Model Evaluation Report",
        author="Multimodal AI Evaluation Platform",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=21,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7,
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.grey,
    )

    recommendation_style = ParagraphStyle(
        "Recommendation",
        parent=styles["BodyText"],
        fontSize=12,
        leading=17,
        spaceAfter=8,
    )

    story = []

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Multimodal AI Model Evaluation Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Generated by Multimodal AI Analysis & Model Evaluation Platform",
            subtitle_style,
        )
    )

    generated_time = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    story.append(
        Paragraph(
            f"<b>Report Generated:</b> {generated_time}",
            body_style,
        )
    )

    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # PROMPT
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "1. Evaluation Prompt",
            heading_style,
        )
    )

    prompt_text = str(
        request.prompt
    ).replace(
        "&",
        "&amp;"
    ).replace(
        "<",
        "&lt;"
    ).replace(
        ">",
        "&gt;"
    ).replace(
        "\n",
        "<br/>"
    )

    story.append(
        Paragraph(
            prompt_text,
            body_style,
        )
    )

    # ---------------------------------------------------------
    # RECOMMENDATION
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "2. Model Recommendation",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Recommended Model:</b> "
            f"{request.recommendation}",
            recommendation_style,
        )
    )

    reason_text = str(
        request.recommendation_reason
    ).replace(
        "&",
        "&amp;"
    ).replace(
        "<",
        "&lt;"
    ).replace(
        ">",
        "&gt;"
    )

    story.append(
        Paragraph(
            f"<b>Reason:</b> {reason_text}",
            body_style,
        )
    )

    # ---------------------------------------------------------
    # SCORE TABLE
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "3. Model Score Comparison",
            heading_style,
        )
    )

    def score_value(scores, key):
        value = scores.get(key, 0)

        try:
            return f"{float(value):.0f}/100"
        except (TypeError, ValueError):
            return "0/100"

    table_data = [
        [
            "Metric",
            "Model A",
            "Model B",
        ],
        [
            "Accuracy",
            score_value(
                request.model_a_scores,
                "accuracy",
            ),
            score_value(
                request.model_b_scores,
                "accuracy",
            ),
        ],
        [
            "Relevance",
            score_value(
                request.model_a_scores,
                "relevance",
            ),
            score_value(
                request.model_b_scores,
                "relevance",
            ),
        ],
        [
            "Quality",
            score_value(
                request.model_a_scores,
                "quality",
            ),
            score_value(
                request.model_b_scores,
                "quality",
            ),
        ],
        [
            "Safety",
            score_value(
                request.model_a_scores,
                "safety",
            ),
            score_value(
                request.model_b_scores,
                "safety",
            ),
        ],
        [
            "Hallucination Risk",
            score_value(
                request.model_a_scores,
                "hallucination",
            ),
            score_value(
                request.model_b_scores,
                "hallucination",
            ),
        ],
        [
            "Overall Score",
            score_value(
                request.model_a_scores,
                "overall",
            ),
            score_value(
                request.model_b_scores,
                "overall",
            ),
        ],
    ]

    score_table = Table(
        table_data,
        colWidths=[
            70 * mm,
            45 * mm,
            45 * mm,
        ],
        repeatRows=1,
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#202b45"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#b8c2d6"),
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor("#f5f7fb"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor("#172039"),
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(score_table)

    # ---------------------------------------------------------
    # LATENCY
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "4. Evaluation Performance",
            heading_style,
        )
    )

    latency_text = "--"

    if request.evaluation_latency is not None:
        latency_text = (
            f"{request.evaluation_latency:.4f} seconds"
        )

    performance_data = [
        [
            "Evaluation Latency",
            latency_text,
        ],
        [
            "Estimated Cost",
            "$0.00",
        ],
    ]

    performance_table = Table(
        performance_data,
        colWidths=[
            70 * mm,
            90 * mm,
        ],
    )

    performance_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#b8c2d6"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#202b45"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "TEXTCOLOR",
                    (1, 0),
                    (1, -1),
                    colors.HexColor("#172039"),
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, -1),
                    colors.HexColor("#f5f7fb"),
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(
        performance_table
    )

    # ---------------------------------------------------------
    # EVALUATION RESULT
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "5. Detailed Evaluation",
            heading_style,
        )
    )

    result_text = str(
        request.evaluation_result
    ).replace(
        "&",
        "&amp;"
    ).replace(
        "<",
        "&lt;"
    ).replace(
        ">",
        "&gt;"
    ).replace(
        "\n",
        "<br/>"
    )

    story.append(
        Paragraph(
            result_text,
            body_style,
        )
    )

    # ---------------------------------------------------------
    # DISCLAIMER
    # ---------------------------------------------------------

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            "Evaluation Note",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "The scores in this report are heuristic evaluation "
            "signals generated by the current local evaluation "
            "engine. They are not ground-truth factual "
            "verification or benchmark scores. For reliable "
            "accuracy and hallucination assessment, responses "
            "should be evaluated against trusted reference "
            "answers or benchmark datasets.",
            small_style,
        )
    )

    # ---------------------------------------------------------
    # BUILD PDF
    # ---------------------------------------------------------

    document.build(
        story
    )

    buffer.seek(0)

    filename = (
        "ai_model_evaluation_report.pdf"
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.get("/dashboard/stats")
def dashboard_stats():
    return get_dashboard_stats()


# =========================================================
# HISTORY
# =========================================================

@app.get("/history")
def history():
    return {
        "history": get_history()
    }


@app.get("/history/{analysis_id}")
def history_item(
    analysis_id: int
):

    item = get_analysis(
            analysis_id
        )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return item


@app.delete("/history/{analysis_id}")
def remove_history_item(
    analysis_id: int
):

    if not delete_analysis(
        analysis_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return {
        "message":
            "Analysis deleted successfully."
    }


@app.delete("/history")
def remove_history():

    delete_all_history()

    return {
        "message":
            "All history deleted successfully."
    }


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR
    ),
    name="static",
)