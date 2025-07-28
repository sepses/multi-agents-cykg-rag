# src/run.py
import argparse
import asyncio
from src.utils.logging_config import setup_logging
from src.graph.workflow import app

async def main():
    """The main function is to run the agent."""
    # Atur logging
    setup_logging()
    
    # Atur parser untuk argumen command-line
    parser = argparse.ArgumentParser(description="Run Multi-Agent with questions.")
    parser.add_argument("question", type=str, help="Questions to ask agents.")
    args = parser.parse_args()

    # Definisikan state awal
    initial_state = {
        "question": args.question,
        "original_question": args.question,
        "messages": [("human", args.question)],
        "cypher_iteration_count": 1,
        "vector_iteration_count": 1,
        "max_iterations": 3,
    }

    config = {"recursion_limit": 30}
    
    # Jalankan agen
    final_result = await app.ainvoke(initial_state, config=config)
    
    # Cetak jawaban akhir
    print("\n--- Final Answer ---")
    print(final_result.get('answer'))

if __name__ == "__main__":
    asyncio.run(main())