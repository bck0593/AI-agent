import streamlit as st
import sqlite3
import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI

# .envの読み込みとAPIキー設定
load_dotenv()
openai_api_key = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=openai_api_key)

# データベース読み込み関数
def load_data():
    conn = sqlite3.connect("db.sqlite3")  # create_db.py と同じファイル名に！
    query = "SELECT * FROM transactions"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# AIアドバイス生成関数
def generate_ai_advice(df, user_message=None):
    total_income = df[df["amount"] > 0]["amount"].sum()
    total_expense = -df[df["amount"] < 0]["amount"].sum()
    balance = total_income - total_expense

    expense_breakdown = df[df["amount"] < 0].groupby("type")["amount"].sum().apply(lambda x: f"{-int(x)}円")
    breakdown_str = "\n".join([f"- {k}: {v}" for k, v in expense_breakdown.items()])

    prompt = f"""
あなたは優秀なフィナンシャルプランナーです。
以下の入出金データをもとに、支出抑制や貯蓄の観点から、具体的な改善アドバイスをください（具体的な数字も交えながら）。
また、将来的な予測も含めながらアドバイスを実施ください。
ユーザーからの質問については、寄り添うような会話にしてほしい。

■収入合計: {int(total_income)}円
■支出合計: {int(total_expense)}円
■残高: {int(balance)}円

■支出の内訳:
{breakdown_str}
"""

    if user_message:
        prompt += f"\n\nユーザーからの質問: {user_message}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはプロのフィナンシャルプランナーです。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()

# --- Streamlit UI ---
st.set_page_config(page_title="AIフィナンシャルプランナー")

st.title("💰 AIフィナンシャルプランナー")
st.markdown("このアプリは、あなたの入出金データをもとに、AIフィナンシャルプランナーがアドバイスします。")

# チャット履歴の保持
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 入出金明細の表示
st.subheader("📊 入出金明細")
df = load_data()
st.dataframe(df)

# アドバイスボタン
st.subheader("💬 AIフィナンシャルプランナーからのアドバイス")
if st.button("アドバイスを取得"):
    try:
        ai_advice = generate_ai_advice(df)
        st.session_state["messages"].append({"role": "ai", "content": ai_advice})
    except Exception as e:
        st.error(f"AIアドバイスの生成に失敗しました: {e}")

# チャット履歴の表示（吹き出し形式）
st.subheader("📝 チャット履歴")

for message in st.session_state["messages"]:
    if message["role"] == "user":
        st.markdown(f"""
        <div style="background-color:#DCF8C6;padding:10px;border-radius:10px;margin-bottom:10px;text-align:right">
        <strong>あなた</strong><br>{message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color:#F1F0F0;padding:10px;border-radius:10px;margin-bottom:10px;text-align:left">
        <strong>AIフィナンシャルプランナー</strong><br>{message["content"]}
        </div>
        """, unsafe_allow_html=True)

# ユーザーの入力と送信フォーム
st.subheader("🗣️ AIに質問してみよう")

with st.form("user_input_form", clear_on_submit=True):
    user_message = st.text_input("あなたの質問を入力してください", placeholder="例：どこを節約すべき？")
    submitted = st.form_submit_button("送信")

    if submitted and user_message:
        st.session_state["messages"].append({"role": "user", "content": user_message})

        try:
            ai_response = generate_ai_advice(df, user_message=user_message)
            st.session_state["messages"].append({"role": "ai", "content": ai_response})
        except Exception as e:
            st.error(f"AIからの回答生成に失敗しました: {e}")

        # 🔁 ここで rerun することで、更新後のチャット履歴を即表示
        st.rerun()
