import streamlit as st
import anthropic
from PIL import Image
import base64
import io

# タイトル
st.title("AIカロリー計算アプリ")

# サイドバーでAPIキー入力
api_key = st.sidebar.text_input("Anthropic APIキー", type="password")

# APIキーがない場合の警告
if not api_key:
    st.warning("左のメニューからAPIキーを入力してください")
    st.stop()

# カメラ入力
camera_image = st.camera_input("カメラで撮影")

# ファイルアップロード
uploaded_file = st.file_uploader("写真を選択", type=["jpg", "png", "jpeg"])

# 画像を選択
image = None
if camera_image is not None:
    image = camera_image
elif uploaded_file is not None:
    image = uploaded_file

if image is not None:
    # 画像をPIL Imageに変換
    img = Image.open(image)
    
    # 画像を表示
    st.image(img, caption="選択された画像", use_container_width=True)
    
    # 画像をbase64にエンコード
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Anthropicクライアント作成
    client = anthropic.Anthropic(api_key=api_key)
    
    # プロンプト
    prompt = """
    この写真に写っている食事の内容を分析し、以下の4点を日本語で分かりやすく出力してください。
    ①推測される料理名と食材
    ②推定される合計カロリー
    ③大まかなPFCバランス（タンパク質・脂質・炭水化物）
    ④健康のためのワンポイントアドバイス
    """
    
    # メッセージ作成
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    
    # 結果を表示
    st.subheader("分析結果")
    st.write(message.content[0].text)