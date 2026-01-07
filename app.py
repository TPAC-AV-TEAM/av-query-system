import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV System OS 26",
    page_icon="🕶️",
    layout="centered"
)

# 2. 進階 macOS 26 視覺規範 (包含 Mobile 行動版優化)
macos_26_mobile_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 全域設定 */
    .stApp {
        background-color: #000000;
        color: #F5F5F7;
        font-family: "SF Pro Display", "-apple-system", "BlinkMacSystemFont", "Inter", sans-serif;
    }

    /* 調整主容器在手機上的間距 */
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 650px;
    }

    header, footer, .stDeployButton, [data-testid="stHeader"] {
        display: none !important;
    }

    /* 標題設計 */
    .main-title {
        font-weight: 700;
        background: linear-gradient(180deg, #FFFFFF 0%, #8E8E93 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 30px;
        letter-spacing: -1px;
        text-align: center;
        padding: 15px 0 5px 0;
    }

    /* macOS 磨砂卡片 */
    .macos-card {
        background: rgba(30, 30, 32, 0.7);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 0.5px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    /* 數據指標字體加大 (桌機版預設) */
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #8E8E93 !important;
    }

    /* --- 手機版專屬優化 (Media Query) --- */
    @media (max-width: 600px) {
        .main-title {
            font-size: 26px; /* 標題稍微縮小一點以防折行 */
        }
        .macos-card {
            padding: 16px; /* 手機版減少內距，爭取空間 */
        }
        /* 加大手機上的數據指標文字 */
        [data-testid="stMetricValue"] {
            font-size: 32px !important; /* 手機上數字要非常大 */
        }
        [data-testid="stMetricLabel"] {
            font-size: 16px !important; /* 標籤也要清晰 */
        }
        /* 加大表格內文字 */
        .stDataFrame div, .stDataFrame td {
            font-size: 16px !important;
        }
        /* 加大 Expander 標題文字 */
        .streamlit-expanderHeader p {
            font-size: 18px !important;
        }
    }

    /* 搜尋框與按鈕 */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    
    .stButton > button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: none !important;
        font-size: 18px !important;
    }
</style>
"""
st.markdown(macos_26_mobile_css, unsafe_allow_html=True)

# 3. 初始化 Session State
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

def clear_search():
    st.session_state.search_query = ""

# 4. 資料讀取邏輯
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

# 5. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    col_input, col_clear = st.columns([0.85, 0.15])
    with col_input:
        user_input = st.text_input("SEARCH", value=st.session_state.search_query, placeholder="輸入編號", label_visibility="collapsed").strip()
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
            
            # 資訊卡片
            st.markdown('<div class="macos-card">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0A84FF; font-size:12px; font-weight:700; letter-spacing:1px; margin-bottom:4px;'>MATCHED</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:28px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='height:1px; background:rgba(255,255,255,0.08); margin:18px 0;'></div>", unsafe_allow_html=True)
            
            # 手機版自動垂直排列或縮放
            c1, c2 = st.columns(2)
            c1.metric("廳別", str(info['廳別']).split('\n')[0])
            c2.metric("詳細位置", str(info['迴路盒位置']).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)

            # 接口統計
            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='margin:0 0 15px 0; font-size:16px; color:#8E8E93;'>📦 接口清單</h3>", unsafe_allow_html=True)
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭', '型式', '數量']
                st.dataframe(
                    summary, 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={"數量": st.column_config.NumberColumn("數量", format="%d")}
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("🔍 完整路徑目的地"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:13px;">READY</p>', unsafe_allow_html=True)
else:
    st.error(f"系統故障: {status}")

# 頁尾
st.markdown('<p style="text-align:center; font-size:10px; color:#3A3A3C; margin-top:50px; letter-spacing: 2px;">OS 26 TERMINAL</p>', unsafe_allow_html=True)
