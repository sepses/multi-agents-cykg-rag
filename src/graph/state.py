# src/graph/state.py
from typing import List, Optional
from typing_extensions import TypedDict, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    question: str
    original_question: str
    is_relevant: bool
    mcp_rdf_context: Optional[str]
    vector_context: Optional[str]
    cypher_context: Optional[List[dict]]
    answer: Optional[str]
    cypher_query: Optional[str]
    error: Optional[str]
    messages: Annotated[list, add_messages] # add_messages
    
    # reflection state
    cypher_iteration_count: int
    vector_iteration_count: int
    vector_answer_sufficient: bool 
    cypher_answer_sufficient: bool 
    
    max_iterations: int