from typing import Annotated
from pydantic import Field

async def search_knowledgebase(
    query: Annotated[str, Field(description="user query")],
) -> str:
    """search knowledge base and return context related to query"""
    return ""
