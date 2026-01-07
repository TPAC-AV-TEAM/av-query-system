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

# 2. 定製 Apple 視覺規範 CSS
apple_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* 容器與背景設定 */
    .stApp {
        background-color: #F5F5F7;
    }

    .block-container {
        padding-top: 1rem !important;
        max-width: 600px;
    }

    /* 隱藏預設元件 */
    header, footer, .stDeployButton, [data-testid="stHeader"] {
        visibility: hidden;
        display: none;
    }

    /* 標題設計 */
    .main-title {
        font-weight: 700;
        color: #1D1D1F;
        font-size: 28px;
        letter-spacing: -0.5px;
        text-align: center;
        padding: 20px 0;
    }

    /* Apple 卡片設計 */
    .apple-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* 指標字體優化 */
    [data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-weight: 600 !important;
    }

    /* 搜尋框優化 */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        background-color: #E8E8ED !important;
        border: none !important;
        padding: 12px 16px !important;
    }
</style>
"""
st.markdown(apple_css, unsafe_allow_html=True)

# 3. 資料讀取邏輯 (增加錯誤回饋)
@st.cache_data(show_spinner="正在讀取資料庫...")
def load_data():
    try:
        all_files = os.listdir(".")
        # 篩選可能的 Excel 檔案
        xlsx_files = [f for f in all_files if f.endswith('.xlsx') and not f.startswith('~$')]
        
        target_file = next((f for f in xlsx_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), None)
        if not target_file and xlsx_files:
            target_file = xlsx_files[0]

        if not target_file:
            return None, "找不到相關的 Excel 檔案。"

        df = pd.read_excel(target_file, engine='openpyxl')
        
        # 欄位檢查
        required_cols = ['迴路盒編號', '廳別', '迴路盒位置']
        if not all(col in df.columns for col in required_cols):
            return None, f"Excel 檔案格式不正確，缺少必要欄位：{required_cols}"

        # 預先處理搜尋 ID
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
        if '接頭數' in df.columns:
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0)
            
        return df, target_file
    except Exception as e:
        return None, f"讀取錯誤: {str(e)}"

df, info_or_error = load_data()

# 4. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區
    with st.container():
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        user_input = st.text_input(
            "搜尋編號", 
            placeholder="例如: AV 04-01 或 04-01", 
            label_visibility="collapsed"
        ).strip()
        st.markdown('</div>', unsafe_allow_html=True)

    if user_input:
        # 處理搜尋字串：轉大寫、去空格、去連字號
        query = user_input.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"):
            query = "AV" + query

        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            
            # 資訊卡片
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#8E8E93; margin-bottom:4px;'>迴路盒編號</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:24px; color:#1D1D1F;'>📍 {info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.write("---")
            
            col1, col2 = st.columns(2)
            col1.metric("廳別", str(info['廳別']).split('\n')[0])
            col2.metric("位置", str(info['迴路盒位置']).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)

            # 接口統計 (僅在有'系統'欄位時顯示)
            if '系統' in match.columns and '接頭' in match.columns:
                st.markdown('<div class="apple-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='margin:0 0 15px 0; font-size:18px;'>📦 接口清單</h3>", unsafe_allow_html=True)
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭', '型式', '數量']
                summary['數量'] = summary['數量'].astype(int)
                st.table(summary)
                st.markdown('</div>', unsafe_allow_html=True)

            # 詳細明細
            with st.expander("🔍 查看完整線路目的地"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error(f"找不到編號 '{user_input}'，請確認格式是否正確。")
    else:
        st.info("💡 請在上方輸入框輸入迴路盒編號開始查詢。")
else:
    st.error(f"⚠️ 系統初始化失敗：{info_or_error}")

# 頁尾
st.markdown('<p style="text-align:center; font-size:12px; color:#8E8E93; margin-top:40px;">Version 1.9 (Optimized Apple Style)</p>', unsafe_allow_html=True)
