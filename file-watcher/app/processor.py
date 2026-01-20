import os
import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class FileProcessor:
    """Process new files and send to backend API"""

    async def process(self, file_path: str):
        """Process a new file and send to backend"""
        try:
            filename = os.path.basename(file_path)

            # Read file and send to backend
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                metadata = {
                    'filename': filename,
                    'source': 'file-watcher'
                }

                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        f"{settings.BACKEND_URL}/api/v1/ingest",
                        json={
                            'text': f.read().decode('utf-8', errors='ignore'),
                            'metadata': metadata
                        }
                    )

                    if response.status_code == 200:
                        logger.info(f"Successfully processed: {filename}")
                        # Copy to processed directory instead of rename (fixes cross-device link issue)
                        processed_path = os.path.join(
                            settings.PROCESSED_PATH,
                            filename
                        )
                        import shutil
                        shutil.copy2(file_path, processed_path)
                        os.remove(file_path)
                    else:
                        logger.error(f"Failed to process {filename}: {response.text}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
