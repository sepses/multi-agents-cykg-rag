# src/run.py
import argparse
from src.utils.logging_config import setup_logging
from src.graph.workflow import app

def main():
    """Fungsi utama untuk menjalankan agen."""
    # Atur logging
    setup_logging()
    
    # Atur parser untuk argumen command-line
    parser = argparse.ArgumentParser(description="Jalankan Multi-Agent dengan pertanyaan.")
    parser.add_argument("question", type=str, help="Pertanyaan yang akan diajukan ke agen.")
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
    final_result = app.invoke(initial_state, config=config)
    
    # Cetak jawaban akhir
    print("\n--- Final Answer ---")
    print(final_result.get('answer'))

if __name__ == "__main__":
    main()