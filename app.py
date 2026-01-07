import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV 系統 04-01", 
    page_icon="🔍",
    layout="centered"
)

# 2. 初始化 Session State
if 'search_input' not in st.session_state:
    st.session_state.search_input = ""
if 'df_font_size' not in st.session_state:
    st.session_state.df_font_size = 18  # 預設表格字體大小

# --- 功能控制函式 ---
def handle_clear():
    st.session_state.search_input_widget = ""

def zoom_in():
    st.session_state.df_font_size += 2

def zoom_out():
    if st.session_state.df_font_size > 12:
        st.session_state.df_font_size -= 2

# 3. 注入動態 CSS (包含表格字體縮放與按鈕樣式)
dynamic_style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp {{ background-color: #000000; color: #F5F5F7; font-family: -apple-system, sans-serif; }}
    header, footer, .stDeployButton, [data-testid="stHeader"] {{ display: none !important; }}

    .main-title {{ font-weight: 700; font-size: 30px; text-align: center; padding: 20px 0 10px 0; color: #FFFFFF; }}
    
    .macos-card {{
        background: rgba(30, 30, 32, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
    }}

    /* 強制併排佈局 (用於搜尋框與標題列按鈕) */
    [data-testid="stHorizontalBlock"] {{ 
        display: flex !important; 
        flex-direction: row !important; 
        align-items: center !important; 
        gap: 8px !important; 
    }}

    /* 搜尋框與縮放按鈕樣式 */
    .stTextInput > div > div > input {{ 
        height: 50px !important; font-size: 18px !important; 
        background: rgba(255,255,255,0.1) !important; color: white !important; border-radius: 12px !important;
    }}
    
    /* 縮放專用按鈕 (細長 macOS 質感) */
    .zoom-btn button {{
        height: 35px !important;
        border-radius: 8px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        font-size: 14px !important;
        padding: 0 !important;
    }}
    .zoom-btn button:active {{ transform: scale(0.9) !important; background: rgba(255, 255, 255, 0.3) !important; }}

    /* 清除按鈕 X */
    .clear-btn button {{
        width: 50px !important; height: 50px !important; border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.2) !important; border: none !important;
    }}

    /* --- 表格字體縮放連動 --- */
    [data-testid="stDataFrame"] div[data-testid="stTable"] td, 
    [data-testid="stDataFrame"] div[data-testid="stTable"] th,
    .stDataFrame div {{
        font-size: {st.session_state.df_font_size}px !important;
    }}

    [data-testid="stMetricValue"] {{ font-size: 38px !important; font-weight: 700 !important; color: #0A84FF !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 16px !important; color: #8E8E93 !important; }}
</style>
"""
st.markdown(dynamic_style, unsafe_allow_html=True)

# 4. 資料讀取邏輯
@st.cache_data(show_spinner=False)
def load_data():
    try:
        all_files = [f for f in os.listdir(".") if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in all_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), all_files[0] if all_files else None)
        if not target_file: return None
        df = pd.read_excel(target_file, engine='openpyxl')
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
        if '接頭數' in df.columns:
            df['接頭數'] = pd.to_numeric(df['接頭數'], errors='coerce').fillna(0).astype(int)
        return df
    except: return None

df = load_data()

# 5. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # --- 搜尋區 ---
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        user_input = st.text_input("SEARCH", placeholder="輸入編號", label_visibility="collapsed", key="search_input_widget").strip()
    with c2:
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        st.button("✕", on_click=handle_clear)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    search_query = st.session_state.search_input_widget
    
    if search_query:
        query = search_query.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            # 基本資訊
            st.markdown(f"""
            <div class="macos-card">
                <p style='color:#0A84FF; font-size:12px; font-weight:700;'>LOCATED: {info['迴路盒編號']}</p>
                <div style='display:flex; justify-content:space-between; margin-top:10px;'>
                    <div style='flex:1;'><p style='color:#8E8E93; font-size:14px; margin:0;'>廳別</p><p style='font-size:24px; font-weight:700; margin:0;'>{str(info['廳別']).split('\\n')[0]}</p></div>
                    <div style='flex:1; text-align:right;'><p style='color:#8E8E93; font-size:14px; margin:0;'>位置</p><p style='font-size:18px; margin:0;'>{str(info['迴路盒位置'])}</p></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- 1. 接口清單 (含側邊縮放鈕) ---
            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                
                # 標題列 + 縮放按鈕
                t1, t2, t3 = st.columns([0.6, 0.2, 0.2])
                t1.markdown("<p style='font-size:18px; font-weight:600; color:#8E8E93; margin:0;'>📦 接口清單</p>", unsafe_allow_html=True)
                with t2:
                    st.markdown('<div class="zoom-btn">', unsafe_allow_html=True)
                    st.button("A -", key="z1_out", on_click=zoom_out)
                    st.markdown('</div>', unsafe_allow_html=True)
                with t3:
                    st.markdown('<div class="zoom-btn">', unsafe_allow_html=True)
                    st.button("A +", key="z1_in", on_click=zoom_in)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統', '接頭', '型式', '數量']
                st.dataframe(summary, hide_index=True, use_container_width=True, column_config={"數量": st.column_config.NumberColumn(format="%d")})
                st.markdown('</div>', unsafe_allow_html=True)

            # --- 2. 詳細明細 (含側邊縮放鈕) ---
            with st.expander("🔍 完整目的地明細", expanded=True):
                # 展開後內部的標題與按鈕
                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
                e1, e2, e3 = st.columns([0.6, 0.2, 0.2])
                e1.markdown(f"<p style='color:#8E8E93; font-size:14px; margin-top:8px;'>字體: {st.session_state.df_font_size}px</p>", unsafe_allow_html=True)
                with e2:
                    st.markdown('<div class="zoom-btn">', unsafe_allow_html=True)
                    st.button("A -", key="z2_out", on_click=zoom_out)
                    st.markdown('</div>', unsafe_allow_html=True)
                with e3:
                    st.markdown('<div class="zoom-btn">', unsafe_allow_html=True)
                    st.button("A +", key="z2_in", on_click=zoom_in)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:14px;">READY TO SCAN</p>', unsafe_allow_html=True)
else:
    st.error("找不到資料檔案。")
