import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="AV 現場極致版", 
    page_icon="🔍",
    layout="centered"
)

# 2. 注入手機 PWA 與 42px+ 極致大字樣式
macos_extreme_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@700&display=swap');
    
    .stApp { background-color: #000000; color: #F5F5F7; }
    header, footer, .stDeployButton, [data-testid="stHeader"] { display: none !important; }

    /* 搜尋列併排強制修正 */
    [data-testid="stHorizontalBlock"] { 
        display: flex !important; flex-direction: row !important; align-items: center !important; gap: 10px !important; 
    }

    /* 搜尋輸入框 (加大觸控區) */
    .stTextInput > div > div > input { 
        height: 60px !important; font-size: 22px !important; 
        background: rgba(255,255,255,0.1) !important; color: white !important; border-radius: 15px !important;
    }

    /* 磨砂卡片 */
    .extreme-card {
        background: rgba(44, 44, 46, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 20px;
    }

    /* 標籤文字 (例如：系統、型式) */
    .label-text { color: #8E8E93; font-size: 18px; margin-bottom: 5px; }

    /* --- 極致大字重點 (42px) --- */
    .big-value { 
        font-size: 42px !important; 
        font-weight: 700; 
        color: #FFFFFF; 
        line-height: 1.2;
        word-wrap: break-word;
    }

    .qty-highlight { 
        font-size: 56px !important; 
        color: #0A84FF; 
        font-weight: 800;
        text-align: right;
    }

    /* 完整明細表格字體同步放大 */
    .stDataFrame td, .stDataFrame th {
        font-size: 28px !important;
    }
</style>
"""
st.markdown(macos_extreme_css, unsafe_allow_html=True)

# 3. 功能函式
def handle_clear():
    st.session_state.search_input_widget = ""

# 4. 資料讀取 (強制處理數量格式)
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
st.markdown('<h2 style="text-align:center; color:#8E8E93;">AV 迴路盒查詢</h2>', unsafe_allow_html=True)

if df is not None:
    # 搜尋區
    st.markdown('<div class="extreme-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        user_input = st.text_input("S", placeholder="輸入編號", label_visibility="collapsed", key="search_input_widget").strip()
    with c2:
        st.button("✕", on_click=handle_clear)
    st.markdown('</div>', unsafe_allow_html=True)

    search_query = st.session_state.search_input_widget
    
    if search_query:
        query = search_query.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV"): query = "AV" + query
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            
            # 1. 核心位置卡片 (超大字)
            st.markdown(f"""
            <div class="extreme-card" style="border-left: 8px solid #0A84FF;">
                <div class="label-text">迴路盒位置</div>
                <div class="big-value">{info['迴路盒位置']}</div>
                <div style="height:20px;"></div>
                <div class="label-text">廳別</div>
                <div class="big-value" style="color:#0A84FF;">{str(info['廳別']).split('\\n')[0]}</div>
            </div>
            """, unsafe_allow_html=True)

            # 2. 接口清單 (改用卡片清單達成 42px+)
            if '系統' in match.columns:
                st.markdown("<h3 style='margin-left:10px; color:#8E8E93;'>📦 接口清單</h3>", unsafe_allow_html=True)
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                
                for _, row in summary.iterrows():
                    st.markdown(f"""
                    <div class="extreme-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="flex:1;">
                                <div class="label-text">系統</div>
                                <div class="big-value" style="font-size:36px !important;">{row['系統']}</div>
                                <div style="height:10px;"></div>
                                <div class="label-text">接頭 / 型式</div>
                                <div style="font-size:24px; color:#FFFFFF;">{row['接頭']} ({row['型式']})</div>
                            </div>
                            <div style="width:100px; text-align:right;">
                                <div class="label-text">數量</div>
                                <div class="qty-highlight">{int(row['數量'])}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 3. 詳細明細 (保留表格供參考)
            with st.expander("🔍 完整目的地明細"):
                show_cols = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[show_cols], use_container_width=True, hide_index=True)
        else:
            st.error("查無此編號。")
    else:
        st.markdown('<p style="text-align:center; color:#48484A; font-size:18px;">請輸入編號開始掃描</p>', unsafe_allow_html=True)
else:
    st.error("找不到 Excel 檔案。")
