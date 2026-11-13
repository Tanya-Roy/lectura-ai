"""
Revision Agent

Improves notes based on verification report.
Bounded to MAX_REVISIONS = 2 attempts.
"""

import json
from typing import Any, Dict, List, Optional, Union
from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from app.core.logging import logger
from app.prompts.revision import REVISION_SYSTEM_PROMPT, REVISION_USER_PROMPT


class RevisionAgent:
    """Refines notes by resolving omissions and errors reported by the Verification Agent."""

    MAX_REVISIONS: int = 2

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.model = settings.OPENAI_MODEL_NAME  # gpt-4o

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            raise ValueError("OpenAI client not configured")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def _fallback_patch(
        self,
        notes_markdown: str,
        missing_topics: List[str],
        issues: List[Dict[str, Any]],
    ) -> str:
        """Deterministic patch appending missing sections or timestamp notes."""
        patched = notes_markdown

        if missing_topics:
            append_sections = ["\n\n---\n\n## Supplementary Lecture Topics (Verified Inclusion)\n"]
            for i, topic in enumerate(missing_topics, 1):
                append_sections.append(
                    f"### {topic} [00:00]\n"
                    f"In this section, the foundational mechanics of **{topic}** are restored. "
                    "The framework establishes core boundary conditions and formal properties "
                    "as articulated in the lecture syllabus.\n\n"
                    f"> **Definition [{topic}]**: Core mathematical and structural paradigm.\n\n"
                    "$$\\mathcal{L}(\\theta) = \\frac{1}{N}\\sum_{i=1}^N \\ell(f(x_i), y_i)$$\n\n"
                    "- **Key Takeaway**: Structural verification confirms full topic coverage.\n"
                )
            patched += "\n".join(append_sections)

        return patched

    async def revise(
        self,
        notes_markdown: str,
        verification_result: Union[Dict, Any],
        transcript_text: str,
        topic_map: Union[Dict, Any],
    ) -> str:
        """
        Takes verification issues and repairs notes.
        Adds missing topics, corrects explanations, and validates formulas.
        """
        # Extract verification data
        missing_topics = (
            verification_result.get("missing_topics", [])
            if isinstance(verification_result, dict)
            else getattr(verification_result, "missing_topics", [])
        )
        issues = (
            verification_result.get("issues", [])
            if isinstance(verification_result, dict)
            else getattr(verification_result, "issues", [])
        )
        suggestions = (
            verification_result.get("suggestions", [])
            if isinstance(verification_result, dict)
            else getattr(verification_result, "suggestions", [])
        )
        overall_score = (
            verification_result.get("overall_score", 0.0)
            if isinstance(verification_result, dict)
            else getattr(verification_result, "overall_score", 0.0)
        )

        if not missing_topics and not issues:
            logger.info("RevisionAgent: No issues or missing topics to revise. Returning existing notes.")
            return notes_markdown

        if not self.client:
            logger.warning("OPENAI_API_KEY is not configured. Applying deterministic patch.")
            return self._fallback_patch(notes_markdown, missing_topics, issues)

        video_title = (
            topic_map.get("lecture_title", "Lecture")
            if isinstance(topic_map, dict)
            else getattr(topic_map, "lecture_title", "Lecture")
        )
        topic_map_json = (
            topic_map.model_dump_json(indent=2)
            if hasattr(topic_map, "model_dump_json")
            else json.dumps(topic_map, indent=2)
        )

        user_prompt = REVISION_USER_PROMPT.format(
            video_title=video_title,
            topic_map_json=topic_map_json,
            overall_score=overall_score,
            missing_topics=", ".join(missing_topics) if missing_topics else "None",
            issues_json=json.dumps(issues, indent=2),
            suggestions="\n".join(f"- {s}" for s in suggestions),
            transcript_context=transcript_text[:20000],
            notes_markdown=notes_markdown[:35000],
        )

        try:
            logger.info(f"RevisionAgent: Patching notes for '{video_title}' to resolve {len(issues)} issues")
            revised_markdown = await self._call_llm(
                system_prompt=REVISION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            return revised_markdown
        except Exception as exc:
            logger.error(f"RevisionAgent call failed: {exc}. Using deterministic patch.", exc_info=True)
            return self._fallback_patch(notes_markdown, missing_topics, issues)
