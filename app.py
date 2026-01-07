import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV 迴路盒系統",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 定製 Apple 視覺規範 CSS (徹底移除頂部空白)
apple_css = """
<style>
    /* 全域字體與背景 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #F5F5F7; 
    }

    /* 徹底移除 Streamlit 所有預設空白 */
    .stApp {
        margin-top: -80px; /* 強制向上位移以抵銷預設間距 */
    }

    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 600px;
    }

    /* 隱藏所有系統介面元件 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stHeader"] {display: none;}

    /* 標題設計 */
    .main-title {
        font-weight: 700;
        color: #1D1D1F;
        font-size: 28px;
        letter-spacing: -0.5px;
        text-align: center;
        padding-top: 40px; /* 給標題適當的頂部距離 */
        margin-bottom: 20px;
    }

    /* Apple 卡片設計 */
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

    /* 輸入框優化 */
    .stTextInput input {
        border-radius: 12px !important;
        background-color: #E8E8ED !important;
        border: none !important;
        padding: 14px !important;
        font-size: 16px !important;
    }

    /* 移除 table 的多餘邊距 */
    .stTable {
        margin-top: -10px;
    }
</style>
"""
st.markdown(apple_css, unsafe_allow_html=True)

# 3. 資料讀取邏輯
@st.cache_data
def load_data():
    all_files = os.listdir(".")
    xlsx_files = [f for f in all_files if f.endswith('.xlsx')]
    
    target_file = None
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
        # 更新搜尋列提示文字
        user_input = st.text_input(
            "搜尋編號", 
            placeholder="輸入迴路盒編號 AV 04-01 或 04-01...", 
            label_visibility="collapsed"
        )
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
            st.error("查無此編號，請重新輸入。")
    else:
        st.markdown('<p style="text-align:center; color:#8E8E93; font-size:14px;">輸入編號快速查詢位置與接口</p>', unsafe_allow_html=True)

else:
    st.error("⚠️ 找不到 Excel 檔案。")

# 頁尾
st.markdown(f'<p style="text-align:center; font-size:11px; color:#C7C7CC; margin-top:30px;">Version 1.8 (Clean Apple Style)</p>', unsafe_allow_html=True)
