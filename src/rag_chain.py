import anthropic
import os
from dotenv import load_dotenv
from src.retrieval import retrieve

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a knowledgeable NHL hockey analyst assistant specializing in the New Jersey Devils, Carolina Hurricanes, and New York Islanders.

You answer questions using only the context provided to you. The context contains real current NHL data including player stats, standings, rosters, and recent news.

Guidelines:
- Answer directly and confidently based on the context
- If the context contains the information, use it precisely
- If the context does not contain enough information to answer, say so clearly
- Keep answers conversational but accurate
- When discussing stats, be specific with numbers
- Today's date is March 28, 2026
- The NHL Olympic break ended approximately February 25, 2026"""

def ask(query: str) -> str:
    retrieved_docs = retrieve(query, n_results=5)
    context = "\n\n---\n\n".join(retrieved_docs)
    user_message = f"""Context:
{context}

Question: {query}

Answer based on the context provided above."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return response.content[0].text