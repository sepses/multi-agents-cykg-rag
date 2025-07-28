# src/config/settings.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.vectorstores.neo4j_vector import Neo4jVector

load_dotenv()

# --- Environment Variables ---
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
# Neo4j
neo4j_uri = os.environ.get("NEO4J_URI")
neo4j_username = os.environ.get("NEO4J_USERNAME")
neo4j_password = os.environ.get("NEO4J_PASSWORD_ICS")

# Langchain
os.environ["LANGCHAIN_TRACING_V2"] = os.environ.get("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY")

# --- LLM init ---
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

# Koneksi ke DB Lokal (MITRE ATT&CK)
graph = Neo4jGraph(
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password
)

vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(),
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password,
    search_type="hybrid",
    node_label="Resource",
    text_node_properties=["ns1__description"],
    embedding_node_property="embedding"
)

# --- Global Configs & Schema ---
DEFAULT_MAX_ITERATIONS = 3
NEO4J_SCHEMA_RAW = graph.schema
NEO4J_SCHEMA_ESCAPED_FOR_PROMPT = NEO4J_SCHEMA_RAW.replace("{", "{{").replace("}", "}}")