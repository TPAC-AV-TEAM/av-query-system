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

# 3. macOS 26 極致行動版 CSS (含跑馬燈與超大字體)
macos_26_marquee_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp { background-color: #000000; color: #F5F5F7; font-family: -apple-system, sans-serif; }
    header, footer, .stDeployButton, [data-testid="stHeader"] { display: none !important; }

    /* 標題與卡片 */
    .main-title { font-weight: 700; font-size: 28px; text-align: center; padding: 15px 0; color: #FFFFFF; }
    .macos-card {
        background: rgba(30, 30, 32, 0.8);
        backdrop-filter: blur(20px);
        border: 0.5px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* 搜尋列併排與觸控優化 */
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; align-items: center !important; gap: 8px !important; }
    .stTextInput > div > div > input { height: 50px !important; font-size: 18px !important; border-radius: 12px !important; background: rgba(255,255,255,0.1) !important; color: white !important; }
    
    .stButton > button {
        width: 50px !important; height: 50px !important; border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.15) !important; border: none !important;
        transition: transform 0.1s ease !important;
    }
    .stButton > button:active { transform: scale(0.8) !important; background: rgba(255, 255, 255, 0.3) !important; }

    /* 數據指標放大 */
    [data-testid="stMetricValue"] { font-size: 40px !important; font-weight: 700 !important; color: #0A84FF !important; }
    [data-testid="stMetricLabel"] { font-size: 18px !important; color: #8E8E93 !important; }

    /* --- 自定義 HTML 表格與跑馬燈 --- */
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .table-header { color: #8E8E93; font-size: 16px; border-bottom: 0.5px solid rgba(255,255,255,0.1); padding-bottom: 8px; text-align: left; }
    .table-row { border-bottom: 0.5px solid rgba(255,255,255,0.05); }
    .table-cell { padding: 12px 0; font-size: 22px; font-weight: 500; color: #FFFFFF; vertical-align: middle; }

    /* 跑馬燈容器 */
    .marquee-box {
        width: 160px; /* 限制寬度 */
        overflow: hidden;
        white-space: nowrap;
        position: relative;
    }
    .marquee-text {
        display: inline-block;
        padding-left: 0%;
        animation: marquee-anim 10s linear infinite;
    }
    @keyframes marquee-anim {
        0% { transform: translateX(0); }
        33% { transform: translateX(0); } /* 停頓一下 */
        100% { transform: translateX(-100%); }
    }
    .qty-cell { text-align: right; color: #0A84FF; font-weight: 700; font-size: 26px; }
</style>
"""
st.markdown(macos_26_marquee_css, unsafe_allow_html=True)

# 4. 初始化狀態
if 'search_query' not in st.session_state: st.session_state.search_query = ""
def clear_search(): st.session_state.search_query = ""

# 5. 資料讀取
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
    except Exception as e: return None, str(e)

df, status = load_data()

# 6. 介面呈現
st.markdown('<h1 class="main-title">音視訊迴路盒</h1>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區 (防換行)
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        user_input = st.text_input("S", value=st.session_state.search_query, placeholder="輸入編號 (如 04-01)", label_visibility="collapsed").strip()
        st.session_state.search_query = user_input
    with c2:
        st.button("✕", on_click=clear_search)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.search_query:
        query = st.session_state.search_query.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            # 1. 廳別位置卡片
            st.markdown('<div class="macos-card">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0A84FF; font-size:14px; font-weight:700;'>ONLINE</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:32px;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.markdown("<div style='height:1px; background:rgba(255,255,255,0.1); margin:15px 0;'></div>", unsafe_allow_html=True)
            mc1, mc2 = st.columns(2)
            mc1.metric("廳別", str(info['廳別']).split('\n')[0])
            mc2.metric("位置", str(info['迴路盒位置']).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)

            # 2. 自定義跑馬燈表格 (接口清單)
            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='margin:0 0 10px 0; font-size:18px; color:#8E8E93;'>📦 接口清單 (超大字體)</h3>", unsafe_allow_html=True)
                
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                
                # 建構 HTML 表格
                rows_html = ""
                for _, row in summary.iterrows():
                    # 如果名稱超過 8 個字，啟動跑馬燈
                    sys_name = str(row['系統'])
                    display_sys = f'<div class="marquee-box"><div class="marquee-text">{sys_name}</div></div>' if len(sys_name) > 8 else sys_name
                    
                    rows_html += f"""
                    <tr class="table-row">
                        <td class="table-cell" style="width:160px;">{display_sys}</td>
                        <td class="table-cell" style="font-size:16px; color:#A1A1A6;">{row['接頭']}<br><span style="font-size:12px;">{row['接頭型式']}</span></td>
                        <td class="table-cell qty-cell">{row['接頭數']}</td>
                    </tr>
                    """
                
                table_html = f"""
                <table class="custom-table">
                    <thead><tr class="table-header"><th>系統</th><th>規格</th><th style="text-align:right;">數量</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                """
                st.markdown(table_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("🔍 詳細明細"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:14px;">READY</p>', unsafe_allow_html=True)
else:
    st.error(f"系統故障: {status}")
