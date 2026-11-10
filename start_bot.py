"""
สคริปต์เปิดระบบอัตโนมัติ (รันทั้ง FastAPI Server + ngrok + อัปเดต LINE Webhook URL อัตโนมัติ)
วิธีใช้: python start_bot.py (หรือดับเบิลคลิกไฟล์ start_bot.bat)
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from dotenv import load_dotenv

NGROK_DEFAULT_PATH = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"
)


def get_ngrok_executable() -> str:
    if os.path.exists(NGROK_DEFAULT_PATH):
        return NGROK_DEFAULT_PATH
    return "ngrok"


def update_line_webhook(webhook_url: str, access_token: str) -> bool:
    try:
        req = urllib.request.Request(
            "https://api.line.me/v2/bot/channel/webhook/endpoint",
            data=json.dumps({"endpoint": webhook_url}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            method="PUT",
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as exc:
        print(f"⚠️ อัปเดต LINE Webhook อัตโนมัติไม่สำเร็จ: {exc}")
        return False


def main():
    load_dotenv(override=True)
    port = os.getenv("PORT", "8000")
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()

    print("🚀 1. กำลังเปิดเซิร์ฟเวอร์ FastAPI (พอร์ต 8000)...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", port]
    )

    print("🌐 2. กำลังเปิด ngrok tunnel...")
    ngrok_proc = subprocess.Popen(
        [get_ngrok_executable(), "http", port],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    public_url = None
    for _ in range(15):
        time.sleep(1)
        try:
            res = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=3)
            data = json.loads(res.read().decode("utf-8"))
            for t in data.get("tunnels", []):
                if t.get("proto") == "https":
                    public_url = t["public_url"]
                    break
            if public_url:
                break
        except Exception:
            pass

    if public_url:
        webhook_url = f"{public_url}/callback"
        print(f"✅ Public URL:  {public_url}")
        print(f"✅ Webhook URL: {webhook_url}")
        if token and token != "your_line_channel_access_token_here":
            if update_line_webhook(webhook_url, token):
                print("✅ อัปเดตลิงก์ Webhook ไปยัง LINE Official Account (SukJai) อัตโนมัติเรียบร้อยแล้ว!")
    else:
        print("⚠️ ไม่สามารถดึง URL จาก ngrok ได้ กรุณาตรวจสอบว่าไม่มี ngrok รันซ้ำซ้อนอยู่")

    print("\n📌 เปิดหน้าเว็บจำลองและดูฐานข้อมูลได้ที่: http://localhost:8000")
    print("📌 กด Ctrl+C เพื่อปิดระบบ\n")

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\nกำลังปิดระบบ...")
    finally:
        ngrok_proc.terminate()
        server_proc.terminate()


if __name__ == "__main__":
    main()
