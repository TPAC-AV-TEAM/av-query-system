import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
APP_NAME = "AV系統-總館" 
st.set_page_config(page_title=APP_NAME, page_icon="🕶️", layout="centered")

# 標題注入
st.components.v1.html(f"<script>window.parent.document.title = '{APP_NAME}';</script>", height=0)

# 2. 定義廳院代碼與配色馬甲
HALL_MAPS = {
    "大劇院": {"display": "GT (Grand Theatre)", "color": "#0A84FF"},
    "多形式中劇院": {"display": "BB (Blue Box)", "color": "#FF375F"},
    "鏡框式中劇院": {"display": "GP (Grand Playhouse)", "color": "#FFD60A"},
    "DEFAULT": {"display": "AV System", "color": "#FFFFFF"}
}

# 3. macOS 26 視覺規範
macos_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #000000; color: #F5F5F7; font-family: "SF Pro Display", sans-serif; }
    .search-container { margin-top: 10px !important; margin-bottom: 20px !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; gap: 10px !important; }
    header, footer, [data-testid="stHeader"] { display: none !important; }
    .main-title { font-weight: 700; background: linear-gradient(180deg, #FFFFFF 0%, #8E8E93 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; text-align: center; margin-bottom: 15px; }
    .macos-card { background: rgba(30, 30, 32, 0.6); backdrop-filter: blur(20px); border: 0.5px solid rgba(255, 255, 255, 0.12); border-radius: 20px; padding: 20px; margin-bottom: 12px; }
    .stTextInput > div > div > input { border-radius: 12px !important; background-color: rgba(255, 255, 255, 0.05) !important; color: #FFFFFF !important; }
    .stButton > button { border-radius: 12px !important; background-color: rgba(255, 255, 255, 0.08) !important; color: #FFFFFF !important; }
    [data-testid="stMetricValue"] { font-size: 22px !important; }
    .status-text { text-align: center; color: #48484A; font-size: 12px; letter-spacing: 1px; margin-top: 15px; }
</style>
"""
st.markdown(macos_style, unsafe_allow_html=True)

# 4. 資料讀取 (強化自動搜尋功能)
@st.cache_data(show_spinner=False)
def load_data():
    try:
        # 優先找包含「迴路盒」關鍵字的 CSV 或 XLSX
        files = [f for f in os.listdir(".") if not f.startswith('~$')]
        target = next((f for f in files if "迴路盒" in f or "Cable" in f), None)
        
        if not target:
            return None, "找不到資料檔，請確認 CSV 是否在資料夾中。"

        if target.endswith('.csv'):
            # 增加 encoding='utf-8-sig' 處理 Excel 產生的 CSV 編碼問題
            df = pd.read_csv(target, encoding='utf-8-sig')
        else:
            df = pd.read_excel(target)
            
        df.columns = [c.strip() for c in df.columns]
        if '迴路盒編號' in df.columns:
            df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
            df['search_id'] = df['search_id'].apply(lambda x: x if x.startswith("AV") else "AV"+x)
        return df, "SUCCESS"
    except Exception as e:
        return None, str(e)

df, status = load_data()

# 5. 介面呈現
st.markdown('<h1 class="main-title">AV BOX SEARCH</h1>', unsafe_allow_html=True)

if df is not None:
    if 'search_query' not in st.session_state: st.session_state.search_query = ""
    
    st.markdown('<div class="macos-card search-container">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.85, 0.15])
    with c1:
        user_input = st.text_input("SEARCH", key="search_input_widget", placeholder="Enter ID (e.g. 07-02)", label_visibility="collapsed").strip()
        st.session_state.search_query = user_input
    with c2:
        if st.button("✕"):
            st.session_state.search_query = ""
            st.session_state["search_input_widget"] = ""
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.search_query:
        query = st.session_state.search_query.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            raw_hall = str(info.get('廳別', 'N/A')).strip()
            badge = HALL_MAPS.get(raw_hall, HALL_MAPS["DEFAULT"])

            # 顯示英文馬甲
            st.markdown(f'''
                <div class="macos-card" style="border-left: 5px solid {badge['color']};">
                    <p style='color:{badge['color']}; font-size:12px; font-weight:700; margin-bottom:4px;'>{badge['display']}</p>
                    <h2 style='margin:0; font-size:26px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>
                    <hr style='border:0.5px solid rgba(255,255,255,0.1); margin:15px 0;'>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('<div class="macos-card" style="margin-top:-20px;">', unsafe_allow_html=True)
            st.metric("LOCATION", badge['display'])
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True) 
            loc_detail = str(info.get('迴路盒位置', 'N/A')).replace('\\n', ' ').replace('\n', ' ')
            st.metric("POSITION DETAIL", loc_detail)
            st.markdown('</div>', unsafe_allow_html=True)

            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown(f"<p style='color:{badge['color']}; font-size:14px; margin-bottom:10px;'>📦 {badge['display']} INTERFACE LIST</p>", unsafe_allow_html=True)
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                st.dataframe(summary, hide_index=True, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("No record found for this ID.")
    else:
        st.markdown('<p class="status-text">READY TO SCAN</p>', unsafe_allow_html=True)
else:
    st.error(f"System Error: {status}")

st.markdown('<p style="text-align:center; font-size:10px; color:#3A3A3C; margin-top:30px; letter-spacing: 2px;">OS 26 TERMINAL</p>', unsafe_allow_html=True)
