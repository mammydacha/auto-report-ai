import requests
import json
from datetime import datetime
import os

# ================================
# 1. ニュース取得（Google News RSS）
# ================================
def fetch_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}"
    r = requests.get(url)
    text = r.text

    items = []
    for line in text.split("<item>")[1:]:
        title = line.split("<title>")[1].split("</title>")[0]
        pub = line.split("<pubDate>")[1].split("</pubDate>")[0]
        items.append({"title": title, "date": pub})
    return items[:10]


# ================================
# 2. 株価取得（Yahoo Finance）
# ================================
def fetch_price(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=7d"
    r = requests.get(url)

    # ★ Yahoo が空レスポンスを返した場合の対策
    if r.status_code != 200 or not r.text.strip():
        return [{"date": "N/A", "close": None}]

    try:
        data = r.json()
    except:
        return [{"date": "N/A", "close": None}]

    try:
        result = data["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        timestamps = result["timestamp"]
    except:
        return [{"date": "N/A", "close": None}]

    prices = []
    for t, c in zip(timestamps, closes):
        day = datetime.fromtimestamp(t).strftime("%Y-%m-%d")
        prices.append({"date": day, "close": c})

    return prices


# ================================
# 3. トレンド取得（Bing Trends）
# ================================
def fetch_trend(keyword):
    url = f"https://api.bing.com/osjson.aspx?query={keyword}"
    r = requests.get(url).json()
    suggestions = r[1]
    return suggestions[:10]


# ================================
# 4. 経済指標（TradingEconomics）
# ================================
def fetch_macro():
    url = "https://api.tradingeconomics.com/markets/country/japan"
    r = requests.get(url).json()
    return r[:5]


# ================================
# 5. AI 要約（LLM API）
# ================================
def ai_summarize(data):
    prompt = f"""
以下のデータをもとに、日本語で投資家向けレポートを作成してください。

【ニュース】
{json.dumps(data["news"], ensure_ascii=False)}

【株価】
{json.dumps(data["price"], ensure_ascii=False)}

【トレンド】
{json.dumps(data["trend"], ensure_ascii=False)}

【経済指標】
{json.dumps(data["macro"], ensure_ascii=False)}

構成：
1. ニュース概要
2. 株価の動き
3. トレンド
4. 経済指標
5. 総合評価
"""

    # ★ あなたの LLM API キーを環境変数に入れておく必要あり
    api_key = os.getenv("LLM_API_KEY")

    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
    ).json()

    return res["choices"][0]["message"]["content"]


# ================================
# 6. メイン処理
# ================================
def main():
    keyword = "NVIDIA"

    data = {
        "news": fetch_news(keyword),
        "price": fetch_price("NVDA"),
        "trend": fetch_trend(keyword),
        "macro": fetch_macro()
    }

    report = ai_summarize(data)

    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("reports", exist_ok=True)

    with open(f"reports/{today}.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("レポート生成完了:", today)


if __name__ == "__main__":
    main()
