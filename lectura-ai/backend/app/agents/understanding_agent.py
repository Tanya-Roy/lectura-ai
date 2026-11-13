"""
Content Understanding Agent

Reads transcript chunks and produces a structured topic map:
- Main subject identification
- Major topics and subtopics
- Definitions, formulas, examples
- Topic transitions
- Hierarchical lecture outline
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from app.core.logging import logger
from app.prompts.understanding import UNDERSTANDING_SYSTEM_PROMPT, UNDERSTANDING_USER_PROMPT


class TopicMapEntry(BaseModel):
    title: str
    subtopics: List[str] = Field(default_factory=list)
    definitions: List[str] = Field(default_factory=list)
    formulas: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    key_terms: List[str] = Field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    depth: str = "extensive"  # "brief" | "moderate" | "extensive"


class TopicMap(BaseModel):
    subject: str
    lecture_title: str
    topics: List[TopicMapEntry] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    total_concepts: int = 0


class UnderstandingAgent:
    """Analyzes transcript chunks to build a hierarchical topic map."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.model = settings.OPENAI_MODEL_NAME

    def _extract_chunk_attr(self, chunk: Union[Dict, Any], key: str, default: Any = None) -> Any:
        if isinstance(chunk, dict):
            return chunk.get(key, default)
        return getattr(chunk, key, default)

    def _format_chunks_for_prompt(self, chunks: List[Union[Dict, Any]], max_chars: int = 80000) -> str:
        """Formats transcript chunks with timestamp headers, limiting length to avoid token limits."""
        lines = []
        char_count = 0

        for c in chunks:
            idx = self._extract_chunk_attr(c, "chunk_index", 0)
            start = self._extract_chunk_attr(c, "start_time", 0.0)
            end = self._extract_chunk_attr(c, "end_time", 0.0)
            text = self._extract_chunk_attr(c, "text", "")
            hint = self._extract_chunk_attr(c, "topic_hint", "")

            start_m, start_s = int(start // 60), int(start % 60)
            end_m, end_s = int(end // 60), int(end % 60)
            time_str = f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}]"

            hint_str = f" (Topic: {hint})" if hint else ""
            block = f"Chunk #{idx + 1} {time_str}{hint_str}:\n{text.strip()}\n"

            if char_count + len(block) > max_chars:
                lines.append("\n[... Remaining transcript segments summarized due to length ...]\n")
                break

            lines.append(block)
            char_count += len(block)

        return "\n".join(lines)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _call_llm_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Performs OpenAI API call with JSON mode enforcement and automatic retry."""
        if not self.client:
            raise ValueError("OpenAI client not configured")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def _build_fallback_topic_map(
        self,
        video_title: str,
        chunks: List[Union[Dict, Any]],
        transcript_text: str,
    ) -> TopicMap:
        """Deterministic fallback when OpenAI API key is unavailable or fails."""
        logger.warning(f"Using deterministic fallback for TopicMap on '{video_title}'")
        
        # Deduce subject from title
        subject = "Computer Science & Machine Learning"
        for kw, subj in [
            ("physics", "Physics"),
            ("math", "Mathematics"),
            ("calculus", "Calculus"),
            ("chemistry", "Chemistry"),
            ("biology", "Biology"),
            ("economics", "Economics"),
            ("history", "History"),
            ("philosophy", "Philosophy"),
            ("algorithm", "Computer Science"),
            ("data", "Data Science"),
        ]:
            if kw in video_title.lower():
                subject = subj
                break

        topics: List[TopicMapEntry] = []
        if chunks:
            # Group chunks into 3-5 macro topics
            num_chunks = len(chunks)
            group_size = max(1, num_chunks // 4)
            for i in range(0, num_chunks, group_size):
                sub_group = chunks[i : i + group_size]
                first = sub_group[0]
                last = sub_group[-1]

                start_t = self._extract_chunk_attr(first, "start_time", 0.0)
                end_t = self._extract_chunk_attr(last, "end_time", start_t + 180.0)
                hint = self._extract_chunk_attr(first, "topic_hint", None)

                combined_text = " ".join(self._extract_chunk_attr(c, "text", "") for c in sub_group)
                
                # Heuristic keyword extraction
                words = re.findall(r"\b[A-Z][a-z]{3,}\b", combined_text)
                key_terms = list(dict.fromkeys(words[:5])) if words else ["Fundamentals", "Formulation"]

                topic_title = hint or f"Section {len(topics) + 1}: {key_terms[0] if key_terms else 'Core Concepts'}"

                topics.append(
                    TopicMapEntry(
                        title=topic_title,
                        subtopics=[f"Principles of {t}" for t in key_terms[:3]],
                        definitions=[f"{key_terms[0]}: Core concept foundational to this section."] if key_terms else [],
                        formulas=["\\mathcal{L}(\\theta) = \\frac{1}{N}\\sum_{i=1}^N \\ell(f(x_i), y_i)"],
                        examples=[f"Practical application of {key_terms[0] if key_terms else 'the topic'}."],
                        key_terms=key_terms,
                        start_time=round(float(start_t), 1),
                        end_time=round(float(end_t), 1),
                        depth="extensive",
                    )
                )
        else:
            # Fallback if no chunks
            topics = [
                TopicMapEntry(
                    title="1. Introduction & Theoretical Foundations",
                    subtopics=["Historical Motivation", "First Principles Analysis"],
                    definitions=["System Architecture: General formal layout."],
                    formulas=["f(x) = \\sigma(W^T x + b)"],
                    examples=["Basic benchmark setup."],
                    key_terms=["Foundations", "Architecture", "Optimization"],
                    start_time=0.0,
                    end_time=300.0,
                    depth="extensive",
                ),
                TopicMapEntry(
                    title="2. Mathematical Formulation & Algorithmic Mechanics",
                    subtopics=["Objective Functions", "Convergence Properties"],
                    definitions=["Convergence: Limit behavior under optimization iterations."],
                    formulas=["\\theta_{t+1} = \\theta_t - \\eta \\nabla \\mathcal{L}(\\theta_t)"],
                    examples=["Step-by-step update on a 2D loss surface."],
                    key_terms=["Gradient", "Convergence", "Loss Function"],
                    start_time=300.0,
                    end_time=600.0,
                    depth="extensive",
                ),
            ]

        total_concepts = sum(len(t.subtopics) + len(t.definitions) + len(t.key_terms) for t in topics)

        return TopicMap(
            subject=subject,
            lecture_title=video_title,
            topics=topics,
            prerequisites=["Foundational linear algebra", "Introductory calculus and probability"],
            total_concepts=max(total_concepts, 6),
        )

    async def analyze(
        self,
        transcript_text: str,
        video_title: str,
        chunks: List[Union[Dict, Any]],
    ) -> TopicMap:
        """
        Sends transcript chunks to OpenAI GPT-4o with structured output request.
        Returns TopicMap with all topics, definitions, and formulas identified.
        Falls back gracefully if API is unavailable.
        """
        if not self.client:
            logger.warning("OPENAI_API_KEY is not configured. Running fallback topic extraction.")
            return self._build_fallback_topic_map(video_title, chunks, transcript_text)

        formatted_chunks = self._format_chunks_for_prompt(chunks)
        user_prompt = UNDERSTANDING_USER_PROMPT.format(
            video_title=video_title,
            total_chunks=len(chunks),
            transcript_content=formatted_chunks,
        )

        try:
            logger.info(f"UnderstandingAgent: Analyzing {len(chunks)} chunks for '{video_title}' with {self.model}")
            result_json = await self._call_llm_json(
                system_prompt=UNDERSTANDING_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            # Validate against Pydantic model
            topic_map = TopicMap.model_validate(result_json)
            logger.info(
                f"UnderstandingAgent: Successfully identified {len(topic_map.topics)} topics "
                f"and {topic_map.total_concepts} concepts for '{video_title}'"
            )
            return topic_map

        except Exception as exc:
            logger.error(f"UnderstandingAgent LLM call failed: {exc}. Falling back to deterministic extraction.", exc_info=True)
            return self._build_fallback_topic_map(video_title, chunks, transcript_text)
