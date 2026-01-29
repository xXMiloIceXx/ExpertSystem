# 部署檢查清單 (Deployment Checklist)

## ✅ 系統準備完成

### 📦 文件狀態
- [x] `streamlit_app.py` - 升級至v2.0，包含所有新功能
- [x] `rules.clp` - CLIPS規則引擎（無修改，相容舊版）
- [x] `case_library.txt` - 替換為20個高質量驗證案例
- [x] `requirements.txt` - 更新版本控制
- [x] `IMPLEMENTATION_SUMMARY.md` - 完整技術文檔
- [x] `DEPLOYMENT_CHECKLIST.md` - 本文檔

### 🔧 核心功能驗證
- [x] **數據標準化**: 所有症狀值已轉換為kebab-case
- [x] **多重診斷**: 可從env.facts()提取ALL診斷，非僅最高分
- [x] **Alternative展現**: Step 6新增主備選診斷層級顯示
- [x] **語義聚合**: 新增`cluster_cbr_solutions()`函數
- [x] **垃圾過濾**: `update_case_feedback()`加入3層過濾
- [x] **案例庫**: 20個驗證案例涵蓋主要故障類型

### 📋 部署前準備

#### 1. 本地測試（開發環境）
```bash
# 進入項目目錄
cd c:\laragon\www\ExpertSystem

# 安裝依賴
pip install -r requirements.txt

# 首次使用需下載Spacy模型
python -m spacy download en_core_web_md

# 運行應用
streamlit run streamlit_app.py

# 訪問Web UI
# http://localhost:8501
```

#### 2. 功能測試清單
- [ ] Step 1-5: 所有UI選項返回kebab-case特徵
- [ ] Step 6: 顯示Primary Recommendation（最高分）
- [ ] Step 6: 顯示Alternative Diagnoses（2-5個備選）
- [ ] 反饋機制: 👍/👎按鈕正常工作
- [ ] 案例提交: 新案例保存到case_library.txt
- [ ] NLP功能: Spacy模型已加載，語義相似度工作正常
- [ ] 垃圾過濾: 嘗試提交低質量內容，應被阻止

#### 3. 性能檢查
- [ ] CBR搜索速度: <1秒（20個案例）
- [ ] NLP推理速度: <2秒（語義相似度計算）
- [ ] UI響應: 無明顯卡頓

---

## 🚀 部署選項

### 選項A: Streamlit Cloud (推薦快速部署)
```bash
# 1. 將代碼推送到GitHub
git add .
git commit -m "v2.0: Expert Intuition & Alternatives"
git push origin main

# 2. 在 https://streamlit.io/cloud 連接GitHub
# 3. 選擇repo和main.py文件
# 4. 配置secrets（如果有API keys）
# 5. Deploy！
```
**優點**: 無需管理服務器，自動HTTPS，零配置  
**缺點**: 免費層有資源限制

### 選項B: Docker (推薦生產部署)
```bash
# 1. 創建Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && \
    python -m spacy download en_core_web_md
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]

# 2. 構建鏡像
docker build -t expert-system:v2.0 .

# 3. 運行容器
docker run -p 8501:8501 expert-system:v2.0
```
**優點**: 環境一致，易於部署，支持水平擴展  
**缺點**: 需要Docker知識

### 選項C: Hugging Face Spaces (免費GPU支持)
```bash
# 1. 在Hugging Face創建新Space
# 2. 選擇Streamlit模板
# 3. 上傳代碼
# 4. 自動部署
```
**優點**: 免費，無需配置，支持ML模型  
**缺點**: 社區公開

### 選項D: 企業內部部署 (Laragon/本地)
```bash
# 當前環境已支持，無需額外配置
# 定期啟動: streamlit run streamlit_app.py
# 或配置Windows任務計劃自動啟動
```
**優點**: 完全控制，數據隱私  
**缺點**: 需要自我管理基礎設施

---

## 📈 部署後監控

### 日誌收集
```python
# streamlit_app.py 頂部添加日誌
import logging
logging.basicConfig(
    filename='expert_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### 關鍵指標
1. **系統可用性**: 檢查應用是否每天正常運行
2. **診斷準確度**: 監控用戶反饋分數（👍 vs 👎 比例）
3. **案例學習**: 追蹤新提交案例和自動晉升數
4. **NLP性能**: 記錄語義相似度計算時間

### 定期維護
- **周**: 檢查case_library.txt大小，清理低分案例
- **月**: 分析診斷準確率，更新rules.clp
- **季**: 重訓練NLP模型，評估Alternative展現方式

---

## 🔐 安全建議

### 生產環境
- [ ] 啟用HTTPS (TLS/SSL)
- [ ] 添加身份驗證 (如OAuth)
- [ ] 實施速率限制 (防止濫用)
- [ ] 數據備份 (case_library.txt)
- [ ] 定期更新依賴包

### 敏感數據
- [ ] case_library.txt: 存儲在安全位置，定期備份
- [ ] 用戶反饋: 不記錄個人信息
- [ ] 日誌文件: 加密存儲

---

## 🎯 關鍵新增功能驗證

### ✨ Feature 1: 數據標準化
**測試方法**:
1. 運行Step 1，選擇"Lines, black blocks, or artifacts"
2. 檢查控制台是否記錄 `screen-visuals:lines-artifacts`
3. 確認特徵格式為kebab-case，無空格

### ✨ Feature 2: Alternative Diagnoses
**測試方法**:
1. 完成Step 1-5診斷
2. 進入Step 6，點擊"🚀 Run Diagnosis"
3. 應看到:
   - 🎯 Primary Recommendation (1個)
   - 📋 Alternative Diagnoses (2-5個，按CF遞減)
4. 點擊展開Alternative，查看詳情

### ✨ Feature 3: 垃圾過濾
**測試方法**:
1. 進入Step 6的知識獲取
2. 嘗試提交: "hello world"
3. 應被阻止，顯示: "Solution too brief (minimum 10 characters required)"
4. 嘗試提交與診斷無關的內容（低NLP相似度）
5. 應被阻止，顯示: "Solution marked as irrelevant (low semantic match)"

### ✨ Feature 4: 自動晉升
**測試方法**:
1. 提交一個高質量案例
2. 多次點擊"👍 Helpful"
3. 當分數達到100點時，自動晉升至VERIFIED
4. 查看case_library.txt，確認STATUS從PENDING改為VERIFIED

---

## 📞 故障排除

### 問題: Spacy模型未加載
```
⚠️ Spacy not installed. Install with: pip install spacy
```
**解決方案**:
```bash
pip install spacy
python -m spacy download en_core_web_md
```

### 問題: CLIPS規則引擎錯誤
```
⚠️ Error loading rules.clp: ...
```
**解決方案**:
1. 檢查rules.clp語法
2. 驗證CLIPS依賴: `pip install clipspy --upgrade`
3. 查看詳細錯誤信息

### 問題: Case Library損壞
```
ValueError: Case parsing error
```
**解決方案**:
1. 備份 case_library.txt
2. 重新格式化: `CASE-ID | STATUS | features | solution | score`
3. 確保特徵是kebab-case格式

---

## 📊 版本控制

### Git工作流
```bash
# 創建部署分支
git checkout -b release/v2.0

# 完成測試後合併
git checkout main
git merge release/v2.0

# 標記版本
git tag -a v2.0 -m "Expert Intuition & Alternatives"
git push origin main --tags
```

---

## ✅ 最終檢查清單

部署前必須確認:

- [ ] 所有依賴已安裝 (`pip list | grep -E "streamlit|clipspy|spacy|pandas"`)
- [ ] Spacy模型已下載 (`python -c "import spacy; spacy.load('en_core_web_md')"`)
- [ ] 案例庫已更新 (20+ VERIFIED cases)
- [ ] requirements.txt版本明確
- [ ] 日誌機制配置完成
- [ ] 備份策略就位
- [ ] 安全設置審查完畢
- [ ] 用戶文檔已更新

---

## 🎉 部署成功標志

當您看到以下輸出時，系統已成功部署:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501

  For better support & bug reporting, please install our analytics library:
  pip install streamlit-analytics

  Ready to accept expert-level diagnostic requests! 🧠
```

---

**部署日期**: ________________  
**部署環境**: ________________  
**部署人員**: ________________  
**驗證狀態**: [ ] 通過 [ ] 需改進

**簽名**: ________________  
**備註**: ________________________________________

