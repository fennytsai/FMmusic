跳至主要內容
Google Classroom
Classroom
中科推廣部-Python
訊息串
課堂作業
成員
主題篩選器主題篩選器主題篩選器
所有主題
沒有主題
資料
book
AI圖像識別訓練
張貼日期：5月5日
資料
book
功能需求單
張貼日期：4月28日
補充教材
資料
book
24 小時 DC機器人(誰是臥底為例)
comment
1
1 則留言
張貼日期：6月15日
資料
book
任務
comment
1
1 則留言
上次編輯時間：6月9日
資料
book
流星大冒險
張貼日期：6月2日
資料
book
模組化程式-Pygame
張貼日期：6月2日
資料
book
DC 註冊指南
張貼日期：4月28日
練習
資料
book
登入頁製作
張貼日期：4月13日
上課講義
資料
book
全端音樂撥放器
上次編輯時間：晚上8:32
Just a moment...
https://gamma.app/docs/Google--oq0hdh1w5wo9lf5

Just a moment...
https://gamma.app/docs/-oyn3hc5z2e8atn1

main.py
文字

index.html
HTML

requirements.txt
文字

資料
book
OOP(物件拆解AI溝通) 初階運用
張貼日期：6月9日
資料
book
自動偵測與智能提醒by discord
張貼日期：6月2日
資料
book
從雲端 CSV 到 Trello 看板微步建構
張貼日期：5月26日
資料
book
Python Streamlit串聯google csv
張貼日期：5月26日
資料
book
第七週 Streamlit 常見功能API
張貼日期：5月19日
資料
book
第六週
comment
1
1 則留言
張貼日期：5月12日
資料
book
Gemeni
張貼日期：5月5日
資料
book
第四周
上次編輯時間：4月28日
資料
book
第三周
上次編輯時間：4月21日
已展開「全端音樂撥放器」
import os
import json
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import yt_dlp
import pandas as pd
import gspread

app = FastAPI(title="雲端智慧電台")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 💡 定義歌曲的資料結構，解決 422 驗證錯誤
class SongItem(BaseModel):
    title: str
    url: str

# =======================================================
# 🔒 真正的、唯一的 gspread 初始化區塊
# =======================================================
def get_sheet_data():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise ValueError("系統找不到 GOOGLE_CREDENTIALS 環境變數，請檢查 Render 後台設定。")
    
    creds_dict = json.loads(creds_json)
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open("music") 
    worksheet = sh.worksheet("playlists")
    return worksheet

# --- API 1: 取得歌單 ---
@app.get("/api/playlist")
def get_playlist():
    try:
        worksheet = get_sheet_data()
        records = worksheet.get_all_records()
        if not records:
            return []
        
        df = pd.DataFrame(records)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        if 'username' not in df.columns:
            return []
            
        return df[df['username'] == 'admin'].to_dict('records')
    except Exception as e:
        return {"error": f"資料庫連線失敗: {str(e)}"}

# --- API 2: 同步歌單 ---
@app.post("/api/playlist/sync")
def sync_playlist(playlist: List[SongItem]):  # 💡 這裡改用 List[SongItem] 接收
    try:
        worksheet = get_sheet_data()
        try:
            records = worksheet.get_all_records()
            if records:
                df_all = pd.DataFrame(records)
                df_all.columns = [str(c).lower().strip() for c in df_all.columns]
                df_others = df_all[df_all['username'] != 'admin']
            else:
                df_others = pd.DataFrame(columns=['username', 'title', 'url'])
        except:
            df_others = pd.DataFrame(columns=['username', 'title', 'url'])
            
        # 💡 將 Pydantic 模型陣列轉換為 Dict 列表，供 Pandas 讀取
        playlist_dicts = [item.dict() for item in playlist]
        new_data = pd.DataFrame(playlist_dicts)
        
        if not new_data.empty:
            new_data.columns = [str(c).lower().strip() for c in new_data.columns]
            new_data['username'] = 'admin'
            new_data = new_data[['username', 'title', 'url']]
            df_final = pd.concat([df_others, new_data], ignore_index=True)
        else:
            df_final = df_others[['username', 'title', 'url']] if 'username' in df_others.columns else pd.DataFrame(columns=['username', 'title', 'url'])
            
        worksheet.clear()
        worksheet.update([['username', 'title', 'url']] + df_final[['username', 'title', 'url']].values.tolist())
        return {"status": "success"}
    except Exception as e:
        return {"error": f"同步失敗: {str(e)}"}

# --- API 3: 搜尋歌曲 ---
@app.get("/api/search")
def search_songs(q: str = Query(...)):
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'playlistend': 20}) as ydl:
            res = ydl.extract_info(f"ytsearch20:{q}", download=False)
            entries = res.get('entries', [])
            
            cleaned_results = []
            for item in entries:
                url = item.get('url') if item.get('url') else f"https://www.youtube.com/watch?v={item.get('id')}"
                cleaned_results.append({
                    "title": item.get("title", "未知歌曲"),
                    "url": url
                })
            return cleaned_results
    except Exception as e:
        return {"error": f"搜尋失敗: {str(e)}"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
main.py
目前顯示的是「main.py」。
