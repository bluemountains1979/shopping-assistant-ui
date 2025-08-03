import streamlit as st
import os
from openai import OpenAI
import json
import time

st.set_page_config(page_title="🛍️ AI Shopping Assistant", layout="centered")

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Available product types
PRODUCT_CATEGORIES = ["headphones", "laptop", "smartphone", "tablet", "wireless earbuds", "smartwatch"]
CATEGORY_IMAGES = {
    "headphones": "https://github.com/bluemountains1979/shopping-assistant-ui/blob/main/headphones.jpg?raw=true",
    "laptop": "https://github.com/bluemountains1979/shopping-assistant-ui/blob/main/laptop.jpg?raw=true",
    "smartphone": "https://github.com/bluemountains1979/shopping-assistant-ui/blob/main/smartphones.jpg?raw=true",
    "tablet": "https://github.com/bluemountains1979/shopping-assistant-ui/blob/main/tablet.jpg?raw=true",
    "wireless earbuds": "https://github.com/bluemountains1979/shopping-assistant-ui/blob/main/wirelessearbuds.png?raw=true",
    "smartwatch": "https://github.com/bluemountains1979/shopping-assistant-ui/blob/main/smartphones.jpg?raw=true"
}





st.markdown("""
    <style>
    .product-img {
        height: 80px;
        margin: 10px;
    }
    .buy-button {
        background-color: #25b679;
        color: white;
        border: none;
        padding: 0.4em 1em;
        border-radius: 5px;
        cursor: not-allowed;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Setup assistant and thread
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = "asst_JIHq7w6MutKtvdzuxG7aG734"  # Replace with your real assistant ID

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "history" not in st.session_state:
    st.session_state.history = []

# Header
st.title("🛍️ AI Shopping Assistant")
st.markdown("#### What are you looking for today?")

# Show product categories visually
cols = st.columns(len(PRODUCT_CATEGORIES))
for i, category in enumerate(PRODUCT_CATEGORIES):
    with cols[i]:
        st.image(CATEGORY_IMAGES[category], use_container_width=True)
        st.caption(category.title())

# Text input without button
user_input = st.text_input("Type a product to search:", placeholder="e.g., Show me wireless earbuds under 3000")

if user_input:
    with st.spinner("Finding products..."):
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if run_status.status in ["completed", "requires_action", "failed"]:
                break
            time.sleep(1)

        if run_status.status == "requires_action":
            tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            product = args.get("product_name", "").lower()
            price_limit = args.get("price_limit")

            fake_results = {
                "headphones": [
                    {"name": "Sony WH-1000XM5", "price": "₹29,990", "image": "https://m.media-amazon.com/images/I/61D8J8aJd5L._SL1500_.jpg"},
                    {"name": "JBL Tune 760NC", "price": "₹5,999", "image": "https://m.media-amazon.com/images/I/61kWB+uzR2L._SL1500_.jpg"},
                    {"name": "boAt Rockerz 450", "price": "₹1,499", "image": "https://m.media-amazon.com/images/I/61u1VALn6JL._SL1500_.jpg"}
                ],
                "laptop": [
                    {"name": "HP Pavilion 15", "price": "₹58,000", "image": "https://m.media-amazon.com/images/I/71--IQUHVwL._SL1500_.jpg"},
                    {"name": "MacBook Air M2", "price": "₹99,900", "image": "https://m.media-amazon.com/images/I/71jG+e7roXL._SL1500_.jpg"}
                ],
                "smartphone": [
                    {"name": "iPhone 14", "price": "₹74,900", "image": "https://m.media-amazon.com/images/I/61bK6PMOC3L._SL1500_.jpg"},
                    {"name": "Samsung Galaxy S23", "price": "₹69,999", "image": "https://m.media-amazon.com/images/I/61RZDb2mQxL._SL1500_.jpg"},
                    {"name": "Redmi Note 12", "price": "₹16,499", "image": "https://m.media-amazon.com/images/I/71bFZ3QW9BL._SL1500_.jpg"}
                ],
                "tablet": [
                    {"name": "iPad 10th Gen", "price": "₹39,900", "image": "https://m.media-amazon.com/images/I/61uA2UVnYWL._SL1500_.jpg"},
                    {"name": "Samsung Galaxy Tab S9", "price": "₹59,999", "image": "https://m.media-amazon.com/images/I/71I3U9p0YAL._SL1500_.jpg"}
                ],
                "wireless earbuds": [
                    {"name": "OnePlus Nord Buds 2", "price": "₹2,999", "image": "https://m.media-amazon.com/images/I/51c+4dB3ViL._SL1500_.jpg"},
                    {"name": "Realme Buds Air 5", "price": "₹3,499", "image": "https://m.media-amazon.com/images/I/61oMmWZl-hL._SL1500_.jpg"}
                ],
                "smartwatch": [
                    {"name": "Apple Watch SE", "price": "₹29,900", "image": "https://m.media-amazon.com/images/I/71E1AmTjG7L._SL1500_.jpg"},
                    {"name": "Noise ColorFit Ultra 3", "price": "₹3,999", "image": "https://m.media-amazon.com/images/I/61ZQUQKGGDL._SL1500_.jpg"}
                ]
            }

            items = fake_results.get(product, [])
            if price_limit:
                items = [item for item in items if int(item["price"].replace("₹", "").replace(",", "")) <= price_limit]

            result = json.dumps({"results": items or [{"name": "No results found", "price": "-"}]})

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=st.session_state.thread_id,
                run_id=run.id,
                tool_outputs=[{
                    "tool_call_id": tool_call.id,
                    "output": result
                }]
            )

            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                time.sleep(1)

        # Step 5: Show assistant reply and matching products
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.session_state.history.append({"query": user_input, "response": msg.content[0].text.value})
                st.markdown(f"**Assistant:** {msg.content[0].text.value}")
                break

        # Show product cards
        if items:
            st.markdown("---")
            st.subheader("🛒 Recommended Products")
            for item in items:
                with st.container():
                    st.image(item["image"], width=150)
                    st.markdown(f"**{item['name']}**")
                    st.markdown(f"💰 {item['price']}")
                    st.markdown('<button class="buy-button">Buy Now</button>', unsafe_allow_html=True)

# Show basic history
if st.session_state.history:
    st.markdown("---")
    st.subheader("🕘 Recent Searches")
    for entry in reversed(st.session_state.history[-5:]):
        st.markdown(f"**You:** {entry['query']}\n\n**Assistant:** {entry['response']}")
