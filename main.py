"""Command-line runner: handy for testing without the web app.

Usage:  python main.py "Tata Motors"
"""
import sys

from stockteam.graph import run_research
from stockteam.llm import ConfigError, LLMError, get_llm
from stockteam.logs import setup_logging


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")        # Windows consoles can choke on symbols like the rupee sign
    setup_logging()
    query = " ".join(sys.argv[1:]) or input("Company name: ")
    try:
        llm = get_llm()
    except ConfigError as exc:
        print(f"\nSetup problem: {exc}")
        return

    shown = set()

    def on_progress(state):
        running = state.get("running_agent")
        if running and running not in shown:
            shown.add(running)
            print(f"... {running} agent running")

    try:
        state = run_research(query, llm, on_progress)
    except LLMError as exc:
        print(f"\nThe language model had a problem: {exc}")
        return

    if state.get("fatal_error"):
        print(f"\n{state['fatal_error']}")
        return
    print("\n" + state["note"])

    m = state["metrics"]
    print("\n--- Run summary ---")
    print(f"Model: {m.model} | total latency: {m.total_seconds}s | tokens in/out: {m.total_input_tokens}/{m.total_output_tokens} "
          f"| est. cost: ${m.total_cost_usd:.4f}")
    for a in m.agents:
        print(f"  {a.agent:<9} attempt {a.attempt} {a.status:<11} {a.seconds}s")
    for t in m.tool_errors:
        print(f"  TOOL ERROR in {t.agent}: {t.tool} -> {t.error}")


if __name__ == "__main__":
    main()
