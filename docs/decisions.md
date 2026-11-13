# Lectura AI - Architecture Decision Records (ADR) 🏛️

## ADR 001: Selection of LangGraph for Agent Orchestration
- **Status**: Accepted
- **Context**: Video lecture synthesis requires multi-stage pipelined intelligence: transcription extraction, topic outline generation, tiered note authoring, mathematical verification, and quiz/flashcard creation. Standard prompt chains cannot handle state rollbacks, intermediate inspections, or conditional routing.
- **Decision**: Adopt LangGraph with a centralized `WorkflowState` (TypedDict) and explicitly modeled nodes (`ingest_video`, `extract_structure`, `generate_notes`, `verify_notes`, `generate_active_recall`, `finalize`).
- **Consequences**: Enables modular testing of each agent node, granular progress reporting (0-100%), and easy addition of human-in-the-loop approvals or retry loops for failed verification audits.

---

## ADR 002: Multi-Tiered Note Synthesis Strategy
- **Status**: Accepted
- **Context**: Students and researchers have different cognitive requirements at different study stages (first-time understanding vs. weekend revision vs. 5 minutes before an exam).
- **Decision**: Generate 3 distinct note representations for every lecture:
  1. **Comprehensive Master Notes**: Deep academic breakdowns with full LaTeX proofs, variable definitions, diagrams, and timestamped citations.
  2. **Revision Cheat Sheet**: Tabular comparison sheets, core formula summaries, and quick checklists.
  3. **Last-Minute Flash Notes**: High-yield 30-second conceptual anchors and common exam pitfalls.
- **Consequences**: Improves student retention, supports differentiated learning styles, and increases platform engagement.

---

## ADR 003: Public Transcript Extraction & oEmbed Fallback
- **Status**: Accepted
- **Context**: Relying exclusively on YouTube Data API v3 requires users or servers to configure Google Cloud project credentials with restrictive daily quota limits (10,000 units/day).
- **Decision**: Use `youtube-transcript-api` for direct subtitle extraction and YouTube's public oEmbed API (`https://www.youtube.com/oembed`) for metadata. Keep YouTube Data API as an optional enhancement.
- **Consequences**: Zero friction during onboarding and local development; operates reliably without API keys for public educational content.

---

## ADR 004: Frontend State Architecture (Zustand + TanStack Query)
- **Status**: Accepted
- **Context**: The frontend needs lightweight global UI state (active course, active video, background synthesis job) alongside robust server caching and background polling for long-running workflows.
- **Decision**: Combine **Zustand** for client state with **TanStack React Query** for server data synchronization and polling hooks (`useJobPolling`).
- **Consequences**: Clean separation of concerns, zero boilerplate compared to Redux, and minimal network overhead.
