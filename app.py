@st.cache_data(show_spinner=False)
def load_data():
    try:
        xlsx_files = [f for f in os.listdir(".") if f.endswith('.xlsx') and not f.startswith('~$')]
        target_file = next((f for f in xlsx_files if any(k in f for k in ["Cable", "音視訊", "迴路盒"])), None)
        if not target_file: return None, "NO_FILE"
        
        df = pd.read_excel(target_file, engine='openpyxl')
        df.columns = [c.strip() for c in df.columns]

        # --- 強化的廳別名稱轉換邏輯 ---
        if '廳別' in df.columns:
            # 先將欄位轉為字串並移除換行符號
            df['廳別'] = df['廳別'].astype(str).str.replace('\n', '', regex=True).str.strip()
            
            # 定義轉換函式 (使用關鍵字比對)
            def transform_venue(name):
                if "大劇院" in name:
                    return "GT"
                elif "多形式" in name or "中劇院" in name and "多形式" in name:
                    return "BB"
                elif "鏡框式" in name:
                    return "GP"
                return name # 若都不符合則回傳原名

            df['廳別'] = df['廳別'].apply(transform_venue)

        # --- 搜尋 ID 處理 ---
        if '迴路盒編號' in df.columns:
            df['search_id'] = df['迴路盒編號'].astype(str).str.upper().str.replace(r'[\s-]', '', regex=True)
            df['search_id'] = df['search_id'].apply(lambda x: x if x.startswith("AV") else "AV"+x)
            
        return df, target_file
    except Exception as e:
        return None, str(e)
