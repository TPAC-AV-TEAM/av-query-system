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
