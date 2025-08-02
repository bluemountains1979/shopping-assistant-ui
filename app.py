import streamlit as st
import os
from openai import OpenAI
import json
import time

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Or use st.secrets if hosted

# Setup
if "assistant_id" not in st.session_state:
    # Use the assistant you created earlier
    st.session_state.assistant_id = "asst_JIHq7w6MutKtvdzuxG7aG734"

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

# Streamlit UI
st.title("🛒 AI Shopping Assistant")

user_input = st.text_input("What do you want to find?", "")

if st.button("Ask"):
    if user_input:
        with st.spinner("Thinking..."):

            # Step 1: Send user message
            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=user_input
            )

            # Step 2: Run assistant
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=st.session_state.assistant_id
            )

            # Step 3: Wait for status
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status in ["completed", "requires_action", "failed"]:
                    break
                time.sleep(1)

            # Step 4: Handle tool call (if any)
            if run_status.status == "requires_action":
                tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
                args = json.loads(tool_call.function.arguments)
                product = args["product_name"]

                # Fake search
                fake_results = {
                    "headphones": [
                        {"name": "Sony WH-1000XM5", "price": "₹29,990"},
                        {"name": "JBL Tune 760NC", "price": "₹5,999"},
                        {"name": "boAt Rockerz 450", "price": "₹1,499"}
                    ],
                    "laptop": [
                        {"name": "HP Pavilion 15", "price": "₹58,000"},
                        {"name": "MacBook Air M2", "price": "₹99,900"}
                    ],
                    "smartphone": [
                        {"name": "iPhone 14", "price": "₹74,900"},
                        {"name": "Samsung Galaxy S23", "price": "₹69,999"},
                        {"name": "Redmi Note 12", "price": "₹16,499"}
                    ],
                    "tablet": [
                        {"name": "iPad 10th Gen", "price": "₹39,900"},
                        {"name": "Samsung Galaxy Tab S9", "price": "₹59,999"}
                    ],
                    "wireless earbuds": [
                        {"name": "OnePlus Nord Buds 2", "price": "₹2,999"},
                        {"name": "Realme Buds Air 5", "price": "₹3,499"}
                    ],
                    "smartwatch": [
                        {"name": "Apple Watch SE", "price": "₹29,900"},
                        {"name": "Noise ColorFit Ultra 3", "price": "₹3,999"}
                    ]                                                               
                                                                                   
                }
                result = json.dumps({"results": fake_results.get(product, [{"name": "Not found", "price": "-"}])})

                # Submit tool output
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": result
                    }]
                )

                # Wait again
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )
                    if run_status.status == "completed":
                        break
                    time.sleep(1)

            # Step 5: Show assistant reply
            messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    st.markdown(f"**Assistant:** {msg.content[0].text.value}")
                    break
