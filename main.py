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
    r = requests.get(url)

    # ★ 空レスポンスやエラー対策
    if r.status_code != 200 or not r.text.strip():
        return [{"indicator": "N/A", "value": None}]

    try:
        data = r.json()
    except:
        return [{"indicator": "N/A", "value": None}]

    # データが空の場合
    if not isinstance(data, list) or len(data) == 0:
        return [{"indicator": "N/A", "value": None}]

    # 上位5件だけ返す
    return data[:5]


# ================================
# 5. AI 要約（LLM API）
# ================================
def ai_summarize(data):
    import requests
    import json

    prompt = f"以下のデータを元に日本語でレポートを作成してください:\n\n{json.dumps(data, ensure_ascii=False)}"

    payload = {
        "model": "llama3",
        "prompt": prompt
    }

    r = requests.post("http://localhost:11434/api/generate", json=payload)
    res = r.json()

    return res.get("response", "レポート生成に失敗しました")


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
