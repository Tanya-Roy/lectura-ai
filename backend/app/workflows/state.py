from typing import Any, Dict, List, Optional, TypedDict


class ChunkItem(TypedDict):
    chunk_index: int
    start_time: float
    end_time: float
    text: str


class TopicItem(TypedDict):
    title: str
    summary: str
    start_time: float
    end_time: float
    order_index: int


class FlashcardItem(TypedDict):
    front: str
    back: str
    topic: str
    difficulty: int


class QuizQuestionItem(TypedDict):
    question_text: str
    options: List[str]
    correct_option_index: int
    explanation: str
    timestamp_reference: Optional[float]


class WorkflowState(TypedDict, total=False):
    """
    Central state dictionary passed across LangGraph pipeline agents:
    Ingestion -> Understanding -> Note Generation -> Verification -> Revision Loop -> Active Recall -> Finalize
    """
    # Identifiers
    video_id: str
    course_id: str
    url: str

    # Video Metadata
    video_title: str
    channel_name: str
    duration_seconds: int

    # Transcripts & Segmentation
    raw_transcript: str
    chunks: List[Dict[str, Any]]
    topics: List[Dict[str, Any]]

    # Phase 3: Topic Map from Understanding Agent
    topic_map: Dict[str, Any]

    # Synthesized Notes (Multi-Tiered)
    comprehensive_notes: str
    revision_notes: str
    last_minute_notes: str
    outline: List[Dict[str, Any]]
    key_takeaways: List[str]
    citations: List[Dict[str, Any]]

    # Academic Verification & Fact-Checking
    rigor_score: float
    is_verified: bool
    claims_verified_count: int
    discrepancies: List[Dict[str, Any]]
    feedback_notes: str
    verification_result: Dict[str, Any]

    # Phase 3: Verification & Revision Tracking
    verification_attempts: int
    max_verification_attempts: int

    # Active Recall Artifacts
    flashcards: List[FlashcardItem]
    quizzes: List[QuizQuestionItem]

    # Generation Settings
    generate_flashcards: bool
    generate_quizzes: bool

    # Execution Tracking
    job_id: str
    status: str
    current_node: str
    progress_percentage: int
    logs: List[Dict[str, Any]]
    error_message: Optional[str]
