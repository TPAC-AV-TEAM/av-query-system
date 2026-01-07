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

# 3. macOS 26 行動跑馬燈 CSS (修正與強化版)
macos_26_final_v2_css = """
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
        height: 52px !important; 
        font-size: 20px !important; 
        background: rgba(255,255,255,0.1) !important; 
        color: white !important; 
        border-radius: 14px !important;
    }
    
    .stButton > button {
        width: 52px !important; height: 52px !important; border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.2) !important; border: none !important;
        transition: transform 0.1s ease !important;
    }
    .stButton > button:active { transform: scale(0.8) !important; }

    /* --- 自定義 HTML 表格與跑馬燈效果 --- */
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 5px; }
    .table-header { color: #8E8E93; font-size: 16px; border-bottom: 1px solid rgba(255,255,255,0.1); text-align: left; }
    .table-cell { padding: 16px 0; vertical-align: middle; border-bottom: 1px solid rgba(255,255,255,0.05); }

    /* 跑馬燈容器：限制寬度並隱藏溢出 */
    .marquee-container {
        width: 150px; /* 根據手機寬度限制 */
        overflow: hidden;
        white-space: nowrap;
    }
    
    .marquee-content {
        display: inline-block;
        font-size: 24px; /* 加大文字 */
        font-weight: 600;
        color: #FFFFFF;
    }

    /* 只有當文字長度觸發跑馬燈時才執行的動畫 */
    .marquee-active {
        animation: marquee-scroll 8s linear infinite;
        padding-left: 10%;
    }

    @keyframes marquee-scroll {
        0% { transform: translateX(0); }
        20% { transform: translateX(0); } /* 停留一下 */
        100% { transform: translateX(-100%); }
    }

    .spec-text { font-size: 14px; color: #A1A1A6; display: block; margin-top: 4px; }
    .qty-text { font-size: 32px; font-weight: 700; color: #0A84FF; text-align: right; }
</style>
"""
st.markdown(macos_26_final_v2_css, unsafe_allow_html=True)

# 4. 初始化狀態
if 'search_query' not in st.session_state: st.session_state.search_query = ""
def clear_search(): st.session_state.search_query = ""

# 5. 資料讀取
@st.cache_data(show_spinner=False)
def load_data():
    try:
        all_files = [f for f in os.listdir(".") if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in all_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), all_files[0] if all_files else None)
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
    # 搜尋區
    st.markdown('<div class="macos-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        user_input = st.text_input("S", value=st.session_state.search_query, placeholder="輸入編號 (如 06-61)", label_visibility="collapsed").strip()
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
            # 廳別與位置
            st.markdown(f"""
            <div class="macos-card">
                <p style='color:#0A84FF; font-size:12px; font-weight:700;'>LOCATION</p>
                <h2 style='margin:0; font-size:32px;'>{info['迴路盒編號']}</h2>
                <div style='height:1px; background:rgba(255,255,255,0.1); margin:15px 0;'></div>
                <div style='display:flex; justify-content:space-between;'>
                    <div><p style='color:#8E8E93; font-size:14px; margin:0;'>廳別</p><p style='font-size:24px; font-weight:600; margin:0;'>{str(info['廳別']).split('\\n')[0]}</p></div>
                    <div style='text-align:right;'><p style='color:#8E8E93; font-size:14px; margin:0;'>位置</p><p style='font-size:24px; font-weight:600; margin:0;'>{str(info['迴路盒位置'])[:10]}...</p></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 接口清單 (自定義 HTML 表格)
            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='margin:0 0 10px 0; font-size:18px; color:#8E8E93;'>📦 接口清單 (超大字體)</h3>", unsafe_allow_html=True)
                
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                
                rows_html = ""
                for _, row in summary.iterrows():
                    sys_name = str(row['系統'])
                    # 判斷是否需要跑馬燈 (超過 8 個字)
                    marquee_class = "marquee-active" if len(sys_name) > 8 else ""
                    
                    rows_html += f"""
                    <tr class="table-row">
                        <td class="table-cell">
                            <div class="marquee-container">
                                <div class="marquee-content {marquee_class}">{sys_name}</div>
                            </div>
                        </td>
                        <td class="table-cell" style="padding-left:10px;">
                            <span style="color:#FFFFFF; font-size:18px;">{row['接頭']}</span>
                            <span class="spec-text">{row['接頭型式']}</span>
                        </td>
                        <td class="table-cell qty-text">{int(row['接頭數'])}</td>
                    </tr>
                    """
                
                # 最終 HTML 包裝
                full_table_html = f"""
                <table class="custom-table">
                    <thead><tr class="table-header"><th>系統</th><th>接頭</th><th style="text-align:right;">數量</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                """
                # 使用唯一包裝確保 HTML 被渲染
                st.write(full_table_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("🔍 完整目的地明細"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:14px;">READY</p>', unsafe_allow_html=True)
else:
    st.error(f"系統故障: {status}")
