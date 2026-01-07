import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV 系統 04-01", 
    page_icon="🕶️",
    layout="centered"
)

# 2. 注入 PWA 與手機優化標籤
st.markdown("""
<head>
    <meta name="apple-mobile-web-app-title" content="AV系統">
    <meta name="theme-color" content="#000000">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
</head>
""", unsafe_allow_html=True)

# 3. macOS 26 行動優化 CSS
macos_26_final_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp { background-color: #000000; color: #F5F5F7; font-family: -apple-system, sans-serif; }
    header, footer, .stDeployButton, [data-testid="stHeader"] { display: none !important; }

    .main-title { font-weight: 700; font-size: 30px; text-align: center; padding: 20px 0 10px 0; color: #FFFFFF; }
    
    .macos-card {
        background: rgba(30, 30, 32, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* 搜尋列併排強制修正 */
    [data-testid="stHorizontalBlock"] { 
        display: flex !important; 
        flex-direction: row !important; 
        align-items: center !important; 
        gap: 10px !important; 
    }
    
    /* 搜尋框輸入文字加大 */
    .stTextInput > div > div > input { 
        height: 52px !important; 
        font-size: 18px !important; 
        background: rgba(255,255,255,0.1) !important; 
        color: white !important; 
        border-radius: 12px !important;
    }
    
    /* 清除按鈕 X 的觸控回饋 */
    .stButton > button {
        width: 52px !important; height: 52px !important; border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.2) !important; border: none !important;
        color: white !important; font-size: 20px !important;
    }
    .stButton > button:active { transform: scale(0.85) !important; background: rgba(255, 255, 255, 0.4) !important; }

    /* 數據指標放大 130% */
    [data-testid="stMetricValue"] { font-size: 38px !important; font-weight: 700 !important; color: #0A84FF !important; }
    [data-testid="stMetricLabel"] { font-size: 18px !important; color: #8E8E93 !important; }

    /* Dataframe 表格文字加大 */
    [data-testid="stDataFrame"] div[data-testid="stTable"] td, 
    [data-testid="stDataFrame"] div[data-testid="stTable"] th {
        font-size: 18px !important;
    }
    
    .streamlit-expanderHeader p { font-size: 18px !important; font-weight: 600 !important; }
</style>
"""
st.markdown(macos_26_final_css, unsafe_allow_html=True)

# 4. 初始化 Session State 與清除功能
if 'search_input' not in st.session_state:
    st.session_state.search_input = ""

def handle_clear():
    # 直接重置綁定的 key 確保立即反應
    st.session_state.search_input_widget = ""
    st.session_state.search_input = ""

# 5. 資料讀取
@st.cache_data(show_spinner=False)
def load_data():
    try:
        all_files = [f for f in os.listdir(".") if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in all_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), all_files[0] if all_files else None)
        if not target_file: return None
        df = pd.read_excel(target_file, engine='openpyxl')
        # 搜尋 ID 正規化
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
        # 數量轉整數
        if '接頭數' in df.columns:
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0).astype(int)
        return df
    except: return None

df = load_data()

# 6. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        # 使用 key 綁定來解決 X 按鈕沒反應的問題
        user_input = st.text_input(
            "SEARCH", 
            placeholder="輸入編號 (如 04-01)", 
            label_visibility="collapsed",
            key="search_input_widget"
        ).strip()
    with c2:
        st.button("✕", on_click=handle_clear)
    st.markdown('</div>', unsafe_allow_html=True)

    # 搜尋邏輯處理
    search_query = st.session_state.search_input_widget
    
    if search_query:
        query = search_query.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            # 1. 基本資訊卡
            st.markdown(f"""
            <div class="macos-card">
                <p style='color:#0A84FF; font-size:12px; font-weight:700; margin-bottom:5px;'>ID: {info['迴路盒編號']}</p>
                <div style='display:flex; justify-content:space-between; align-items:flex-end;'>
                    <div style='flex:1;'><p style='color:#8E8E93; font-size:14px; margin:0;'>廳別</p><p style='font-size:26px; font-weight:700; margin:0;'>{str(info['廳別']).split('\\n')[0]}</p></div>
                    <div style='flex:1; text-align:right;'><p style='color:#8E8E93; font-size:14px; margin:0;'>位置</p><p style='font-size:20px; font-weight:600; margin:0;'>{str(info['迴路盒位置'])}</p></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. 接口清單 (還原為可拖拉的 dataframe)
            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='margin:0 0 15px 0; font-size:18px; color:#8E8E93;'>📦 接口清單</h3>", unsafe_allow_html=True)
                
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭', '型式', '數量']
                
                st.dataframe(
                    summary, 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={
                        "數量": st.column_config.NumberColumn("數量", format="%d") # 移除小數點
                    }
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # 3. 詳細明細
            with st.expander("🔍 完整目的地明細"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:14px; letter-spacing:1px;">READY TO SCAN</p>', unsafe_allow_html=True)
else:
    st.error("找不到資料檔案。")
