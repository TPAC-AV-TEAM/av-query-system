import streamlit as st
import pandas as pd
import os

# 網頁基本設定
st.set_page_config(
    page_title="AV 迴路盒查詢系統",
    page_icon="🔍",
    layout="wide"
)

# 套用自定義 CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 定義讀取資料的函數
@st.cache_data
def load_data():
    # 預設檔名
    default_file = "Cable list  音視訊 20201109.xlsx"
    
    # 獲取目前目錄下的所有檔案
    all_files = os.listdir(".")
    xlsx_files = [f for f in all_files if f.endswith('.xlsx')]
    
    target_file = None

    # 1. 先嘗試精確匹配
    if default_file in all_files:
        target_file = default_file
    # 2. 如果失敗，嘗試尋找包含關鍵字的任何 xlsx 檔案
    elif xlsx_files:
        for f in xlsx_files:
            if "Cable" in f or "音視訊" in f:
                target_file = f
                break
        # 3. 如果還是沒找到，就抓第一個 xlsx 檔案
        if not target_file:
            target_file = xlsx_files[0]

    if not target_file:
        st.error("⚠️ 找不到任何 Excel (.xlsx) 檔案！")
        st.write("📊 **目前資料夾內容：**", all_files)
        return None

    try:
        # 讀取 Excel
        df = pd.read_excel(target_file, engine='openpyxl')
        
        # 檢查是否有「迴路盒編號」這一欄
        if '迴路盒編號' not in df.columns:
            st.error(f"❌ 檔案 `{target_file}` 格式不符：找不到「迴路盒編號」欄位。")
            return None

        # 資料預處理
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(' ', '').str.replace('-', '')
        st.sidebar.success(f"✅ 已成功讀取：{target_file}")
        return df
    except Exception as e:
        st.error(f"❌ 讀取失敗：{target_file}")
        st.write(f"錯誤訊息: {e}")
        return None

# 執行讀取資料
df = load_data()

# 標題區
st.title("📟 音視訊迴路盒快速查詢系統")
st.markdown("---")

if df is not None:
    st.subheader("請輸入迴路盒編號")
    user_input = st.text_input("例如：04-01 或 AV 04-01", placeholder="請在此輸入...")

    if user_input:
        query = user_input.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV") and query:
            query = "AV" + query

        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                theater = str(info['廳別']).split('\n')[0]
                st.metric("所屬廳別", theater)
            with col2:
                location = str(info['迴路盒位置']).replace('\n', ' ')
                st.metric("位置詳細", location)

            st.markdown("---")
            st.subheader("📦 接口數量匯總")
            
            # 過濾掉欄位全空或不正確的資料後進行加總
            if '系統' in match.columns and '接頭' in match.columns:
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                summary.columns = ['系統類型', '接頭型號', '安裝/型式', '總數量']
                st.table(summary)

            with st.expander("🔍 查看詳細線路目的地"):
                # 選擇存在的欄位顯示
                cols_to_show = [c for c in ['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位'] if c in match.columns]
                st.dataframe(match[cols_to_show], use_container_width=True)
        else:
            st.warning(f"找不到編號「{user_input}」，請檢查輸入是否正確。")
    else:
        st.info("💡 提示：輸入 4F 的編號（如 04-01）可快速查看現場設備狀況。")

st.markdown("---")
st.caption("環境狀態：已自動識別 Excel 資料庫 | 系統版本：v1.4 (自動適應檔名版)")
