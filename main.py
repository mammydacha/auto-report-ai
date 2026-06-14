import json
import datetime
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# ---------------------------------------------------------
#  トレンド記号ルール
# ---------------------------------------------------------
def trend_symbol(status, strength=0):
    if status == "up_transition":
        return "/▲"
    if status == "up_strong":
        return "▲" + "+" * strength
    if status == "up_weak":
        return "△"
    if status == "down_transition":
        return "\\▼"
    if status == "down_strong":
        return "▼" + "-" * strength
    if status == "down_weak":
        return "▽"
    if status == "spike":
        return "※"
    return ""


# ---------------------------------------------------------
#  トレンド図生成
# ---------------------------------------------------------
def generate_trend_diagram(trend_data):
    lines = []
    lines.append("トレンド推移（■ = 強さのイメージ）\n")

    for day in trend_data:
        lines.append(f"{day['date']}")
        for topic, info in day["topics"].items():
            level = "■" * info["level"]
            status = info.get("status", "")
            strength = info.get("strength", 0)
            symbol = trend_symbol(status, strength)
            if symbol:
                lines.append(f"  {topic:<10} {level} {symbol}")
            else:
                lines.append(f"  {topic:<10} {level}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------
#  プロンプト読み込み
# ---------------------------------------------------------
def load_prompt(mode):
    if mode == "100":
        path = "prompt/prompt_100.txt"
    elif mode == "150":
        path = "prompt/prompt_150.txt"
    elif mode == "design":
        path = "prompt/prompt_design.txt"
    elif mode == "sstock":
        path = "prompt/prompt_sstock.txt"
    elif mode == "all":
        path = "report_prompt.txt"
    else:
        raise ValueError("mode が不正です")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------
#  モデル読み込み（llama3:3b）
# ---------------------------------------------------------
def load_model():
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    return tokenizer, model


# ---------------------------------------------------------
#  推論実行
# ---------------------------------------------------------
def run_model(prompt, tokenizer, model):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    output = model.generate(
        **inputs,
        max_new_tokens=1500,
        temperature=0.7
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)


# ---------------------------------------------------------
#  メイン処理
# ---------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, required=True)
    args = parser.parse_args()

    # data.json 読み込み
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # トレンド図生成
    trend_diagram = generate_trend_diagram(data["trend"])

    # プロンプト読み込み
    base_prompt = load_prompt(args.mode)

    # 最終プロンプト
    final_prompt = base_prompt + "\n\n" + trend_diagram

    # モデル読み込み
    tokenizer, model = load_model()

    # 推論
    report = run_model(final_prompt, tokenizer, model)

    # 保存
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    out_path = f"reports/{today}_report.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"レポート生成完了: {out_path}")


if __name__ == "__main__":
    main()
