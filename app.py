import streamlit as st
import google.generativeai as genai

# UIの基本設定
st.set_page_config(page_title="PK Insight Canvas", layout="wide")

st.title("🎨 Playknot Insight Canvas (Prototype v0.1)")
st.caption("戦略の壁打ちから上申資料の骨子作成まで")

# サイドバーで設定
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Keyを直接入力してください", type="password")
    st.info("APIキーは保存されません。ブラウザを閉じると消去されます。")

# メイン入力エリア
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 戦略のインプット")
    client_name = st.text_input("クライアント名", placeholder="例：日本国内大手車メーカー")
    product_name = st.text_input("対象車種/プロジェクト名", placeholder="例：新型EV SUV")
    target_user = st.text_area("ターゲットペルソナ", placeholder="例：都市部住み、30代、ITリテラシー高め、キャンプ好き")
    
    st.subheader("2. 微調整（AIへの個別指示）")
    feedback = st.text_area("追加のこだわりポイント", placeholder="例：ブランドの信頼性を保ちつつ、先進的なXR体験を軸にしたい")
    
    generate_btn = st.button("戦略と上申資料案を生成する", type="primary")

# 生成ロジック
if generate_btn:
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        genai.configure(api_key=api_key)
       model = genai.GenerativeModel('gemini-3-flash')
        
        with st.spinner("PKの知見を統合して戦略を練っています..."):
            prompt = f"""
            あなたはplayknot社の優秀な戦略PdMです。
            クライアント：{client_name} / 商品：{product_name} / ターゲット：{target_user}
            こだわり：{feedback}

            以下の8項目で上申資料のドラフトを作成してください。
            各項目は「プロ向けの論理的かつ鋭い」内容にしてください。
            1.現状の整理(As-is)
            2.課題と目的の定義(To-be)
            3.戦略コンセプト(Why this?)
            4.施策案（クリエイティブ・手法含む）
            5.技術的優位性（なぜPlayknotか）
            6.実行スケジュール
            7.予算
            8.ROIのシミュレーション
            """
            response = model.generate_content(prompt)
            
            with col2:
                st.subheader("3. 生成された上申資料ドラフト")
                st.markdown(response.text)
                st.success("この内容をベースにブラッシュアップしていきましょう！")
