import openai
import PyPDF2
import gradio as gr
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("api")

# 📄 Load and store PDF content
pdf_text = ""
with open("POLICIES_AND_PROCEDURES.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pdf_text += text

# 💬 Real chat function with memory
def chat_with_pdf(message, history):
    context = pdf_text  # This is your PDF content
    query = message     # User’s question

    # Build your detailed prompt using your format
    prompt = f"""
You are a knowledgeable assistant that helps users understand **KYC (Know Your Customer) policies and procedures** based on official documentation.
Always answer using only the information from the provided context below.
If the context does not contain enough detail to answer confidently, respond with:
"I'm sorry, I don't have enough information in the document to answer that."

--- CONTEXT START ---
{context}
--- CONTEXT END ---

Question: {query}
Answer:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message["content"].strip()
    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    updated_history = history + [(message, reply)]
    return updated_history, updated_history, ""

# 🎨 Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 📄 Ask Questions About Your PDF")

    chatbot = gr.Chatbot()
    msg_input = gr.Textbox(placeholder="Ask a question about the PDF...", show_label=False)
    state = gr.State([])  # For keeping history
    clear = gr.Button("🗑️ Clear")

    # Handle submission: update chat, state, clear input
    msg_input.submit(chat_with_pdf, [msg_input, state], [chatbot, state, msg_input])

    # Clear button wipes everything
    clear.click(lambda: ([], [], ""), None, [chatbot, state, msg_input])

demo.launch()
