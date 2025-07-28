# src/chains/review.py 
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class ReviewOutput(BaseModel):
    """Decision model for reviewing the sufficiency of an answer."""
    decision: Literal["sufficient", "insufficient"] = Field(description="Is the provided context sufficient to answer the user's question?")
    reasoning: str = Field(description="A brief explanation for the decision.")


review_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in evaluating the quality of retrieved information. Your task is to determine if the provided 'Context' is sufficient to fully answer the 'Original Question'. Do not try to answer the question yourself, only evaluate the context."),
    ("human", "Original Question: {question}\n\nContext:\n{context}\n\nBased on the context, is it sufficient to answer the question?"),
])

review_chain = review_prompt | llm.with_structured_output(ReviewOutput)