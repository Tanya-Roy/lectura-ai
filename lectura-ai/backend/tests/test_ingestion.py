import pytest
from app.services.youtube_service import (
    TopicBoundaryChunker,
    TranscriptExtractor,
    TranscriptNormalizer,
    TranscriptSegment,
    YouTubeURLParser,
)


class TestURLParser:
    def test_extract_video_id_standard(self):
        assert (
            YouTubeURLParser.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            == "dQw4w9WgXcQ"
        )

    def test_extract_video_id_short(self):
        assert (
            YouTubeURLParser.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
            == "dQw4w9WgXcQ"
        )

    def test_extract_video_id_embed(self):
        assert (
            YouTubeURLParser.extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ")
            == "dQw4w9WgXcQ"
        )

    def test_extract_video_id_shorts(self):
        assert (
            YouTubeURLParser.extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ")
            == "dQw4w9WgXcQ"
        )

    def test_extract_video_id_live(self):
        assert (
            YouTubeURLParser.extract_video_id("https://www.youtube.com/live/dQw4w9WgXcQ")
            == "dQw4w9WgXcQ"
        )

    def test_extract_playlist_id(self):
        url = "https://www.youtube.com/playlist?list=PLUl4u3cNGP63oMNUHXqIUcrkS2PivhN3k"
        assert (
            YouTubeURLParser.extract_playlist_id(url)
            == "PLUl4u3cNGP63oMNUHXqIUcrkS2PivhN3k"
        )

    def test_classify_video(self):
        assert (
            YouTubeURLParser.classify_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            == "video"
        )

    def test_classify_playlist(self):
        url = "https://www.youtube.com/playlist?list=PLUl4u3cNGP63oMNUHXqIUcrkS2PivhN3k"
        assert YouTubeURLParser.classify_url(url) == "playlist"

    def test_classify_video_in_playlist(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLUl4u3cNGP63oMNUHXqIUcrkS2PivhN3k"
        assert YouTubeURLParser.classify_url(url) == "video_in_playlist"

    def test_classify_invalid(self):
        assert YouTubeURLParser.classify_url("https://google.com") == "invalid"

    def test_invalid_url(self):
        assert not YouTubeURLParser.is_valid_youtube_url("not-a-url")
        assert not YouTubeURLParser.is_valid_youtube_url("https://vimeo.com/123456")


class TestTranscriptNormalizer:
    def test_clean_music_tag(self):
        segments = [TranscriptSegment(start=0.0, end=5.0, text="[Music] Hello world")]
        cleaned = TranscriptNormalizer.normalize(segments)
        assert len(cleaned) == 1
        assert cleaned[0].text == "Hello world"

    def test_clean_applause_and_html(self):
        segments = [
            TranscriptSegment(
                start=0.0, end=5.0, text="[Applause] &quot;Great lecture&quot; &amp; notes"
            )
        ]
        cleaned = TranscriptNormalizer.normalize(segments)
        assert cleaned[0].text == '"Great lecture" & notes'

    def test_merge_short_segments(self):
        segments = [
            TranscriptSegment(start=0.0, end=1.0, text="Hi"),
            TranscriptSegment(start=1.0, end=3.5, text="everyone welcome"),
        ]
        merged = TranscriptNormalizer.merge_short_segments(segments, min_duration=2.0)
        assert len(merged) == 1
        assert merged[0].text == "Hi everyone welcome"


class TestTopicBoundaryChunker:
    def test_basic_chunking(self):
        segments = [
            TranscriptSegment(
                start=float(i * 30),
                end=float((i + 1) * 30),
                text=f"This is segment number {i}.",
            )
            for i in range(10)
        ]
        chunker = TopicBoundaryChunker()
        chunks = chunker.chunk(segments, target_chunk_seconds=120)
        assert len(chunks) > 0
        assert all(c.start_time < c.end_time for c in chunks)

    def test_topic_transition_trigger(self):
        segments = [
            TranscriptSegment(start=0.0, end=35.0, text="First topic is completed here."),
            TranscriptSegment(start=35.0, end=70.0, text="Now let's move on to the second topic."),
            TranscriptSegment(start=70.0, end=100.0, text="Further elaboration on second topic."),
        ]
        chunker = TopicBoundaryChunker()
        chunks = chunker.chunk(segments, target_chunk_seconds=120)
        assert len(chunks) >= 2
        assert "First topic" in chunks[0].text
        assert "Now let's" in chunks[1].text

    def test_gap_boundary_trigger(self):
        segments = [
            TranscriptSegment(start=0.0, end=35.0, text="First topic is completed."),
            # Gap of 5 seconds (35 to 40)
            TranscriptSegment(start=40.0, end=75.0, text="Next concept starts after silence."),
        ]
        chunker = TopicBoundaryChunker()
        chunks = chunker.chunk(segments, target_chunk_seconds=120)
        assert len(chunks) == 2


class TestSRTParser:
    def test_parse_valid_srt(self):
        srt_content = """1
00:00:00,000 --> 00:00:05,000
Hello everyone welcome to the lecture.

2
00:00:05,500 --> 00:00:10,000
Today we will study operating systems."""
        extractor = TranscriptExtractor()
        segments = extractor.parse_srt(srt_content)
        assert len(segments) == 2
        assert segments[0].start == 0.0
        assert segments[0].end == 5.0
        assert segments[0].text == "Hello everyone welcome to the lecture."
        assert segments[1].start == 5.5
        assert segments[1].end == 10.0
        assert segments[1].text == "Today we will study operating systems."

    def test_strip_html_tags_srt(self):
        srt_content = """1
00:00:00,000 --> 00:00:05,000
<font color="#ffff00"><i>Important definition:</i></font> Operating System"""
        extractor = TranscriptExtractor()
        segments = extractor.parse_srt(srt_content)
        assert len(segments) == 1
        assert segments[0].text == "Important definition: Operating System"


class TestVTTParser:
    def test_parse_valid_vtt(self):
        vtt_content = """WEBVTT

00:00:00.000 --> 00:00:05.000
Hello everyone.

00:00:05.500 --> 00:00:10.000
Today's topic is memory management."""
        extractor = TranscriptExtractor()
        segments = extractor.parse_vtt(vtt_content)
        assert len(segments) == 2
        assert segments[0].start == 0.0
        assert segments[0].text == "Hello everyone."
        assert segments[1].start == 5.5
        assert segments[1].text == "Today's topic is memory management."


class TestTXTParser:
    def test_parse_txt(self):
        txt_content = """Paragraph one of lecture notes.

Paragraph two explaining algorithms."""
        extractor = TranscriptExtractor()
        segments = extractor.parse_txt(txt_content)
        assert len(segments) == 2
        assert segments[0].text == "Paragraph one of lecture notes."
        assert segments[1].text == "Paragraph two explaining algorithms."
