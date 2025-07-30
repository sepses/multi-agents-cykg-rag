from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class RouteQuery(BaseModel):
    """ 
    Routes the user's question to the appropriate tool
    """
    datasource: Literal["log_analysis", "cyber_knowledge"] = Field(
        description="Given the user question, route it to the 'log_analysis' tool if it is about specific log events, users, or system activities, or to 'cyber_knowledge' if it is a general cybersecurity question."
    )
    
router_prompt = ChatPromptTemplate.from_messages([
    (
        
        "system",
        """You are an expert at routing a user's question to the appropriate data source.

        Follow these rules:
        1.  **Prioritize Log Analysis**: If the question contains a specific entity name (like a username 'daryl', a server name, an IP address, or a specific process), ALWAYS route it to 'log_analysis'.
        2.  **Use Cyber Knowledge for General Queries**: If the question is about a general concept, tactic, or threat (e.g., "What is brute force?"), route it to 'cyber_knowledge'.
        
        """
    ),
    (
        "human", 
        "Question: {question}"
    ),
])

router_chain = router_prompt | llm.with_structured_output(RouteQuery)