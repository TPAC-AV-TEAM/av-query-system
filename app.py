import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定 (Apple 風格優化)
st.set_page_config(
    page_title="AV 迴路盒系統",
    page_icon="🔍",
    layout="centered", # 使用居中佈局，在手機上閱讀更舒適
    initial_sidebar_state="collapsed"
)

# 2. 定製 Apple 視覺規範 CSS
apple_css = """
<style>
    /* 全域字體與背景 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #F5F5F7; /* Apple 淺灰背景 */
    }

    /* 頂部標題加粗 */
    .main-title {
        font-weight: 700;
        color: #1D1D1F;
        letter-spacing: -0.5px;
        text-align: center;
        padding-top: 2rem;
        margin-bottom: 0.5rem;
    }

    /* 手機端卡片設計 */
    .apple-card {
        background: white;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid #E5E5E7;
    }

    /* 指標數據優化 */
    .stMetric {
        background-color: #FBFBFD;
        border-radius: 12px;
        padding: 12px !important;
        border: 1px solid #F0F0F2;
    }

    /* 按鈕樣式：iOS 藍 */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        border: none;
        background-color: #007AFF;
        color: white;
        font-weight: 600;
        padding: 10px 0;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }

    /* 隱藏預設元件提升簡約感 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 針對手機屏幕優化輸入框尺寸 */
    .stTextInput input {
        border-radius: 12px !important;
        padding: 12px !important;
        font-size: 16px !important; /* 防止 iOS 自動縮放 */
    }
</style>
"""
st.markdown(apple_css, unsafe_allow_html=True)

# 3. 資料讀取邏輯
@st.cache_data
def load_data():
    default_file = "Cable list  音視訊 20201109.xlsx"
    all_files = os.listdir(".")
    xlsx_files = [f for f in all_files if f.endswith('.xlsx')]
    
    target_file = None
    if default_file in all_files:
        target_file = default_file
    elif xlsx_files:
        for f in xlsx_files:
            if any(k in f for k in ["Cable", "音視訊", "迴路盒"]):
                target_file = f
                break
        if not target_file:
            target_file = xlsx_files[0]

    if not target_file:
        return None

    try:
        df = pd.read_excel(target_file, engine='openpyxl')
        if '迴路盒編號' not in df.columns: return None
        
        # 數據預處理
        if '接頭數' in df.columns:
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0)
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(' ', '').str.replace('-', '')
        return df, target_file
    except:
        return None

data_tuple = load_data()

# 4. 主介面設計
st.markdown('<h1 class="main-title">音視訊迴路盒查詢</h1>', unsafe_allow_html=True)

if data_tuple:
    df, filename = data_tuple
    
    # 搜尋區卡片
    with st.container():
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        user_input = st.text_input("請輸入編號", placeholder="例如: 04-01", label_visibility="collapsed")
        
        # 快速按鈕區 (針對手機觸控優化)
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
            
            # 位置資訊卡片
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            st.markdown(f"### 📍 {user_input.upper()}")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("廳別", str(info['廳別']).split('\n')[0])
            with c2:
                # 針對手機螢幕簡化位置文字
                loc = str(info['迴路盒位置']).replace('\n', ' ')
                st.metric("位置詳細", loc)
            st.markdown('</div>', unsafe_allow_html=True)

            # 統計匯總卡片
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            st.markdown("### 📦 接口統計")
            if '系統' in match.columns:
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭型號', '型式', '數量']
                summary['數量'] = summary['數量'].astype(int)
                # 使用 table 更適合手機顯示固定寬度
                st.table(summary)
            st.markdown('</div>', unsafe_allow_html=True)

            # 詳細明細 (收納式設計)
            with st.expander("🔍 完整線路目的地明細"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True)
        else:
            st.error("查無資料，請檢查編號。")
    else:
        st.markdown('<p style="text-align:center; color:#8E8E93;">輸入 4F 編號快速查看現場設備狀況</p>', unsafe_allow_html=True)

else:
    st.error("⚠️ 環境中找不到資料檔案，請確認 Excel 已上傳。")

# 頁尾
st.markdown(f'<p style="text-align:center; font-size:12px; color:#AEAEB2; margin-top:50px;">系統版本 v1.6 (iOS Optimized)<br>資料來源: {data_tuple[1] if data_tuple else "未連結"}</p>', unsafe_allow_html=True)
