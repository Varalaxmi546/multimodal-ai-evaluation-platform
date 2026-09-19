(() => {
    "use strict";


    /* =========================================================
       PAGE CONFIGURATION
    ========================================================= */

    const pages = {
        dashboard: "dashboard-page",
        text: "text-page",
        image: "image-page",
        pdf: "pdf-page",
        evaluation: "evaluation-page",
        history: "history-page"
    };


    const titles = {

        dashboard: [
            "Dashboard",
            "Analyze multimodal AI outputs and compare models."
        ],

        text: [
            "Text Analysis",
            "Analyze relevance, quality and safety."
        ],

        image: [
            "Image Analysis",
            "Inspect uploaded visual content."
        ],

        pdf: [
            "PDF Analysis",
            "Extract and analyze PDF documents."
        ],

        evaluation: [
            "Model Evaluation",
            "Compare AI model responses using evaluation metrics."
        ],

        history: [
            "History",
            "Review and manage previous analyses."
        ]

    };


    /* =========================================================
       STORE LAST EVALUATION
    ========================================================= */

    let lastEvaluation = null;


    /* =========================================================
       HELPER
    ========================================================= */

    function $(id) {
        return document.getElementById(id);
    }


    /* =========================================================
       PAGE NAVIGATION
    ========================================================= */

    function showPage(name) {

        if (!pages[name]) {
            return;
        }


        document
            .querySelectorAll(".page")
            .forEach(page => {

                page.classList.remove("active");

            });


        const selectedPage =
            $(pages[name]);


        if (selectedPage) {

            selectedPage.classList.add("active");

        }


        document
            .querySelectorAll(".nav-item")
            .forEach(button => {

                button.classList.toggle(
                    "active",
                    button.dataset.page === name
                );

            });


        $("page-title").textContent =
            titles[name][0];


        $("page-description").textContent =
            titles[name][1];


        if (name === "dashboard") {
            loadStats();
        }


        if (name === "history") {
            loadHistory();
        }

    }


    /* =========================================================
       API REQUEST
    ========================================================= */

    async function requestJSON(
        url,
        options = {}
    ) {

        const response =
            await fetch(
                url,
                options
            );


        let data = {};


        try {

            data =
                await response.json();

        } catch (_) {

            data = {};

        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Request failed."
            );

        }


        return data;

    }


    /* =========================================================
       RESULT DISPLAY
    ========================================================= */

    function showResult(
        id,
        text
    ) {

        const element =
            $(id);


        if (!element) {
            return;
        }


        element.textContent =
            typeof text === "string"
                ? text
                : JSON.stringify(
                    text,
                    null,
                    2
                );

    }


    /* =========================================================
       HEALTH
    ========================================================= */

    async function loadHealth() {

        try {

            const data =
                await requestJSON(
                    "/health"
                );


            $("health-status").textContent =
                data.status === "online"
                    ? "● Online"
                    : "Offline";

        } catch (_) {

            $("health-status").textContent =
                "● Offline";

        }

    }


    /* =========================================================
       DASHBOARD
    ========================================================= */

    async function loadStats() {

        try {

            const stats =
                await requestJSON(
                    "/dashboard/stats"
                );


            $("total-analyses").textContent =
                stats.total_analyses;


            $("total-evaluations").textContent =
                stats.total_evaluations;


            $("text-analyses").textContent =
                stats.text_analyses;


            $("media-analyses").textContent =
                stats.image_analyses +
                stats.pdf_analyses;

        } catch (error) {

            console.error(
                "Dashboard statistics error:",
                error
            );

        }

    }


    /* =========================================================
       TEXT ANALYSIS
    ========================================================= */

    async function analyzeText() {

        const text =
            $("text-input")
                .value
                .trim();


        if (!text) {

            return alert(
                "Please enter some text."
            );

        }


        $("analyze-text-btn").disabled =
            true;


        $("analyze-text-btn").textContent =
            "Analyzing...";


        try {

            const data =
                await requestJSON(
                    "/analyze/text",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            text: text
                        })

                    }
                );


            showResult(
                "text-result",
                data.result
            );


            loadStats();

        } catch (error) {

            showResult(
                "text-result",
                "Error: " +
                error.message
            );

        } finally {

            $("analyze-text-btn").disabled =
                false;


            $("analyze-text-btn").textContent =
                "Analyze Text";

        }

    }


    /* =========================================================
       IMAGE ANALYSIS
    ========================================================= */

    async function analyzeImage() {

        const file =
            $("image-input")
                .files[0];


        if (!file) {

            return alert(
                "Please select an image."
            );

        }


        const form =
            new FormData();


        form.append(
            "file",
            file
        );


        $("analyze-image-btn").disabled =
            true;


        $("analyze-image-btn").textContent =
            "Analyzing...";


        try {

            const data =
                await requestJSON(
                    "/analyze/image",
                    {

                        method: "POST",

                        body: form

                    }
                );


            showResult(
                "image-result",
                data.result
            );


            loadStats();

        } catch (error) {

            showResult(
                "image-result",
                "Error: " +
                error.message
            );

        } finally {

            $("analyze-image-btn").disabled =
                false;


            $("analyze-image-btn").textContent =
                "Analyze Image";

        }

    }


    /* =========================================================
       PDF ANALYSIS
    ========================================================= */

    async function analyzePdf() {

        const file =
            $("pdf-input")
                .files[0];


        if (!file) {

            return alert(
                "Please select a PDF."
            );

        }


        const form =
            new FormData();


        form.append(
            "file",
            file
        );


        $("analyze-pdf-btn").disabled =
            true;


        $("analyze-pdf-btn").textContent =
            "Analyzing...";


        try {

            const data =
                await requestJSON(
                    "/analyze/pdf",
                    {

                        method: "POST",

                        body: form

                    }
                );


            showResult(
                "pdf-result",
                data.result
            );


            loadStats();

        } catch (error) {

            showResult(
                "pdf-result",
                "Error: " +
                error.message
            );

        } finally {

            $("analyze-pdf-btn").disabled =
                false;


            $("analyze-pdf-btn").textContent =
                "Analyze PDF";

        }

    }


    /* =========================================================
       AUTOMATIC EVALUATION
    ========================================================= */

    async function automaticEvaluation() {

        const prompt =
            $("auto-prompt")
                .value
                .trim();


        if (!prompt) {

            return alert(
                "Please enter a prompt."
            );

        }


        $("automatic-evaluate-btn")
            .disabled = true;


        $("automatic-evaluate-btn")
            .textContent =
            "Evaluating...";


        try {

            const data =
                await requestJSON(
                    "/evaluate/automatic",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            prompt: prompt
                        })

                    }
                );


            lastEvaluation = {

                prompt:
                    prompt,

                model_a_scores:
                    data.model_a_scores || {},

                model_b_scores:
                    data.model_b_scores || {},

                evaluation_result:
                    data.evaluation?.result ||
                    data.result ||
                    "Evaluation completed.",

                evaluation_latency:
                    data.evaluation_latency ??
                    null

            };


            updateEvaluationMetrics(
                data
            );


            renderModelRecommendation(
                data
            );


            updateReportButton();


            showResult(
                "evaluation-result",
                lastEvaluation.evaluation_result
            );


            loadStats();

        } catch (error) {

            showResult(
                "evaluation-result",
                "Error: " +
                error.message
            );

        } finally {

            $("automatic-evaluate-btn")
                .disabled = false;


            $("automatic-evaluate-btn")
                .textContent =
                "Run Automatic Evaluation";

        }

    }


    /* =========================================================
       MANUAL EVALUATION
    ========================================================= */

    async function manualEvaluation() {

        const prompt =
            $("manual-prompt")
                .value
                .trim();


        const modelA =
            $("model-a")
                .value
                .trim();


        const modelB =
            $("model-b")
                .value
                .trim();


        if (
            !prompt ||
            !modelA ||
            !modelB
        ) {

            return alert(
                "Fill the prompt and both model responses."
            );

        }


        $("manual-evaluate-btn")
            .disabled = true;


        $("manual-evaluate-btn")
            .textContent =
            "Comparing...";


        try {

            const data =
                await requestJSON(
                    "/evaluate/models",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            prompt:
                                prompt,

                            model_a_response:
                                modelA,

                            model_b_response:
                                modelB

                        })

                    }
                );


            lastEvaluation = {

                prompt:
                    prompt,

                model_a_scores:
                    data.model_a_scores || {},

                model_b_scores:
                    data.model_b_scores || {},

                evaluation_result:
                    data.result ||
                    "Evaluation completed.",

                evaluation_latency:
                    data.evaluation_latency ??
                    null

            };


            updateEvaluationMetrics(
                data
            );


            renderModelRecommendation(
                data
            );


            updateReportButton();


            showResult(
                "evaluation-result",
                lastEvaluation.evaluation_result
            );


            loadStats();

        } catch (error) {

            showResult(
                "evaluation-result",
                "Error: " +
                error.message
            );

        } finally {

            $("manual-evaluate-btn")
                .disabled = false;


            $("manual-evaluate-btn")
                .textContent =
                "Compare Models";

        }

    }


    /* =========================================================
       SCORE BARS
    ========================================================= */

    function renderScoreBars(
        containerId,
        scores
    ) {

        const container =
            $(containerId);


        if (!container) {
            return;
        }


        const metrics = [

            {
                label: "Accuracy",
                key: "accuracy"
            },

            {
                label: "Relevance",
                key: "relevance"
            },

            {
                label: "Quality",
                key: "quality"
            },

            {
                label: "Safety",
                key: "safety"
            },

            {
                label: "Hallucination Risk",
                key: "hallucination"
            },

            {
                label: "Overall Score",
                key: "overall"
            }

        ];


        container.innerHTML =
            metrics
                .map(metric => {

                    const value =
                        Number(
                            scores?.[
                                metric.key
                            ] ?? 0
                        );


                    const safeValue =
                        Math.max(
                            0,
                            Math.min(
                                100,
                                value
                            )
                        );


                    return `

                        <div class="score-row">

                            <div class="score-row-header">

                                <span>
                                    ${metric.label}
                                </span>

                                <span class="score-value">
                                    ${safeValue}/100
                                </span>

                            </div>


                            <div class="score-track">

                                <div
                                    class="score-fill"
                                    style="width: ${safeValue}%;">
                                </div>

                            </div>

                        </div>

                    `;

                })
                .join("");

    }


    /* =========================================================
       RECOMMENDATION CALCULATION
    ========================================================= */

    function calculateRecommendation(
        modelA,
        modelB
    ) {

        const a =
            modelA || {};


        const b =
            modelB || {};


        const overallA =
            Number(
                a.overall ?? 0
            );


        const overallB =
            Number(
                b.overall ?? 0
            );


        if (
            overallA >
            overallB
        ) {

            return {

                model:
                    "Model A",

                reason:
                    `Model A has the higher overall score (${overallA}/100 vs ${overallB}/100).`,

                type:
                    "recommendation"

            };

        }


        if (
            overallB >
            overallA
        ) {

            return {

                model:
                    "Model B",

                reason:
                    `Model B has the higher overall score (${overallB}/100 vs ${overallA}/100).`,

                type:
                    "recommendation"

            };

        }


        const tieBreakers = [

            {
                key: "accuracy",
                label: "accuracy"
            },

            {
                key: "relevance",
                label: "relevance"
            },

            {
                key: "quality",
                label: "quality"
            },

            {
                key: "safety",
                label: "safety"
            }

        ];


        for (
            const metric
            of tieBreakers
        ) {

            const scoreA =
                Number(
                    a[metric.key] ?? 0
                );


            const scoreB =
                Number(
                    b[metric.key] ?? 0
                );


            if (
                scoreA >
                scoreB
            ) {

                return {

                    model:
                        "Model A",

                    reason:
                        `Overall scores are tied, but Model A has higher ${metric.label} (${scoreA}/100 vs ${scoreB}/100).`,

                    type:
                        "tie-break"

                };

            }


            if (
                scoreB >
                scoreA
            ) {

                return {

                    model:
                        "Model B",

                    reason:
                        `Overall scores are tied, but Model B has higher ${metric.label} (${scoreB}/100 vs ${scoreA}/100).`,

                    type:
                        "tie-break"

                };

            }

        }


        const hallucinationA =
            Number(
                a.hallucination ?? 0
            );


        const hallucinationB =
            Number(
                b.hallucination ?? 0
            );


        if (
            hallucinationA <
            hallucinationB
        ) {

            return {

                model:
                    "Model A",

                reason:
                    `Primary scores are tied, but Model A has lower hallucination risk (${hallucinationA}/100 vs ${hallucinationB}/100).`,

                type:
                    "tie-break"

            };

        }


        if (
            hallucinationB <
            hallucinationA
        ) {

            return {

                model:
                    "Model B",

                reason:
                    `Primary scores are tied, but Model B has lower hallucination risk (${hallucinationB}/100 vs ${hallucinationA}/100).`,

                type:
                    "tie-break"

            };

        }


        return {

            model:
                "No clear recommendation",

            reason:
                "Both models received identical evaluation scores.",

            type:
                "tie"

        };

    }


    /* =========================================================
       DISPLAY RECOMMENDATION
    ========================================================= */

    function renderModelRecommendation(
        data
    ) {

        const modelA =
            data.model_a_scores || {};


        const modelB =
            data.model_b_scores || {};


        const recommendation =
            calculateRecommendation(
                modelA,
                modelB
            );


        const box =
            $("model-recommendation");


        if (!box) {
            return;
        }


        box.style.display =
            "block";


        const icon =
            recommendation.type === "tie"
                ? "＝"
                : "✓";


        box.innerHTML = `

            <div class="recommendation-header">

                <div class="recommendation-icon">

                    ${icon}

                </div>


                <div>

                    <div class="recommendation-label">

                        Evaluation Recommendation

                    </div>


                    <div class="recommendation-model">

                        ${escapeHTML(
                            recommendation.model
                        )}

                    </div>

                </div>

            </div>


            <div class="recommendation-reason">

                ${escapeHTML(
                    recommendation.reason
                )}

            </div>


            <div class="recommendation-note">

                This recommendation is based on the
                current evaluation scores. The scores
                are heuristic signals and are not
                ground-truth benchmark results.

            </div>

        `;


        /*
         * Store recommendation for PDF.
         */

        if (lastEvaluation) {

            lastEvaluation.recommendation =
                recommendation.model;


            lastEvaluation.recommendation_reason =
                recommendation.reason;

        }


        updateReportButton();

    }


    /* =========================================================
       EVALUATION METRICS
    ========================================================= */

    function updateEvaluationMetrics(
        data
    ) {

        const modelA =
            data.model_a_scores || {};


        const modelB =
            data.model_b_scores || {};


        const accuracyA =
            modelA.accuracy ?? 0;


        const relevanceA =
            modelA.relevance ?? 0;


        const qualityA =
            modelA.quality ?? 0;


        const safetyA =
            modelA.safety ?? 0;


        const hallucinationA =
            modelA.hallucination ?? 0;


        const overallA =
            modelA.overall ?? 0;


        const accuracyB =
            modelB.accuracy ?? 0;


        const relevanceB =
            modelB.relevance ?? 0;


        const qualityB =
            modelB.quality ?? 0;


        const safetyB =
            modelB.safety ?? 0;


        const hallucinationB =
            modelB.hallucination ?? 0;


        const overallB =
            modelB.overall ?? 0;


        const accuracyElement =
            $("metric-accuracy");


        if (accuracyElement) {

            accuracyElement.textContent =
                `A: ${accuracyA} | B: ${accuracyB}`;

        }


        const relevanceElement =
            $("metric-relevance");


        if (relevanceElement) {

            relevanceElement.textContent =
                `A: ${relevanceA} | B: ${relevanceB}`;

        }


        const qualityElement =
            $("metric-quality");


        if (qualityElement) {

            qualityElement.textContent =
                `A: ${qualityA} | B: ${qualityB}`;

        }


        const safetyElement =
            $("metric-safety");


        if (safetyElement) {

            safetyElement.textContent =
                `A: ${safetyA} | B: ${safetyB}`;

        }


        const hallucinationElement =
            $("metric-hallucination");


        if (hallucinationElement) {

            hallucinationElement.textContent =
                `A: ${hallucinationA} | B: ${hallucinationB}`;

        }


        const overallElement =
            $("metric-overall");


        if (overallElement) {

            overallElement.textContent =
                `A: ${overallA} | B: ${overallB}`;

        }


        const latencyElement =
            $("metric-latency");


        const latency =
            data.evaluation_latency;


        if (latencyElement) {

            if (
                latency !== undefined &&
                latency !== null
            ) {

                latencyElement.textContent =
                    `${Number(
                        latency
                    ).toFixed(4)} s`;

            } else {

                latencyElement.textContent =
                    "--";

            }

        }


        const costElement =
            $("metric-cost");


        if (costElement) {

            costElement.textContent =
                "$0.00";

        }


        const modelASummary =
            $("model-a-score-summary");


        if (modelASummary) {

            modelASummary.innerHTML = `

                <strong>
                    Overall Score: ${overallA}/100
                </strong>

                <br><br>

                Accuracy:
                <strong>
                    ${accuracyA}/100
                </strong>

                <br>

                Relevance:
                <strong>
                    ${relevanceA}/100
                </strong>

                <br>

                Quality:
                <strong>
                    ${qualityA}/100
                </strong>

                <br>

                Safety:
                <strong>
                    ${safetyA}/100
                </strong>

                <br>

                Hallucination Risk:
                <strong>
                    ${hallucinationA}/100
                </strong>

            `;

        }


        const modelBSummary =
            $("model-b-score-summary");


        if (modelBSummary) {

            modelBSummary.innerHTML = `

                <strong>
                    Overall Score: ${overallB}/100
                </strong>

                <br><br>

                Accuracy:
                <strong>
                    ${accuracyB}/100
                </strong>

                <br>

                Relevance:
                <strong>
                    ${relevanceB}/100
                </strong>

                <br>

                Quality:
                <strong>
                    ${qualityB}/100
                </strong>

                <br>

                Safety:
                <strong>
                    ${safetyB}/100
                </strong>

                <br>

                Hallucination Risk:
                <strong>
                    ${hallucinationB}/100
                </strong>

            `;

        }


        renderScoreBars(
            "model-a-score-bars",
            modelA
        );


        renderScoreBars(
            "model-b-score-bars",
            modelB
        );

    }


    /* =========================================================
       ENABLE REPORT BUTTON
    ========================================================= */

    function updateReportButton() {

        const button =
            $("download-report-btn");


        const status =
            $("report-status");


        if (!button) {
            return;
        }


        if (
            lastEvaluation &&
            lastEvaluation.recommendation
        ) {

            button.disabled =
                false;


            if (status) {

                status.textContent =
                    "Report ready to download.";

            }

        } else {

            button.disabled =
                true;


            if (status) {

                status.textContent =
                    "Run an evaluation first.";

            }

        }

    }


    /* =========================================================
       DOWNLOAD EVALUATION REPORT
    ========================================================= */

    async function downloadEvaluationReport() {

        if (
            !lastEvaluation ||
            !lastEvaluation.recommendation
        ) {

            return alert(
                "Run an evaluation first."
            );

        }


        const button =
            $("download-report-btn");


        const status =
            $("report-status");


        button.disabled =
            true;


        button.textContent =
            "Generating Report...";


        if (status) {

            status.textContent =
                "Creating PDF report...";

        }


        try {

            const response =
                await fetch(
                    "/report/evaluation",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            prompt:
                                lastEvaluation.prompt,

                            model_a_scores:
                                lastEvaluation.model_a_scores,

                            model_b_scores:
                                lastEvaluation.model_b_scores,

                            recommendation:
                                lastEvaluation.recommendation,

                            recommendation_reason:
                                lastEvaluation.recommendation_reason,

                            evaluation_result:
                                lastEvaluation.evaluation_result,

                            evaluation_latency:
                                lastEvaluation.evaluation_latency

                        })

                    }
                );


            if (!response.ok) {

                let message =
                    "Could not generate report.";

                try {

                    const error =
                        await response.json();

                    message =
                        error.detail ||
                        message;

                } catch (_) {}


                throw new Error(
                    message
                );

            }


            const blob =
                await response.blob();


            const url =
                window.URL.createObjectURL(
                    blob
                );


            const link =
                document.createElement(
                    "a"
                );


            link.href =
                url;


            link.download =
                "ai_model_evaluation_report.pdf";


            document
                .body
                .appendChild(link);


            link.click();


            link.remove();


            window.URL.revokeObjectURL(
                url
            );


            if (status) {

                status.textContent =
                    "PDF report generated successfully.";

            }

        } catch (error) {

            console.error(
                "Report generation error:",
                error
            );


            if (status) {

                status.textContent =
                    "Report error: " +
                    error.message;

            }


            alert(
                "Could not generate the report: " +
                error.message
            );

        } finally {

            button.disabled =
                false;


            button.textContent =
                "Download Evaluation Report";

        }

    }


    /* =========================================================
       HISTORY
    ========================================================= */

    async function loadHistory() {

        try {

            const data =
                await requestJSON(
                    "/history"
                );


            const list =
                $("history-list");


            if (
                !data.history.length
            ) {

                list.textContent =
                    "No analyses yet.";

                return;

            }


            list.innerHTML =
                data.history
                    .map(
                        item => `

                            <div class="history-item">

                                <div class="history-head">

                                    <span class="history-type">

                                        ${escapeHTML(
                                            item.analysis_type
                                        )}

                                    </span>


                                    <button
                                        class="delete-one"
                                        data-id="${item.id}">

                                        Delete

                                    </button>

                                </div>


                                <div class="history-date">

                                    ${escapeHTML(
                                        item.created_at ||
                                        ""
                                    )}

                                </div>


                                <div class="history-prompt">

                                    ${escapeHTML(
                                        item.prompt
                                    )}

                                </div>


                                <div class="result">

                                    ${escapeHTML(
                                        item.result
                                    )}

                                </div>

                            </div>

                        `
                    )
                    .join("");


            document
                .querySelectorAll(
                    ".delete-one"
                )
                .forEach(button => {

                    button.addEventListener(
                        "click",
                        () =>
                            deleteHistoryItem(
                                button.dataset.id
                            )
                    );

                });


        } catch (error) {

            $("history-list").textContent =
                "Error: " +
                error.message;

        }

    }


    /* =========================================================
       DELETE HISTORY ITEM
    ========================================================= */

    async function deleteHistoryItem(
        id
    ) {

        if (
            !confirm(
                "Delete this analysis?"
            )
        ) {

            return;

        }


        try {

            await requestJSON(
                "/history/" + id,
                {
                    method: "DELETE"
                }
            );


            loadHistory();

            loadStats();

        } catch (error) {

            alert(
                error.message
            );

        }

    }


    /* =========================================================
       CLEAR HISTORY
    ========================================================= */

    async function clearHistory() {

        if (
            !confirm(
                "Delete all history?"
            )
        ) {

            return;

        }


        try {

            await requestJSON(
                "/history",
                {
                    method: "DELETE"
                }
            );


            loadHistory();

            loadStats();

        } catch (error) {

            alert(
                error.message
            );

        }

    }


    /* =========================================================
       HTML ESCAPING
    ========================================================= */

    function escapeHTML(
        value
    ) {

        return String(
            value ?? ""
        )

            .replaceAll(
                "&",
                "&amp;"
            )

            .replaceAll(
                "<",
                "&lt;"
            )

            .replaceAll(
                ">",
                "&gt;"
            )

            .replaceAll(
                '"',
                "&quot;"
            )

            .replaceAll(
                "'",
                "&#039;"
            );

    }


    /* =========================================================
       INITIALIZE APPLICATION
    ========================================================= */

    document.addEventListener(
        "DOMContentLoaded",
        () => {

            document
                .querySelectorAll(
                    ".nav-item, .action-card"
                )
                .forEach(button => {

                    button.addEventListener(
                        "click",
                        () => {

                            showPage(
                                button.dataset.page
                            );

                        }
                    );

                });


            $("start-evaluation-btn")
                .addEventListener(
                    "click",
                    () =>
                        showPage(
                            "evaluation"
                        )
                );


            $("analyze-text-btn")
                .addEventListener(
                    "click",
                    analyzeText
                );


            $("analyze-image-btn")
                .addEventListener(
                    "click",
                    analyzeImage
                );


            $("analyze-pdf-btn")
                .addEventListener(
                    "click",
                    analyzePdf
                );


            $("automatic-evaluate-btn")
                .addEventListener(
                    "click",
                    automaticEvaluation
                );


            $("manual-evaluate-btn")
                .addEventListener(
                    "click",
                    manualEvaluation
                );


            $("clear-history-btn")
                .addEventListener(
                    "click",
                    clearHistory
                );


            const reportButton =
                $("download-report-btn");


            if (reportButton) {

                reportButton.addEventListener(
                    "click",
                    downloadEvaluationReport
                );

            }


            loadHealth();

            loadStats();

            updateReportButton();

        }
    );


    /* =========================================================
       GLOBAL FUNCTIONS
    ========================================================= */

    window.showPage =
        showPage;


    window.analyzeText =
        analyzeText;


    window.analyzeImage =
        analyzeImage;


    window.analyzePdf =
        analyzePdf;


    window.automaticEvaluation =
        automaticEvaluation;


    window.manualEvaluation =
        manualEvaluation;


    window.loadHistory =
        loadHistory;


    window.clearHistory =
        clearHistory;


    window.downloadEvaluationReport =
        downloadEvaluationReport;

})();
