# src/graph/workflow.py
import logging
from langgraph.graph import StateGraph, END
from src.graph.state import AgentState

# Import all chains dan agen func
from src.chains.guardrails import guardrails_chain
from src.chains.review import review_chain
from src.chains.synthesizer import synthesis_chain
from src.agents.vector_agent import query_vector_search
from src.agents.cypher_agent import query_cypher
from src.agents.reflection_agents import vector_reflection_chain, reflection_chain
from src.agents.mcp_rdf_agent import run_mcp_agent

logger = logging.getLogger(__name__)

# --- Node Definition: Guardrails ---
def guardrails_node(state: AgentState):
    """Decides if the question is relevant."""
    logger.info("--- Executing Node: [[Guardrails]] ---")
    question = state['question']
    result = guardrails_chain.invoke({"question": question})
    if result.decision == "irrelevant":
        logger.warning(f"[[Guardrails]]: Irrelevant question detected -> '{question}'")
        return {"is_relevant": False, "answer": "Sorry, I can only answer questions related to cybersecurity and MITRE ATT&CK."}
    else:
        logger.info("[[Guardrails]]: Question is relevant.")
        return {"is_relevant": True}

# --- Node Definition: MCP RDF Agent ---
async def mcp_rdf_agent_node(state: dict) -> dict:
    """An asynchronous node for LangGraph that runs the MCP agent."""
    logger.info("--- Executing Node: [[mcp_rdf_agent]] ---")
    question = state.get("question")
    
    try:
        mcp_context = await run_mcp_agent(question)
        logger.info(f"[[MCP RDF Agent]]: Search completed. Context found:\n{mcp_context}")
        return {"mcp_rdf_context": mcp_context}
    except Exception as e:
        logger.error(f"[[MCP RDF Agent]]: Gagal menjalankan node: {e}")
        return {"mcp_rdf_context": f"Error in MCP RDF Agent node: {e}"}

# --- Node Definition: Vector Agent ---
def vector_search_node(state: AgentState):
    """Calls the vector search tool and populates the state."""
    logger.info("--- Executing Node: [[vector_agent]] ---")
    question = state['question']
    try:
        vector_context = query_vector_search(question)
        logger.info("[[Vector Agent]] : Vector search completed successfully.")
        logger.info(f"[[Vector Agent]] : Vector search context found:\n{vector_context}")
        return {"vector_context": vector_context}
    except Exception as e:
        logger.error(f"[[Vector Agent]] : Vector search failed: {e}")
        return {"vector_context": f"Error during vector search: {e}"}

# --- Node Definition: Review Vector Answer ---
def review_vector_node(state: AgentState):
    """Reviews the context from the vector search."""
    logger.info("--- Executing Node: [[review_vector_answer]] ---")
    question = state['original_question']
    context = state['vector_context']
    
    if not context or "Error during vector search" in context:
        logger.warning("[[Review Vector]]: Context is empty or contains an error. Marking as insufficient.")
        return {"vector_answer_sufficient": False}

    review = review_chain.invoke({"question": question, "context": context})
    logger.info(f"[[Review Vector]]: Decision: {review.decision}. Reasoning: {review.reasoning}")
    
    return {"vector_answer_sufficient": review.decision == "sufficient"}

# --- Node Definition: Vector Reflection ---
def vector_reflection_node(state: AgentState):
    """Reflects on the failed vector search and rephrases the question."""
    logger.info("--- Executing Node: [[vector_reflection]] ---")
    original_question = state['original_question']
    insufficient_context = state['vector_context']
    
    rephrased_result = vector_reflection_chain.invoke({
        "original_question": original_question,
        "vector_context": insufficient_context
    })
    
    new_question = rephrased_result.rephrased_question
    iteration_count = state['vector_iteration_count'] + 1
    logger.info(f"[[Vector Reflection]]: Rephrasing question to: '{new_question}'. New attempt: {iteration_count}.")
    
    return {"question": new_question, "vector_iteration_count": iteration_count}

# --- Node Definition: Cypher Agent ---
def cypher_query_node(state: AgentState):
    """Calls the cypher search tool and populates the state."""
    logger.info(f"--- Executing Node: [[cypher_agent]] (Attempt: {state.get('iteration_count', 1)}) ---")
    question = state['question']
    try:
        cypher_result = query_cypher(question)
        context = cypher_result.get("context", [])
        generated_query = cypher_result.get("query", "")

        if not context:
            logger.warning(f"[[Cypher Agent]]: No results found for query: {generated_query}")
        else:
            logger.info(f"[[Cypher Agent]]: Found context. Query: {generated_query}")

        return {
            "cypher_query": generated_query,
            "cypher_context": context
        }
    except Exception as e:
        logger.error(f"[[Cypher Agent]] failed: {e}", exc_info=True)
        return {
            "error": f"Query Cypher failed: {e}",
            "cypher_context": [],
            "cypher_query": "Failed to generate Cypher query due to an error."
        }

# --- Node Definition: Review Cypher Answer ---
def review_cypher_node(state: AgentState):
    """Reviews the context from the cypher search."""
    logger.info("--- Executing Node: [[review_cypher_answer]] ---")
    question = state['original_question']
    context = str(state['cypher_context'])

    if not state.get('cypher_context'):
        logger.warning("[[Review Cypher]]: Context is empty. Marking as insufficient.")
        return {"cypher_answer_sufficient": False}
        
    review = review_chain.invoke({"question": question, "context": context})
    logger.info(f"[[Review Cypher]]: Decision: {review.decision}. Reasoning: {review.reasoning}")

    return {"cypher_answer_sufficient": review.decision == "sufficient"}

# --- Node Definition: Cypher Reflection ---
def cypher_reflection_node(state: AgentState):
    """Reflects on the failed cypher query and rephrases the question."""
    logger.info("--- Executing Node: [[cypher_reflection]] ---") 
    original_question = state['original_question']
    failed_query = state['cypher_query']
    
    rephrased_result = reflection_chain.invoke({
        "original_question": original_question,
        "cypher_query": failed_query
    })
    
    new_question = rephrased_result.rephrased_question
    iteration_count = state['cypher_iteration_count'] + 1
    logger.info(f"[[Cypher Reflection]]: Rephrasing question to: '{new_question}'. New attempt: {iteration_count}.")
    
    return {"question": new_question, "cypher_iteration_count": iteration_count}

# --- Node Definition: Synthesizer ---
def synthesize_node(state: AgentState):
    """Generates the final compiled answer for the user based on all gathered context."""
    logger.info("--- Executing Node: [[synthesizer]] ---")
    
    # Check if any context exists at all after all retries
    if not state.get('vector_context') and not state.get('cypher_context'):
        final_answer = "Sorry, after several attempts, I could not find any information related to your question from any of our data sources."
    else:
        logger.info("[[Synthesizer]]: Compiling final answer from available context.")
        final_answer = synthesis_chain.invoke({
            "question": state['original_question'],
            "mcp_rdf_context": str(state.get('mcp_rdf_context', 'No data was provided from this source.')),
            "cypher_context": str(state.get('cypher_context', 'No data was provided from this source.')),
            "vector_context": str(state.get('vector_context', 'No data was provided from this source.'))
        })
        
    return {"answer": final_answer}

# --- Perakitan Graph ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("guardrails", guardrails_node)
workflow.add_node("mcp_rdf_agent", mcp_rdf_agent_node)
workflow.add_node("vector_agent", vector_search_node)
workflow.add_node("review_vector_answer", review_vector_node)
workflow.add_node("vector_reflection", vector_reflection_node)
workflow.add_node("cypher_agent", cypher_query_node)
workflow.add_node("review_cypher_answer", review_cypher_node)
workflow.add_node("cypher_reflection", cypher_reflection_node)
workflow.add_node("synthesizer", synthesize_node)

# 1. Decision after Guardrails
def decide_relevance(state: AgentState):
    if state.get('is_relevant'):
        logger.info("[Decision] Question is relevant, proceeding to search.")
        return "mcp_rdf_agent"
    else:
        logger.info("[Decision] Question is irrelevant, ending execution.")
        return END


# 2. Decision after Vector Review
def decide_after_vector_review(state: AgentState):
    if state.get('vector_answer_sufficient'):
        logger.info("[Decision] Vector context is sufficient. Proceeding to Cypher agent.")
        return "cypher_agent"
    if state.get("vector_iteration_count", 0) < state.get("max_iterations", 3):
        logger.warning("[Decision] Vector context is insufficient. Proceeding to reflection.")
        return "vector_reflection"
    else:
        logger.error("[Decision] Max retries for Vector search reached. Proceeding to Cypher agent.")
        return "cypher_agent"
    

# 3. Decision after Cypher Review
def decide_after_cypher_review(state: AgentState):
    if state.get('cypher_answer_sufficient'):
        logger.info("[Decision] Cypher context is sufficient. Proceeding to synthesizer.")
        return "synthesizer"
    if state.get("cypher_iteration_count", 0) < state.get("max_iterations", 3):
        logger.warning("[Decision] Cypher context is insufficient. Proceeding to reflection.")
        return "cypher_reflection"
    else:
        logger.error("[Decision] Max retries for Cypher reached. Proceeding to synthesizer.")
        return "synthesizer"

# --- Define Edges ---
workflow.set_entry_point("guardrails")

# Add Edges to the graph
workflow.add_conditional_edges(
    "guardrails", 
    decide_relevance, 
    {
        "mcp_rdf_agent": "mcp_rdf_agent", 
        END: END
    }
)
workflow.add_edge(
    "mcp_rdf_agent",
    "vector_agent"
)

workflow.add_edge(
    "vector_agent",
    "review_vector_answer"
)

workflow.add_conditional_edges(
    "review_vector_answer", 
    decide_after_vector_review, 
    {
        "cypher_agent": "cypher_agent", 
        "vector_reflection": "vector_reflection"
    }
)

workflow.add_edge(
    "vector_reflection",
    "vector_agent"
)

workflow.add_edge(
    "cypher_agent",
    "review_cypher_answer"
)

workflow.add_conditional_edges(
    "review_cypher_answer",
    decide_after_cypher_review,
    {
        "synthesizer": "synthesizer",
        "cypher_reflection": "cypher_reflection"
    }
)

workflow.add_edge(
    "cypher_reflection", 
    "cypher_agent"
)

workflow.add_edge(
    "synthesizer", 
    END
)

# Compile graph
app = workflow.compile()