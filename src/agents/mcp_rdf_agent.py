# src/agents/mcp_rdf_agent.py (File Baru)
import os
import logging
from mcp_use import MCPAgent, MCPClient
from src.config.settings import llm

logger = logging.getLogger(__name__)

# --- Konfigurasi dan Inisialisasi Agen MCP ---
# Path sekarang relatif terhadap root proyek
CONFIG_PATH = "browser_mcp.json"

# Inisialisasi client sekali saja untuk efisiensi
try:
    os.environ["MCP_USE_ANONYMIZED_TELEMETRY"] = "false"
    client = MCPClient.from_config_file(CONFIG_PATH)
except Exception as e:
    logger.error(f"Failed to load MCPClient from {CONFIG_PATH}: {e}")
    client = None

strict_system_prompt = """
You are a specialized cybersecurity assistant that answers questions ONLY by using the provided tools.
You MUST NOT answer any questions from your own knowledge. Your only source of information is the statements.ttl file and the result from the query.
Your thought process should be:
1.  Analyze the user's question.
2.  If after several attempts at correcting the query you still cannot find an answer, only then you must state that you could not find the information in the database.
3.  NEVER provide an answer from memory or without a successful tool call.
"""

mcp_agent = MCPAgent(
    llm=llm, 
    client=client, 
    max_steps=30, 
    verbose=True, 
    system_prompt=strict_system_prompt
) if client else None

# --- Helper Functions ---
async def run_mcp_agent(question: str) -> str:
    """function for executing MCP queries."""
    if not mcp_agent:
        return "Error: MCP Agent is not initialized correctly."
    try:
        # Menjalankan agen dengan query yang diberikan
        result = await mcp_agent.run(question)
        return result
    except Exception as e:
        logger.error(f"An error occurred while running the MCP Agent: {e}")
        return f"Error during MCP agent execution: {e}"