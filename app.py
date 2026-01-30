import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches
import re

# ページ設定
st.set_page_config(page_title="PK-Insight Canvas", layout="wide")

# スライド作成関数
def create_pptx(strategy_text, images, client_name, product_name):
    prs = Presentation()
    # 表紙
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = f"{product_name} 戦略提案書"
    slide.placeholders[1].text = f"Client: {client_name}\nPowered by PK-Insight Canvas"

    # 戦略項目スライド
    sections = re.split(r'\n(?=\d\.)', strategy_text)
    for section in sections:
        if not section.strip(): continue
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        lines = section.strip().split('\n')
        slide.shapes.title.text = lines[0]
        slide.placeholders[1].text = "\n".join(lines[1:])

    # ビジュアルスライド
    for idx, img in enumerate(images):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        slide.shapes.add_picture(img_io, Inches(1), Inches(1), width=Inches(8))

    ppt_io = BytesIO()
    prs.save(ppt_io)
    return ppt_io.getvalue()

# --- UI ---
st.title("🚀 PK-Insight Canvas v0.2 (Stable)")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    client_name = st.text_input("クライアント名", "大手自動車メーカー")
    product_name = st.text_input("対象商品", "新型EV")
    target_user = st.text_area("ターゲット", "30代、都心、先進層")
    feedback = st.text_area("追加要望", "先進的な未来感")
    generate_btn = st.button("Generate Strategy & Slide")

if generate_btn:
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # ステップ1: 戦略テキストの生成
            with st.spinner("戦略ロジックを構築中..."):
                text_prompt = f"{client_name}の{product_name}に関する上申用戦略(1-8の項目)を作成してください。ターゲットは{target_user}、要望は{feedback}です。"
                text_response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=text_prompt
                )
                strategy_text = text_response.text

            # ステップ2: クリエイティブ画像の生成（Imagenへの依頼）
            # ※API経由での画像生成指示は、モデルにテキストで「生成せよ」と伝える形式で安定させます
            with st.spinner("ビジュアルラフを描画中..."):
                # 画像生成は別途、画像生成機能を明示的に呼び出す必要があります。
                # 現状、Gemini 2.0 APIのテキスト生成から直接画像を「ファイル」として受け取るのが不安定なため
                # テキストベースで非常に詳細な「画像指示書」を作り、それを表示する形にします。
                image_desc_prompt = f"上記の戦略に最適なバナーの『具体的で詳細な画像指示書』を書いてください。"
                image_desc_response = client.models.generate_content(model="gemini-2.0-flash", contents=image_desc_prompt)
                image_desc = image_desc_response.text

            # レイアウト表示
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Strategic Logic")
                st.write(strategy_text)
            with col2:
                st.subheader("🎨 Creative Description")
                st.info("※現在APIの制限により、画像生成は詳細な『デザイン指示書』として出力されます。")
                st.write(image_desc)

            # PPTX生成（画像は今回は含まずテキスト主体で構成）
            st.divider()
            pptx_data = create_pptx(strategy_text, [], client_name, product_name)
            st.download_button("📥 PowerPointをダウンロード", data=pptx_data, file_name="strategy_draft.pptx")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
