# src/chains/guardrails.py
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class GuardrailsOutput(BaseModel):
    decision: Literal["relevant", "irrelevant"] = Field(description="Checks if the question is relevant to cybersecurity topics including log analysis, threat detection, vulnerability assesment and attack pattern reconstruction.")

guardrails_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """
        You are a gatekeeper for a Q&A system that queries a knowledge graph.
        Your task is to determine if a question is answerable by the graph.
        The graph contains two types of information:
            1.  **Log Data:** Detailed records of system events, including specific users, servers, hosts, processes, and session activities (e.g., login successes or failures).
            2.  **Cybersecurity Knowledge:** knowledge base for threat intelligence, including CVE, CWE, CAPEC and MITRE ATT&CK.

        A question is **relevant** if it asks about security log analysis such as finding suspicious activities in log or identify specific entities in logs such as users, hosts, ip-address, log events, OR general cybersecurity topics.
        A question is **irrelevant** if it is completely off-topic (e.g., 'what is the weather?', 'tell me a joke').

        Only allow relevant questions to pass.
        """
    ),
    ("human", "Question: {question}"),
])
guardrails_chain = guardrails_prompt | llm.with_structured_output(GuardrailsOutput)