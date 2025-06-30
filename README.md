# Taipei Day Trip - 台北一日遊旅遊電商網站

[![Demo](https://img.shields.io/badge/Demo-Live-brightgreen?style=flat-square)](https://taipei-day-trip.ayating.lol/)

**線上體驗 Demo:** [https://taipei-day-trip.ayating.lol/](https://taipei-day-trip.ayating.lol/)

## 專案簡介

Taipei Day Trip 是一個為計畫前往台北的旅客所設計的旅遊景點電商網站。使用者可以輕鬆瀏覽豐富的台北景點、查詢相關資訊，並直接完成線上預約與付款。

## 我的角色

此專案由本人獨立開發，我負責了從 **前端互動、後端邏輯、資料庫設計到雲端部署與自動化維運** 的完整開發流程。

## 功能特色

- **🗺️ 互動式景點探索：**

  - **無限滾動載入：** 採用 `IntersectionObserver` API 實現，當使用者滾動至頁面底部時自動載入更多景點，提供無間斷的瀏覽體驗。
  - **多維度搜尋：** 支援依景點名稱或捷運站名的關鍵字模糊搜尋，並提供捷運站快選列表，讓使用者能快速篩選、定位目標。

- **🔐 無狀態會員認證：**

  - **JWT 安全認證：** 使用者登入後，後端簽發具時效性的 JWT。前端將其儲存於 `localStorage`，並透過 `Authorization` 標頭實現無狀態 (Stateless) 的 API 安全請求。
  - **動態 UI 與路由保護：** 導覽列會根據登入狀態動態顯示「登入/註冊」或「登出系統」。未登入用戶若嘗試預約，會畫面會自動跳出登入視窗。

- **📅 端到端預約流程：**

  - **行程預訂與管理：** 使用者可在景點頁選擇日期、時間，並將行程加入待預訂清單，且可隨時在預定頁面查看或刪除待預訂的行程。
  - **TapPay 金流整合：** 串接 TapPay 金流服務。前端透過其 SDK 將信用卡資訊轉換為安全的 `prime` 金鑰，再交由後端完成扣款，信用卡資訊由 TapPay SDK 直接處理，不經過我方伺服器，保障交易安全。

- **📱 跨裝置響應式設計 (RWD)：**
  - 確保網站在桌機、平板、手機等不同尺寸的裝置上，皆能維持最佳的版面配置與操作體驗。

## 技術棧

- **後端 (Backend):**

  - Python 3 ＋ FastAPI
  - PyJWT
  - bcrypt
  - AWS RDS for MySQL
  - `mysql-connector-python`

- **前端 (Frontend):**

  - JavaScript (ES6+ Modules, Async/Await)
  - HTML5
  - CSS3
  - `Fetch API`
  - `IntersectionObserver API`

- **部署與維運 (Deployment & DevOps):**

  - Docker
  - AWS EC2
  - GitHub Actions (CI/CD)
  - nginx

- **第三方服務 (3rd-Party Services):**
  - **支付：** TapPay

## 架構概觀

本專案採用經典的前後端分離架構，並整合雲端服務與自動化流程，各部分職責分明：

1.  **應用程式與部署：**

    - 應用的核心 **FastAPI** 提供了所有業務邏輯的 RESTful API，並連接 **AWS RDS** 資料庫進行資料操作。
    - 整個應用（前後端）被封裝在一個 **Docker** 容器內，部署於 **AWS EC2** 實例上，確保了環境的穩定與可移植性。

2.  **支付流程 (Payment Flow)：**

    - 使用者在前端輸入信用卡資訊，**TapPay SDK** 將其轉換為安全的 `prime`。
    - 前端將 `prime` 與訂單資訊傳送至後端 API。
    - 後端伺服器再將 `prime` 發送至 TapPay 伺服器完成實際扣款，並根據回傳結果更新訂單狀態。

3.  **自動化維運 (CI/CD)：**
    - 開發者將程式碼推送到 GitHub。
    - **GitHub Actions** 偵測到變更，觸發預設的工作流程。
    - 安裝在 EC2 上的 **Self-hosted Runner** 會主動向 GitHub 請求並接收這個指派給它的工作
    - Runner 在接收到指令後， 便在 EC2 本機上執行自動化腳本，完成拉取程式碼、建置新映像檔、重啟容器等一系列部署動作，實現無縫更新。
