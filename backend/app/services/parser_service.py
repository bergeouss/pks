from typing import Optional
import httpx
from bs4 import BeautifulSoup
import logging
import PyPDF2
import docx

logger = logging.getLogger(__name__)


class ParserService:
    """Parse various file and web formats"""

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
            elif file_path_lower.endswith('.txt'):
                return self._parse_txt(file_path)
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
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()


parser_service = ParserService()
