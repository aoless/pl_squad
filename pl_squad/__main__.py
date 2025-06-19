from pl_squad.agents.football_agent import answer_football_question

if __name__ == "__main__":
    print("⚽ Premier‑League Q&A REPL (Ctrl‑C to exit)")
    while True:
        try:
            _q = input("PL_SQUAD › ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not _q.strip():
            continue
        print(answer_football_question(_q))
