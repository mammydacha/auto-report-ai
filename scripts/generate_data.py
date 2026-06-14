#!/usr/bin/env python3
# scripts/generate_data.py
import json
import requests
import os
from datetime import datetime

# 設定
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")  # GitHub Actions では secrets を環境変数に設定する
TIMEOUT = 10

def safe_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # 必要ならログ出力
        print(f"[WARN] request failed: {url} -> {e}")
        return None

def fetch_news():
    if not NEWS_API_KEY:
        print("[INFO] NEWS_API_KEY not set, returning empty news list")
        return []
    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": "jp", "apiKey": NEWS_API_KEY, "pageSize": 20}
    res = safe_get(url, params=params)
    if not res:
        return []
    return res.get("articles", [])

def fetch_prices(tickers):
    prices = {}
    for t in tickers:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}"
            res = safe_get(url)
            prices[t] = res if res is not None else {}
        except Exception as e:
            print(f"[WARN] price fetch error for {t}: {e}")
            prices[t] = {}
    return prices

def fetch_macro():
    # TradingEconomics の guest API を例示
    url = "https://api.tradingeconomics.com/japan/indicators"
    params = {"c": "guest:guest"}
    res = safe_get(url, params=params)
    return res if res is not None else {}

def main():
    data = {}
    # ニュース
    data["news"] = fetch_news()

    # 株価（例としていくつかのティッカー）
    tickers = ["^N225", "9984.T", "8306.T", "7203.T"]
    data["price"] = fetch_prices(tickers)

    # トレンド（ここは後で Google Trends 等に差し替え可能）
    data["trend"] = {"keywords": ["株価", "円安", "インフレ"], "generated_at": datetime.utcnow().isoformat() + "Z"}

    # マクロ指標
    data["macro"] = fetch_macro()

    # ファイル出力
    out_path = "data.json"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] wrote {out_path}")
    except Exception as e:
        print(f"[ERROR] failed to write {out_path}: {e}")

if __name__ == "__main__":
    main()
