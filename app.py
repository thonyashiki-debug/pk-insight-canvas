import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# ページ設定：プロフェッショナルなワイドレイアウト
st.set_page_config(page_title="PK-Insight Canvas", layout="wide", initial_sidebar_state="expanded")

# カスタムCSSでUIを洗練
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .report-box { padding: 20px; border-radius: 10px; background-color: #1e2130; border-left: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 PK-Insight Canvas")
st.caption("Strategic Planning & Creative Visualizer | Powered by Playknot Logic")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    
    st.subheader("📝 Input Strategy")
    client_name = st.text_input("クライアント名", "大手自動車メーカー")
    product_name = st.text_input("対象商品", "新型EV SUV")
    target_user = st.text_area("ターゲット", "30代後半、都心在住、ITリテラシーが高くサステナビリティに関心がある層")
    feedback = st.text_area("追加のこだわり/トーン", "先進性と信頼性の両立。AR/XR体験を想起させる未来的なビジュアル。")
    
    generate_btn = st.button("Generate Strategy & Visuals")

# --- メインコンテンツ ---
if generate_btn:
    if not api_key:
        st.error("APIキーを入力してください。")
    else:
        try:
            # 最新の GenAI クライアント初期化
            client = genai.Client(api_key=api_key)
            
            # 1. 戦略テキストと画像生成の同時リクエスト
            # Gemini 2.0 Flash は 'Text' と 'Image' の両方を出力可能
            prompt = f"""
            あなたは株式会社playknotのシニア戦略PdM兼クリエイティブディレクターです。
            以下の情報を元に、上席への上申にそのまま使えるレベルの戦略案と、その核となるバナー広告のビジュアル案を生成してください。

            クライアント: {client_name}
            対象商品: {product_name}
            ターゲット: {target_user}
            こだわり: {feedback}

            【出力構成】
            1. 戦略セクション：現状の整理(As-is)、課題(To-be)、戦略コンセプト(Why this?)、施策案、技術的優位性、ROIシミュレーション。
            2. ビジュアルセクション：上記戦略を体現した、高品質なバナー広告のコンセプト画像を生成してください。

            ※戦略は論理的に、画像は{client_name}のブランドを毀損しない高級感あるタッチで生成してください。
            """

            with st.spinner("思考を言語化し、ビジュアルを構築中..."):
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                        temperature=0.7
                    )
                )

            # --- 結果の表示 ---
            col_text, col_visual = st.columns([1, 1], gap="large")

            # テキスト部分の抽出と表示
            strategy_text = ""
            generated_images = []

            for part in response.candidates[0].content.parts:
                if part.text:
                    strategy_text += part.text
                elif part.inline_data:
                    img = Image.open(BytesIO(part.inline_data.data))
                    generated_images.append(img)

            with col_text:
                st.subheader("📊 Generated Proposal Draft")
                st.markdown(f'<div class="report-box">{strategy_text}</div>', unsafe_allow_html=True)

            with col_visual:
                st.subheader("🎨 Creative Visual Draft")
                if generated_images:
                    for idx, img in enumerate(generated_images):
                        st.image(img, caption=f"バナー案 {idx+1} - {product_name}", use_container_width=True)
                        # ダウンロードボタン
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(label=f"画像をダウンロード", data=buf.getvalue(), file_name=f"draft_{idx}.png", mime="image/png")
                else:
                    st.warning("ビジュアルの生成に失敗しました。プロンプトを調整して再試行してください。")
                    # 画像が生成されなかった場合のテキストフィードバック（ある場合）を表示
                    if not strategy_text:
                        st.write(response.text)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.info("APIキーの権限や、Gemini 2.0 Flashの利用可否を確認してください。")

else:
    # 初期画面のガイド
    st.info("← サイドバーにAPIキーと戦略情報を入力し、生成ボタンを押してください。")
    
    # プロダクトの付加価値を説明
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Strategy", "Logic-Based")
    col_b.metric("Creative", "AI-Generated")
    col_c.metric("Goal", "Internal Approval")
