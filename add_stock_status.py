import pandas as pd
import openai
import os
from dotenv import load_dotenv
import time

# 環境変数の読み込み（.envのAPIキーを使う）
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# CSVファイル読み込み
df = pd.read_csv("data/products.csv")

# stock_status列がないときだけ追加する
if "stock_status" not in df.columns:
    stock_statuses = []

    for i, row in df.iterrows():
        prompt = f"""
以下の商品情報を参考にして、「在庫状況」を次の3つから1つだけ選んでください：「あり」「残りわずか」「なし」。
出力は日本語で、1語のみでお願いします。

商品名：「{row['name']}」
カテゴリ：「{row['category']}」
価格：「{row['price']}」
メーカー：「{row['maker']}」
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # GPT-4に変更しても可
                messages=[
                    {"role": "system", "content": "出力は必ず「あり」「残りわずか」「なし」のいずれかの1語だけにしてください。理由や補足説明は不要です。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

            stock_status = response.choices[0].message.content.strip()
            print(f"{i+1}件目: {stock_status}")
            stock_statuses.append(stock_status)

            time.sleep(1)  # API負荷対策のため1秒休止

        except Exception as e:
            print(f"❌ エラー（商品ID: {row['id']}）: {e}")
            stock_statuses.append("あり")  # デフォルトで"あり"にしておく

    df["stock_status"] = stock_statuses

    # 上書き保存
    df.to_csv("data/products.csv", index=False)
    print("✅ stock_status列の追加が完了しました。")

else:
    print("✅ すでに 'stock_status' 列が存在しています。")
