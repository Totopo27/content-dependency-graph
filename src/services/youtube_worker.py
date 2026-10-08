import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
except ImportError:
    print("Error: youtube-transcript-api is not installed. Run 'pip install youtube-transcript-api'.", file=sys.stderr)
    sys.exit(1)


def extract_video_id(url_or_id: str) -> str:
    """Extracts raw YouTube video ID from various URL formats or returns ID if already bare."""
    clean = url_or_id.strip()
    match = re.search(r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})", clean)
    if match:
        return match.group(1)
    if len(clean) == 11:
        return clean
    raise ValueError(f"Invalid YouTube video URL or ID: {url_or_id}")


class YouTubeTranscriptWorker:
    def __init__(self, target_languages: Optional[List[str]] = None):
        self.target_languages = target_languages or ["es", "en"]
        self.api = YouTubeTranscriptApi()

    def fetch_video_transcript(self, video_id: str) -> List[Dict[str, Any]]:
        """Fetches raw transcript segments from YouTube with fallback across languages."""
        try:
            transcript_list = self.api.list(video_id)
            
            # 1. Try finding manually created or generated in preferred languages
            transcript = None
            try:
                transcript = transcript_list.find_transcript(self.target_languages)
            except Exception:
                # 2. Fallback to any available language
                for t in transcript_list:
                    transcript = t
                    break

            if not transcript:
                raise NoTranscriptFound(video_id, self.target_languages, None)

            raw_snippets = transcript.fetch()
            # In youtube_transcript_api modern versions, items are FetchedTranscriptSnippet dataclasses
            clean_items = []
            for item in raw_snippets:
                text_val = item.text if hasattr(item, "text") else item.get("text", "")
                start_val = item.start if hasattr(item, "start") else item.get("start", 0)
                dur_val = item.duration if hasattr(item, "duration") else item.get("duration", 0)
                clean_items.append({
                    "text": text_val,
                    "start": float(start_val),
                    "duration": float(dur_val),
                })
            return clean_items
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"Warning: No transcript available for {video_id}: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Error fetching transcript for {video_id}: {e}", file=sys.stderr)
            return []

    def chunk_transcript(
        self, raw_chunks: List[Dict[str, Any]], chunk_duration_sec: int = 300
    ) -> List[Dict[str, Any]]:
        """Groups micro-caption lines into macro semantic chunks (e.g. 5-minute blocks)."""
        if not raw_chunks:
            return []

        macro_segments: List[Dict[str, Any]] = []
        current_text: List[str] = []
        current_start = raw_chunks[0].get("start", 0)
        current_end = current_start

        for item in raw_chunks:
            start = item.get("start", 0)
            dur = item.get("duration", 0)
            text = item.get("text", "").strip()
            current_end = start + dur

            current_text.append(text)

            if (current_end - current_start) >= chunk_duration_sec:
                macro_segments.append({
                    "start_time": int(current_start),
                    "end_time": int(current_end),
                    "transcript_text": " ".join(current_text),
                })
                current_text = []
                current_start = current_end

        # Append remainder
        if current_text:
            macro_segments.append({
                "start_time": int(current_start),
                "end_time": int(current_end),
                "transcript_text": " ".join(current_text),
            })

        return macro_segments

    def process_video_list(
        self,
        videos_input: List[Dict[str, str]],
        channel_id: str = "custom_channel",
        channel_title: str = "Curated Channel",
        chunk_duration_sec: int = 300,
        ollama_client: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Ingests multiple videos, fetches transcripts, segments them, and formats for the Go Core.

        If ollama_client is provided, runs automated concept extraction on each segment.
        """
        catalog_videos: List[Dict[str, Any]] = []

        for idx, v_info in enumerate(videos_input, start=1):
            raw_url = v_info.get("url") or v_info.get("id") or ""
            video_id = extract_video_id(raw_url)
            title = v_info.get("title", f"Video {idx}: {video_id}")
            published_at = v_info.get("published_at", datetime.now(timezone.utc).isoformat())

            print(f"[{idx}/{len(videos_input)}] Fetching transcript for: {title} ({video_id})...")
            raw_transcript = self.fetch_video_transcript(video_id)
            chunks = self.chunk_transcript(raw_transcript, chunk_duration_sec)

            segments: List[Dict[str, Any]] = []
            for seg_idx, chunk in enumerate(chunks, start=1):
                seg_id = f"seg_{video_id}_{seg_idx:02d}"
                taught: List[str] = []
                required: List[str] = []

                if ollama_client is not None and chunk["transcript_text"].strip():
                    print(f"   -> Extracting concepts with Ollama for {seg_id}...")
                    try:
                        extracted_seg = ollama_client.extract_from_transcript(
                            segment_id=seg_id,
                            transcript_text=chunk["transcript_text"],
                            start_time=chunk["start_time"],
                            end_time=chunk["end_time"],
                        )
                        taught = extracted_seg.concepts_taught
                        required = extracted_seg.concepts_required
                    except Exception as e:
                        print(f"   [!] Ollama extraction error for {seg_id}: {e}", file=sys.stderr)

                segments.append({
                    "segment_id": seg_id,
                    "video_id": video_id,
                    "start_time": chunk["start_time"],
                    "end_time": chunk["end_time"],
                    "transcript_text": chunk["transcript_text"],
                    "concepts_taught": taught,
                    "concepts_required": required,
                })

            duration = chunks[-1]["end_time"] if chunks else 0

            catalog_videos.append({
                "id": video_id,
                "title": title,
                "published_at": published_at,
                "duration": duration,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "segments": segments,
            })

        return {
            "channel_id": channel_id,
            "channel_title": channel_title,
            "videos": catalog_videos,
        }


def main():
    parser = argparse.ArgumentParser(description="YouTube Ingestion Worker for Content Dependency Graph")
    parser.add_argument("--urls", nargs="+", help="List of YouTube URLs or Video IDs", required=True)
    parser.add_argument("--channel-title", default="YouTube Curated Channel", help="Title of the channel/course")
    parser.add_argument("--output", default="tests/fixtures/live_channel_catalog.json", help="Path to output JSON")
    parser.add_argument("--chunk-size", type=int, default=300, help="Chunk length in seconds (default: 300s / 5 min)")
    parser.add_argument("--extract-ollama", action="store_true", help="Extract concepts automatically using local Ollama LLM")
    parser.add_argument("--ollama-model", default="richardyoung/qwen2.5-coder-14b-instruct-abliterated:latest", help="Ollama model to use")
    args = parser.parse_args()

    worker = YouTubeTranscriptWorker()
    video_inputs = [{"url": u} for u in args.urls]

    ollama_client = None
    if args.extract_ollama:
        try:
            from src.services.ollama_client import OllamaExtractionClient
            ollama_client = OllamaExtractionClient(model=args.ollama_model)
            if not ollama_client.is_available():
                print("[!] Warning: Ollama daemon is not responding at localhost:11434. Running without LLM extraction.", file=sys.stderr)
                ollama_client = None
            else:
                print(f"[*] Ollama connected. Using model: {args.ollama_model}")
        except Exception as e:
            print(f"[!] Could not initialize Ollama client: {e}", file=sys.stderr)

    catalog = worker.process_video_list(
        video_inputs,
        channel_title=args.channel_title,
        chunk_duration_sec=args.chunk_size,
        ollama_client=ollama_client,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Catalog successfully exported with {len(catalog['videos'])} videos to {output_path}")


if __name__ == "__main__":
    main()
