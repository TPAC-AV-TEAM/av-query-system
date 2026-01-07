import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="迴路盒查詢", # <--- 修改處 1
    page_icon="🕶️",
    layout="centered"
)

# 解決 Android 安裝名稱問題的 JavaScript
st.components.v1.html(
    f"""
    <script>
        window.parent.document.title = "迴路盒查詢"; // <--- 修改處 2
    </script>
    """,
    height=0,
)

# 2. 進階 macOS 26 視覺規範
macos_26_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #F5F5F7;
        font-family: "SF Pro Display", "-apple-system", "Inter", sans-serif;
    }

    /* 修正：調整間距，避免搜尋框擋住標題 */
    .search-container {
        margin-top: 5px !important; /* 恢復正常間距，移除激進的負值 */
        margin-bottom: 15px !important;
    }

    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 10px !important;
    }
    [data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
    }
    [data-testid="column"]:nth-child(2) {
        flex: 0 0 45px !important;
    }

    .block-container {
        padding-top: 2rem !important; /* 增加頂部留白，給標題空間 */
        max-width: 600px;
    }

    header, footer, [data-testid="stHeader"] { display: none !important; }

    .main-title {
        font-weight: 700;
        background: linear-gradient(180deg, #FFFFFF 0%, #8E8E93 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
        text-align: center;
        margin-bottom: 20px; /* 增加標題下方間距，防止重疊 */
    }

    .macos-card {
        background: rgba(30, 30, 32, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 0.5px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .stTextInput > div > div > input {
        border-radius: 12px !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        padding: 10px 14px !important;
        font-size: 16px !important;
    }

    .stButton > button {
        border-radius: 12px !important;
        width: 42px !important;
        height: 42px !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 0.5px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
    }

    [data-testid="stMetricValue"] { font-size: 22px !important; }
    .status-text { text-align: center; color: #48484A; font-size: 12px; letter-spacing: 1px; margin-top: 10px; }
</style>
"""
st.markdown(macos_26_style, unsafe_allow_html=True)

# 3. 初始化與功能函數
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

def clear_search():
    st.session_state.search_query = ""
    st.session_state["search_input_widget"] = ""

# 4. 資料讀取
@st.cache_data(show_spinner=False)
def load_data():
    try:
        xlsx_files = [f for f in os.listdir(".") if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in xlsx_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), None)
        if not target_file: return None, "NO_FILE"
        df = pd.read_excel(target_file, engine='openpyxl')
        df.columns = [c.strip() for c in df.columns]
        if '迴路盒編號' in df.columns:
            df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
            df['search_id'] = df['search_id'].apply(lambda x: x if x.startswith("AV") else "AV"+x)
        return df, target_file
    except Exception as e:
        return None, str(e)

df, status = load_data()

# 5. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區塊
    st.markdown('<div class="macos-card search-container">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.85, 0.15])
    with c1:
        user_input = st.text_input(
            "SEARCH", key="search_input_widget",
            placeholder="輸入編號 (例如: 07-02)",
            label_visibility="collapsed"
        ).strip()
        st.session_state.search_query = user_input
    with c2:
        st.button("✕", on_click=clear_search)
    st.markdown('</div>', unsafe_allow_html=True)

    # 搜尋結果
    if st.session_state.search_query:
        query = st.session_state.search_query.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            st.markdown('<div class="macos-card">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0A84FF; font-size:11px; font-weight:700; margin-bottom:4px;'>SYSTEM SCAN OK</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:26px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.markdown("<hr style='border:0.5px solid rgba(255,255,255,0.1); margin:15px 0;'>", unsafe_allow_html=True)
            
            # 垂直排列
            st.metric("廳別", str(info.get('廳別', 'N/A')).split('\n')[0])
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True) 
            st.metric("詳細位置", str(info.get('迴路盒位置', 'N/A')).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)

            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<p style='color:#8E8E93; font-size:14px; margin-bottom:10px;'>📦 接口清單</p>", unsafe_allow_html=True)
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                st.dataframe(summary, hide_index=True, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("查無此編號")
    else:
        st.markdown('<p class="status-text">READY TO SCAN</p>', unsafe_allow_html=True)
else:
    st.error(f"系統故障: {status}")

st.markdown('<p style="text-align:center; font-size:10px; color:#3A3A3C; margin-top:30px; letter-spacing: 2px;">OS 26 TERMINAL</p>', unsafe_allow_html=True)
