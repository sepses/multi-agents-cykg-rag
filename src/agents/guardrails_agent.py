# src/chains/guardrails.py
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class GuardrailsOutput(BaseModel):
    decision: Literal["relevant", "irrelevant"] = Field(description="Checks if the question is relevant to cybersecurity topics within the knowledge graph, including log analysis, malware, and threat actors.")

guardrails_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """
        You are a gatekeeper for a Q&A system that queries a knowledge graph.
        Your task is to determine if a question is answerable by the graph.
        The graph contains two types of information:
            1.  **Log Data:** Detailed records of system events, including specific users, servers, hosts, processes, and session activities (e.g., login successes or failures).
            2.  **Cybersecurity Knowledge:** General concepts like malware, threat actors, and attack frameworks (e.g., MITRE ATT&CK).

        A question is **relevant** if it asks about specific entities found in logs (like 'user danette', 'server-db-01') OR general cybersecurity topics.
        A question is **irrelevant** if it is completely off-topic (e.g., 'what is the weather?', 'tell me a joke').

        Only allow relevant questions to pass.
        """
    ),
    ("human", "Question: {question}"),
])
guardrails_chain = guardrails_prompt | llm.with_structured_output(GuardrailsOutput)