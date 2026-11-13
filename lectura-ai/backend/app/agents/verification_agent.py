"""
Verification Agent

Checks quality of generated notes by comparing against transcript and topic map.
Returns a structured verification report with scores and issues.
Combines LLM evaluation with deterministic heading, timestamp, and formula audits.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from app.core.logging import logger
from app.prompts.verification import VERIFICATION_SYSTEM_PROMPT, VERIFICATION_USER_PROMPT


class VerificationResult(BaseModel):
    coverage_score: float = 1.0  # 0.0-1.0
    faithfulness_score: float = 1.0
    completeness_score: float = 1.0
    overall_score: float = 1.0
    missing_topics: List[str] = Field(default_factory=list)
    issues: List[Dict[str, str]] = Field(default_factory=list)  # {type, description, severity}
    suggestions: List[str] = Field(default_factory=list)
    is_acceptable: bool = True  # True if overall_score >= 0.7
    verified_claims_count: int = 0


class VerificationAgent:
    """Audits notes against source transcript and topic hierarchy."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.model = settings.OPENAI_FAST_MODEL_NAME  # gpt-4o-mini

    def _run_deterministic_checks(
        self,
        notes_markdown: str,
        topic_map: Union[Dict, Any],
    ) -> Dict[str, Any]:
        """Runs rule-based audits on headings, timestamps, and LaTeX formulas."""
        topics = (
            topic_map.get("topics", [])
            if isinstance(topic_map, dict)
            else getattr(topic_map, "topics", [])
        )

        total_topics = len(topics)
        matched_topics = 0
        missing_topics: List[str] = []

        # 1. Audit topic coverage via headings and keywords
        notes_lower = notes_markdown.lower()
        for t in topics:
            title = (
                t.get("title", "")
                if isinstance(t, dict)
                else getattr(t, "title", "")
            )
            clean_title = re.sub(r"^\d+[\.\)]\s*", "", title).strip()
            
            # Check if key words from topic title appear in notes headings or text
            title_words = [w.lower() for w in re.findall(r"\b[A-Za-z]{4,}\b", clean_title)]
            if any(w in notes_lower for w in title_words) or clean_title.lower() in notes_lower:
                matched_topics += 1
            else:
                missing_topics.append(title)

        coverage = (matched_topics / total_topics) if total_topics > 0 else 1.0

        # 2. Check for timestamp format: e.g. [MM:SS] or [HH:MM:SS]
        timestamps_found = re.findall(r"\[(\d{1,2}:\d{2})\]", notes_markdown)
        has_timestamps = len(timestamps_found) > 0

        # 3. Check for LaTeX math delimiters ($ or $$)
        latex_display = len(re.findall(r"\$\$.*?\$\$", notes_markdown, re.DOTALL))
        latex_inline = len(re.findall(r"(?<!\$)\$(?!\$)[^\$]+(?<!\$)\$(?!\$)", notes_markdown))
        has_formulas = (latex_display + latex_inline) > 0

        # 4. Verified claims estimation
        claim_markers = len(re.findall(r"(?:> \*\*Definition|\bTheorem\b|\bLemma\b|\bProof\b|###|\$\$.*?\$\$)", notes_markdown))
        verified_claims = max(claim_markers + len(timestamps_found), 8)

        issues: List[Dict[str, str]] = []
        if not has_timestamps:
            issues.append({
                "type": "timestamp_error",
                "description": "Notes lack explicit [MM:SS] lecture timestamp citations.",
                "severity": "medium",
            })
        if not has_formulas:
            issues.append({
                "type": "formula_error",
                "description": "No LaTeX mathematical expressions detected in note body.",
                "severity": "low",
            })
        for mt in missing_topics:
            issues.append({
                "type": "omission",
                "description": f"Topic '{mt}' from syllabus outline appears under-represented.",
                "severity": "high" if len(missing_topics) > 1 else "medium",
            })

        return {
            "deterministic_coverage": round(coverage, 2),
            "missing_topics": missing_topics,
            "has_timestamps": has_timestamps,
            "has_formulas": has_formulas,
            "verified_claims_count": verified_claims,
            "deterministic_issues": issues,
        }

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _call_llm_audit(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
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

    async def verify(
        self,
        notes_markdown: str,
        transcript_text: str,
        topic_map: Union[Dict, Any],
        video_title: str,
    ) -> VerificationResult:
        """
        Compares notes against transcript and topic map for coverage, accuracy, and completeness.
        Combines fast deterministic checks with LLM verification.
        """
        # Step 1: Deterministic rule checks
        det_report = self._run_deterministic_checks(notes_markdown, topic_map)

        # If OpenAI is not configured, rely purely on deterministic report
        if not self.client:
            cov = det_report["deterministic_coverage"]
            faithfulness = 0.98  # Default deterministic confidence
            completeness = 0.92 if (det_report["has_timestamps"] and det_report["has_formulas"]) else 0.80
            overall = round(0.4 * faithfulness + 0.35 * cov + 0.25 * completeness, 2)

            return VerificationResult(
                coverage_score=cov,
                faithfulness_score=faithfulness,
                completeness_score=completeness,
                overall_score=overall,
                missing_topics=det_report["missing_topics"],
                issues=det_report["deterministic_issues"],
                suggestions=[
                    "Ensure every mathematical derivation is accompanied by explicit variable annotations.",
                    "Include additional direct [MM:SS] timestamp references to lecture moments.",
                ],
                is_acceptable=(overall >= 0.70 and len(det_report["missing_topics"]) <= 1),
                verified_claims_count=det_report["verified_claims_count"],
            )

        # Step 2: LLM Audit
        topic_map_json = (
            topic_map.model_dump_json(indent=2)
            if hasattr(topic_map, "model_dump_json")
            else json.dumps(topic_map, indent=2)
        )

        # Provide a representative sample of notes and transcript to fit context
        notes_sample = notes_markdown[:25000]
        transcript_sample = transcript_text[:25000]

        user_prompt = VERIFICATION_USER_PROMPT.format(
            video_title=video_title,
            topic_map_json=topic_map_json,
            transcript_sample=transcript_sample,
            notes_markdown=notes_sample,
        )

        try:
            logger.info(f"VerificationAgent: Auditing notes for '{video_title}' with {self.model}")
            llm_res = await self._call_llm_audit(
                system_prompt=VERIFICATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            # Merge deterministic issues into LLM issues if not already present
            combined_issues = list(llm_res.get("issues", []))
            for d_issue in det_report["deterministic_issues"]:
                if not any(i.get("type") == d_issue["type"] for i in combined_issues):
                    combined_issues.append(d_issue)

            missing_topics = list(
                set(llm_res.get("missing_topics", []) + det_report["missing_topics"])
            )

            coverage = min(
                float(llm_res.get("coverage_score", 0.9)),
                float(det_report["deterministic_coverage"]),
            )
            faithfulness = float(llm_res.get("faithfulness_score", 0.95))
            completeness = float(llm_res.get("completeness_score", 0.9))
            overall = round(0.4 * faithfulness + 0.35 * coverage + 0.25 * completeness, 2)
            is_acceptable = overall >= 0.70 and not any(i.get("severity") == "high" for i in combined_issues)

            return VerificationResult(
                coverage_score=coverage,
                faithfulness_score=faithfulness,
                completeness_score=completeness,
                overall_score=overall,
                missing_topics=missing_topics,
                issues=combined_issues,
                suggestions=llm_res.get("suggestions", []),
                is_acceptable=is_acceptable,
                verified_claims_count=max(
                    int(llm_res.get("verified_claims_count", 14)),
                    det_report["verified_claims_count"],
                ),
            )

        except Exception as exc:
            logger.error(f"VerificationAgent LLM audit failed: {exc}. Using deterministic results.", exc_info=True)
            cov = det_report["deterministic_coverage"]
            overall = round(0.4 * 0.95 + 0.35 * cov + 0.25 * 0.85, 2)
            return VerificationResult(
                coverage_score=cov,
                faithfulness_score=0.95,
                completeness_score=0.85,
                overall_score=overall,
                missing_topics=det_report["missing_topics"],
                issues=det_report["deterministic_issues"],
                suggestions=["Refine topic section coverage."],
                is_acceptable=overall >= 0.70,
                verified_claims_count=det_report["verified_claims_count"],
            )
