# src/agents/cypher_agent.py
from langchain_core.prompts import PromptTemplate
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from src.config.settings import graph

# --- Cypher Generation Prompt Template ---
cypher_generation_template = """
You are an expert Neo4j Cypher translator who converts English to Cypher based on the Neo4j Schema provided, following the instructions below:
        1. Generate Cypher query compatible ONLY for Neo4j Version 5
        2. Do not use EXISTS, SIZE, HAVING keywords in the cypher. Use alias when using the WITH keyword
        3. Use only Nodes and relationships mentioned in the schema
        5. Never use relationships that are not mentioned in the given schema
        6. For all node labels and relationship types, add namespace prefix `ns0__` before the actual label or relationship type. E.g., `MATCH (n:ns0__NodeLabel)-[:ns0__RelationshipType]->(m:ns0__NodeLabel)`.
        7. Node properties with `created`, `description`, `identifier`, `modified`, `title` and `version`, add prefix `ns1__` instead. E.g., `MATCH (n:ns0__NodeLabel) RETURN n.ns1__title AS Title`.
        8. Always do a case-insensitive and fuzzy search for any properties related search. Eg: to search for a Tactic, use `toLower(Tactic.ns1__title) contains 'persistence'`.
        9. Always assign a meaningful name to every node and relationship in the MATCH clause
        10. Never return components not explicitly named in the MATCH clause.
        11. In the RETURN clause, include all named components (nodes, relationships, or properties) to ensure consistency and understanding.
        12. Always return all the nodes used in the MATCH clause to provide complete information to the user.
        13. When counting distinct items that come from an `OPTIONAL MATCH`, prefer to `collect()` them first and then use `size()` on the collected list to avoid warnings about null values. For example, instead of `count(DISTINCT optional_item)`, use `WITH main_node, collect(DISTINCT optional_item) AS items` and then in the `RETURN` clause use `size(items) AS itemCount`.
        14. To create unique pairs of nodes for comparison (e.g., for similarity calculations), use the `elementId()` function instead of the deprecated `id()` function. For example: `WHERE elementId(node1) < elementId(node2)`.
        15. use `toLower()` function to ensure case-insensitive comparisons for string properties.

Schema:
{schema}

Note: 
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than
for you to construct a Cypher statement. Do not include any text except
the generated Cypher statement. Make sure the direction of the relationship is
correct in your queries. Make sure you alias both entities and relationships
properly. Do not run any queries that would add to or delete from
the database. Make sure to alias all statements that follow as with
statement

In Cypher, you can alias nodes and relationships, but not entire pattern matches using AS directly after a MATCH clause.If you want to alias entire patterns or results of more complex expressions, that should be done in the RETURN clause, not the MATCH clause.
If you want to include any specific properties from these nodes in your results, you can add them to your RETURN statement.

Examples : 

1. Which techniques are commonly used by at least 3 different threat groups?
MATCH (g:ns0__Group)-[:ns0__usesTechnique]->(t:ns0__Technique)
WITH t, count(g) as groupCount
WHERE groupCount >= 3
MATCH (g:ns0__Group)-[:ns0__usesTechnique]->(t)
RETURN t.ns1__title as CommonTechnique, t.ns1__identifier as TechniqueID, 
       groupCount as NumberOfGroups,
       collect(g.ns1__title) as Groups
ORDER BY groupCount DESC

2. Find tactical areas where we have the most significant defensive gaps by identifying tactics that have many techniques but few mitigations, and rank them by coverage percentage!

MATCH (tactic:ns0__Tactic)<-[:ns0__accomplishesTactic]-(technique:ns0__Technique)
WITH tactic, collect(technique) as techniques, count(technique) as techniqueCount
UNWIND techniques as technique
OPTIONAL MATCH (mitigation:ns0__Mitigation)-[:ns0__preventsTechnique]->(technique)
WITH tactic, techniqueCount, technique, count(mitigation) > 0 as hasMitigation

WITH tactic, techniqueCount, 
     sum(CASE WHEN hasMitigation THEN 1 ELSE 0 END) as mitigatedTechniques,
     collect(CASE WHEN NOT hasMitigation THEN technique.ns1__title ELSE NULL END) as unmitigatedTechniques

WITH tactic, techniqueCount, mitigatedTechniques,
     [x IN unmitigatedTechniques WHERE x IS NOT NULL] as filteredUnmitigatedTechniques,
     (toFloat(mitigatedTechniques) / techniqueCount * 100) as coveragePercentage

RETURN tactic.ns1__title as Tactic,
       tactic.ns1__identifier as TacticID,
       techniqueCount as TotalTechniques,
       mitigatedTechniques as MitigatedTechniques,
       techniqueCount - mitigatedTechniques as UnmitigatedTechniqueCount,
       toInteger(coveragePercentage) as CoveragePercentage,
       CASE 
         WHEN coveragePercentage < 30 THEN "CRITICAL" 
         WHEN coveragePercentage < 60 THEN "HIGH" 
         WHEN coveragePercentage < 80 THEN "MEDIUM"
         ELSE "LOW"
       END as RiskLevel,
       filteredUnmitigatedTechniques as UnmitigatedTechniques
ORDER BY coveragePercentage ASC, techniqueCount DESC


The question is:
{question}

"""

cyper_generation_prompt = PromptTemplate(
    template=cypher_generation_template,
    input_variables=["schema","question"]
)

# --- Cypher QA Prompt Template ---
qa_template = """
You are an assistant that takes the results from a Neo4j Cypher query and forms a human-readable response. The query results section contains the results of a Cypher query that was generated based on a user's natural language question. The provided information is authoritative; you must never question it or use your internal knowledge to alter it. Make the answer sound like a response to the question.
Final answer should be easily readable and structured.
Query Results:
{context}

Question: {question}
If the provided information is empty, respond by stating that you don't know the answer. Empty information is indicated by: []
If the information is not empty, you must provide an answer using the results. If the question involves a time duration, assume the query results are in units of days unless specified otherwise.
Never state that you lack sufficient information if data is present in the query results. Always utilize the data provided.
Helpful Answer:
"""

qa_generation_prompt = PromptTemplate(
    template=qa_template,
    input_variables=["context", "question"]
)

# --- Cypher QA Chain and Query Function ---
cypher_qa_chain = GraphCypherQAChain.from_llm(
    top_k=10,
    graph=graph,
    verbose=True,
    validate_cypher=True,
    return_intermediate_steps=True,
    cypher_prompt=cyper_generation_prompt,
    qa_prompt=qa_generation_prompt,
    qa_llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
    cypher_llm=ChatOpenAI(model="gpt-4o", temperature=0),
    allow_dangerous_requests=True,
    use_function_response=True
)

def query_cypher(question: str) -> dict:
    """
    Generate and run a Cypher query against the graph database.
    Use this for complex questions requiring structured data, aggregations, or specific graph traversals
    Returns the query and the result context.
    """
    print(f"--- Executing Cypher Search for: {question} ---")
    response = cypher_qa_chain.invoke({"query": question})
    return {
        "query": response["intermediate_steps"][0]["query"],
        "context": response["intermediate_steps"][1]["context"]
    }