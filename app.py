import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import re

# ページ設定
st.set_page_config(page_title="PK-Insight Canvas", layout="wide")

# スライド作成関数
def create_pptx(strategy_text, images, client_name, product_name):
    prs = Presentation()
    
    # 1. 表紙スライド
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = f"{product_name} プロモーション戦略案"
    subtitle.text = f"クライアント: {client_name}\n作成: PK-Insight Canvas"

    # 戦略テキストを項目ごとに分割（1. 2. などの数字で分割）
    sections = re.split(r'\n(?=\d\.)', strategy_text)

    for section in sections:
        if not section.strip(): continue
        
        slide_layout = prs.slide_layouts[1] # タイトルとコンテンツのレイアウト
        slide = prs.slides.add_slide(slide_layout)
        
        # タイトルと本文の分離
        lines = section.strip().split('\n')
        header = lines[0]
        body = "\n".join(lines[1:])
        
        slide.shapes.title.text = header
        tf = slide.placeholders[1].text_frame
        tf.text = body
        tf.word_wrap = True

    # 3. ビジュアルスライド（画像がある場合）
    if images:
        for idx, img in enumerate(images):
            slide = prs.slides.add_slide(prs.slide_layouts[6]) # 空白レイアウト
            # タイトル追加
            txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(1))
            tf = txBox.text_frame
            tf.text = f"クリエイティブ案 {idx+1}"
            
            # 画像の挿入
            img_io = BytesIO()
            img.save(img_io, format='PNG')
            img_io.seek(0)
            slide.shapes.add_picture(img_io, Inches(1), Inches(1.5), width=Inches(8))

    # バイナリデータに変換
    ppt_io = BytesIO()
    prs.save(ppt_io)
    return ppt_io.getvalue()

# --- UI定義 ---
st.title("🚀 PK-Insight Canvas v0.2")
st.caption("Strategy to Slide | One-Click Executive Reporting")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    client_name = st.text_input("クライアント名", "大手自動車メーカー")
    product_name = st.text_input("対象商品", "新型EV SUV")
    target_user = st.text_area("ターゲット", "30代後半、都心在住層")
    feedback = st.text_area("追加要望", "先進的なXR体験を想起させるビジュアル。")
    generate_btn = st.button("Generate Everything")

if generate_btn:
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"{client_name}の{product_name}に関する上申戦略（1-8の項目）と、バナー案の画像生成を同時に行ってください。ターゲットは{target_user}、要望は{feedback}です。"

            with st.spinner("戦略構築およびスライド構成をデザイン中..."):
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
                    contents=prompt
                )

                strategy_text = ""
                images = []
                for part in response.candidates[0].content.parts:
                    if part.text: strategy_text += part.text
                    elif part.inline_data: images.append(Image.open(BytesIO(part.inline_data.data)))

                col_text, col_visual = st.columns(2)
                with col_text:
                    st.subheader("📊 Proposal Draft")
                    st.write(strategy_text)
                with col_visual:
                    st.subheader("🎨 Visual Draft")
                    for img in images: st.image(img)

                # --- PowerPoint生成セクション ---
                st.divider()
                st.subheader("📂 Export to Presentation")
                pptx_data = create_pptx(strategy_text, images, client_name, product_name)
                st.download_button(
                    label="📥 PowerPointをダウンロード (.pptx)",
                    data=pptx_data,
                    file_name=f"{product_name}_戦略案.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                st.success("スライドの準備が整いました。")

        except Exception as e:
            st.error(f"エラー: {e}")
