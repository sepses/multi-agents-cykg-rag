# src/chains/synthesizer.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from src.config.settings import llm

synthesis_prompt = ChatPromptTemplate.from_template("""You are an expert cybersecurity analyst. Your task is to synthesize information from multiple sources to create a comprehensive report that answers the user's question.

The final output MUST follow this exact structure, including the markdown for bolding and formatting. Do not add any text outside of this structure.

**Key Findings from Each Source:**
1. **Context from MCP/RDF Query (.ttl file):**
    [Summarize the key findings from the MCP/RDF context here. If the context is empty or contains an error message, state that "No relevant data was found from this source."]
    
2.  **Context from Cypher Query:**
    [Summarize the key findings from the Cypher context here. If the context is empty, null, or contains 'No data', state that "No data was provided from this source."]

3.  **Context from Vector Search:**
    [Summarize the key findings from the Vector context here. You can break this down into "Structured Data" and "Unstructured Data" if the context allows. If the context is empty, null, or contains 'No data', state that "No data was provided from this source."]

**Critical Analysis:**

[Provide a critical analysis of how the combined information answers the "Original Question". If one source is empty, analyze the sufficiency of the information from the other source. Explain whether the information is comprehensive or if there are any gaps.]

**Final Answer:**

[Based on your analysis, construct a final, cohesive answer that **directly addresses the user's Original Question**. Synthesize all findings into a clear, human-readable response.]

---
Here is the data to use for generating the report:

**Original Question:** {question}

**Context from MCP/RDF Query:**
{mcp_rdf_context}

**Context from Cypher Query:**
{cypher_context}

**Context from Vector Search:**
{vector_context}
""")

synthesis_chain = synthesis_prompt | llm | StrOutputParser()