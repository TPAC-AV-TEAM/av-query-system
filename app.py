import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV 迴路盒系統 (macOS 26 Edition)",
    page_icon="🕶️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 定製 macOS 26 深色磨砂風格 CSS
macos_26_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* 全域背景：深空黑 */
    .stApp {
        background-color: #000000;
        color: #F5F5F7;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 650px;
    }

    /* 隱藏系統元件 */
    header, footer, .stDeployButton, [data-testid="stHeader"] {
        visibility: hidden;
        display: none;
    }

    /* 標題設計：金屬質感文字 */
    .main-title {
        font-weight: 700;
        background: linear-gradient(180deg, #FFFFFF 0%, #A1A1A6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
        letter-spacing: -0.8px;
        text-align: center;
        padding: 30px 0;
    }

    /* macOS 磨砂玻璃卡片 */
    .macos-card {
        background: rgba(28, 28, 30, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 22px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    /* 搜尋框優化：深色質感 */
    .stTextInput > div > div > input {
        border-radius: 14px !important;
        background-color: rgba(44, 44, 46, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border: 1px solid #0A84FF !important;
        box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.3) !important;
    }

    /* Metric 數據樣式修正 */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8E8E93 !important;
    }

    /* 表格深色適配 */
    .stTable {
        background-color: transparent !important;
        border-radius: 12px;
        overflow: hidden;
    }
    table {
        color: #F5F5F7 !important;
    }
    thead tr th {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #0A84FF !important;
    }

    /* Expander 調整 */
    .streamlit-expanderHeader {
        background-color: rgba(44, 44, 46, 0.5) !important;
        border-radius: 12px !important;
        border: none !important;
    }
</style>
"""
st.markdown(macos_26_css, unsafe_allow_html=True)

# 3. 資料讀取邏輯 (保持穩定)
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
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0)
        return df, target_file
    except Exception as e:
        return None, str(e)

df, status = load_data()

# 4. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    user_input = st.text_input(
        "SEARCH", 
        placeholder="輸入編號 (例如: 04-01)", 
        label_visibility="collapsed"
    ).strip()
    st.markdown('</div>', unsafe_allow_html=True)

    if user_input:
        query = user_input.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            
            # 資訊卡片
            st.markdown('<div class="macos-card">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0A84FF; font-weight:600; margin-bottom:4px;'>LOCATED</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:28px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='height:1px; background:rgba(255,255,255,0.1); margin:15px 0;'></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("廳別", str(info['廳別']).split('\n')[0])
            c2.metric("詳細位置", str(info['迴路盒位置']).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)

            # 接口統計
            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='margin:0 0 15px 0; font-size:18px; color:#A1A1A6;'>📦 接口清單</h3>", unsafe_allow_html=True)
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭', '型式', '數量']
                st.table(summary)
                st.markdown('</div>', unsafe_allow_html=True)

            # 展開明細
            with st.expander("🔍 完整路徑目的地"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號，請重新確認。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:14px;">ENTER ID TO SCAN SYSTEM</p>', unsafe_allow_html=True)

else:
    st.error(f"系統故障: {status}")

# 頁尾
st.markdown('<p style="text-align:center; font-size:11px; color:#48484A; margin-top:50px; letter-spacing: 1px;">SYSTEM OS 26 // ENCRYPTED ACCESS</p>', unsafe_allow_html=True)
