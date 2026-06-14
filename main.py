import os
import json
import requests
from datetime import datetime

# --- データ取得（あなたの元の処理をそのまま使う想定） ---
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# --- Ollama でレポート生成 ---
def ai_summarize(data):
    prompt = f"""
以下のデータを元に、日本語で投資家向けレポートを作成してください。

【ニュース】
{json.dumps(data.get("news", {}), ensure_ascii=False)}

【株価】
{json.dumps(data.get("price", {}), ensure_ascii=False)}

【トレンド】
{json.dumps(data.get("trend", {}), ensure_ascii=False)}

【経済指標】
{json.dumps(data.get("macro", {}), ensure_ascii=False)}

構成：
1. ニュース概要
2. 株価の動き
3. トレンド
4. 経済指標
5. 総合評価
"""

    payload = {
        "model": "llama3",
        "prompt": prompt
    }

    # Ollama API に送信
    r = requests.post("http://localhost:11434/api/generate", json=payload)
    res = r.json()

    return res.get("response", "レポート生成に失敗しました")

# --- レポート保存 ---
def save_report(text):
    today = datetime.now().strftime("%Y-%m-%d")
    path = f"reports/{today}.md"

    os.makedirs("reports", exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved report: {path}")

# --- メイン処理 ---
def main():
    data = load_data()
    report = ai_summarize(data)
    save_report(report)

if __name__ == "__main__":
    main()
