from typing import Optional
import httpx
from bs4 import BeautifulSoup
import logging
import PyPDF2
import docx
import google.generativeai as genai
from PIL import Image
from app.core.config import settings

logger = logging.getLogger(__name__)


class ParserService:
    """Parse various file and web formats"""

    def __init__(self):
        # Configure Gemini for image OCR
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    async def fetch_webpage(self, url: str) -> str:
        """Fetch and extract text from a webpage"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logger.error(f"Error fetching webpage {url}: {str(e)}")
            raise

    async def parse_file(self, file_path: str) -> str:
        """Parse text from various file formats"""
        file_path_lower = file_path.lower()

        try:
            if file_path_lower.endswith('.pdf'):
                return self._parse_pdf(file_path)
            elif file_path_lower.endswith('.docx'):
                return self._parse_docx(file_path)
            elif file_path_lower.endswith(('.txt', '.md')):
                return self._parse_txt(file_path)
            elif file_path_lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                return await self._parse_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            raise

    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()

    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()

    def _parse_txt(self, file_path: str) -> str:
        """Extract text from TXT or MD"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()

    async def _parse_image(self, file_path: str) -> str:
        """Extract text from image using Gemini Vision"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            image = Image.open(file_path)

            response = await model.generate_content_async([
                "Extract all text content from this image. If there's no text, describe what you see in detail.",
                image
            ])

            logger.info(f"Extracted text from image using Gemini Vision")
            return response.text
        except Exception as e:
            logger.error(f"Error parsing image {file_path}: {str(e)}")
            raise


parser_service = ParserService()
