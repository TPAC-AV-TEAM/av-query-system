import streamlit as st
import pandas as pd

# 網頁基本設定
st.set_page_config(
    page_title="AV 迴路盒查詢系統",
    page_icon="🔍",
    layout="wide"
)

# 套用自定義 CSS 提升質感
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 定義讀取資料的函數
@st.cache_data
def load_data():
    # 修改處：將檔名改為您的 .xlsx 檔名
    # 注意：此處檔名必須與您上傳到 GitHub 的檔案名稱完全一致
    file_path = "Cable list 20201109.xlsx"
    try:
        # 修改處：使用 read_excel 並指定引擎為 openpyxl
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # 資料預處理：建立搜尋用 ID (大寫、去空格、去橫線)
        df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(' ', '').str.replace('-', '')
        return df
    except Exception as e:
        st.error(f"⚠️ 環境檢查失敗：無法讀取 Excel 檔案。請確認 GitHub 中是否有檔案：\n`{file_path}`\n錯誤訊息: {e}")
        return None

# 執行讀取資料
df = load_data()

# 標題區
st.title("📟 音視訊迴路盒快速查詢系統")
st.markdown("---")

if df is not None:
    # 建立搜尋列
    st.subheader("請輸入迴路盒編號")
    user_input = st.text_input("搜尋範例：04-01 或 AV 04-01", placeholder="請在此輸入...")

    if user_input:
        # 處理使用者輸入
        query = user_input.upper().replace(' ', '').replace('-', '')
        if not query.startswith("AV") and query:
            query = "AV" + query

        # 在資料中比對
        match = df[df['search_id'] == query]

        if not match.empty:
            info = match.iloc[0]
            
            # 顯示主要位置資訊
            col1, col2 = st.columns(2)
            with col1:
                theater = str(info['廳別']).split('\n')[0]
                st.metric("所屬廳別", theater)
            with col2:
                location = str(info['迴路盒位置']).replace('\n', ' ')
                st.metric("位置詳細", location)

            st.markdown("---")
            
            # 顯示接口統計
            st.subheader("📦 接口數量匯總")
            summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
            summary.columns = ['系統類型', '接頭型號', '安裝/型式', '總數量']
            st.table(summary)

            # 詳細線路
            with st.expander("🔍 查看詳細線路目的地"):
                detailed = match[['迴路標示號碼', '線材', '目的地樓層', '機房名稱', '機櫃', '點位']].copy()
                st.dataframe(detailed, use_container_width=True)
        else:
            st.warning(f"找不到編號「{user_input}」，請檢查輸入是否正確。")
    else:
        st.info("💡 提示：輸入 4F 的編號（如 04-01）可快速查看現場設備狀況。")

# 頁尾資訊
st.markdown("---")
st.caption("環境狀態：已連線至 GitHub Excel 資料庫 | 系統版本：v1.2")
