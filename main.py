"""Run with python main.py OR streamlit run main.py."""
import subprocess
import sys
from pathlib import Path
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
import json

# Display labels are friendly; values match the existing nine-tool registry.
TOOL_CHOICES = {
    "All tools · full trip planning": None,
    "Weather": "get_weather",
    "Attractions": "search_attractions",
    "Travel time": "get_travel_time",
    "Budget": "calculate_budget",
    "Save itinerary": "save_itinerary",
    "Load itinerary": "load_itinerary",
    "Currency conversion": "get_currency_conversion",
    "Packing list": "get_packing_list",
    "Local tips": "get_local_tips",
}

EXAMPLES = {
    None: "Plan 2 days in Colombo starting tomorrow for one traveler with USD 70",
    "get_weather": "Weather in Colombo for tomorrow and the following day",
    "search_attractions": "Find museums and parks in Colombo",
    "get_travel_time": "Walking time from National Museum to Viharamahadevi Park in Colombo",
    "calculate_budget": "2 days, 1 traveler, meals USD 10/day, transport USD 5/day, total admissions USD 6, budget USD 70",
    "save_itinerary": "Save the complete plan above as my_trip.json",
    "load_itinerary": "Load my_trip.json",
    "get_currency_conversion": "Convert USD 100 to EUR",
    "get_packing_list": "Packing for walking and temples: 24–31°C, 80% chance of rain (assumed)",
    "get_local_tips": "Local food and travel tips for Colombo",
}


def render_trace(events):
    for event in events:
        with st.expander(f"Step {event['step']} · {event['name']}", expanded=False):
            st.caption("Arguments")
            st.json(event["arguments"])
            st.caption("Result")
            st.json(event["result"])


def app():
    from agent import MODEL, new_history, run_agent
    from tools.itinerary import DATA_DIR, load_itinerary

    st.set_page_config(
        page_title="TravelStudio • AI Trip Planner",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # ====================== CUSTOM CSS ======================
    st.markdown("""
<style>
/* ---------- Global ---------- */
.stApp {
    background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 40%, #f0fdfa 100%);
    color: #0f172a;
}
.block-container {
    max-width: 1120px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #f8fafc !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: #1e293b;
    color: #f1f5f9 !important;
    border: 1px solid #475569;
    border-radius: 12px;
    font-weight: 500;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #334155;
    border-color: #38bdf8;
    color: white !important;
}
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background-color: #1e293b;
    border-color: #475569;
    color: #e2e8f0;
}

/* ---------- Metric Cards ---------- */
div[data-testid="stMetric"] {
    background: white;
    padding: 18px 20px;
    border-radius: 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    text-align: center;
}
div[data-testid="stMetric"] label {
    color: #64748b !important;
    font-size: 0.85rem !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
}

/* ---------- Chat Messages ---------- */
div[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 14px 18px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    margin-bottom: 12px;
}

/* ---------- Chat Input (Typed text white) ---------- */
div[data-testid="stChatInput"] textarea {
    color: white !important;
    background-color: #1e293b !important;
    border: 1px solid #475569 !important;
    border-radius: 4px !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8 !important;
}

/* ---------- Titles ---------- */
h1 {
    letter-spacing: -1.2px;
    font-weight: 800 !important;
    color: #0f172a !important;
}

/* Hide default Streamlit footer */
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

    # ====================== SESSION STATE ======================
    if "messages" not in st.session_state:
        st.session_state.messages = new_history()
        st.session_state.turns = []

    # ====================== SIDEBAR ======================
    with st.sidebar:
        st.markdown("## ✈️ TravelStudio")
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
        st.write("Colombo · Kandy · Paris · London · Tokyo · Bali")

        st.caption("Live weather & currency APIs need internet.\nNo real bookings or payments.")

        st.markdown("---")
        if st.button("＋ New conversation", use_container_width=True):
            st.session_state.messages = new_history()
            st.session_state.turns = []
            st.rerun()

        st.caption("Chat memory lasts for this browser session.\nSaved JSON files survive restarts.")

        st.markdown("---")
        st.markdown("### 📁 Saved itineraries")
        files = sorted(DATA_DIR.glob("*.json")) if DATA_DIR.exists() else []
        if files:
            selected = st.selectbox("Choose a file", [p.name for p in files], label_visibility="collapsed")
            loaded = load_itinerary(selected)
            if loaded["ok"]:
                st.download_button(
                    "⬇ Download JSON",
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
    st.markdown('<div class="input-card">', unsafe_allow_html=True)

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
        st.caption("✨ **All tools** — the agent will automatically choose the tools needed for your request.")
    else:
        st.caption(f"Selected: `{selected_tool}`. Enter the details, then send. Choose **All tools** for a complete trip.")

    st.markdown('</div>', unsafe_allow_html=True)

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
                    status.info(f"🧠 Planning · model step {event['step']} of 10")
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


if __name__ == "__main__":
    if get_script_run_ctx(suppress_warning=True) is None:
        print("Starting Travel Studio → http://localhost:8501", flush=True)
        try:
            exit_code = subprocess.call([
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(Path(__file__).resolve()),
                "--server.address=localhost",
                "--server.port=8501",
            ] + sys.argv[1:])
        except KeyboardInterrupt:
            print("\nTravel Studio stopped.")
            exit_code = 0
        raise SystemExit(exit_code)
    app()