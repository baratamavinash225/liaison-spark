import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()
from agent import app as agent_app
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="Liaison-Spark", layout="wide")

st.title("🏗️ Liaison-Spark: The Autonomous Big Data Analyst")
st.markdown("Transform natural language into optimized, production-ready PySpark jobs.")

env_api_key = os.environ.get("OPENAI_API_KEY", "")
api_key = st.text_input("MeshAPI Key", value=env_api_key, type="password")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

query = st.text_area("What do you want to query?", "Show me the total quantity of products bought by customers in the UK, grouped by event_date.")

if st.button("Generate PySpark Code"):
    if not api_key:
        st.error("Please provide an MeshAPI Key.")
    else:
        with st.spinner("Analyzing schema and planning execution..."):
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "iteration": 0,
                "errors": ""
            }
            
            # Using invoke instead of stream for simplicity in UI state management
            state_output = agent_app.invoke(initial_state)
            
            st.info("🧠 Architect Plan created")
            with st.expander("View Plan"):
                st.write(state_output["plan"])
            
            if state_output.get("errors"):
                st.warning(f"🔍 QA caught issues (unresolved after 3 iterations): {state_output['errors']}")
            else:
                st.success("✅ QA Approved!")
            
            st.subheader("Optimized PySpark Code:")
            st.code(state_output["code"], language="python")
