# 🧠 Apex AI

### Customer Support Agent with Long-Term Memory

Apex AI is an AI-powered customer support agent that remembers previous customer conversations and uses that knowledge to provide more personalized and efficient support.

The core of Apex AI is **Hindsight memory**, which allows the agent to learn from previous interactions instead of treating every conversation as a completely new conversation.

## 🚀 Key Features

- 🧠 Long-term customer memory using Hindsight
- 💬 AI-powered customer support
- 🔄 Recalls relevant previous conversations
- 📄 PDF and text-file attachments
- ⚡ Fast responses using Groq
- 🎨 Simple Streamlit interface
- 🔐 API credentials stored using environment variables

## 🧠 How Hindsight Is Used

Apex AI stores important information from customer interactions in a Hindsight memory bank.

When a customer sends a new message:

1. Apex AI searches Hindsight for relevant previous memories.
2. Retrieved memories are added to the AI's context.
3. The AI uses the previous context to answer the customer.
4. The new interaction is stored for future conversations.

This allows Apex AI to improve its responses across multiple interactions.

## 🏗️ Technology Stack

- Python
- Streamlit
- Hindsight
- Groq
- GPT-OSS-120B
- python-dotenv
- PyPDF
- Pillow

## 📁 Project Structure

```text
apex-ai/
├── app.py
├── style.css
├── README.md
├── .gitignore
└── .env