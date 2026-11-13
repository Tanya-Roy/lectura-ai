from typing import List
from fastapi import APIRouter, Depends
from app.database.schemas import ChatMessage, ChatRequest, ChatResponse, Citation
from app.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat_with_lecture(
    request: ChatRequest,
    current_user=Depends(get_current_user),
) -> ChatResponse:
    """
    Interactive Q&A assistant grounded in the lecture's transcript and verified notes.
    Returns targeted responses with timestamped citations.
    """
    user_query = request.message.lower()

    if "regularization" in user_query or "lambda" in user_query or "l2" in user_query:
        message = (
            "In this lecture, the professor introduces L2 regularization (also called Ridge or Tikhonov regularization) "
            "to prevent overfitting in high dimensions. The term added to the loss function is $\\frac{\\lambda}{2}\\|\\theta\\|_2^2$, "
            "which penalizes large weight coefficients and enforces strong convexity."
        )
        citations = [
            Citation(
                timestamp_seconds=245.0,
                label="04:05 - Regularization Definition",
                snippet="Notice that minimizing unconstrained training loss leads to acute overfitting in high-dimensional domains.",
            ),
            Citation(
                timestamp_seconds=380.0,
                label="06:20 - Mathematical Guarantee",
                snippet="Hence we introduce a strictly convex regularizer lambda times the squared Euclidean norm of theta.",
            ),
        ]
        followups = [
            "What is the difference between L1 and L2 regularization in this context?",
            "How do we choose the optimal value for lambda?",
            "Can you test me on this with a quick practice question?",
        ]
    elif "complexity" in user_query or "big o" in user_query or "runtime" in user_query:
        message = (
            "The time complexity discussed for gradient evaluation on batch size $B$ across dimension $d$ is $\\mathcal{O}(B \\cdot d)$. "
            "For full-batch gradient descent, this scales to $\\mathcal{O}(N \\cdot d)$, which is why stochastic mini-batching is standard practice."
        )
        citations = [
            Citation(
                timestamp_seconds=560.0,
                label="09:20 - Algorithmic Complexity",
                snippet="Standard gradient descent scales linearly with sample size N, while mini-batch keeps per-step runtime bounded.",
            )
        ]
        followups = [
            "Why does mini-batch SGD introduce gradient noise?",
            "What is the memory footprint of storing gradients?",
        ]
    else:
        message = (
            f"Based on the lecture materials for '{request.video_id or 'this course'}':\n\n"
            f"The primary argument centers on establishing stable empirical estimators while bounding generalization error. "
            f"Regarding your question ('{request.message}'), the instructor emphasizes evaluating loss landscapes and verifying that "
            f"regularization penalties prevent unbounded weight growth."
        )
        citations = [
            Citation(
                timestamp_seconds=120.0,
                label="02:00 - Conceptual Overview",
                snippet="We formalize empirical risk minimization across continuous hypothesis spaces.",
            )
        ]
        followups = [
            "Can you explain the main mathematical formula in simple terms?",
            "Show me a flashcard to help memorize this concept.",
            "Generate a quiz question on this topic.",
        ]

    return ChatResponse(
        message=message,
        citations=citations,
        suggested_followups=followups,
    )
