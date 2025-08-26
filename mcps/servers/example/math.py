from typing import Annotated
from fastmcp import Context
from pydantic import Field

async def multiply_tool(
    a: Annotated[int, Field(description="multiplier")],
    b: Annotated[int, Field(description="multiplier")],
    ctx: Context,
) -> str:
    '''
    Multiply two integers and return the result
    '''
    return a * b

async def add_tool(
    a: Annotated[int, Field(description="addend")],
    b: Annotated[int, Field(description="addend")],
    ctx: Context,
) -> str:
    '''
    Add two integers and returns the result
    '''
    return a + b

