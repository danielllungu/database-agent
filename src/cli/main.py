import json
from agent.logging import setup_logging
from agent.config import settings
from agent.utils.utility import now_iso_tz
from agent.graph import build_graph

def main():
    setup_logging()
    graph = build_graph()

    print("SQL Agent CLI. Type 'exit' to quit, 'reset' to clear context.\n")
    previous_turns = []

    while True:
        try:
            user_q = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not user_q:
            continue
        if user_q.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        if user_q.lower() == "reset":
            previous_turns = []
            print("(context cleared)")
            continue

        state = {
            "user_query": user_q,
            "now_iso": now_iso_tz(settings.app_timezone),
            "timezone": settings.app_timezone,
            "previous_turns": previous_turns,
        }
        final = graph.invoke(state)

        reply = final.get("reply_text") or "(no reply)"
        print(f"\nAssistant> {reply}\n")

        if final.get("validated_sql"):
            print("— Final SQL —")
            print(final["validated_sql"])
        if final.get("result_rows") is not None:
            print("— Preview —")
            print(json.dumps(final["result_rows"][:10], indent=2, default=str))
            print(f"(rowcount={final.get('rowcount', 0)})\n")

        previous_turns = final.get("previous_turns", previous_turns)

if __name__ == "__main__":
    main()
