import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV System OS 26",
    page_icon="🕶️",
    layout="centered"
)

# 2. 進階 macOS 26 視覺規範 (包含移除數量小數點、優化表格)
macos_26_advanced_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 全域設定 */
    .stApp {
        background-color: #000000;
        color: #F5F5F7;
        font-family: "SF Pro Display", "-apple-system", "BlinkMacSystemFont", "Inter", sans-serif;
    }

    .block-container {
        padding-top: 1.5rem !important;
        max-width: 650px;
    }

    /* 隱藏系統多餘元件 */
    header, footer, .stDeployButton, [data-testid="stHeader"] {
        display: none !important;
    }

    /* 標題：更細緻的漸層 */
    .main-title {
        font-weight: 700;
        background: linear-gradient(180deg, #FFFFFF 0%, #8E8E93 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 34px;
        letter-spacing: -1px;
        text-align: center;
        padding: 20px 0 5px 0;
    }

    /* macOS 26 磨砂卡片：增加微光邊框 */
    .macos-card {
        background: rgba(30, 30, 32, 0.65);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 0.5px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 18px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
        margin-top: -5px; /* 縮減與標題間距 */
    }

    /* 搜尋框：更深邃的設計 */
    .stTextInput > div > div > input {
        border-radius: 14px !important;
        background-color: rgba(0, 0, 0, 0.4) !important;
        border: 0.5px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border: 1px solid #0A84FF !important;
        background-color: rgba(10, 132, 255, 0.05) !important;
        box-shadow: 0 0 15px rgba(10, 132, 255, 0.2) !important;
    }

    /* 表格美化：移除框線，改用 macOS 條列感 */
    [data-testid="stDataFrame"] {
        border: none !important;
    }
    
    /* 針對表格內的數字與文字進行對齊與加粗 */
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        letter-spacing: -0.5px;
    }
</style>
"""
st.markdown(macos_26_advanced_css, unsafe_allow_html=True)

# 3. 資料讀取邏輯
@st.cache_data(show_spinner=False)
def load_data():
    try:
        all_files = os.listdir(".")
        xlsx_files = [f for f in all_files if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in xlsx_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), None)
        if not target_file and xlsx_files: target_file = xlsx_files[0]
        if not target_file: return None, "NO_FILE"

        df = pd.read_excel(target_file, engine='openpyxl')
        # 搜尋 ID 正規化
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
        # 強制轉換「接頭數」為整數，避免出現小數點
        if '接頭數' in df.columns:
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0).astype(int)
        return df, target_file
    except Exception as e:
        return None, str(e)

df, status = load_data()

# 4. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    user_input = st.text_input("SEARCH", placeholder="輸入編號 (例如: 04-01)", label_visibility="collapsed").strip()
    st.markdown('</div>', unsafe_allow_html=True)

    if user_input:
        query = user_input.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            
            # 資訊卡片
            st.markdown('<div class="macos-card">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0A84FF; font-size:12px; font-weight:700; letter-spacing:1px; margin-bottom:4px;'>SYSTEM SCAN OK</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:28px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='height:1px; background:rgba(255,255,255,0.08); margin:18px 0;'></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("廳別", str(info['廳別']).split('\n')[0])
            c2.metric("詳細位置", str(info['迴路盒位置']).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)

            # 接口統計：這裡解決小數點與索引問題
            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='margin:0 0 15px 0; font-size:16px; color:#8E8E93;'>📦 接口清單</h3>", unsafe_allow_html=True)
                
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭', '型式', '數量']
                
                # 使用 st.dataframe 並隱藏索引，同時確保數字格式
                st.dataframe(
                    summary, 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={
                        "數量": st.column_config.NumberColumn("數量", format="%d")
                    }
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # 展開明細
            with st.expander("🔍 完整路徑目的地"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號，請重新確認。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:13px; letter-spacing:1px;">READY TO SCAN</p>', unsafe_allow_html=True)
else:
    st.error(f"系統故障: {status}")

# 頁尾
st.markdown('<p style="text-align:center; font-size:10px; color:#3A3A3C; margin-top:50px; letter-spacing: 2px;">OS 26 TERMINAL // NO ACCESS LOGS</p>', unsafe_allow_html=True)
