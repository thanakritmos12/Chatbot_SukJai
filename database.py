"""
ระบบจัดการฐานข้อมูล (Google Sheets + SQLite Local Fallback)
สำหรับระบบคัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง
- จดจำชื่อ-นามสกุลของผู้ป่วยตาม LINE User ID อัตโนมัติ (ทั้งใน SQLite และค้นหาจาก Google Sheets)
- บันทึกผลการคัดกรองลงใน Google Sheets และ SQLite ควบคู่กัน
"""

import json
import logging
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials

    GSPREAD_AVAILABLE = True
except ImportError:
    gspread = None
    Credentials = None
    GSPREAD_AVAILABLE = False

logger = logging.getLogger(__name__)

# คอลัมน์ที่จะสร้างใน Google Sheets แถวที่ 1 (Header 17 คอลัมน์)
SHEET_HEADERS = [
    "วัน-เวลา (Timestamp)",
    "LINE User ID",
    "ชื่อ LINE (Display Name)",
    "ชื่อ-นามสกุลผู้ป่วย (Patient Name)",
    "1. อายุ",
    "2. โรคประจำตัวเรื้อรัง",
    "3. การคุมความดันโลหิต",
    "4. น้ำตาลและไขมันในเลือด",
    "5. ความสม่ำเสมอในการทานยา",
    "6. บุหรี่/แอลกอฮอล์",
    "7. รูปร่าง/การออกกำลังกาย",
    "8. ประวัติครอบครัวเป็นสโตรก",
    "9. อาการเตือน (B.E.F.A.S.T.)",
    "คะแนนรวม (Score)",
    "ระดับความเสี่ยง (Risk Level)",
    "โอกาสเกิดโรค",
    "คำแนะนำการดูแลสุขภาพ",
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class DatabaseManager:
    def __init__(self, sqlite_path: str = "screening_records.db"):
        self.sqlite_path = sqlite_path
        self._init_sqlite()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self) -> None:
        """สร้างตาราง SQLite สำหรับเก็บข้อมูลชื่อ-นามสกุลผู้ป่วย, Session และประวัติการคัดกรอง"""
        with closing(self._get_conn()) as conn:
            # ตารางจดจำชื่อ-นามสกุลผู้ป่วยตาม LINE User ID
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS patient_profiles (
                    user_id TEXT PRIMARY KEY,
                    patient_name TEXT NOT NULL,
                    display_name TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )
            # ตารางเก็บสถานะระหว่างทำแบบคัดกรอง
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT,
                    patient_name TEXT DEFAULT '',
                    current_step INTEGER NOT NULL DEFAULT 0,
                    answers_json TEXT NOT NULL DEFAULT '{}',
                    updated_at TEXT NOT NULL
                )
                """
            )
            # ตรวจสอบกรณีตารางเก่าไม่มีคอลัมน์ patient_name
            session_cols = [
                r["name"]
                for r in conn.execute("PRAGMA table_info(user_sessions)").fetchall()
            ]
            if "patient_name" not in session_cols:
                conn.execute(
                    "ALTER TABLE user_sessions ADD COLUMN patient_name TEXT DEFAULT ''"
                )

            # ตารางเก็บผลการคัดกรองโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stroke_screening_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    display_name TEXT,
                    patient_name TEXT NOT NULL,
                    age TEXT,
                    chronic_disease TEXT,
                    bp_control TEXT,
                    sugar_lipid TEXT,
                    med_adherence TEXT,
                    smoking_alcohol TEXT,
                    bmi_exercise TEXT,
                    family_stroke TEXT,
                    befast_symptoms TEXT,
                    total_score INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    probability TEXT,
                    recommendations TEXT,
                    synced_to_sheet INTEGER DEFAULT 0
                )
                """
            )
            conn.commit()

    # =========================================================
    # ระบบจดจำชื่อ-นามสกุลของผู้ป่วย (Patient Name Memory)
    # =========================================================
    def save_patient_name(
        self, user_id: str, patient_name: str, display_name: str = ""
    ) -> None:
        """บันทึกหรืออัปเดตชื่อ-นามสกุลของผู้ป่วยผูกกับ LINE User ID"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with closing(self._get_conn()) as conn:
            conn.execute(
                """
                INSERT INTO patient_profiles (user_id, patient_name, display_name, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    patient_name = excluded.patient_name,
                    display_name = excluded.display_name,
                    updated_at = excluded.updated_at
                """,
                (user_id, patient_name.strip(), display_name, now),
            )
            conn.commit()

    def get_patient_name(self, user_id: str) -> Optional[str]:
        """ดึงชื่อ-นามสกุลของผู้ป่วยที่เคยบันทึกไว้สำหรับ LINE User ID นี้"""
        with closing(self._get_conn()) as conn:
            row = conn.execute(
                "SELECT patient_name FROM patient_profiles WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            if row and row["patient_name"]:
                return row["patient_name"]

            # ค้นหาสำรองจากตารางประวัติการคัดกรองในเครื่อง
            rec = conn.execute(
                """
                SELECT patient_name FROM stroke_screening_records
                WHERE user_id = ? AND patient_name != ''
                ORDER BY id DESC LIMIT 1
                """,
                (user_id,),
            ).fetchone()
            if rec and rec["patient_name"]:
                self.save_patient_name(user_id, rec["patient_name"])
                return rec["patient_name"]

        # ค้นหาสำรองจาก Google Sheets (กรณีรันบน Cloud เช่น Render แล้ว Container รีสตาร์ท)
        worksheet = self._get_google_worksheet()
        if worksheet is not None:
            try:
                all_rows = worksheet.get_all_values()
                for r in reversed(all_rows[1:]):
                    if len(r) >= 4 and r[1] == user_id and r[3].strip():
                        found_name = r[3].strip()
                        self.save_patient_name(user_id, found_name, r[2] if len(r) > 2 else "")
                        return found_name
            except Exception as exc:
                logger.warning(f"ค้นหาชื่อผู้ป่วยจาก Google Sheets ไม่สำเร็จ: {exc}")

        return None

    # =========================================================
    # จัดการสถานะการถาม-ตอบ (Session Management)
    # =========================================================
    def start_session(
        self,
        user_id: str,
        display_name: str = "ผู้ใช้งาน LINE",
        patient_name: str = "",
        initial_step: int = 0,
    ) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with closing(self._get_conn()) as conn:
            conn.execute(
                """
                INSERT INTO user_sessions (user_id, display_name, patient_name, current_step, answers_json, updated_at)
                VALUES (?, ?, ?, ?, '{}', ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    patient_name = excluded.patient_name,
                    current_step = excluded.current_step,
                    answers_json = '{}',
                    updated_at = excluded.updated_at
                """,
                (user_id, display_name, patient_name, initial_step, now),
            )
            conn.commit()

    def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_conn()) as conn:
            row = conn.execute(
                "SELECT * FROM user_sessions WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return None
            return {
                "user_id": row["user_id"],
                "display_name": row["display_name"],
                "patient_name": row["patient_name"] or "",
                "current_step": row["current_step"],
                "answers": json.loads(row["answers_json"]),
                "updated_at": row["updated_at"],
            }

    def update_session(
        self, user_id: str, next_step: int, answers: Dict[str, Any]
    ) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with closing(self._get_conn()) as conn:
            conn.execute(
                """
                UPDATE user_sessions
                SET current_step = ?, answers_json = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (next_step, json.dumps(answers, ensure_ascii=False), now, user_id),
            )
            conn.commit()

    def clear_session(self, user_id: str) -> None:
        with closing(self._get_conn()) as conn:
            conn.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
            conn.commit()

    # =========================================================
    # เชื่อมต่อและบันทึกข้อมูลลง Google Sheets
    # =========================================================
    def _get_google_worksheet(self):
        """เชื่อมต่อกับ Google Sheets API หากตั้งค่าไว้ใน .env"""
        try:
            from dotenv import load_dotenv

            load_dotenv(override=True)
        except ImportError:
            pass

        sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
        if not sheet_id or sheet_id == "your_google_sheet_id_here":
            return None

        if not GSPREAD_AVAILABLE:
            logger.warning(
                "ยังไม่ได้ติดตั้งไลบรารี gspread / google-auth (รัน pip install -r requirements.txt)"
            )
            return None

        creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json").strip()
        creds_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip()
        worksheet_name = os.getenv("GOOGLE_WORKSHEET_NAME", "ScreeningRecords").strip()

        try:
            if creds_json_str:
                creds_info = json.loads(creds_json_str)
                creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
            elif os.path.exists(creds_file):
                creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
            else:
                logger.warning(
                    f"ไม่พบไฟล์ {creds_file} สำหรับเชื่อมต่อ Google Sheets (ระบบจะบันทึกลง SQLite สำรองแทน)"
                )
                return None

            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(sheet_id)

            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name, rows=1000, cols=len(SHEET_HEADERS)
                )
                worksheet.append_row(SHEET_HEADERS, value_input_option="USER_ENTERED")
                return worksheet

            # ตรวจสอบและอัปเดตแถวที่ 1 (Header) ให้ตรงกับเกณฑ์โรคหลอดเลือดสมอง
            first_row = worksheet.row_values(1)
            if not first_row:
                worksheet.append_row(SHEET_HEADERS, value_input_option="USER_ENTERED")
            elif first_row != SHEET_HEADERS:
                worksheet.update(
                    range_name="A1:Q1",
                    values=[SHEET_HEADERS],
                    value_input_option="USER_ENTERED",
                )

            return worksheet
        except Exception as exc:
            logger.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {exc}")
            return None

    def save_screening_result(
        self,
        user_id: str,
        display_name: str,
        patient_name: str,
        answers: Dict[str, Dict[str, Any]],
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """บันทึกผลการคัดกรองภาวะโรคหลอดเลือดสมองลงทั้ง Google Sheets และ SQLite"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean_patient_name = (patient_name or display_name).strip()

        # จดจำชื่อ-นามสกุลผู้ป่วยไว้สำหรับครั้งถัดไปเสมอ
        self.save_patient_name(user_id, clean_patient_name, display_name)

        def ans_text(key: str) -> str:
            item = answers.get(key, {})
            return f"{item.get('text', '-')} ({item.get('score', 0)})"

        recommendations_str = " | ".join(evaluation.get("recommendations", []))

        row_values = [
            timestamp,
            user_id,
            display_name,
            clean_patient_name,
            ans_text("age"),
            ans_text("chronic_disease"),
            ans_text("bp_control"),
            ans_text("sugar_lipid"),
            ans_text("med_adherence"),
            ans_text("smoking_alcohol"),
            ans_text("bmi_exercise"),
            ans_text("family_stroke"),
            ans_text("befast_symptoms"),
            evaluation["total_score"],
            evaluation["risk_level"],
            evaluation["probability"],
            recommendations_str,
        ]

        # 1. บันทึกลง Google Sheets
        synced_to_sheet = 0
        worksheet = self._get_google_worksheet()
        if worksheet is not None:
            try:
                worksheet.append_row(row_values, value_input_option="USER_ENTERED")
                synced_to_sheet = 1
                logger.info(
                    f"บันทึกข้อมูลผู้ป่วย {clean_patient_name} ({user_id}) ลง Google Sheets สำเร็จ"
                )
            except Exception as exc:
                logger.error(f"ไม่สามารถบันทึกลง Google Sheets ได้: {exc}")

        # 2. บันทึกลงฐานข้อมูล SQLite ในเครื่อง
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                """
                INSERT INTO stroke_screening_records (
                    timestamp, user_id, display_name, patient_name,
                    age, chronic_disease, bp_control, sugar_lipid,
                    med_adherence, smoking_alcohol, bmi_exercise, family_stroke, befast_symptoms,
                    total_score, risk_level, probability, recommendations, synced_to_sheet
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*row_values, synced_to_sheet),
            )
            record_id = cursor.lastrowid
            conn.commit()

        return {
            "record_id": record_id,
            "timestamp": timestamp,
            "synced_to_sheet": bool(synced_to_sheet),
        }

    def get_latest_record(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ดึงประวัติการคัดกรองล่าสุดของผู้ใช้รายนั้น"""
        with closing(self._get_conn()) as conn:
            row = conn.execute(
                """
                SELECT * FROM stroke_screening_records
                WHERE user_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (user_id,),
            ).fetchone()
            return dict(row) if row else None

    def get_recent_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """ดึงรายการคัดกรองล่าสุดสำหรับแสดงผลบนหน้า Dashboard"""
        with closing(self._get_conn()) as conn:
            rows = conn.execute(
                """
                SELECT * FROM stroke_screening_records
                ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def sync_pending_records(self) -> int:
        """ซิงก์ข้อมูลที่ยังไม่ได้ส่งขึ้น Google Sheets"""
        worksheet = self._get_google_worksheet()
        if worksheet is None:
            return 0

        synced_count = 0
        with closing(self._get_conn()) as conn:
            rows = conn.execute(
                "SELECT * FROM stroke_screening_records WHERE synced_to_sheet = 0 ORDER BY id ASC"
            ).fetchall()
            for r in rows:
                row_values = [
                    r["timestamp"],
                    r["user_id"],
                    r["display_name"],
                    r["patient_name"],
                    r["age"],
                    r["chronic_disease"],
                    r["bp_control"],
                    r["sugar_lipid"],
                    r["med_adherence"],
                    r["smoking_alcohol"],
                    r["bmi_exercise"],
                    r["family_stroke"],
                    r["befast_symptoms"],
                    r["total_score"],
                    r["risk_level"],
                    r["probability"],
                    r["recommendations"],
                ]
                try:
                    worksheet.append_row(row_values, value_input_option="USER_ENTERED")
                    conn.execute(
                        "UPDATE stroke_screening_records SET synced_to_sheet = 1 WHERE id = ?",
                        (r["id"],),
                    )
                    conn.commit()
                    synced_count += 1
                except Exception as exc:
                    logger.error(f"ซิงก์ข้อมูลย้อนหลังรายการ #{r['id']} ไม่สำเร็จ: {exc}")
                    break
        return synced_count

    def get_status_info(self) -> Dict[str, Any]:
        """ตรวจสอบสถานะการเชื่อมต่อฐานข้อมูล"""
        try:
            from dotenv import load_dotenv

            load_dotenv(override=True)
        except ImportError:
            pass

        sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
        creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json").strip()
        has_sheet_config = bool(sheet_id and sheet_id != "your_google_sheet_id_here")
        has_creds_file = os.path.exists(creds_file) or bool(
            os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip()
        )

        if has_sheet_config and has_creds_file:
            self.sync_pending_records()

        with closing(self._get_conn()) as conn:
            total_records = conn.execute(
                "SELECT COUNT(*) AS cnt FROM stroke_screening_records"
            ).fetchone()["cnt"]
            total_patients = conn.execute(
                "SELECT COUNT(*) AS cnt FROM patient_profiles"
            ).fetchone()["cnt"]

        return {
            "total_records": total_records,
            "total_patients": total_patients,
            "google_sheet_configured": has_sheet_config and has_creds_file,
            "google_sheet_id": sheet_id if has_sheet_config else None,
            "credentials_found": has_creds_file,
        }
