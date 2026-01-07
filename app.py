import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV 系統 04-01", 
    page_icon="🕶️",
    layout="centered"
)

# 2. 注入手機優化標籤
st.markdown("""
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#000000">
</head>
""", unsafe_allow_html=True)

# 3. macOS 26 行動跑馬燈與大字體 CSS
style_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp { background-color: #000000; color: #F5F5F7; font-family: -apple-system, sans-serif; }
    header, footer, .stDeployButton, [data-testid="stHeader"] { display: none !important; }

    .main-title { font-weight: 700; font-size: 28px; text-align: center; padding: 15px 0; color: #FFFFFF; }
    
    .macos-card {
        background: rgba(30, 30, 32, 0.85);
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
        gap: 8px !important; 
    }
    
    .stTextInput > div > div > input { 
        height: 52px !important; font-size: 20px !important; 
        background: rgba(255,255,255,0.1) !important; color: white !important; border-radius: 14px !important;
    }
    
    .stButton > button {
        width: 52px !important; height: 52px !important; border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.2) !important; border: none !important;
    }
    .stButton > button:active { transform: scale(0.8) !important; }

    /* --- 自定義 HTML 表格樣式 --- */
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .table-header-cell { color: #8E8E93; font-size: 14px; padding-bottom: 8px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .table-cell { padding: 16px 0; vertical-align: middle; border-bottom: 1px solid rgba(255,255,255,0.05); overflow: hidden; }

    /* 跑馬燈設定 */
    .marquee-container { width: 100%; overflow: hidden; white-space: nowrap; }
    .marquee-content { display: inline-block; font-size: 24px; font-weight: 600; color: #FFFFFF; }
    .marquee-active { animation: marquee-scroll 10s linear infinite; padding-left: 5px; }
    @keyframes marquee-scroll {
        0% { transform: translateX(0); }
        20% { transform: translateX(0); }
        100% { transform: translateX(-100%); }
    }

    .spec-text { font-size: 15px; color: #A1A1A6; display: block; margin-top: 2px; }
    .qty-text { font-size: 34px; font-weight: 700; color: #0A84FF; text-align: right; }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# 4. 初始化狀態與資料讀取
if 'search_query' not in st.session_state: st.session_state.search_query = ""
def clear_search(): st.session_state.search_query = ""

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
    # 搜尋區
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.82, 0.18])
    with c1:
        user_input = st.text_input("S", value=st.session_state.search_query, placeholder="輸入編號", label_visibility="collapsed").strip()
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
            # 1. 基本資訊卡
            st.markdown(f"""
            <div class="macos-card">
                <p style='color:#0A84FF; font-size:12px; font-weight:700; margin-bottom:5px;'>ID: {info['迴路盒編號']}</p>
                <div style='display:flex; justify-content:space-between; align-items:flex-end;'>
                    <div style='flex:1;'><p style='color:#8E8E93; font-size:14px; margin:0;'>廳別</p><p style='font-size:26px; font-weight:700; margin:0;'>{str(info['廳別']).split('\\n')[0]}</p></div>
                    <div style='flex:1; text-align:right;'><p style='color:#8E8E93; font-size:14px; margin:0;'>位置</p><p style='font-size:20px; font-weight:600; margin:0;'>{str(info['迴路盒位置'])[:12]}</p></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. 接口清單 (使用單一 Markdown 塊避免渲染錯誤)
            if '系統' in match.columns:
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                
                rows_html = ""
                for _, row in summary.iterrows():
                    sys_name = str(row['系統'])
                    # 長度判斷：超過 8 個字啟動跑馬燈
                    marquee_class = "marquee-active" if len(sys_name) > 8 else ""
                    
                    rows_html += f"""
                    <tr>
                        <td class="table-cell" style="width:45%;">
                            <div class="marquee-container">
                                <div class="marquee-content {marquee_class}">{sys_name}</div>
                            </div>
                        </td>
                        <td class="table-cell" style="width:35%; padding-left:10px;">
                            <span style="color:#FFFFFF; font-size:18px; font-weight:500;">{row['接頭']}</span>
                            <span class="spec-text">{row['接頭型式']}</span>
                        </td>
                        <td class="table-cell qty-text" style="width:20%;">{int(row['接頭數'])}</td>
                    </tr>"""
                
                table_final = f"""
                <div class="macos-card">
                    <h3 style='margin:0 0 15px 0; font-size:18px; color:#8E8E93;'>📦 接口清單 (130% 放大)</h3>
                    <table class="custom-table">
                        <thead><tr><th class="table-header-cell">系統</th><th class="table-header-cell" style="padding-left:10px;">接頭</th><th class="table-header-cell" style="text-align:right;">數量</th></tr></thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                </div>"""
                st.markdown(table_final, unsafe_allow_html=True)

            with st.expander("🔍 完整目的地明細"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:14px;">READY</p>', unsafe_allow_html=True)
else:
    st.error("找不到資料檔案。")
