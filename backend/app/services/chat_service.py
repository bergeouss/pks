from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service
from app.services.llm_provider_service import llm_provider_service
from app.core.config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """RAG-powered chat service"""

    async def chat(self, query: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate RAG-powered response to user query"""
        # Generate query embedding
        query_vector = await embedding_service.embed_text(query)
        logger.info(f"Generated query embedding")

        # Retrieve relevant chunks
        results = await qdrant_service.search(query_vector, limit=settings.TOP_K_RESULTS)
        logger.info(f"Retrieved {len(results)} relevant chunks")

        # Build context
        context = self._build_context(results)

        # Generate response using LLM
        llm = llm_provider_service.get_llm()
        prompt = self._build_prompt(query, context, conversation_history or [])

        try:
            response = await llm.ainvoke(prompt)
            logger.info(f"Generated LLM response")
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise

        # Handle different response formats
        if response is None:
            raise ValueError("LLM returned None response")

        # Try to get content, handling different response formats
        content = None
        if hasattr(response, 'content'):
            content = response.content
        elif isinstance(response, str):
            content = response
        else:
            # Try string representation as fallback
            content = str(response)

        if content is None:
            logger.error(f"LLM response format unexpected: {type(response)}, response: {response}")
            raise ValueError("Could not extract content from LLM response")

        return {
            "response": content,
            "sources": self._extract_sources(results),
            "context_used": len(results),
        }

    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context string from search results"""
        contexts = []
        for i, r in enumerate(results):
            contexts.append(
                f"[Source {i+1}] {r['text']}\n  URL: {r.get('url', 'N/A')}\n  Title: {r.get('title', 'N/A')}"
            )
        return "\n\n".join(contexts)

    def _build_prompt(self, query: str, context: str, history: List[Dict[str, str]]) -> str:
        """Build RAG prompt with context and conversation history"""
        prompt = f"""You are a helpful AI assistant. Answer the user's question based on the context provided below.

Context:
{context}

User Question: {query}

Provide a comprehensive answer. Cite your sources using [Source X] notation."""

        if history:
            prompt += "\n\nConversation History:\n"
            for msg in history[-3:]:  # Last 3 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt += f"{role}: {content}\n"

        return prompt

    def _extract_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract unique sources from results"""
        sources = {}
        for r in results:
            doc_id = r.get("document_id")
            if doc_id and doc_id not in sources:
                sources[doc_id] = {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "source": r.get("source", ""),
                }
        return list(sources.values())


chat_service = ChatService()
