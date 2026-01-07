import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定 (極簡化佈局)
st.set_page_config(
    page_title="AV 迴路盒系統",
    page_icon="🔍",
    layout="centered", # 保持居中以符合 Apple 審美，但會透過 CSS 移除頂部空白
    initial_sidebar_state="collapsed"
)

# 2. 定製 Apple 視覺規範 CSS (移除頂部與多餘空白)
apple_css = """
<style>
    /* 全域字體與背景 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #F5F5F7; /* Apple 官方背景色 */
    }

    /* 移除 Streamlit 預設的頂部空白與邊距 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 600px; /* 限制寬度讓手機與電腦看起來都像一條精緻的卡片流 */
    }

    /* 隱藏 Streamlit 頂部狀態列 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* 標題設計 */
    .main-title {
        font-weight: 700;
        color: #1D1D1F;
        font-size: 28px;
        letter-spacing: -0.5px;
        text-align: center;
        margin-bottom: 24px;
    }

    /* Apple 卡片設計：去掉邊框，使用極細陰影 */
    .apple-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }

    /* 數據指標樣式 */
    .stMetric {
        background-color: #FBFBFD;
        border-radius: 14px;
        padding: 10px !important;
        border: none !important;
    }

    /* iOS 藍按鈕樣式 */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        border: none;
        background-color: #007AFF;
        color: white;
        font-weight: 600;
        padding: 12px 0;
        transition: transform 0.1s;
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* 輸入框優化 */
    .stTextInput input {
        border-radius: 12px !important;
        background-color: #E8E8ED !important;
        border: none !important;
        padding: 14px !important;
        font-size: 16px !important;
    }
</style>
"""
st.markdown(apple_css, unsafe_allow_html=True)

# 3. 資料讀取邏輯 (保持自動識別)
@st.cache_data
def load_data():
    all_files = os.listdir(".")
    xlsx_files = [f for f in all_files if f.endswith('.xlsx')]
    
    target_file = None
    # 優先尋找包含關鍵字的檔案
    for f in xlsx_files:
        if any(k in f for k in ["Cable", "音視訊", "迴路盒"]):
            target_file = f
            break
    
    if not target_file and xlsx_files:
        target_file = xlsx_files[0]

    if not target_file:
        return None

    try:
        df = pd.read_excel(target_file, engine='openpyxl')
        if '迴路盒編號' not in df.columns: return None
        
        if '接頭數' in df.columns:
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0)
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(' ', '').str.replace('-', '')
        return df, target_file
    except:
        return None

data_tuple = load_data()

# 4. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if data_tuple:
    df, filename = data_tuple
    
    # 搜尋區
    with st.container():
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        user_input = st.text_input("搜尋編號", placeholder="例如: 04-01", label_visibility="collapsed")
        
        # 快捷按鈕 (手機橫向排列)
        cols = st.columns(4)
        samples = ["04-01", "04-02", "04-05", "04-08"]
        for i, sid in enumerate(samples):
            if cols[i].button(sid):
                user_input = sid
        st.markdown('</div>', unsafe_allow_html=True)

    if user_input:
        query = user_input.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV") and query:
            query = "AV" + query

        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            
            # 資訊卡片
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:20px;'>📍 {user_input.upper()}</h2>", unsafe_allow_html=True)
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("廳別", str(info['廳別']).split('\n')[0])
            with c2:
                loc = str(info['迴路盒位置']).replace('\n', ' ')
                st.metric("位置", loc)
            st.markdown('</div>', unsafe_allow_html=True)

            # 接口統計
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            st.markdown("<h3 style='margin:0 0 10px 0; font-size:18px;'>📦 接口清單</h3>", unsafe_allow_html=True)
            if '系統' in match.columns:
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭', '型式', '數量']
                summary['數量'] = summary['數量'].astype(int)
                st.table(summary)
            st.markdown('</div>', unsafe_allow_html=True)

            # 詳細明細
            with st.expander("🔍 完整線路目的地"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#8E8E93; font-size:14px;">輸入編號快速查詢位置與接口</p>', unsafe_allow_html=True)

else:
    st.error("⚠️ 找不到 Excel 檔案。")

# 頁尾
st.markdown(f'<p style="text-align:center; font-size:11px; color:#C7C7CC; margin-top:30px;">Version 1.7 (Pure Apple Style)</p>', unsafe_allow_html=True)
