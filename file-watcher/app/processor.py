import os
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Extensions the backend parser supports (mirrors ingestion.py SUPPORTED_EXTENSIONS)
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.png', '.jpg', '.jpeg', '.webp', '.gif'}


class FileProcessor:
    """Process new files and send to backend API as multipart uploads.

    Sends to /api/v1/upload (not /api/v1/ingest) so the backend parser handles
    binary formats (PDF/DOCX/images) correctly. The previous implementation
    base-decoded binaries as UTF-8 text, which corrupted everything but .txt.
    """

    async def process(self, file_path: str):
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Skipping unsupported file type: {filename} ({ext})")
            return

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                metadata = {
                    'filename': filename,
                    'source': 'file-watcher',
                }

                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        f"{settings.BACKEND_URL}/api/v1/upload",
                        files=files,
                        data={'metadata': __import__('json').dumps(metadata)},
                    )

                    if response.status_code == 200:
                        logger.info(f"Successfully processed: {filename}")
                        # Copy to processed then remove original (cross-device safe)
                        import shutil
                        processed_path = os.path.join(settings.PROCESSED_PATH, filename)
                        shutil.copy2(file_path, processed_path)
                        os.remove(file_path)
                    else:
                        logger.error(f"Failed to process {filename}: {response.text}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")