import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from pathlib import Path

async def main():
    # Get the parent directory path
    os.environ["MCP_USE_ANONYMIZED_TELEMETRY"] = "false"
    
    config_path = "browser_mcp.json"
    load_dotenv()

    # Create MCP Client from config
    client = MCPClient.from_config_file(config_path)

    llm = ChatOpenAI(model="gpt-4o")

    strict_system_prompt = """
    You are a specialized cybersecurity assistant that answers questions ONLY by using the provided tools.
    You MUST NOT answer any questions from your own knowledge. Your only source of information is the statements.ttl file and the result from the query.

    Your thought process should be:
    1.  Analyze the user's question.
    2.  If after several attempts at correcting the query you still cannot find an answer, only then you must state that you could not find the information in the database.
    3.  NEVER provide an answer from memory or without a successful tool call.
    """

    query_1 = "can you tell me all the techniques under Initial Access?"
    query_2 = "What are the techniques used for Privilege Escalation?"
    query_3 = "Show 5 available tactics in the database"
    
    # Buat agen
    agent = MCPAgent(llm=llm, client=client, max_steps=30, verbose=True, system_prompt=strict_system_prompt)

    # Jalankan kueri
    result = await agent.run(query_1)
    print(f"\nHasil: {result}")

if __name__ == "__main__":
    asyncio.run(main())
