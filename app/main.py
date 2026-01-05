import gradio as gr
import pandas as pd

# ----------- SERVICES & UTILITIES -----------
from services.expense_manager import load_expenses, add_expense
from services.receipt_service import save_receipt
from services.document_ai_service import extract_text_from_receipt
from services.receipt_parser import parse_receipt_text
from utils.charts import monthly_expense_chart, category_expense_chart
from services.chatbot_service import generate_chat_response

# ----------- BASIC HANDLERS -----------

def check_status():
    return "PocketPilot AI is running successfully!"


# ----------- EXPENSES -----------

def get_expenses():
    df = load_expenses()
    if df is None or df.empty:
        return pd.DataFrame(
            columns=["id", "date", "type", "amount", "category", "merchant", "notes"]
        )
    return df


# ----------- DASHBOARD -----------

def load_dashboard():
    df = load_expenses()
    bar = monthly_expense_chart(df)
    pie = category_expense_chart(df)
    return bar, pie


# ----------- RECEIPT OCR & PARSING -----------

def handle_receipt_ocr(file):
    """
    Upload → OCR → parse structured fields
    """
    if file is None:
        return "", "", None, ""

    # Save uploaded file locally
    saved_path = save_receipt(file)

    text = extract_text_from_receipt(
        file_path=saved_path,
        project_id="YOUR_PROJECT_ID",
        location="YOUR_LOCATION",
        processor_id="YOUR_PROCESSOR_ID"
    )

    data = parse_receipt_text(text)

    return (
        data.get("merchant", ""),
        data.get("date", ""),
        data.get("amount", None),
        data.get("category", "Uncategorized")
    )


# ----------- SAVE RECEIPT AS EXPENSE -----------

def save_receipt_expense(merchant, date, amount, category):
    if not merchant or amount is None:
        return "❌ Merchant and amount are required."

    add_expense(
        expense_type="expense",
        amount=amount,
        category=category or "Uncategorized",
        merchant=merchant,
        notes="Added via receipt"
    )

    return "✅ Expense saved successfully!"

# -------- GEMINI CHAT --------

def handle_chat(query):
    if not query:
        return "Please ask a question."
    return generate_chat_response(query)


# ================= UI =================

with gr.Blocks(title="PocketPilot AI") as app:
    gr.Markdown("# 💰 PocketPilot AI")
    gr.Markdown("Your personal finance assistant")

    # ---------- HOME ----------
    with gr.Tab("Home"):
        status_box = gr.Textbox(label="App Status", interactive=False)
        check_button = gr.Button("Check Status")
        check_button.click(check_status, outputs=status_box)

    # ---------- EXPENSES ----------
    with gr.Tab("Expenses"):
        gr.Markdown("### 📊 Expense Records")

        expenses_table = gr.Dataframe(
            interactive=False,
            wrap=True
        )

        refresh_button = gr.Button("Load Expenses")
        refresh_button.click(get_expenses, outputs=expenses_table)

    # ---------- DASHBOARD ----------
    with gr.Tab("Dashboard"):
        gr.Markdown("## 📈 Spending Overview")

        monthly_chart = gr.Plot()
        category_chart = gr.Plot()

        load_button = gr.Button("Load Dashboard")
        load_button.click(
            fn=load_dashboard,
            outputs=[monthly_chart, category_chart]
        )

    # ---------- UPLOAD RECEIPT ----------
    with gr.Tab("Upload Receipt"):
        gr.Markdown("## 🧾 Upload, Extract & Save Receipt")

        receipt_file = gr.File(
            label="Upload Receipt",
            file_types=[".png", ".jpg", ".jpeg", ".pdf"]
        )

        merchant = gr.Textbox(label="Merchant")
        date = gr.Textbox(label="Date (YYYY-MM-DD)")
        amount = gr.Number(label="Amount")
        category = gr.Textbox(label="Category")

        extract_button = gr.Button("Extract Data")
        save_button = gr.Button("Save Expense")

        status = gr.Textbox(label="Status", interactive=False)

        extract_button.click(
            fn=handle_receipt_ocr,
            inputs=receipt_file,
            outputs=[merchant, date, amount, category]
        )

        save_button.click(
            fn=save_receipt_expense,
            inputs=[merchant, date, amount, category],
            outputs=status
        )

    # ---- GEMINI CHAT ----
    
    with gr.Tab("Chat with PocketPilot"):
        user_query = gr.Textbox(
            label="Ask PocketPilot",
            placeholder="e.g. Where did I spend the most?"
        )
        chat_response = gr.Textbox(lines=8, label="Response")

        gr.Button("Ask").click(
            handle_chat,
            inputs=user_query,
            outputs=chat_response
        )

# ----------- RUN APP -----------
app.launch()
