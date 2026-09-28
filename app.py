import os
import asyncio
import streamlit as st
from pypdf import PdfReader
from PIL import Image
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_API_URL = os.getenv("HINDSIGHT_API_URL")

BANK_ID = "apex-ai"

groq = Groq(api_key=GROQ_API_KEY)

st.set_page_config(
    page_title="Apex AI",
    page_icon="🧠",
    layout="wide"
)
with open("style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

st.markdown('<div class="main-title">🧠 Apex AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Customer Support Agent • Powered by Hindsight Memory</div>', unsafe_allow_html=True)
st.markdown('<div class="memory-status">🧠 Long-term memory active</div>', unsafe_allow_html=True)
# --------------------------------------------------
# HINDSIGHT FUNCTIONS
# Each operation gets its own client and closes it.
# This prevents event-loop/session errors.
# --------------------------------------------------

async def save_to_hindsight(content):
    client = Hindsight(
        base_url=HINDSIGHT_API_URL,
        api_key=HINDSIGHT_API_KEY
    )

    try:
        return await client.aretain(
            bank_id=BANK_ID,
            content=content
        )
    finally:
        await client.aclose()


async def recall_from_hindsight(query):
    client = Hindsight(
        base_url=HINDSIGHT_API_URL,
        api_key=HINDSIGHT_API_KEY
    )

    try:
        return await client.arecall(
            bank_id=BANK_ID,
            query=query,
            max_tokens=1200
        )
    finally:
        await client.aclose()


def run_async(coroutine):
    return asyncio.run(coroutine)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "memories" not in st.session_state:
    st.session_state.memories = []


# --------------------------------------------------
# UI
# --------------------------------------------------

st.subheader("💬 Support Chat")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------
with st.popover("➕"):
    uploaded_files = st.file_uploader(
        "Attach files",
        type=["png", "jpg", "jpeg", "pdf", "txt", "docx"],
        accept_multiple_files=True
    )

user_message = st.chat_input(
    "Describe your customer-support problem..."
)


if user_message:
    attachment_text = ""

    if uploaded_files:

       for file in uploaded_files:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )
            attachment_text += f"\nPDF CONTENT:\n{text}"

        elif file.type == "text/plain":
            text = file.read().decode("utf-8", errors="ignore")
            attachment_text += f"\nTEXT FILE CONTENT:\n{text}"
            

        elif file.type in ["image/png", "image/jpeg"]:
            image = Image.open(file)
            attachment_text += f"\nImage attached: {file.name}"

    # --------------------------------------------------
    # SHOW USER MESSAGE
    # --------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })


    # --------------------------------------------------
    # 1. RECALL PREVIOUS MEMORY
    # --------------------------------------------------

    result = run_async(
        recall_from_hindsight(user_message)
    )

    recalled_memories = [
        item.text
        for item in result.results
    ]

    st.session_state.memories = recalled_memories


    # --------------------------------------------------
    # 2. PREPARE MEMORY FOR GROQ
    # --------------------------------------------------

    if recalled_memories:

        memory_text = "\n".join(
            f"- {item}"
            for item in recalled_memories
        )

    else:

        memory_text = "No previous relevant memory found."


    # --------------------------------------------------
    # 3. ASK GROQ
    # --------------------------------------------------

    prompt = f"""
You are Apex AI, a customer-support agent.

Your main special ability is persistent memory provided by Hindsight.

PREVIOUS MEMORY:
{memory_text}

CURRENT CUSTOMER MESSAGE:
{user_message}

{attachment_text}
s
Rules:

- Use previous memory when relevant.
- Never invent customer history.
- Do not make the customer repeat information already remembered.
- If this is a recurring problem, clearly acknowledge the previous context.
- Give practical support.
- Keep the answer concise.
- Do not produce a huge troubleshooting checklist.
- Ask only one follow-up question if necessary.
- Keep the response below 100 words.
"""

    response = groq.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    answer = response.choices[0].message.content


    # --------------------------------------------------
    # 4. SAVE THIS INTERACTION TO HINDSIGHT
    # --------------------------------------------------

    memory_content = f"""
Customer message:
{user_message}

Apex AI response:
{answer}
"""

    try:
        run_async(
            save_to_hindsight(memory_content)
    )
    except Exception:
        pass


    # --------------------------------------------------
    # 5. SHOW AI RESPONSE
    # --------------------------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()