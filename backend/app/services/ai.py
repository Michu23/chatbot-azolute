from typing import List, Dict, Optional
import openai
from app.core.config import settings
from app.services.cache import cache_get, cache_set


# Initialize OpenAI
openai.api_key = settings.OPENAI_API_KEY


async def generate_chat_response(
    message: str,
    bot_name: str,
    personality: str,
    system_prompt: Optional[str] = None,
    context: Optional[List[Dict[str, str]]] = None,
    temperature: float = 0.7,
    model: str = "gpt-3.5-turbo"
) -> str:
    """Generate AI chat response"""

    # Build system prompt
    if not system_prompt:
        personality_prompts = {
            "friendly": "You are a friendly and warm AI assistant. Be conversational and approachable.",
            "professional": "You are a professional AI assistant. Be formal, clear, and business-like.",
            "sales_focused": "You are a sales-oriented AI assistant. Be persuasive and focus on converting leads.",
            "custom": "You are a helpful AI assistant."
        }
        system_prompt = personality_prompts.get(personality, personality_prompts["custom"])

    system_prompt = f"{system_prompt}\n\nYour name is {bot_name}."

    # Build messages
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation context
    if context:
        messages.extend(context[-10:])  # Last 10 messages for context

    # Add current message
    messages.append({"role": "user", "content": message})

    try:
        # Generate response
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI Error: {e}")
        # Fallback response
        return f"Thank you for your message! I'm {bot_name}. I'm experiencing technical difficulties. Please try again shortly."


async def generate_embeddings(text: str) -> List[float]:
    """Generate embeddings for text using OpenAI"""
    try:
        response = await openai.Embedding.acreate(
            model="text-embedding-ada-002",
            input=text
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []


async def search_knowledge_base(
    query: str,
    bot_id: int,
    top_k: int = 3
) -> List[Dict[str, any]]:
    """Search knowledge base for relevant context"""
    from sqlalchemy import select, func
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import AsyncSessionLocal
    from app.models.knowledge import DocumentChunk

    # Generate query embedding
    query_embedding = await generate_embeddings(query)

    if not query_embedding:
        return []

    # Search vector database
    async with AsyncSessionLocal() as db:
        # Vector similarity search using pgvector
        result = await db.execute(
            select(
                DocumentChunk.content,
                DocumentChunk.metadata,
                DocumentChunk.embedding.cosine_distance(query_embedding).label('distance')
            )
            .join(DocumentChunk.document)
            .join(Document.source)
            .where(KnowledgeSource.bot_id == bot_id)
            .order_by('distance')
            .limit(top_k)
        )

        chunks = result.all()

        return [
            {
                "content": chunk.content,
                "metadata": chunk.metadata,
                "score": 1 - chunk.distance  # Convert distance to similarity score
            }
            for chunk in chunks
        ]


async def generate_rag_response(
    message: str,
    bot_id: int,
    bot_name: str,
    personality: str,
    system_prompt: Optional[str] = None,
    context: Optional[List[Dict[str, str]]] = None,
    temperature: float = 0.7,
    model: str = "gpt-3.5-turbo"
) -> tuple[str, List[Dict]]:
    """Generate response with RAG (Retrieval Augmented Generation)"""

    # Search knowledge base
    relevant_chunks = await search_knowledge_base(message, bot_id)

    # Build context from knowledge base
    if relevant_chunks:
        knowledge_context = "\n\n".join([
            f"Source {i+1}:\n{chunk['content']}"
            for i, chunk in enumerate(relevant_chunks)
        ])

        # Enhance system prompt with knowledge
        enhanced_prompt = f"""{system_prompt or ''}

Use the following information from the knowledge base to answer the user's question:

{knowledge_context}

If the information above is relevant to the user's question, use it in your response.
If not, respond based on your general knowledge."""
    else:
        enhanced_prompt = system_prompt

    # Generate response
    response = await generate_chat_response(
        message=message,
        bot_name=bot_name,
        personality=personality,
        system_prompt=enhanced_prompt,
        context=context,
        temperature=temperature,
        model=model
    )

    return response, relevant_chunks
