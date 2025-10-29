# Exam Practice Agent

Exam Practice Agent 是我為考古題練習網站打造的 LangGraph 型智能助理原型，聚焦「如何用結構化狀態與節點協作」快速串起解題、檢索與學習分析。這份專案把核心概念拆成模組化元件：從路由判斷、RAG 流程到個人化回饋，每個步驟都保留可延伸的掛點，方便部署在真實服務或在面試時展示系統設計思維。

如果你想了解一個具備問題分類、動態檢索、練習題生成與報告匯整的 AI 助理是如何被串起來的，往下看就能看到完整狀態模型、節點責任與測試策略。

---

## 系統架構

```
.
├── main.py
├── langgraph_structure.png
└── exam_practice_agent
    ├── __init__.py
    ├── graph.py
    ├── routing.py
    ├── state.py
    ├── llm.py
    ├── prompts/
    └── nodes/
```

- graph.py 定義 LangGraph 節點與邊
- routing.py 將模型決策轉換為圖中的節點路徑
- state.py 描述狀態欄位與型別，確保節點間資料契約一致
- nodes/ 包含初始化、解題、檢索、測驗、報告等節點實作
- prompts/ 儲存 Router 與內部知識提示詞，可依需求調整

---

## State

`state.py` 定義 `ConversationState` 作為節點間共享的資料契約，確保 LangGraph 流程有一致的輸入輸出。初始化節點 `initialize_state` 建立這份狀態，後續節點皆針對特定欄位讀寫，避免隱性耦合。

| 欄位 | 說明 |
| --- | --- |
| `history` | 當前 thread 的用戶問答與 agent 回應歷史紀錄，供節點追溯上下文。 |
| `user_message` | 本輪客戶問題原文。 |
| `current_question` | 客戶選定的題目標題或題號，與評測節點共用。 |
| `problem_solver_model` | 本輪解題所選用的模型標籤。 |
| `model_think` | 模型對當前題目的推理與暫定回答。 |
| `model_think_confidence` | 模型對 `model_think` 的信心度（0-10）。 |
| `retrieved_context` | 檢索補充資料的累積結果，供回答或分析節點引用。 |
| `current_route` | 路由決策選擇的下一個節點或流程路徑。 |
---

## 核心流程

1. 初始化與路由  
   `initialize_state` 整理輸入並產生狀態快照，`routing.task_router` 依 ROUTER_PROMPT 規則給出 `reasoning` 與 `next_state`，確保先用模型內部知識評估能否回答，再決定是否需要額外檢索。

2. Problem Solving 流程  
   `model_internal_solver` 先以模型內部知識推導答案並評估信心，若信心不足才由 `retrieval_orchestrator` 啟動 RAG 檢索補強，確保檢索只在必要時進行。

3. Direct Answer 回覆  
   當 ROUTER_PROMPT 判定 `direct_answer` 時，`solution_responder` 直接整理可用資訊快速作答，避免額外迴圈以降低延遲。

4. Analyze 與 Quiz 任務  
   只有當使用者請求與錯誤分析或練習題相關功能，節點才會連結 user database 取得資料：`history_insights`/`report_compiler` 生成分析報告，`quiz_generator` 建立題目 session 並交由 `quiz_insights` 紀錄表現。

5. Unknown 防護  
   遇到與題目無關或疑似 Prompt Attack 的訊息，路由會輸出 `unknow`，由固定模板回覆並避免將內容注入模型內部流程。

---

## 節點職責

| 節點 | 檔案 | 功能摘要 |
| --- | --- | --- |
| `initialize_state` | `nodes/initialize_state_node.py` | 重置暫存欄位並依 ROUTER_PROMPT 決定下一步 |
| `model_internal_solver` | `nodes/model_internal_solver_node.py` | 產出內部解題推理、信心與建議檢索詞 |
| `solution_responder` | `nodes/solution_responder_node.py` | 整合內部解答並判斷是否需檢索 |
| `answer_retrieval_orchestrator` | `nodes/answer_retrieval_orchestrator_node.py` | 在低信心時管理題目檢索流程 |
| `profile_retrieval_orchestrator` | `nodes/profile_retrieval_orchestrator_node.py` | 連結 database 取得使用者,題目資料 |
| `quiz_generator` | `nodes/quiz_generator_node.py` | 建立練習題目 session |
| `report_generator` | `nodes/report_generator_node.py` | 根據 使用者答題資訊 結果生成報告 |
| `fallback_handler` | `nodes/fallback_handler_node.py` | 以固定模板回覆 unknow 並阻擋攻擊 |

---

### 未來測試構想
- 針對現有路由與節點流程進行單元測試，確保狀態更新與邏輯判斷符合預期。
- 利用 LangGraph runtime 模擬多種任務場景，檢視狀態欄位與輸出是否正確。
- 針對檢索結果建立相似度排序流程，依使用者問題計算 embedding 分數並只保留最相關片段，降低資訊爆炸風險。
- 為題目檢索的 RAG 建立離線驗證資料集，量測招回率、正確率與錯誤類型，作為 retriever 或 prompt 調整的準則。
- 進行 prompt 攻擊與越權測試，驗證 initialize_state 與 fallback_handler 能阻擋惡意輸入並保護關鍵狀態。
- 面試加分方向：加入自動化評分報告（延伸 RAG 指標）、建立節點延遲與成本儀表板、針對個人化建議設計 A/B 測試腳本。

---

## 授權

專案採用 [MIT License](LICENSE)。
