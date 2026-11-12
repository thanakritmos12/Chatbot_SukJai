"""
แอปพลิเคชันหลักของ LINE Chatbot คัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง
รองรับ:
1. POST /callback - Webhook สำหรับเชื่อมต่อกับ LINE Messaging API
2. GET  /         - หน้าเว็บจำลองการแชต (Simulator) และตารางดูข้อมูลผู้ป่วยที่คัดกรองแล้ว
3. GET  /api/records - ดึงข้อมูลที่บันทึกไว้ในระบบ
"""

import asyncio
import logging
import os
import threading
import urllib.request
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    FlexContainer,
    FlexMessage,
    MessageAction,
    MessagingApi,
    PushMessageRequest,
    QuickReply,
    QuickReplyItem,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import FollowEvent, MessageEvent, TextMessageContent

from database import DatabaseManager
from flex_templates import build_welcome_flex
from screening import process_user_message

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("stroke-screening-bot")

db = DatabaseManager()


async def _keep_alive_loop():
    """ส่งสัญญาณกระตุ้นเซิร์ฟเวอร์ตัวเองทุก 10 นาที เพื่อป้องกันไม่ให้ Render Free Tier หลับ"""
    target_url = os.getenv(
        "RENDER_EXTERNAL_URL", "https://chatbot-sukjai.onrender.com"
    ).rstrip("/") + "/health"
    while True:
        await asyncio.sleep(600)
        try:
            await asyncio.to_thread(
                lambda: urllib.request.urlopen(target_url, timeout=15).read()
            )
            logger.info(f"Keep-alive ping successful: {target_url}")
        except Exception as exc:
            logger.debug(f"Keep-alive ping skipped: {exc}")


@asynccontextmanager
async def lifespan(application: FastAPI):
    # โหลดรายชื่อผู้ป่วยเดิมจาก Google Sheets เข้าหน่วยความจำตอนเริ่มต้น
    threading.Thread(target=db.preload_from_google_sheet, daemon=True).start()
    keep_alive_task = asyncio.create_task(_keep_alive_loop())
    yield
    keep_alive_task.cancel()


app = FastAPI(
    title="LINE Chatbot คัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง",
    description="ระบบคัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรังผ่าน LINE พร้อมจดจำชื่อผู้ป่วยและบันทึกข้อมูลลง Google Sheets",
    version="2.1.0",
    lifespan=lifespan,
)

# ตั้งค่า LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

line_configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
webhook_handler = WebhookHandler(LINE_CHANNEL_SECRET)


def _to_line_quick_reply(items: List[Dict[str, str]]) -> QuickReply:
    """แปลงรายการปุ่มเป็น QuickReply ของ LINE SDK v3"""
    return QuickReply(
        items=[
            QuickReplyItem(
                action=MessageAction(
                    label=item["label"][:20],
                    text=item["text"],
                )
            )
            for item in items
        ]
    )


# =====================================================================
# LINE Messaging API Webhook Endpoints
# =====================================================================
@app.post("/callback")
async def line_webhook_callback(request: Request):
    """รับ Webhook Event จาก LINE Platform"""
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")

    if not LINE_CHANNEL_SECRET or LINE_CHANNEL_SECRET == "your_line_channel_secret_here":
        raise HTTPException(
            status_code=400,
            detail="ยังไม่ได้ตั้งค่า LINE_CHANNEL_SECRET ในไฟล์ .env",
        )

    try:
        webhook_handler.handle(body_text, signature)
    except InvalidSignatureError:
        logger.warning("Invalid LINE signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


@webhook_handler.add(FollowEvent)
def handle_follow_event(event: FollowEvent):
    """เมื่อผู้ใช้แอดเพื่อน LINE OA ให้ส่งการ์ดต้อนรับทันที"""
    user_id = event.source.user_id
    remembered_name = db.get_patient_name(user_id)

    with ApiClient(line_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        welcome_flex = build_welcome_flex(remembered_name=remembered_name)
        qr_items = [
            {"label": "🧠 เริ่มคัดกรอง (9 ข้อ)", "text": "เริ่มคัดกรอง"},
            {"label": "📊 เกณฑ์การประเมิน", "text": "เกณฑ์การประเมิน"},
        ]
        if remembered_name:
            qr_items.insert(1, {"label": "✏️ เปลี่ยนชื่อผู้ป่วย", "text": "เปลี่ยนชื่อ"})

        quick_reply = _to_line_quick_reply(qr_items)
        messages = [
            FlexMessage(
                alt_text="ยินดีต้อนรับสู่ระบบคัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง",
                contents=FlexContainer.from_dict(welcome_flex),
                quick_reply=quick_reply,
            )
        ]
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages,
                )
            )
        except Exception:
            line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=messages,
                )
            )


@webhook_handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    """เมื่อผู้ใช้ส่งข้อความเข้ามาใน LINE OA"""
    user_id = event.source.user_id
    user_text = event.message.text
    display_name = "ผู้ใช้งาน LINE"

    with ApiClient(line_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        existing_session = db.get_session(user_id)
        if existing_session and existing_session.get("display_name"):
            display_name = existing_session["display_name"]
        else:
            try:
                profile = line_bot_api.get_profile(user_id)
                if profile and profile.display_name:
                    display_name = profile.display_name
            except Exception:
                pass

        result = process_user_message(
            user_id=user_id,
            display_name=display_name,
            user_text=user_text,
            database=db,
        )

        quick_reply = (
            _to_line_quick_reply(result["quick_replies"])
            if result.get("quick_replies")
            else None
        )

        messages = []
        if result["type"] in ("welcome", "result") and result.get("flex"):
            messages.append(
                FlexMessage(
                    alt_text=result["text"][:300],
                    contents=FlexContainer.from_dict(result["flex"]),
                    quick_reply=quick_reply,
                )
            )
        else:
            messages.append(
                TextMessage(
                    text=result["text"],
                    quick_reply=quick_reply,
                )
            )

        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages,
                )
            )
        except Exception as exc:
            logger.warning(f"reply_message ล้มเหลว (อาจเกิดจาก Cold Start): {exc} -> ส่งด้วย push_message แทน")
            line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=messages,
                )
            )


# =====================================================================
# Web Simulator & Dashboard API
# =====================================================================
class SimulateRequest(BaseModel):
    user_id: str = "U_STROKE_PATIENT_01"
    display_name: str = "LINE_User_01"
    message: str


@app.post("/api/simulate")
async def simulate_chat(req: SimulateRequest):
    """API สำหรับทดสอบคุยกับบอทผ่านหน้าเว็บโดยตรง"""
    res = process_user_message(
        user_id=req.user_id,
        display_name=req.display_name,
        user_text=req.message,
        database=db,
    )
    return JSONResponse(res)


@app.get("/api/records")
async def list_records():
    """ดึงข้อมูลประวัติผู้เข้ารับการคัดกรองและสถานะฐานข้อมูล"""
    return JSONResponse(
        {
            "status": db.get_status_info(),
            "records": db.get_recent_records(limit=100),
        }
    )


@app.get("/health")
async def health_check():
    return {"status": "ok", "database": db.get_status_info()}


@app.get("/", response_class=HTMLResponse)
async def index_page():
    """หน้าเว็บจำลองแชต LINE และตารางฐานข้อมูลผู้ป่วยโรคหลอดเลือดสมอง"""
    return """<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>LINE Chatbot คัดกรองภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; background: #f0f4f8; color: #1e293b; }
        header {
            background: linear-gradient(135deg, #0f172a, #1e40af);
            color: #fff; padding: 16px 28px;
            display: flex; justify-content: space-between; align-items: center;
        }
        header h1 { margin: 0; font-size: 1.2rem; }
        .badge {
            padding: 6px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;
            background: rgba(255,255,255,0.15);
        }
        .container {
            max-width: 1280px; margin: 20px auto; padding: 0 16px;
            display: grid; grid-template-columns: 420px 1fr; gap: 20px;
        }
        @media (max-width: 900px) { .container { grid-template-columns: 1fr; } }
        .phone-card {
            background: #8cabd9; border-radius: 18px; overflow: hidden;
            box-shadow: 0 10px 25px rgba(0,0,0,0.12); display: flex; flex-direction: column;
            height: 700px; border: 4px solid #1e293b;
        }
        .line-header {
            background: #222e3e; color: #fff; padding: 12px 16px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .chat-messages {
            flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px;
        }
        .msg-bot, .msg-user {
            max-width: 85%; padding: 10px 14px; border-radius: 14px; font-size: 0.9rem;
            line-height: 1.45; white-space: pre-wrap;
        }
        .msg-bot { background: #fff; align-self: flex-start; border-top-left-radius: 3px; }
        .msg-user { background: #85e249; align-self: flex-end; border-top-right-radius: 3px; }
        .quick-replies {
            background: rgba(255,255,255,0.92); padding: 8px 10px;
            display: flex; gap: 6px; overflow-x: auto; border-top: 1px solid #cbd5e1;
        }
        .qr-btn {
            background: #eff6ff; border: 1px solid #3b82f6; color: #1d4ed8;
            border-radius: 999px; padding: 6px 12px; font-size: 0.8rem; cursor: pointer;
            white-space: nowrap; font-weight: 600;
        }
        .qr-btn:hover { background: #dbeafe; }
        .chat-input {
            background: #fff; padding: 10px; display: flex; gap: 8px;
        }
        .chat-input input {
            flex: 1; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 999px; outline: none;
        }
        .chat-input button {
            background: #06c755; color: #fff; border: none; border-radius: 999px;
            padding: 8px 16px; font-weight: 600; cursor: pointer;
        }
        .panel {
            background: #fff; border-radius: 16px; padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        .user-bar {
            display: flex; gap: 10px; margin-bottom: 14px; align-items: center; flex-wrap: wrap;
        }
        .user-bar input {
            padding: 6px 10px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.85rem;
        }
        table { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 10px; }
        th, td { padding: 10px 8px; border-bottom: 1px solid #e2e8f0; text-align: left; }
        th { background: #f8fafc; color: #475569; font-weight: 600; }
        .risk-pill {
            display: inline-block; padding: 3px 8px; border-radius: 6px; color: #fff; font-weight: 600; font-size: 0.75rem;
        }
    </style>
</head>
<body>
<header>
    <div>
        <h1>🧠 LINE Chatbot คัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง</h1>
        <small>ถามชื่อ-นามสกุลผู้ป่วยและจดจำ User อัตโนมัติ | บันทึกลง Google Sheets (sukjai_db)</small>
    </div>
    <div id="dbStatusBadge" class="badge">กำลังตรวจสอบฐานข้อมูล...</div>
</header>

<div class="container">
    <!-- LINE Chat Simulator -->
    <div class="phone-card">
        <div class="line-header">
            <span>💬 จำลองแชต LINE OA (คลิกปุ่มเพื่อทดสอบ)</span>
            <button onclick="sendMsg('เริ่มคัดกรอง')" style="background:#06c755;color:#fff;border:none;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:0.75rem;">เริ่มคัดกรอง</button>
        </div>
        <div id="chatBox" class="chat-messages"></div>
        <div id="qrBox" class="quick-replies"></div>
        <div class="chat-input">
            <input id="msgInput" type="text" placeholder="พิมพ์ชื่อ-นามสกุล หรือกดปุ่มตัวเลือก..." onkeydown="if(event.key==='Enter') sendInput()" />
            <button onclick="sendInput()">ส่ง</button>
        </div>
    </div>

    <!-- Database Records -->
    <div class="panel">
        <div class="user-bar">
            <strong>🆔 LINE User ID จำลอง:</strong>
            <input id="simUserId" value="U_STROKE_001" placeholder="LINE User ID" />
            <input id="simUserName" value="LINE_User_01" placeholder="LINE Display Name" />
            <button onclick="loadRecords()" style="padding:6px 12px;border-radius:8px;border:1px solid #cbd5e1;background:#f8fafc;cursor:pointer;">🔄 รีเฟรชข้อมูล</button>
        </div>

        <h3 style="margin-top:0;">📊 ประวัติผู้ป่วยโรคเรื้อรังที่คัดกรองภาวะโรคหลอดเลือดสมองล่าสุด</h3>
        <div style="overflow-x:auto;">
            <table>
                <thead>
                    <tr>
                        <th>วัน-เวลา</th>
                        <th>ชื่อ-นามสกุลผู้ป่วย</th>
                        <th>โรคประจำตัวเรื้อรัง</th>
                        <th>การคุมความดัน</th>
                        <th>อาการ B.E.F.A.S.T.</th>
                        <th>คะแนน</th>
                        <th>ระดับความเสี่ยง</th>
                        <th>Google Sheet</th>
                    </tr>
                </thead>
                <tbody id="recordsBody">
                    <tr><td colspan="8">กำลังโหลดข้อมูล...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
async function sendMsg(text) {
    const chatBox = document.getElementById('chatBox');
    const userDiv = document.createElement('div');
    userDiv.className = 'msg-user';
    userDiv.textContent = text;
    chatBox.appendChild(userDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: document.getElementById('simUserId').value,
            display_name: document.getElementById('simUserName').value,
            message: text
        })
    });
    const data = await res.json();

    const botDiv = document.createElement('div');
    botDiv.className = 'msg-bot';
    botDiv.textContent = data.text;
    chatBox.appendChild(botDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    const qrBox = document.getElementById('qrBox');
    qrBox.innerHTML = '';
    if (data.quick_replies) {
        data.quick_replies.forEach(item => {
            const btn = document.createElement('button');
            btn.className = 'qr-btn';
            btn.textContent = item.label;
            btn.onclick = () => sendMsg(item.text);
            qrBox.appendChild(btn);
        });
    }

    if (data.type === 'result') {
        loadRecords();
    }
}

function sendInput() {
    const input = document.getElementById('msgInput');
    if (!input.value.trim()) return;
    sendMsg(input.value.trim());
    input.value = '';
}

async function loadRecords() {
    const res = await fetch('/api/records');
    const data = await res.json();
    const badge = document.getElementById('dbStatusBadge');
    if (data.status.google_sheet_configured) {
        badge.textContent = `✅ เชื่อมต่อ Google Sheets แล้ว (${data.status.total_records} รายการ | จดจำผู้ป่วย ${data.status.total_patients} ราย)`;
        badge.style.background = '#16a34a';
    } else {
        badge.textContent = `💾 โหมด SQLite ในเครื่อง (${data.status.total_records} รายการ)`;
    }

    const tbody = document.getElementById('recordsBody');
    if (!data.records.length) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#64748b;">ยังไม่มีข้อมูลการคัดกรอง ลองกดเริ่มคัดกรองในช่องแชตด้านซ้าย</td></tr>';
        return;
    }
    tbody.innerHTML = data.records.map(r => {
        let color = '#2E7D32';
        if (r.risk_level.includes('ระดับที่ 2')) color = '#EF6C00';
        if (r.risk_level.includes('ระดับที่ 3')) color = '#D84315';
        if (r.risk_level.includes('ระดับที่ 4')) color = '#C62828';
        return `<tr>
            <td>${r.timestamp}</td>
            <td><strong>${r.patient_name}</strong><br><small style="color:#64748b">${r.user_id}</small></td>
            <td>${r.chronic_disease}</td>
            <td>${r.bp_control}</td>
            <td>${r.befast_symptoms}</td>
            <td><strong>${r.total_score}</strong></td>
            <td><span class="risk-pill" style="background:${color}">${r.risk_level}</span></td>
            <td>${r.synced_to_sheet ? '✅ ซิงก์แล้ว' : '💾 Local'}</td>
        </tr>`;
    }).join('');
}

window.onload = () => {
    sendMsg('สวัสดี');
    loadRecords();
};
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
