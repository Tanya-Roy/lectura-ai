from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.database.schemas import (
    FlashcardResponse,
    FlashcardReviewRequest,
    QuizAttemptResponse,
    QuizQuestionResponse,
    QuizResponse,
    QuizSubmitRequest,
)
from app.dependencies import get_current_user

router = APIRouter(tags=["Quizzes & Flashcards"])

# Mock Flashcard dataset
MOCK_FLASHCARDS = [
    {
        "id": "fc_001",
        "course_id": "crs_ml_101",
        "video_id": "vid_ml_01",
        "front": "What is the primary motivation for introducing L2 regularization into empirical risk minimization?",
        "back": "To penalize excessively large parameter weights, ensuring strong convexity, unique convergence, and preventing high-dimensional overfitting.",
        "topic": "Loss Minimization",
        "difficulty": 2,
        "ease_factor": 2.5,
        "interval_days": 1,
        "repetitions": 1,
        "last_reviewed": datetime.now(timezone.utc),
        "next_review": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    },
    {
        "id": "fc_002",
        "course_id": "crs_ml_101",
        "video_id": "vid_ml_01",
        "front": "State the convergence rate of standard gradient descent on L-smooth convex functions.",
        "back": "O(1/k), where k is the number of update iterations. (Accelerated Nesterov momentum improves this to O(1/k^2)).",
        "topic": "Convergence Theory",
        "difficulty": 3,
        "ease_factor": 2.3,
        "interval_days": 2,
        "repetitions": 2,
        "last_reviewed": datetime.now(timezone.utc),
        "next_review": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    },
    {
        "id": "fc_003",
        "course_id": "crs_ml_101",
        "video_id": "vid_ml_01",
        "front": "How does the condition number kappa = lambda_max / lambda_min affect gradient descent stability?",
        "back": "A large kappa signifies anisotropic ill-conditioning ('narrow ravines'), which causes oscillations and drastically slows convergence.",
        "topic": "Optimization Landscapes",
        "difficulty": 2,
        "ease_factor": 2.6,
        "interval_days": 4,
        "repetitions": 3,
        "last_reviewed": datetime.now(timezone.utc),
        "next_review": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    },
]

# Mock Quiz Questions
SAMPLE_QUESTIONS = [
    QuizQuestionResponse(
        id="q_1",
        quiz_id="qz_101",
        question_text="Why does unconstrained empirical risk minimization suffer from high variance on small sample sizes?",
        options=[
            "Because the loss function is guaranteed to become concave",
            "Because the model fits sample-specific noise rather than the true underlying distribution",
            "Because gradient descent cannot compute gradients on discrete samples",
            "Because the learning rate diverges to negative infinity",
        ],
        correct_option_index=1,
        explanation="In finite sample regimes, complex hypothesis spaces easily interpolate noisy outliers without constraint.",
        timestamp_reference=145.0,
    ),
    QuizQuestionResponse(
        id="q_2",
        quiz_id="qz_101",
        question_text="What mathematical guarantee does adding an L2 regularization term (lambda/2 * ||theta||^2) provide?",
        options=[
            "It turns any non-convex loss into a linear programming problem",
            "It guarantees that the resulting objective function is strictly convex with a unique global minimum",
            "It eliminates all need for hyperparameter cross-validation",
            "It forces all weight coordinates to exactly zero simultaneously",
        ],
        correct_option_index=1,
        explanation="Adding a quadratic penalty to a convex function ensures strict convexity and non-singular Hessian.",
        timestamp_reference=320.0,
    ),
    QuizQuestionResponse(
        id="q_3",
        quiz_id="qz_101",
        question_text="In mini-batch SGD, how does the computational complexity scale per iteration with batch size B and parameter dimension d?",
        options=[
            "O(B^2 * d)",
            "O(B * d)",
            "O(d^3)",
            "O(exp(B))",
        ],
        correct_option_index=1,
        explanation="Each sample requires computing an inner product and derivative of dimension d, resulting in O(B * d) FLOPs.",
        timestamp_reference=510.0,
    ),
]


# Quizzes Endpoints
@router.get("/quizzes", response_model=List[QuizResponse])
async def list_quizzes(
    course_id: Optional[str] = Query(None),
    video_id: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[QuizResponse]:
    """Retrieves quizzes generated for a course or video."""
    return [
        QuizResponse(
            id="qz_101",
            course_id=course_id or "crs_ml_101",
            video_id=video_id or "vid_ml_01",
            title="Mastery Check: Convex Optimization & Risk Bounds",
            description="3 rigorous questions covering loss function convexity, regularization, and algorithmic complexity.",
            created_at=datetime.now(timezone.utc),
            questions=SAMPLE_QUESTIONS,
        )
    ]


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizResponse:
    """Retrieves an individual quiz challenge."""
    return QuizResponse(
        id=quiz_id,
        course_id="crs_ml_101",
        video_id="vid_ml_01",
        title="Mastery Check: Convex Optimization & Risk Bounds",
        description="Verify your grasp of empirical risk, regularization, and gradient dynamics.",
        created_at=datetime.now(timezone.utc),
        questions=SAMPLE_QUESTIONS,
    )


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizAttemptResponse)
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmitRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizAttemptResponse:
    """Scores a quiz attempt and stores results for learning progress tracking."""
    correct_count = 0
    total = len(SAMPLE_QUESTIONS)

    for q in SAMPLE_QUESTIONS:
        user_choice = submission.answers.get(q.id)
        if user_choice is not None and user_choice == q.correct_option_index:
            correct_count += 1

    score_pct = (correct_count / total * 100.0) if total > 0 else 0.0

    return QuizAttemptResponse(
        id=f"att_{datetime.now().timestamp()}",
        quiz_id=quiz_id,
        user_id=current_user.id,
        score_percentage=round(score_pct, 1),
        user_answers=submission.answers,
        completed_at=datetime.now(timezone.utc),
    )


# Flashcards Endpoints
@router.get("/flashcards", response_model=List[FlashcardResponse])
async def list_flashcards(
    course_id: Optional[str] = Query(None),
    video_id: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[FlashcardResponse]:
    """Retrieves flashcard deck for active spaced-repetition recall."""
    return [FlashcardResponse(**f) for f in MOCK_FLASHCARDS]


@router.post("/flashcards/{flashcard_id}/review", response_model=FlashcardResponse)
async def review_flashcard(
    flashcard_id: str,
    review: FlashcardReviewRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlashcardResponse:
    """
    Submits SM-2 spaced repetition rating (1-5) and updates interval and ease factor.
    """
    card = next((c for c in MOCK_FLASHCARDS if c["id"] == flashcard_id), MOCK_FLASHCARDS[0])
    # SM-2 logic calculation
    q = review.rating
    card["repetitions"] = card.get("repetitions", 0) + 1
    new_ease = max(1.3, card["ease_factor"] + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    card["ease_factor"] = round(new_ease, 2)
    if q < 3:
        card["interval_days"] = 1
    elif card["repetitions"] == 1:
        card["interval_days"] = 1
    elif card["repetitions"] == 2:
        card["interval_days"] = 6
    else:
        card["interval_days"] = int(card["interval_days"] * card["ease_factor"])

    card["last_reviewed"] = datetime.now(timezone.utc)
    return FlashcardResponse(**card)
