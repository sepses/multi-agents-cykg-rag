from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class LogAnalysisOutput(BaseModel):
    """
    Output model for the log analysis agent
    """
    decision: Literal["cskg_required", "cskg_not_required"] = Field(description="Checks if epth analysis with cybersecurity knowledge is required")
    log_summary: str = Field(description="A concise summary of the findings from the log data that answers the original question.")
    generated_question: str = Field(description="question for a cybersecurity knowledge based on original user's question and provided context (findings on log data).")

log_analysis_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """You are a security analyst expert. You have received structured and unstructured data from system logs.
        Your tasks are:
        1.  Summarize the findings from the provided log context to directly answer the user's original question.
        2.  Based on summarized findings, determine whether it requires depth analysis with MCP cybersecurity knowledge. 
        3.  return 'cskg_required' if it requires depth analysis with MCP cybersecurity knowledge. Return 'cskg_not_required' if it does not. 

        """
    ),
    (
        "human", 
        """
        Original Question: {original_question}

        Context from Vector Search:
        {log_vector_context}

        Context from Cypher Query:
        {log_cypher_context}

        Based on the provided context, perform your tasks.
        """
    ),
])
log_analysis_chain = log_analysis_prompt | llm.with_structured_output(LogAnalysisOutput)