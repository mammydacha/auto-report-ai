#!/usr/bin/env python3
import json
import requests
import os
from datetime import datetime

TIMEOUT = 10

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

def safe_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[WARN] GET failed: {url} -> {e}")
        return None

# -----------------------------
# 1. ニュース（NewsAPI）
# -----------------------------
def fetch_news():
    if not NEWS_API_KEY:
        return []
    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": "jp", "apiKey": NEWS_API_KEY, "pageSize": 20}
    res = safe_get(url, params)
    return res.get("articles", []) if res else []

# -----------------------------
# 2. 株価（Yahoo Finance）
# -----------------------------
def fetch_prices():
    tickers = [
        "^N225", "9984.T", "8306.T", "7203.T",
        "6758.T", "9432.T", "7974.T", "6861.T"
    ]
    prices = {}
    for t in tickers:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}"
        res = safe_get(url)
        prices[t] = res if res else {}
    return prices

# -----------------------------
# 3. SBI S株向けデータ（単元未満株の人気ランキング）
# -----------------------------
def fetch_sbi_s_stock():
    # SBI証券のランキングAPIは非公開のため、代替として
    # “S株で人気の銘柄リスト” を構造化して提供
    return {
        "popular": [
            "8306.T",  # 三菱UFJ
            "7203.T",  # トヨタ
            "9432.T",  # NTT
            "9984.T",  # ソフトバンクG
            "6758.T",  # ソニー
        ],
        "note": "S株は単元未満株のため、少額分散投資に向く"
    }

# -----------------------------
# 4. トレンド（Google Trends 代替）
# -----------------------------
def fetch_trend():
    return {
        "keywords": ["株価", "円安", "インフレ", "日経平均", "S株"],
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

# -----------------------------
# 5. 経済指標（TradingEconomics）
# -----------------------------
def fetch_macro():
    url = "https://api.tradingeconomics.com/japan/indicators"
    params = {"c": "guest:guest"}
    res = safe_get(url, params)
    return res if res else []

# -----------------------------
# 6. メイン処理
# -----------------------------
def main():
    data = {
        "news": fetch_news(),
        "price": fetch_prices(),
        "trend": fetch_trend(),
        "macro": fetch_macro(),
        "s_stock": fetch_sbi_s_stock(),
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("[OK] data.json generated")

if __name__ == "__main__":
    main()
