from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class LogAnalysisOutput(BaseModel):
    """
    Output model for the log analysis agent
    """
    log_summary: str = Field(description="A concise summary of the findings from the log data that answers the original question.")
    generated_question: str = Field(description="A new, insightful question for a cybersecurity knowledge base, based on the patterns or events found in the log data.")

log_analysis_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """You are a senior security analyst. You have received structured and unstructured data from system logs.
        Your tasks are:
        1.  Summarize the findings from the provided log context to directly answer the user's original question.
        2.  Based on these findings, formulate a single, insightful question to query a separate cybersecurity knowledge base. This question should aim to find potential attack techniques, tactics, or threat actors related to the observed log activity.
        3.  Don't use any external information, only use information from the context that you got
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