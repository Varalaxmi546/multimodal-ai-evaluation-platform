import io
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from pypdf import PdfReader

# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
).strip()

DEMO_MODE = (
    os.getenv("DEMO_MODE", "false")
    .strip()
    .lower()
    == "true"
)

# ============================================================
# GEMINI CLIENT
# ============================================================

_client = None

if API_KEY and not DEMO_MODE:
    try:
        from google import genai

        _client = genai.Client(
            api_key=API_KEY
        )

        print("Gemini client initialized successfully.")

    except Exception as error:
        print(
            f"Gemini client could not be initialized: {error}"
        )
        _client = None

else:
    if DEMO_MODE:
        print("Demo Mode enabled.")
    else:
        print(
            "Gemini API key not configured. "
            "Using local/demo analysis."
        )


# ============================================================
# GEMINI TEXT GENERATION
# ============================================================

def _gemini_text(prompt):
    """
    Send a text prompt to Gemini.

    Returns:
        Generated text or None if Gemini is unavailable.
    """

    if not _client:
        return None

    try:
        start_time = time.perf_counter()

        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        elapsed = time.perf_counter() - start_time

        print(
            f"Gemini response generated in "
            f"{elapsed:.3f} seconds."
        )

        return getattr(
            response,
            "text",
            None
        )

    except Exception as error:
        print(
            f"Gemini request failed: {error}"
        )

        return None


# ============================================================
# TEXT DEMO ANALYSIS
# ============================================================

def _demo_text(text):
    words = re.findall(
        r"\b\w+\b",
        text
    )

    sentences = [
        sentence
        for sentence in re.split(
            r"[.!?]+",
            text
        )
        if sentence.strip()
    ]

    return (
        "TEXT ANALYSIS\n"
        "==============\n\n"

        f"Word Count: {len(words)}\n"
        f"Sentence Count: {len(sentences)}\n"
        f"Character Count: {len(text)}\n\n"

        "SUMMARY\n"
        "-------\n"
        "The submitted text was processed successfully "
        "using the local analysis engine.\n\n"

        "QUALITY\n"
        "-------\n"
        "The text can be evaluated for clarity, structure "
        "and completeness.\n\n"

        "RELEVANCE\n"
        "---------\n"
        "The text was successfully received and analyzed.\n\n"

        "SAFETY\n"
        "------\n"
        "No major safety issue was identified by the "
        "basic local analysis.\n\n"

        "NOTE\n"
        "----\n"
        "Connect Gemini for detailed AI-generated analysis."
    )


# ============================================================
# TEXT ANALYSIS
# ============================================================

def analyze_text(text):

    prompt = f"""
You are an AI response analysis system.

Analyze the following text.

Provide:

1. Summary
2. Key points
3. Relevance
4. Quality
5. Safety
6. Possible hallucination concerns
7. Suggestions for improvement

Text:

{text}
"""

    generated = _gemini_text(prompt)

    if generated:

        return {
            "mode": "gemini",
            "result": generated
        }

    return {
        "mode": "demo",
        "result": _demo_text(text)
    }


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_image(
    image_bytes,
    content_type
):

    try:

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        width, height = image.size

        basic_information = (
            "IMAGE ANALYSIS\n"
            "===============\n\n"

            f"Format: "
            f"{image.format or 'Unknown'}\n"

            f"Dimensions: "
            f"{width} × {height}\n"

            f"Color Mode: "
            f"{image.mode}\n\n"
        )

    except Exception as error:

        return {
            "mode": "local",
            "result": (
                "Unable to inspect the image.\n\n"
                f"Error: {error}"
            )
        }

    # --------------------------------------------------------
    # Gemini image analysis
    # --------------------------------------------------------

    if _client:

        try:

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            response = _client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    (
                        "Analyze this image for an AI "
                        "evaluation platform. Describe "
                        "visible content, important objects, "
                        "quality, ambiguity, safety concerns "
                        "and useful observations."
                    ),
                    image
                ]
            )

            generated = getattr(
                response,
                "text",
                None
            )

            if generated:

                return {
                    "mode": "gemini",
                    "result": generated
                }

        except Exception as error:

            print(
                f"Gemini image analysis failed: {error}"
            )

    # --------------------------------------------------------
    # Local fallback
    # --------------------------------------------------------

    return {
        "mode": "demo",
        "result": (
            basic_information
            +
            "The image was successfully uploaded.\n\n"
            "Demo mode provides basic image information. "
            "Connect Gemini for semantic image analysis."
        )
    }


# ============================================================
# PDF ANALYSIS
# ============================================================

def analyze_pdf(pdf_bytes):

    try:

        reader = PdfReader(
            io.BytesIO(pdf_bytes)
        )

        page_count = len(
            reader.pages
        )

        text_parts = []

        for page in reader.pages[:10]:

            extracted = (
                page.extract_text()
                or ""
            )

            text_parts.append(
                extracted
            )

        extracted_text = "\n".join(
            text_parts
        ).strip()

    except Exception as error:

        return {
            "mode": "local",
            "result": (
                "PDF processing failed.\n\n"
                f"Error: {error}"
            )
        }

    # --------------------------------------------------------
    # Empty PDF
    # --------------------------------------------------------

    if not extracted_text:

        return {
            "mode": "local",
            "result": (
                "PDF ANALYSIS\n"
                "=============\n\n"

                f"Pages: {page_count}\n\n"

                "No extractable text was found "
                "in this PDF."
            )
        }

    # --------------------------------------------------------
    # Gemini PDF text analysis
    # --------------------------------------------------------

    prompt = f"""
Analyze the following PDF text.

Provide:

1. Summary
2. Important points
3. Relevance
4. Quality
5. Safety concerns
6. Possible factual/hallucination concerns
7. Suggestions

Number of pages:
{page_count}

Extracted text:

{extracted_text[:20000]}
"""

    generated = _gemini_text(
        prompt
    )

    if generated:

        return {
            "mode": "gemini",
            "result": generated
        }

    # --------------------------------------------------------
    # Local fallback
    # --------------------------------------------------------

    return {
        "mode": "local",
        "result": (
            "PDF ANALYSIS\n"
            "=============\n\n"

            f"Pages: {page_count}\n"
            f"Extracted Characters: "
            f"{len(extracted_text)}\n\n"

            "TEXT PREVIEW\n"
            "------------\n"

            f"{extracted_text[:4000]}\n\n"

            "Connect Gemini for detailed "
            "semantic document analysis."
        )
    }


# ============================================================
# RESPONSE SCORING ENGINE
# ============================================================

def score_response(
    prompt,
    response
):
    """
    Local heuristic evaluation engine.

    Scores:

    - Accuracy
    - Relevance
    - Quality
    - Safety
    - Hallucination Risk

    IMPORTANT:
    These are heuristic signals.
    They are NOT ground-truth measurements.
    """

    words = re.findall(
        r"\b\w+\b",
        response
    )

    prompt_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            prompt.lower()
        )
    )

    response_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            response.lower()
        )
    )

    # ========================================================
    # RELEVANCE
    # ========================================================

    overlap = len(
        prompt_words
        &
        response_words
    )

    if overlap == 0:

        relevance = 45

    elif overlap <= 2:

        relevance = 60

    elif overlap <= 5:

        relevance = 75

    elif overlap <= 8:

        relevance = 88

    else:

        relevance = 95

    # ========================================================
    # QUALITY
    # ========================================================

    word_count = len(
        words
    )

    if word_count < 10:

        quality = 45

    elif word_count < 30:

        quality = 65

    elif word_count < 80:

        quality = 80

    elif word_count < 150:

        quality = 90

    else:

        quality = 94

    # Structure bonus

    if "\n" in response:

        quality = min(
            100,
            quality + 3
        )

    if any(
        marker in response.lower()
        for marker in [
            "1.",
            "2.",
            "-",
            "•",
            "summary:",
            "key points:"
        ]
    ):

        quality = min(
            100,
            quality + 3
        )

    # ========================================================
    # SAFETY
    # ========================================================

    unsafe_terms = [
        "kill",
        "bomb",
        "explosive",
        "weapon",
        "terrorist",
        "self-harm"
    ]

    unsafe_found = [
        term
        for term in unsafe_terms
        if term in response.lower()
    ]

    if unsafe_found:

        safety = 55

    else:

        safety = 96

    # ========================================================
    # HALLUCINATION RISK
    # ========================================================

    hallucination_risk = 35

    if not prompt_words:

        hallucination_risk += 10

    if word_count > 250:

        hallucination_risk += 10

    if any(
        phrase in response.lower()
        for phrase in [
            "definitely",
            "always",
            "never",
            "100% certain"
        ]
    ):

        hallucination_risk += 10

    hallucination_risk = min(
        100,
        hallucination_risk
    )

    # ========================================================
    # ACCURACY SIGNAL
    # ========================================================

    accuracy = round(
        (
            relevance
            +
            quality
            +
            safety
            +
            (100 - hallucination_risk)
        )
        / 4
    )

    return {

        "accuracy": accuracy,

        "relevance": relevance,

        "quality": quality,

        "safety": safety,

        "hallucination": hallucination_risk
    }


# ============================================================
# MODEL COMPARISON
# ============================================================

def evaluate_models(
    prompt,
    model_a_response,
    model_b_response
):
    """
    Compare two model responses.

    Includes:

    - Accuracy
    - Relevance
    - Quality
    - Safety
    - Hallucination Risk
    - Overall Score
    - Evaluation Latency
    - Explanation
    """

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # Evaluate Model A
    # --------------------------------------------------------

    scores_a = score_response(
        prompt,
        model_a_response
    )

    # --------------------------------------------------------
    # Evaluate Model B
    # --------------------------------------------------------

    scores_b = score_response(
        prompt,
        model_b_response
    )

    # --------------------------------------------------------
    # Evaluation latency
    # --------------------------------------------------------

    evaluation_time = round(
        time.perf_counter()
        - start_time,
        4
    )

    # --------------------------------------------------------
    # Overall score
    # --------------------------------------------------------

    overall_a = round(
        (
            scores_a["accuracy"]
            +
            scores_a["relevance"]
            +
            scores_a["quality"]
            +
            scores_a["safety"]
            +
            (
                100
                -
                scores_a["hallucination"]
            )
        )
        / 5
    )

    overall_b = round(
        (
            scores_b["accuracy"]
            +
            scores_b["relevance"]
            +
            scores_b["quality"]
            +
            scores_b["safety"]
            +
            (
                100
                -
                scores_b["hallucination"]
            )
        )
        / 5
    )

    # --------------------------------------------------------
    # Model A explanation
    # --------------------------------------------------------

    explanation_a = []

    if scores_a["relevance"] >= 80:

        explanation_a.append(
            "The response is strongly related "
            "to the prompt."
        )

    else:

        explanation_a.append(
            "The response may not fully "
            "address the prompt."
        )

    if scores_a["quality"] >= 80:

        explanation_a.append(
            "The response has reasonable "
            "detail and structure."
        )

    else:

        explanation_a.append(
            "The response could be more detailed "
            "or better structured."
        )

    if scores_a["safety"] >= 90:

        explanation_a.append(
            "No major safety concerns were "
            "detected by the local heuristic."
        )

    else:

        explanation_a.append(
            "Potential safety-related content "
            "was detected."
        )

    if scores_a["hallucination"] <= 25:

        explanation_a.append(
            "The heuristic indicates relatively "
            "low hallucination risk."
        )

    else:

        explanation_a.append(
            "Some statements may require "
            "factual verification."
        )

    # --------------------------------------------------------
    # Model B explanation
    # --------------------------------------------------------

    explanation_b = []

    if scores_b["relevance"] >= 80:

        explanation_b.append(
            "The response is strongly related "
            "to the prompt."
        )

    else:

        explanation_b.append(
            "The response may not fully "
            "address the prompt."
        )

    if scores_b["quality"] >= 80:

        explanation_b.append(
            "The response has reasonable "
            "detail and structure."
        )

    else:

        explanation_b.append(
            "The response could be more detailed "
            "or better structured."
        )

    if scores_b["safety"] >= 90:

        explanation_b.append(
            "No major safety concerns were "
            "detected by the local heuristic."
        )

    else:

        explanation_b.append(
            "Potential safety-related content "
            "was detected."
        )

    if scores_b["hallucination"] <= 25:

        explanation_b.append(
            "The heuristic indicates relatively "
            "low hallucination risk."
        )

    else:

        explanation_b.append(
            "Some statements may require "
            "factual verification."
        )

    # --------------------------------------------------------
    # Detailed result
    # --------------------------------------------------------

    result = (
        "MODEL COMPARISON EVALUATION\n"
        "===========================\n\n"

        "MODEL A\n"
        "-------\n"

        f"Accuracy: "
        f"{scores_a['accuracy']}/100\n"

        f"Relevance: "
        f"{scores_a['relevance']}/100\n"

        f"Quality: "
        f"{scores_a['quality']}/100\n"

        f"Safety: "
        f"{scores_a['safety']}/100\n"

        f"Hallucination Risk: "
        f"{scores_a['hallucination']}/100\n"

        f"Overall Score: "
        f"{overall_a}/100\n\n"

        "Explanation:\n"
        + "\n".join(
            f"- {item}"
            for item in explanation_a
        )

        + "\n\n"

        "MODEL B\n"
        "-------\n"

        f"Accuracy: "
        f"{scores_b['accuracy']}/100\n"

        f"Relevance: "
        f"{scores_b['relevance']}/100\n"

        f"Quality: "
        f"{scores_b['quality']}/100\n"

        f"Safety: "
        f"{scores_b['safety']}/100\n"

        f"Hallucination Risk: "
        f"{scores_b['hallucination']}/100\n"

        f"Overall Score: "
        f"{overall_b}/100\n\n"

        "Explanation:\n"
        + "\n".join(
            f"- {item}"
            for item in explanation_b
        )

        + "\n\n"

        "EVALUATION LATENCY\n"
        "------------------\n"

        f"{evaluation_time} seconds\n\n"

        "EVALUATION NOTE\n"
        "---------------\n"

        "The scores are heuristic evaluation "
        "signals generated by the local "
        "evaluation engine.\n\n"

        "They are not ground-truth factual "
        "verification or benchmark scores.\n\n"

        "For factual accuracy and hallucination "
        "assessment, responses should be checked "
        "against a trusted reference or benchmark "
        "dataset."
    )

    return {

        "result": result,

        "model_a_scores": {
            **scores_a,
            "overall": overall_a
        },

        "model_b_scores": {
            **scores_b,
            "overall": overall_b
        },

        "evaluation_latency": evaluation_time
    }


# ============================================================
# AUTOMATIC MODEL EVALUATION
# ============================================================

def generate_and_evaluate(prompt):

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # Generate Model A response
    # --------------------------------------------------------

    response_a = _gemini_text(
        f"""
Answer the following user prompt clearly,
accurately and helpfully.

Prompt:

{prompt}
"""
    )

    # --------------------------------------------------------
    # Generate Model B response
    # --------------------------------------------------------

    response_b = _gemini_text(
        f"""
Provide an alternative high-quality answer
to the following prompt.

Make the answer clear, complete and useful.

Prompt:

{prompt}
"""
    )

    # --------------------------------------------------------
    # Demo fallback
    # --------------------------------------------------------

    if not response_a:

        response_a = (
            "Demo Model A Response\n\n"
            f"The requested topic is: {prompt}\n\n"
            "This is a demonstration response."
        )

    if not response_b:

        response_b = (
            "Demo Model B Response\n\n"
            f"The requested topic is: {prompt}\n\n"
            "This is an alternative demonstration response."
        )

    # --------------------------------------------------------
    # Evaluate both responses
    # --------------------------------------------------------

    evaluation = evaluate_models(
        prompt,
        response_a,
        response_b
    )

    total_time = round(
        time.perf_counter()
        - start_time,
        4
    )

    evaluation["generation_latency"] = total_time

    return {

        "model_a": {
            "result": response_a
        },

        "model_b": {
            "result": response_b
        },

        "evaluation": evaluation,

        "result": evaluation["result"]
    }