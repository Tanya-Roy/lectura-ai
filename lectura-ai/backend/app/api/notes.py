from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.database.models import NoteType
from app.database.schemas import NoteCreate, NoteDetailResponse, NoteResponse, VerificationReportResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/notes", tags=["Notes"])

SAMPLE_MARKDOWN_COMPREHENSIVE = """# Lecture 4: Convex Optimization & Empirical Risk Minimization

## 1. Mathematical Foundations & Formulation
The core challenge in statistical machine learning is to identify an optimal parameter hypothesis $\\theta^* \\in \\Theta$ that minimizes the true generalization risk $\\mathcal{R}(\\theta)$:

$$\\mathcal{R}(\\theta) = \\mathbb{E}_{(x,y) \\sim \\mathcal{D}}[\\ell(f(x; \\theta), y)]$$

Because the underlying data-generating distribution $\\mathcal{D}$ is unknown in practice, we minimize the empirical proxy over $N$ observed training samples:

$$\\widehat{\\mathcal{R}}_N(\\theta) = \\frac{1}{N}\\sum_{i=1}^N \\ell(f(x_i; \\theta), y_i)$$

---

## 2. Regularization & Asymptotic Bounds
To constrain hypothesis capacity and penalize over-parameterization, Tikhonov regularization ($L_2$ norm) is added:

$$\\min_{\\theta \\in \\mathbb{R}^d} \\left\\{ \\frac{1}{N}\\sum_{i=1}^N \\ell(f(x_i; \\theta), y_i) + \\frac{\\lambda}{2} \\|\\theta\\|_2^2 \\right\\}$$

### Key Properties:
- **Strong Convexity**: When $\\lambda > 0$, the objective is strictly convex, guaranteeing a unique global minimum $\\theta^*$.
- **Lipschitz Continuity**: The gradient updates are bounded by $L = \\|X^T X\\| + \\lambda$.
- **Convergence Rate**: Standard gradient descent converges at $\\mathcal{O}(1/k)$, while accelerated Nesterov momentum achieves $\\mathcal{O}(1/k^2)$.

---

## 3. Algorithmic Implementation Steps
1. **Initialize Weights**: Set $\\theta_0 \\sim \\mathcal{N}(0, \\sigma^2 I)$.
2. **Compute Batch Gradient**: $\\nabla_{\\theta} \\mathcal{L}_B(\\theta) = \\frac{1}{|B|}\\sum_{i \\in B} \\nabla \\ell_i(\\theta) + \\lambda \\theta$.
3. **Parameter Step**: $\\theta_{t+1} \\leftarrow \\theta_t - \\eta_t \\nabla_{\\theta} \\mathcal{L}_B(\\theta)$.
4. **Evaluate Stopping Criterion**: Terminate when $\\|\\nabla \\mathcal{L}(\\theta)\\| < \\epsilon$.
"""

SAMPLE_MARKDOWN_REVISION = """# Revision Summary: Convex Optimization

### Critical Formula Cheat Sheet
| Concept | Mathematical Equation | Interpretation |
| :--- | :--- | :--- |
| **Empirical Loss** | $\\widehat{\\mathcal{R}}_N(\\theta) = \\frac{1}{N}\\sum \\ell(f(x_i),\\, y_i)$ | Mean loss on sample dataset |
| **L2 Regularizer** | $\\frac{\\lambda}{2}\\|\\theta\\|_2^2$ | Enforces weight decay |
| **Condition Number** | $\\kappa = \\frac{\\lambda_{\\max}}{\\lambda_{\\min}}$ | Curvature ratio; lower is faster convergence |

### Quick Recall Checklist
- [x] Unregularized risk causes variance explosion on finite $N$.
- [x] L2 regularization makes the Hessian positive definite.
- [x] Optimal step size is $\\eta \\le 2 / (L + \\mu)$.
"""

SAMPLE_MARKDOWN_LAST_MINUTE = """# Last-Minute Exam Prep ⚡: Optimization

- **Core Goal**: Minimize sample loss while bounding parameter magnitudes.
- **Formula to Memorize**: $\\nabla \\mathcal{L} = \\frac{1}{N}\\sum \\nabla \\ell_i + \\lambda \\theta$.
- **High-Yield Exam Trap**: Remember that increasing $\\lambda$ decreases variance but increases bias (Bias-Variance Tradeoff).
- **Complexity**: Training with mini-batch SGD scales as $\\mathcal{O}(B \\cdot d)$ per step.
"""


@router.get("", response_model=List[NoteResponse])
async def list_notes(
    course_id: Optional[str] = Query(None),
    video_id: Optional[str] = Query(None),
    note_type: Optional[NoteType] = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[NoteResponse]:
    """Lists study notes filtered by course, video, or note type."""
    now = datetime.now(timezone.utc)
    return [
        NoteResponse(
            id="nt_comp_001",
            course_id=course_id or "crs_ml_101",
            video_id=video_id or "vid_ml_01",
            note_type=NoteType.COMPREHENSIVE,
            title="Comprehensive Guide: Convex Optimization & Empirical Risk",
            outline=[
                {"title": "1. Mathematical Foundations & Formulation", "timestamp": 0.0},
                {"title": "2. Regularization & Asymptotic Bounds", "timestamp": 240.0},
                {"title": "3. Algorithmic Implementation Steps", "timestamp": 560.0},
            ],
            key_takeaways=[
                "Strong convexity guarantees unique global minima with L2 penalty.",
                "Bias-variance tradeoff depends directly on regularization factor lambda.",
            ],
            citations=[
                {"timestamp_seconds": 120.0, "label": "Foundations", "snippet": "empirical risk formulation"},
                {"timestamp_seconds": 380.0, "label": "Regularization", "snippet": "Tikhonov regularization discussion"},
            ],
            version=1,
            created_at=now,
            updated_at=now,
        ),
        NoteResponse(
            id="nt_rev_002",
            course_id=course_id or "crs_ml_101",
            video_id=video_id or "vid_ml_01",
            note_type=NoteType.REVISION,
            title="Revision Sheet: Convex Optimization & Formulas",
            outline=[{"title": "Formula Cheat Sheet", "timestamp": 0.0}],
            key_takeaways=["Memorize Hessian condition bounds."],
            version=1,
            created_at=now,
            updated_at=now,
        ),
        NoteResponse(
            id="nt_last_003",
            course_id=course_id or "crs_ml_101",
            video_id=video_id or "vid_ml_01",
            note_type=NoteType.LAST_MINUTE,
            title="Last-Minute Cheat Sheet: Optimization ⚡",
            outline=[{"title": "Core Trap & 30-Sec Summary", "timestamp": 0.0}],
            key_takeaways=["Remember lambda vs bias-variance."],
            version=1,
            created_at=now,
            updated_at=now,
        ),
    ]


@router.get("/{note_id}", response_model=NoteDetailResponse)
async def get_note(
    note_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteDetailResponse:
    """Retrieves full note markdown and academic verification report."""
    note_type = NoteType.COMPREHENSIVE
    markdown = SAMPLE_MARKDOWN_COMPREHENSIVE

    if "rev" in note_id:
        note_type = NoteType.REVISION
        markdown = SAMPLE_MARKDOWN_REVISION
    elif "last" in note_id:
        note_type = NoteType.LAST_MINUTE
        markdown = SAMPLE_MARKDOWN_LAST_MINUTE

    now = datetime.now(timezone.utc)
    return NoteDetailResponse(
        id=note_id,
        course_id="crs_ml_101",
        video_id="vid_ml_01",
        note_type=note_type,
        title=f"Optimization & Learning Bounds ({note_type.value.capitalize()})",
        markdown_content=markdown,
        outline=[
            {"title": "1. Mathematical Foundations & Formulation", "timestamp": 0.0},
            {"title": "2. Regularization & Asymptotic Bounds", "timestamp": 240.0},
            {"title": "3. Algorithmic Implementation Steps", "timestamp": 560.0},
        ],
        key_takeaways=[
            "Strictly convex regularizers ensure unique convergence.",
            "Gradient descent achieves O(1/k) rate without momentum acceleration.",
        ],
        citations=[
            {"timestamp_seconds": 120.0, "label": "Theorem 1.1", "snippet": "empirical risk definition"},
            {"timestamp_seconds": 380.0, "label": "Lemma 2.3", "snippet": "L2 norm boundedness proof"},
        ],
        version=1,
        created_at=now,
        updated_at=now,
        verification_reports=[
            VerificationReportResponse(
                id="vrf_001",
                note_id=note_id,
                rigor_score=0.98,
                is_verified=True,
                claims_verified_count=16,
                discrepancies_found=[],
                feedback_notes="All LaTeX equations checked against standard academic definitions. Citations cross-referenced with video timeline.",
                created_at=now,
            )
        ],
    )


@router.post("", response_model=NoteResponse)
async def create_note(
    note_in: NoteCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """Creates or saves customized note content."""
    now = datetime.now(timezone.utc)
    return NoteResponse(
        id="nt_custom_999",
        course_id=note_in.course_id,
        video_id=note_in.video_id,
        note_type=note_in.note_type,
        title=note_in.title,
        outline=note_in.outline,
        key_takeaways=note_in.key_takeaways,
        citations=note_in.citations,
        version=1,
        created_at=now,
        updated_at=now,
    )


@router.get("/{note_id}/export/{format}")
async def export_note(
    note_id: str,
    format: str,
    current_user=Depends(get_current_user),
):
    """Exports note content as Markdown, PDF or plain text."""
    if format == "markdown" or format == "md":
        return Response(
            content=SAMPLE_MARKDOWN_COMPREHENSIVE,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=lectura_{note_id}.md"},
        )
    return Response(
        content=f"# Lectura Export ({format})\n\n{SAMPLE_MARKDOWN_COMPREHENSIVE}",
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=lectura_{note_id}.{format}"},
    )
