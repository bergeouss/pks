from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)


class YouTubeService:
    """Fetch transcripts from YouTube videos"""

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    async def get_transcript(self, url: str) -> str:
        """Fetch transcript from YouTube video"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                raise ValueError(f"Could not extract video ID from URL: {url}")

            # Try to get transcript with multiple language fallbacks
            transcript_list = None
            languages_to_try = ['en', 'en-US', 'en-GB']  # Try English variants first

            for lang in languages_to_try:
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                    break
                except Exception:
                    continue

            # If no English transcript, try to get any available transcript
            if transcript_list is None:
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                except Exception:
                    pass

            if transcript_list is None:
                raise ValueError(f"No transcript available for video: {video_id}")

            transcript_text = "\n".join([entry['text'] for entry in transcript_list])

            logger.info(f"Fetched transcript for video {video_id}")
            return transcript_text

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching YouTube transcript: {str(e)}")
            # Provide more helpful error message
            if "no element found" in str(e).lower():
                raise ValueError(f"Could not fetch transcript for video {video_id}. The video may not have captions, or YouTube may be blocking automated requests. Try a different video or use direct text/file ingestion instead.")
            raise ValueError(f"Failed to fetch YouTube transcript: {str(e)}")


youtube_service = YouTubeService()
