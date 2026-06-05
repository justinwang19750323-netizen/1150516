"""
title: Example Filter
author: open-webui
author_url: https://github.com/open-webui
funding_url: https://github.com/open-webui
version: 0.1
"""
# 這是一個 Open WebUI 的「過濾器（Filter）」範例
# 過濾器可以在訊息送出前（inlet）和收到回應後（outlet）進行處理
# 常見用途：限制對話輪數、過濾敏感詞、記錄日誌等

from pydantic import BaseModel, Field  # 用於定義資料模型和欄位設定
from typing import Optional            # 用於標示可選型別（可以是 None）


class Filter:
    """
    Filter 主類別
    Open WebUI 載入這個檔案時，會自動識別這個類別作為過濾器
    """

    class Valves(BaseModel):
        """
        管理員層級的設定（全域設定）
        管理員可以在 Open WebUI 後台調整這些參數
        """
        priority: int = Field(
            default=0,
            description="過濾器執行的優先順序，數字越小越先執行"
        )
        max_turns: int = Field(
            default=8,
            description="整個系統允許的最大對話輪數（管理員設定的上限）"
        )
        pass

    class UserValves(BaseModel):
        """
        使用者層級的設定（個人設定）
        每個使用者可以自行調整，但不能超過管理員設定的上限
        """
        max_turns: int = Field(
            default=4,
            description="單一使用者允許的最大對話輪數（預設 4 輪）"
        )
        pass

    def __init__(self):
        """
        初始化過濾器
        建立 Filter 物件時自動執行
        """
        # 注意：file_handler 功能目前被註解掉
        # 如果啟用（self.file_handler = True），可以自訂檔案處理邏輯
        # 預設由 Open WebUI 處理檔案上傳
        # self.file_handler = True

        # 使用 Valves 類別建立設定物件，套用預設值
        self.valves = self.Valves()
        pass

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        前置處理器（Pre-processor）
        每次使用者送出訊息時，在送到 AI 模型之前先執行這個函式
        
        參數：
            body: 請求內容，包含對話紀錄等資訊
            __user__: 目前使用者的資訊（角色、設定等）
        
        回傳：
            修改後的 body，會繼續傳給 AI 模型
        """
        # 印出除錯資訊，方便開發時追蹤
        print(f"inlet:{__name__}")         # 印出模組名稱
        print(f"inlet:body:{body}")        # 印出請求內容
        print(f"inlet:user:{__user__}")    # 印出使用者資訊

        # 檢查使用者角色是否為 "user" 或 "admin"
        if __user__.get("role", "admin") in ["user", "admin"]:
            
            # 取得目前的對話紀錄列表
            messages = body.get("messages", [])

            # 計算實際允許的最大輪數：取使用者設定和管理員設定的較小值
            # 例如：使用者設定 4，管理員設定 8 → 實際上限為 4
            max_turns = min(__user__["valves"].max_turns, self.valves.max_turns)

            # 如果對話輪數超過上限，拋出例外錯誤，終止這次請求
            if len(messages) > max_turns:
                raise Exception(
                    f"已超過對話輪數限制。最大輪數：{max_turns}"
                )

        # 回傳（可能已修改的）請求內容
        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        後置處理器（Post-processor）
        每次 AI 模型回應後，在顯示給使用者之前先執行這個函式
        
        參數：
            body: 回應內容，包含 AI 的回答
            __user__: 目前使用者的資訊
        
        回傳：
            修改後的 body，會顯示給使用者
        """
        # 印出除錯資訊
        print(f"outlet:{__name__}")        # 印出模組名稱
        print(f"outlet:body:{body}")       # 印出回應內容
        print(f"outlet:user:{__user__}")   # 印出使用者資訊

        # 目前直接回傳原始回應，沒有做任何修改
        # 可以在這裡加入：過濾敏感詞、記錄日誌、統計 token 數等功能
        return body
