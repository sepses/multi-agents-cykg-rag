
# Multi-Agent RAG with a Cybersecurity Knowledge Graph (Without Log)

A Multi-agent system designed to answer questions about cybersecurity and the MITRE ATT&CK framework. The system incorporates several search and reasoning techniques, such as vector search, Cypher query to Neo4j, and integration with MCP RDF agent for graph and RDF-based data exploration.
## Core Components

- Multi-Agent System (LangGraph): The primary application logic that orchestrates the entire workflow. It includes specialized agents for validating questions, querying databases, reflecting on results, and synthesizing final answers
- Neo4j Knowledge Graph: A graph database storing structured cybersecurity data (e.g., from the MITRE ATT&CK framework), which is queried using the Cypher language.
- MCP RDF Explorer: Model Context Protocol (MCP) server that provides a conversational interface for RDF-based Knowledge Graph (Turtle) exploration and analysis in local file mode or SPARQL endpoint mode. (https://github.com/emekaokoye/mcp-rdf-explorer)

## Setup and Installation

How to use

Make sure that you already have uv installed on your desktop, if not then here's the installation guide : https://docs.astral.sh/uv/getting-started/installation/ 

```bash
  git clone <this-project>
  cd <this-project>
  uv sync
```

After that, you can use the kernel of .venv to run these python notebook project. to run this : 
- setup MCP server with information on github [MCP RDF Explorer](https://github.com/emekaokoye/mcp-rdf-explorer)
- dont forget to start the databases first
- you can use docker to start 2 databases simultaneously
- but here using neo4j local and also neo4j cloud (aura).

```bash
  uv run -m src.run -- "Your question here"
```

Make sure again that the .env file is filled !!!
```bash
OPENAI_API_KEY=
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=
LANGCHAIN_ENDPOINT=
LANGCHAIN_PROJECT=
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=    
NEO4J_PASSWORD_ICS=
NEO4J_DATABASE=

NEO4J_AURA=
NEO4J_AURA_USERNAME=
NEO4J_AURA_PASSWORD=
NEO4J_AURA_DATABASE=
```
## Features

- **Multi-agent workflow**: Uses LangGraph to manage the workflow between agents (guardrails, vector search, cypher search, MCP RDF, reflection, and synthesizer).

- **Guardrails**: Ensures the questions asked are relevant to the cybersecurity domain.

- **Vector & Cypher Search**: Searches for answers from a vector and graph database (Neo4j) with automatic iteration and reflection if results are insufficient.

- **MCP RDF Agent**: Integrates RDF-based search to enrich the context of answers.

- **Synthesizer**: Combines results from multiple sources into a comprehensive final answer.

- **Logging & Configuration**: Supports structured logging and configuration via .env files.

