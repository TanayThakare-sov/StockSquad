"""Streamlit front-end:  streamlit run app.py"""
import pandas as pd
import streamlit as st

import config
from stockteam.agents.supervisor import AGENTS
from stockteam.graph import run_research
from stockteam.llm import ConfigError, LLMError, get_llm
from stockteam.logs import setup_logging

setup_logging()
st.set_page_config(page_title="AI Stock Research Team", page_icon="📈", layout="wide")

LABELS = {
    "data": "Data agent: fetching prices and financial statements",
    "analysis": "Analysis agent: calculating ratios in Python",
    "news": "News agent: reading recent headlines",
    "writer": "Writer agent: drafting the one-page note",
}
ICONS = {"pending": "⏳", "ok": "✅", "failed": "⚠️", "unavailable": "❌"}


def render_progress(state) -> str:
    lines = []
    for agent in AGENTS:
        status = state.get("status", {}).get(agent, "pending")
        icon = "🔄" if state.get("running_agent") == agent else ICONS.get(status, "⏳")
        suffix = " (unavailable)" if status == "unavailable" else ""
        lines.append(f"{icon} {LABELS[agent]}{suffix}")
    return "\n\n".join(lines)


st.title("📈 Multi-agent stock research team")
st.caption("Type an Indian large-cap company. A team of AI agents researches it and writes a one-page note.")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Gemini model", value=config.LLM_MODEL,
                          help="Change this to compare models. Cost and latency per run are shown below the note.")
    with st.expander("Supported companies"):
        sectors = {}
        for entry in config.UNIVERSE:
            sectors.setdefault(entry["sector"], []).append(entry["name"])
        for sector, names in sectors.items():
            st.markdown(f"**{sector}**: " + ", ".join(names))

query = st.text_input("Company name", placeholder="e.g. Tata Motors, Infosys, HDFC Bank")
clicked = st.button("Generate research note", type="primary")

if clicked:
    st.session_state.pop("result", None)
    if not query.strip():
        st.warning("Please type a company name first.")
    else:
        try:
            llm = get_llm(model=model.strip() or None)
        except ConfigError as exc:
            st.error(str(exc))
            st.stop()
        with st.status("Research team is working...", expanded=True) as box:
            progress = st.empty()
            progress.markdown(render_progress({}))
            try:
                result = run_research(query, llm=llm, on_progress=lambda s: progress.markdown(render_progress(s)))
                st.session_state["result"] = result
                box.update(label="Finished", state="error" if result.get("fatal_error") else "complete")
            except LLMError as exc:
                box.update(label="The language model had a problem", state="error")
                st.error(str(exc))
            except Exception as exc:  # noqa: BLE001
                box.update(label="Something went wrong", state="error")
                st.error(f"Unexpected error: {exc}")

result = st.session_state.get("result")
if result:
    if result.get("fatal_error"):
        st.error(result["fatal_error"])
    else:
        st.markdown(result["note"])
        words = len(result["note"].split())
        st.caption(f"{words} words")
        st.download_button("Download note (.md)", result["note"],
                           file_name=f"{result['target'].ticker}_research_note.md", mime="text/markdown")

    m = result["metrics"]
    with st.expander("Run details (latency, tokens, cost, errors)"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total latency", f"{m.total_seconds:.1f}s")
        c2.metric("Tokens in / out", f"{m.total_input_tokens} / {m.total_output_tokens}")
        c3.metric("Estimated cost", f"${m.total_cost_usd:.4f}")
        c4.metric("Tool errors", len(m.tool_errors))
        if m.agents:
            st.markdown("**Time per agent**")
            st.dataframe(pd.DataFrame([a.model_dump() for a in m.agents]), hide_index=True, use_container_width=True)
        if m.tools:
            st.markdown("**Tool calls**")
            st.dataframe(pd.DataFrame([t.model_dump() for t in m.tools]), hide_index=True, use_container_width=True)
        if result.get("errors"):
            st.markdown("**Agent errors**")
            for error in result["errors"]:
                st.code(error)
