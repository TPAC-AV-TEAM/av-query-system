import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV System OS 26",
    page_icon="🕶️",
    layout="centered"
)

# 2. 進階 macOS 26 視覺規範 (包含行動端防換行修正)
macos_26_advanced_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #F5F5F7;
        font-family: "SF Pro Display", "-apple-system", "BlinkMacSystemFont", "Inter", sans-serif;
    }

    /* 行動端強制不換行邏輯 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }

    /* 調整欄位間距，避免手機上太擠 */
    [data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 650px;
    }

    header, footer, .stDeployButton, [data-testid="stHeader"] {
        display: none !important;
    }

    .main-title {
        font-weight: 700;
        background: linear-gradient(180deg, #FFFFFF 0%, #8E8E93 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 34px;
        letter-spacing: -1px;
        text-align: center;
        padding-bottom: 25px;
    }

    .macos-card {
        background: rgba(30, 30, 32, 0.65);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 0.5px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
    }

    /* 搜尋框樣式 */
    .stTextInput > div > div > input {
        border-radius: 14px !important;
        background-color: rgba(0, 0, 0, 0.4) !important;
        border: 0.5px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        padding: 12px 16px !important;
        font-size: 16px !important; /* 防止 iOS 自動放大 */
    }

    /* 清除按鈕樣式 - 固定大小避免擠壓 */
    .stButton > button {
        border-radius: 50% !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        padding: 0 !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: none !important;
        color: #8E8E93 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: #FFFFFF !important;
    }

    [data-testid="stDataFrame"] { border: none !important; }
    [data-testid="stMetricValue"] { font-size: 24px !important; letter-spacing: -0.5px; }
</style>
"""
st.markdown(macos_26_advanced_css, unsafe_allow_html=True)

# 3. 初始化 Session State
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

def clear_search():
    # 清空 session state 中的值
    st.session_state.search_query = ""
    # 同步更新 Widget 自己的內部狀態
    st.session_state["search_input_widget"] = ""

# 4. 資料讀取邏輯 (保持不變)
@st.cache_data(show_spinner=False)
def load_data():
    try:
        all_files = os.listdir(".")
        xlsx_files = [f for f in all_files if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in xlsx_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), None)
        if not target_file and xlsx_files: target_file = xlsx_files[0]
        if not target_file: return None, "NO_FILE"

        df = pd.read_excel(target_file, engine='openpyxl')
        df.columns = [c.strip() for c in df.columns]
        if '迴路盒編號' in df.columns:
            df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
            df['search_id'] = df['search_id'].apply(lambda x: x if x.startswith("AV") else "AV"+x)
        if '接頭數' in df.columns:
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0).astype(int)
        return df, target_file
    except Exception as e:
        return None, str(e)

df, status = load_data()

# 5. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒系統</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區 (使用強制不換行佈局)
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    # 稍微調整比例，給按鈕固定空間
    col_input, col_clear = st.columns([0.85, 0.15])
    
    with col_input:
        user_input = st.text_input(
            "SEARCH", 
            key="search_input_widget",
            value=st.session_state.search_query,
            placeholder="輸入編號 (例如: 04-01)", 
            label_visibility="collapsed"
        ).strip()
        st.session_state.search_query = user_input

    with col_clear:
        # 顯示清除按鈕
        st.button("✕", on_click=clear_search)
    st.markdown('</div>', unsafe_allow_html=True)

    # 搜尋結果顯示
    if st.session_state.search_query:
        query = st.session_state.search_query.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            st.markdown('<div class="macos-card">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0A84FF; font-size:12px; font-weight:700;'>SYSTEM SCAN OK</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:28px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='height:1px; background:rgba(255,255,255,0.08); margin:18px 0;'></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("廳別", str(info.get('廳別', 'N/A')).split('\n')[0])
            c2.metric("詳細位置", str(info.get('迴路盒位置', 'N/A')).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ... 其他結果顯示部分保持原樣 ...
        else:
            st.warning("查無此編號")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:13px; letter-spacing:1px; margin-top:10px;">READY TO SCAN</p>', unsafe_allow_html=True)
else:
    st.error(f"系統故障: {status}")

st.markdown('<p style="text-align:center; font-size:10px; color:#3A3A3C; margin-top:50px; letter-spacing: 2px;">OS 26 TERMINAL // NO ACCESS LOGS</p>', unsafe_allow_html=True)
