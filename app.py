import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定 (手機瀏覽器標籤名稱)
st.set_page_config(
    page_title="AV 系統 04-01", 
    page_icon="🕶️",
    layout="centered"
)

# 2. 注入 PWA 與手機優化標籤 (解決多個 App 命名與狀態列顏色)
pwa_meta = """
<head>
    <meta name="apple-mobile-web-app-title" content="AV系統">
    <meta name="application-name" content="AV系統">
    <meta name="theme-color" content="#000000">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
</head>
"""
st.markdown(pwa_meta, unsafe_allow_html=True)

# 3. macOS 26 深色磨砂視覺 (文字大小 130% 強化版)
macos_26_final_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #F5F5F7;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
    }

    /* 隱藏預設元件 */
    header, footer, .stDeployButton, [data-testid="stHeader"] { display: none !important; }

    .main-title {
        font-weight: 700;
        background: linear-gradient(180deg, #FFFFFF 0%, #8E8E93 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
        text-align: center;
        padding: 20px 0 10px 0;
    }

    /* macOS 磨砂卡片 */
    .macos-card {
        background: rgba(30, 30, 32, 0.75);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 0.5px solid rgba(255, 255, 255, 0.15);
        border-radius: 22px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
    }

    /* --- 關鍵優化：查詢結果文字放大 120%-130% --- */
    
    /* 數據指標 (廳別、位置) */
    [data-testid="stMetricValue"] {
        font-size: 36px !important; /* 放大約 130% */
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 18px !important; /* 放大約 125% */
        color: #8E8E93 !important;
        margin-bottom: 5px !important;
    }

    /* 表格文字 (接口清單、詳細明細) */
    .stDataFrame div, .stDataFrame td, .stDataFrame th {
        font-size: 18px !important; /* 從預設 14px 提升至 18px */
        line-height: 1.5 !important;
    }

    /* Expander 標題文字 */
    .streamlit-expanderHeader p {
        font-size: 20px !important;
        font-weight: 600 !important;
    }

    /* 搜尋框與按鈕在手機上的優化 */
    @media (max-width: 600px) {
        .stTextInput > div > div > input {
            height: 55px !important;
            font-size: 20px !important; /* 手機輸入文字加大 */
            border-radius: 14px !important;
        }
        .stButton > button {
            width: 55px !important;
            height: 55px !important;
            font-size: 22px !important;
            background-color: rgba(255, 255, 255, 0.15) !important;
        }
    }
</style>
"""
st.markdown(macos_26_final_css, unsafe_allow_html=True)

# 4. 初始化 Session State (用於快速清除)
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

def clear_search():
    st.session_state.search_query = ""

# 5. 資料讀取
@st.cache_data(show_spinner=False)
def load_data():
    try:
        all_files = os.listdir(".")
        xlsx_files = [f for f in all_files if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in xlsx_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), None)
        if not target_file and xlsx_files: target_file = xlsx_files[0]
        if not target_file: return None, "NO_FILE"

        df = pd.read_excel(target_file, engine='openpyxl')
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
        if '接頭數' in df.columns:
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0).astype(int)
        return df, target_file
    except Exception as e:
        return None, str(e)

df, status = load_data()

# 6. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區 (手機觸控強化版)
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    col_input, col_clear = st.columns([0.82, 0.18])
    with col_input:
        user_input = st.text_input("SEARCH", value=st.session_state.search_query, placeholder="輸入編號 (如 04-01)", label_visibility="collapsed").strip()
        st.session_state.search_query = user_input
    with col_clear:
        st.button("✕", on_click=clear_search)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.search_query:
        query = st.session_state.search_query.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            
            # 資訊卡片：顯示位置 (文字已放大)
            st.markdown('<div class="macos-card">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0A84FF; font-size:14px; font-weight:700; letter-spacing:1px; margin-bottom:10px;'>SYSTEM LOCATED</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:32px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='height:1px; background:rgba(255,255,255,0.1); margin:20px 0;'></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("廳別", str(info['廳別']).split('\n')[0])
            c2.metric("位置", str(info['迴路盒位置']).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)

            # 接口統計 (文字已放大)
            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='margin:0 0 15px 0; font-size:20px; color:#8E8E93;'>📦 接口清單</h3>", unsafe_allow_html=True)
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭', '型式', '數量']
                st.dataframe(
                    summary, 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={"數量": st.column_config.NumberColumn("數量", format="%d")}
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # 詳細明細
            with st.expander("🔍 完整目的地明細"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:14px; letter-spacing:1px;">READY TO SCAN</p>', unsafe_allow_html=True)
else:
    st.error(f"系統故障: {status}")

# 頁尾
st.markdown('<p style="text-align:center; font-size:12px; color:#3A3A3C; margin-top:50px; letter-spacing: 2px;">OS 26 TERMINAL // HIGH READABILITY</p>', unsafe_allow_html=True)
