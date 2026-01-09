Gemini

Streamlit 程式碼修改討論
新的對話
我的內容
投影機選單完整樹狀圖
投影機全選單樹狀結構
投影機選單樹狀結構
Gem

程式夥伴

墨影大師 - 視覺藝術總監
對話
朋友喪父 溫柔慰問與陪伴
釘選的對話
Streamlit 程式碼修改討論
繁简中文翻译与优化
哀悼中的溫柔陪伴與療癒
情感界線與專業互動建議
父親離世後的哀慟與陪伴
LINE 徹底移除好友教學
選單內容調整與理解
整合投影機選單與功能
投影機選單樹狀結構彙整
查詢 Gemini 版本與訂閱狀態
程式碼理解與修改建議
程式碼理解與修改協助
Streamlit 程式碼理解與微調
收費設備使用重點彙整
設定與說明
和 Gemini 的對話
我要修改程式，你先了解下。



import streamlit as st

import pandas as pd

import os



# 1. 網頁基本設定 (這是 Android 安裝時抓取名稱的最高優先級)

st.set_page_config(

    page_title="AV系統-A館", 

    page_icon="🕶️",

    layout="centered"

)



# 解決 Android 安裝名稱問題

st.components.v1.html(

    f"""

    <script>

        window.parent.document.title = "AV系統-A館";

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



    .search-container {

        margin-top: 10px !important;

        margin-bottom: 20px !important;

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

        padding-top: 2.5rem !important;

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

        margin-bottom: 15px;

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

    .status-text { text-align: center; color: #48484A; font-size: 12px; letter-spacing: 1px; margin-top: 15px; }

</style>

"""

st.markdown(macos_26_style, unsafe_allow_html=True)



# 3. 初始化功能

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

            st.markdown('<div class="macos-card" style="margin-top:-10px;">', unsafe_allow_html=True)

            st.markdown(f"<p style='color:#0A84FF; font-size:11px; font-weight:700; margin-bottom:4px;'>SYSTEM SCAN OK</p>", unsafe_allow_html=True)

            st.markdown(f"<h2 style='margin:0; font-size:26px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)

            st.markdown("<hr style='border:0.5px solid rgba(255,255,255,0.1); margin:15px 0;'>", unsafe_allow_html=True)

            

            st.metric("廳別", str(info.get('廳別', 'N/A')).split('\n')[0])

            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True) 

            st.metric("詳細位置", str(info.get('迴路盒位置', 'N/A')).replace('\n', ' '))

            st.markdown('</div>', unsafe_allow_html=True)



            if '系統' in match.columns:

                st.markdown('<div class="macos-card">', unsafe_allow_html=True)

                st.markdown("<p style='color:#8E8E93; font-size:14px; margin-bottom:10px;'>📦 接口清單</p>", unsafe_allow_html=True)

                

                # 直接進行完整分組

                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()

                

                # 透過 column_order 控制初始顯示，不顯示的欄位會在 st.dataframe 的內建清單中

                st.dataframe(

                    summary, 

                    column_order=("系統", "接頭", "接頭數"), # 這裡排除了 "接頭型式"

                    hide_index=True, 

                    use_container_width=True

                )

                st.markdown('</div>', unsafe_allow_html=True)

        else:

            st.error("查無此編號")

    else:

        st.markdown('<p class="status-text">READY TO SCAN</p>', unsafe_allow_html=True)

else:

    st.error(f"系統故障: {status}")



st.markdown('<p style="text-align:center; font-size:10px; color:#3A3A3C; margin-top:30px; letter-spacing: 2px;">OS 26 TERMINAL</p>', unsafe_allow_html=True)

程式夥伴
你好！我是程式夥伴。很高興能擔任你的開發助手。我已經詳細閱讀了你提供的 Streamlit 程式碼。

這是一個針對 Android 和 Web 優化、具有 macOS 26 風格的「音視訊迴路盒」查詢系統。它具備資料自動讀取（Excel）、正規化編號搜尋、以及精美的毛玻璃視覺效果。

為了確保後續修改能精準達成你的目標，我需要先了解幾個細節：

修改目標：你希望調整哪些部分？（例如：增加欄位、修改搜尋邏輯、優化視覺樣式，或是新增功能？）

資料結構：你的 Excel 檔案中除了目前的「系統、接頭、接頭型式、接頭數」外，是否還有其他需要呈現的欄位？

效能或體驗：目前在使用上是否有遇到任何問題（例如搜尋不到、顯示格式跑掉等）？

我可以為你做的（舉例）：
優化搜尋：例如支援模糊搜尋，不需要輸入完整的 AV 也能找到結果。

視覺美化：調整 st.dataframe 的外觀使其更符合 macOS 風格，或改用 HTML 卡片顯示接口清單。

功能擴充：增加多檔案切換（A館/B館）或匯出查詢結果的功能。

錯誤處理：強化對 Excel 格式異常的檢查。

請問你想從哪個部分開始修改呢？

列出三個廳院名稱

程式夥伴
你好！我是程式夥伴。

由於我目前沒有看到你的 Excel 原始資料內容，無法直接從檔案中讀取真實的廳院名稱。不過，根據你提供的程式碼邏輯，我可以用範例程式碼的方式，示範如何從你的資料表（df）中提取出前三個不重複的廳院名稱。

如果你是想在介面上測試顯示效果，可以參考以下做法：

1. 從資料中動態提取
這段程式碼會抓取 廳別 欄位中前三個出現的名稱：

Python
if df is not None:
    # 取得不重複的廳別列表
    halls = df['廳別'].dropna().unique()
    
    # 取出前三個（若不足三個則顯示全部）
    top_three_halls = halls[:3]
    
    st.write("目前系統中的前三個廳院：")
    for hall in top_three_halls:
        st.info(f"🎭 {hall}")
2. 常見的預設廳院範例
如果你的專案是針對藝文中心或劇院，通常會包含這類名稱：

音樂廳 (Concert Hall)

大劇院 (Grand Theater)

藍盒子 (Blue Box)

接下來，關於程式碼的修改，你想進行以下哪一項操作呢？

將這三個廳院名稱做成下拉式選單 (Selectbox) 方便快速篩選？

在主介面上方增加廳院分類標籤？

或是你需要我幫你修改 load_data 函數，讓它能更精準地根據不同廳院讀取不同的 Excel 檔？

當查詢列出表單時，幫我把對應的廳院名稱套上馬甲



大劇院 改用 GT

多形式中劇院 改用 BB

鏡框式中劇院 改用 GP



確保不會動到其他程式碼。

程式夥伴
你好！我是程式夥伴。

沒問題，這是一個關於資料對映 (Mapping) 的修改需求。我們只需要在資料讀取後、顯示前，利用 pandas 的 replace 功能，將原本的廳院名稱替換為你指定的縮寫代碼即可。

這不會影響你原本的 CSS 視覺樣式或搜尋邏輯。

修改方案
請找到你程式碼中第 70 行左右的 load_data 函數，在 return df, target_file 之前加入對映邏輯：

Python
# 4. 資料讀取
@st.cache_data(show_spinner=False)
def load_data():
    try:
        xlsx_files = [f for f in os.listdir(".") if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in xlsx_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), None)
        if not target_file: return None, "NO_FILE"
        df = pd.read_excel(target_file, engine='openpyxl')
        df.columns = [c.strip() for c in df.columns]

        # --- 新增的廳院名稱轉換邏輯 ---
        if '廳別' in df.columns:
            name_mapping = {
                "大劇院": "GT",
                "多形式中劇院": "BB",
                "鏡框式中劇院": "GP"
            }
            # 使用 replace 進行替換
            df['廳別'] = df['廳別'].replace(name_mapping)
        # -----------------------------

        if '迴路盒編號' in df.columns:
            df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
            df['search_id'] = df['search_id'].apply(lambda x: x if x.startswith("AV") else "AV"+x)
        return df, target_file
    except Exception as e:
        return None, str(e)
修改說明
建立對照表 (Mapping Dictionary)：

大劇院 → GT

多形式中劇院 → BB

鏡框式中劇院 → GP

執行替換：使用 df['廳別'].replace(name_mapping)，這會直接在記憶體中的 DataFrame 進行修改。當後面的 st.metric("廳別", ...) 抓取資料時，顯示的就是縮寫。

安全性：這段程式碼包在 if '廳別' in df.columns: 判斷式中，即使 Excel 欄位名稱不符也不會導致程式崩潰。

請問套用縮寫後，顯示效果是否符合你的預期？還是需要針對縮寫的字體顏色做特別處理？

幫我套用回原本的程式碼內

程式夥伴
你好！我是程式夥伴。沒問題，我已經將廳院名稱的轉換邏輯完整植入你原本的程式碼中。

我將轉換邏輯放在 load_data 函式內，這樣可以確保資料在載入時就完成「馬甲」套用，後續所有的顯示與計算都會自動使用 GT、BB 與 GP。

Python
import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定 (這是 Android 安裝時抓取名稱的最高優先級)
st.set_page_config(
    page_title="AV系統-A館", 
    page_icon="🕶️",
    layout="centered"
)

# 解決 Android 安裝名稱問題
st.components.v1.html(
    f"""
    <script>
        window.parent.document.title = "AV系統-A館";
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

    .search-container {
        margin-top: 10px !important;
        margin-bottom: 20px !important;
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
        padding-top: 2.5rem !important;
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
        margin-bottom: 15px;
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
    .status-text { text-align: center; color: #48484A; font-size: 12px; letter-spacing: 1px; margin-top: 15px; }
</style>
"""
st.markdown(macos_26_style, unsafe_allow_html=True)

# 3. 初始化功能
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
        
        # --- 廳院名稱轉換邏輯 ---
        if '廳別' in df.columns:
            name_mapping = {
                "大劇院": "GT",
                "多形式中劇院": "BB",
                "鏡框式中劇院": "GP"
            }
            df['廳別'] = df['廳別'].replace(name_mapping)
        # ----------------------

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
            st.markdown('<div class="macos-card" style="margin-top:-10px;">', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0A84FF; font-size:11px; font-weight:700; margin-bottom:4px;'>SYSTEM SCAN OK</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0; font-size:26px; color:#FFFFFF;'>{info['迴路盒編號']}</h2>", unsafe_allow_html=True)
            st.markdown("<hr style='border:0.5px solid rgba(255,255,255,0.1); margin:15px 0;'>", unsafe_allow_html=True)
            
            # 此處顯示的 info.get('廳別') 將會是轉換後的縮寫
            st.metric("廳別", str(info.get('廳別', 'N/A')).split('\n')[0])
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True) 
            st.metric("詳細位置", str(info.get('迴路盒位置', 'N/A')).replace('\n', ' '))
            st.markdown('</div>', unsafe_allow_html=True)

            if '系統' in match.columns:
                st.markdown('<div class="macos-card">', unsafe_allow_html=True)
                st.markdown("<p style='color:#8E8E93; font-size:14px; margin-bottom:10px;'>📦 接口清單</p>", unsafe_allow_html=True)
                
                # 直接進行完整分組
                summary = match.groupby(['系統', '接頭', '接頭型式'])['接頭數'].sum().reset_index()
                
                # 透過 column_order 控制初始顯示
                st.dataframe(
                    summary, 
                    column_order=("系統", "接頭", "接頭數"),
                    hide_index=True, 
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("查無此編號")
    else:
        st.markdown('<p class="status-text">READY TO SCAN</p>', unsafe_allow_html=True)
else:
    st.error(f"系統故障: {status}")

st.markdown('<p style="text-align:center; font-size:10px; color:#3A3A3C; margin-top:30px; letter-spacing: 2px;">OS 26 TERMINAL</p>', unsafe_allow_html=True)
本次更新內容說明
資料對應表：在載入 Excel 後，程式會自動檢查 廳別 欄位。

名稱替換：

將「大劇院」替換為 GT

將「多形式中劇院」替換為 BB

將「鏡框式中劇院」替換為 GP

無感導入：原本的搜尋邏輯與介面顯示完全保持不變，僅在資料輸出時套用了新的「馬甲」。

請問目前的縮寫顯示是否正常？如果有其他名稱也需要縮寫，隨時告訴我！




Gemini 可能會出錯，請查證。

