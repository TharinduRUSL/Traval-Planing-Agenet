"""Member A: Streamlit presentation and browser-session memory."""
import json
from pathlib import Path
import streamlit as st
from frontend.components import TOOL_CHOICES, EXAMPLES, render_trace
from tools._catalog import supported_cities

def app():
    from agent import MODEL, new_history, run_agent
    from tools.itinerary import DATA_DIR, load_itinerary

    st.set_page_config(
        page_title="TravelStudio • AI Trip Planner",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    css_path = Path(__file__).with_name("styles.css")
    st.markdown("<style>" + css_path.read_text(encoding="utf-8") + "</style>", unsafe_allow_html=True)

    # ====================== SESSION STATE ======================
    if "messages" not in st.session_state:
        st.session_state.messages = new_history()
        st.session_state.turns = []

    # ====================== SIDEBAR ======================
    with st.sidebar:
        st.markdown("##  TravelStudio")
        st.caption("Your local AI planning companion")

        st.markdown("---")

        # ===== STYLED MODEL BADGE =====
        st.markdown("**Local model**")
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #0ea5e9, #6366f1);
                color: white;
                padding: 8px 16px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 0.95rem;
                display: inline-block;
                margin-top: 4px;
                margin-bottom: 6px;
                box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
            ">
                {MODEL}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("Maximum 10 model steps per request")

        st.markdown("---")
        st.markdown("**Curated destinations**")
        st.write(" · ".join(supported_cities()))

        st.caption("Live weather & currency APIs need internet.\nNo real bookings or payments.")

        st.markdown("---")
        if st.button("＋ New conversation", use_container_width=True):
            st.session_state.messages = new_history()
            st.session_state.turns = []
            st.rerun()

        st.caption("Chat memory lasts for this browser session.\nSaved JSON files survive restarts.")

        st.markdown("---")
        st.markdown("")
        files = sorted(DATA_DIR.glob("*.json")) if DATA_DIR.exists() else []
        if files:
            selected = st.selectbox("Choose a file", [p.name for p in files], label_visibility="collapsed")
            loaded = load_itinerary(selected)
            if loaded["ok"]:
                st.download_button(
                    "Download JSON",
                    json.dumps(loaded["data"]["itinerary"], indent=2, ensure_ascii=False),
                    file_name=selected,
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.error(loaded["error"])
        else:
            st.caption("Ask the assistant to save your final plan.")

    # ====================== MAIN CONTENT ======================
    st.markdown(
        "<p style='text-align:center; color:#64748b; font-size:0.85rem; letter-spacing:1px; margin-bottom:4px;'>"
        "PLAN THOUGHTFULLY  •  EXPLORE CONFIDENTLY</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h1 style='text-align:center; margin-bottom:6px;'>A better trip starts here.</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:#475569; font-size:1.1rem; margin-bottom:28px;'>"
        "Tell me where, when, your interests and your budget. Watch each tool work as we build your itinerary.</p>",
        unsafe_allow_html=True
    )

    # Metrics
    a, b, c = st.columns(3)
    a.metric("Planning tools", "9")
    b.metric("Model location", "Your laptop")
    c.metric("Bookings", "None")

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat History
    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.caption(turn.get("selection", "All tools · full trip planning"))
            st.write(turn["user"])
        with st.chat_message("assistant"):
            if turn["trace"]:
                render_trace(turn["trace"])
            st.markdown(turn["answer"])

    # ====================== INPUT AREA ======================
    # Native Streamlit layout keeps the selector and input together.

    selector_column, input_column = st.columns([1.1, 3])

    with selector_column:
        selection = st.selectbox(
            "Choose a tool",
            list(TOOL_CHOICES),
            key="tool_selection",
            label_visibility="collapsed"
        )
    selected_tool = TOOL_CHOICES[selection]

    with input_column:
        prompt = st.chat_input(EXAMPLES[selected_tool], key="travel_prompt")

    if selected_tool is None:
        st.caption(" **All tools** — the agent will automatically choose the tools needed for your request.")
    else:
        st.caption(f"Selected: `{selected_tool}`. Enter the details, then send. Choose **All tools** for a complete trip.")



    # ====================== HANDLE PROMPT ======================
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)

        trace = []
        with st.chat_message("assistant"):
            status = st.empty()
            active = None
            answer = ""

            for event in run_agent(st.session_state.messages, prompt, selected_tool=selected_tool):
                if event["type"] == "step":
                    status.info(f" Planning · model step {event['step']} of 10")
                elif event["type"] == "tool_start":
                    active = st.expander(f"Step {event['step']} · {event['name']}", expanded=True)
                    active.caption("Arguments")
                    active.json(event["arguments"])
                    active.caption("Running…")
                elif event["type"] == "tool_result":
                    trace.append(event)
                    if active is not None:
                        active.caption("Result")
                        active.json(event["result"])
                elif event["type"] == "final":
                    answer = event["content"]

            status.empty()
            st.markdown(answer)

        st.session_state.turns.append({
            "user": prompt,
            "answer": answer,
            "trace": trace,
            "selection": selection
        })
        st.rerun()
