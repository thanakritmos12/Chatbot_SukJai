"""
สร้างข้อความรูปแบบพิเศษสำหรับ LINE Messaging API (Flex Message และ Quick Reply)
สำหรับระบบคัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง
"""

from typing import Any, Dict, List, Optional


def build_welcome_flex(remembered_name: Optional[str] = None) -> Dict[str, Any]:
    """สร้าง Flex Bubble ต้อนรับพร้อมแสดงชื่อผู้ป่วยที่ระบบจดจำไว้ (ถ้ามี)"""
    body_contents: List[Dict[str, Any]] = []

    if remembered_name:
        body_contents.append(
            {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#E3F2FD",
                "cornerRadius": "8px",
                "paddingAll": "10px",
                "contents": [
                    {
                        "type": "text",
                        "text": f"👤 ผู้ป่วยที่จดจำไว้: คุณ{remembered_name}",
                        "size": "xs",
                        "weight": "bold",
                        "color": "#0D47A1",
                        "wrap": True,
                    },
                    {
                        "type": "text",
                        "text": "กดเริ่มทำแบบคัดกรองได้ทันทีโดยไม่ต้องพิมพ์ชื่อซ้ำ",
                        "size": "xxs",
                        "color": "#1565C0",
                        "wrap": True,
                    },
                ],
            }
        )

    body_contents.extend(
        [
            {
                "type": "text",
                "text": "ผู้ป่วยโรคเรื้อรัง (ความดันสูง เบาหวาน ไขมันสูง โรคหัวใจ) มีความเสี่ยงต่อโรคหลอดเลือดสมอง (อัมพฤกษ์-อัมพาต) สูงกว่าคนทั่วไป มาตรวจเช็กความเสี่ยงด้วยแบบประเมิน 9 ข้อกันครับ",
                "wrap": True,
                "size": "sm",
                "color": "#424242",
                "margin": "md" if remembered_name else "none",
            },
            {"type": "separator", "margin": "md"},
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "margin": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "เกณฑ์ระดับความเสี่ยงโรคหลอดเลือดสมอง:",
                        "weight": "bold",
                        "size": "sm",
                        "color": "#1565C0",
                    },
                    {
                        "type": "text",
                        "text": "🟢 ระดับ 1 (0-4 คะแนน): ความเสี่ยงต่ำ",
                        "size": "xs",
                        "color": "#2E7D32",
                    },
                    {
                        "type": "text",
                        "text": "🟡 ระดับ 2 (5-9 คะแนน): ความเสี่ยงปานกลาง",
                        "size": "xs",
                        "color": "#EF6C00",
                    },
                    {
                        "type": "text",
                        "text": "🟠 ระดับ 3 (10-14 คะแนน): ความเสี่ยงสูง",
                        "size": "xs",
                        "color": "#D84315",
                    },
                    {
                        "type": "text",
                        "text": "🔴 ระดับ 4 (15+ หรือมีอาการ B.E.F.A.S.T.): เสี่ยงสูงมาก",
                        "size": "xs",
                        "color": "#C62828",
                    },
                ],
            },
        ]
    )

    footer_buttons: List[Dict[str, Any]] = [
        {
            "type": "button",
            "style": "primary",
            "color": "#1565C0",
            "action": {
                "type": "message",
                "label": "เริ่มทำแบบคัดกรอง (9 ข้อ)",
                "text": "เริ่มคัดกรอง",
            },
        }
    ]

    if remembered_name:
        footer_buttons.append(
            {
                "type": "button",
                "style": "secondary",
                "action": {
                    "type": "message",
                    "label": "เปลี่ยนชื่อ-นามสกุลผู้ป่วย",
                    "text": "เปลี่ยนชื่อ",
                },
            }
        )

    footer_buttons.extend(
        [
            {
                "type": "button",
                "style": "secondary",
                "action": {
                    "type": "message",
                    "label": "ดูเกณฑ์การให้คะแนน",
                    "text": "เกณฑ์การประเมิน",
                },
            },
            {
                "type": "button",
                "style": "link",
                "action": {
                    "type": "message",
                    "label": "ดูประวัติผลการคัดกรองล่าสุด",
                    "text": "ประวัติ",
                },
            },
        ]
    )

    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#1565C0",
            "paddingAll": "20px",
            "contents": [
                {
                    "type": "text",
                    "text": "STROKE RISK IN CHRONIC DISEASE",
                    "color": "#BBDEFB",
                    "size": "xs",
                    "weight": "bold",
                },
                {
                    "type": "text",
                    "text": "คัดกรองภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง",
                    "color": "#FFFFFF",
                    "size": "md",
                    "weight": "bold",
                    "wrap": True,
                    "margin": "xs",
                },
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": body_contents,
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": footer_buttons,
        },
    }


def build_question_text_and_choices(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    สร้างข้อความคำถามและรายการปุ่มกดเลือกคำตอบ (Quick Reply)
    """
    lines = [
        f"📋 {question['title']}",
        f"{question['question']}",
        "",
        "กดปุ่มตัวเลือกด้านล่าง หรือพิมพ์หมายเลข:",
    ]
    for c in question["choices"]:
        lines.append(f"  [{c['key']}] {c['text']}")

    quick_reply_items = [
        {
            "label": f"{c['key']}. {c['label']}"[:20],
            "text": c["key"],
        }
        for c in question["choices"]
    ]
    quick_reply_items.append({"label": "❌ ยกเลิก", "text": "ยกเลิก"})

    return {
        "text": "\n".join(lines),
        "quick_replies": quick_reply_items,
    }


def build_result_flex(
    patient_name: str, evaluation: Dict[str, Any], saved_info: Dict[str, Any]
) -> Dict[str, Any]:
    """สร้าง Flex Message แสดงผลการประเมินความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง"""
    color = evaluation["color"]

    risk_factors: List[str] = evaluation.get("risk_factors", [])
    if risk_factors:
        factor_contents = [
            {
                "type": "text",
                "text": f"• {rf}",
                "size": "xs",
                "color": "#555555",
                "wrap": True,
            }
            for rf in risk_factors[:6]
        ]
    else:
        factor_contents = [
            {
                "type": "text",
                "text": "• ไม่พบปัจจัยเสี่ยงที่มีนัยสำคัญ",
                "size": "xs",
                "color": "#2E7D32",
                "wrap": True,
            }
        ]

    rec_contents = [
        {
            "type": "text",
            "text": f"{idx}. {rec}",
            "size": "xs",
            "color": "#333333",
            "wrap": True,
            "margin": "xs",
        }
        for idx, rec in enumerate(evaluation["recommendations"], start=1)
    ]

    db_status_text = (
        "บันทึกข้อมูลลง Google Sheets เรียบร้อยแล้ว"
        if saved_info.get("synced_to_sheet")
        else f"บันทึกข้อมูลเรียบร้อย (#{saved_info.get('record_id', '-')})"
    )

    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": color,
            "paddingAll": "18px",
            "contents": [
                {
                    "type": "text",
                    "text": f"👤 ผู้ป่วย: คุณ{patient_name}",
                    "color": "#FFFFFF",
                    "size": "sm",
                    "weight": "bold",
                    "wrap": True,
                },
                {
                    "type": "text",
                    "text": evaluation["risk_level"],
                    "color": "#FFFFFF",
                    "size": "md",
                    "weight": "bold",
                    "wrap": True,
                    "margin": "xs",
                },
                {
                    "type": "text",
                    "text": f"คะแนนความเสี่ยงรวม: {evaluation['total_score']} คะแนน",
                    "color": "#FFFFFF",
                    "size": "xs",
                    "margin": "xs",
                },
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": evaluation["probability"],
                    "weight": "bold",
                    "size": "sm",
                    "color": color,
                    "wrap": True,
                },
                {
                    "type": "text",
                    "text": evaluation["summary"],
                    "size": "xs",
                    "color": "#555555",
                    "wrap": True,
                },
                {"type": "separator", "margin": "md"},
                {
                    "type": "text",
                    "text": "ปัจจัยเสี่ยงที่พบจากคำตอบของผู้ป่วย:",
                    "weight": "bold",
                    "size": "xs",
                    "color": "#222222",
                    "margin": "md",
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": factor_contents,
                },
                {"type": "separator", "margin": "md"},
                {
                    "type": "text",
                    "text": "คำแนะนำการปฏิบัติตัวและป้องกันโรคหลอดเลือดสมอง:",
                    "weight": "bold",
                    "size": "sm",
                    "color": "#1565C0",
                    "margin": "md",
                    "wrap": True,
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": rec_contents,
                },
                {"type": "separator", "margin": "md"},
                {
                    "type": "text",
                    "text": f"หมายเหตุ: หากมีอาการ B.E.F.A.S.T. (เดินเซ ตาพร่า หน้าเบี้ยว แขนอ่อนแรง พูดไม่ชัด) ให้โทร 1669 ทันที ({db_status_text})",
                    "size": "xxs",
                    "color": "#888888",
                    "wrap": True,
                    "margin": "sm",
                },
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": color,
                    "action": {
                        "type": "message",
                        "label": "ทำแบบคัดกรองอีกครั้ง",
                        "text": "เริ่มคัดกรอง",
                    },
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",
                        "label": "เปลี่ยนชื่อ-นามสกุลผู้ป่วย",
                        "text": "เปลี่ยนชื่อ",
                    },
                },
            ],
        },
    }


def build_criteria_text() -> str:
    """ข้อความอธิบายเกณฑ์การให้คะแนนและระดับความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง"""
    return (
        "🧠 เกณฑ์คัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง (9 ปัจจัย)\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ อายุ: <45 ปี (0) | 45-59 ปี (1) | 60+ ปี (2)\n"
        "2️⃣ โรคเรื้อรังประจำตัว: มี 1 โรค (1) | มี >=2 โรค (2) | โรคหัวใจ AF/เคยเป็นสโตรก (4)\n"
        "3️⃣ การคุมความดันโลหิต: <140/90 (0) | 140/90-159/99 หรือไม่ค่อยได้วัด (2) | >=160/100 (3)\n"
        "4️⃣ น้ำตาลและไขมันในเลือด: ตามเกณฑ์แพทย์ (0) | สูงเล็กน้อย (1) | น้ำตาล/ไขมันสูงมากคุมไม่ได้ (2)\n"
        "5️⃣ ความสม่ำเสมอในการทานยา: ทานครบทุกวัน (0) | ลืมบางครั้ง (1) | ขาดยาบ่อย/หยุดยาเอง (3)\n"
        "6️⃣ บุหรี่และแอลกอฮอล์: ไม่สูบไม่ดื่ม (0) | เคยสูบ/ดื่มครั้งคราว (1) | สูบประจำ/ดื่มบ่อย (3)\n"
        "7️⃣ รูปร่างและการออกกำลังกาย: สมส่วน+ออกกำลังกาย (0) | ท้วม/ออกน้อย (1) | อ้วนลงพุง+ไม่ออกกำลัง (2)\n"
        "8️⃣ ประวัติครอบครัวเป็นสโตรก: ไม่มี (0) | ไม่แน่ใจ (1) | มีพ่อ/แม่/พี่น้องเป็น (2)\n"
        "9️⃣ อาการเตือน B.E.F.A.S.T.: ไม่มี (0) | มึนศีรษะ/ชาปลายมือเท้า (2) | ปากเบี้ยว/แขนอ่อนแรง/พูดไม่ชัด/เดินเซ (+6)\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🎯 การแปลผลคะแนนรวม:\n"
        "🟢 0 - 4 คะแนน : ระดับที่ 1 ความเสี่ยงต่ำ\n"
        "🟡 5 - 9 คะแนน : ระดับที่ 2 ความเสี่ยงปานกลาง\n"
        "🟠 10 - 14 คะแนน : ระดับที่ 3 ความเสี่ยงสูง\n"
        "🔴 15 คะแนนขึ้นไป (หรือมีอาการ B.E.F.A.S.T.) : ระดับที่ 4 ความเสี่ยงสูงมาก (ควรพบแพทย์ด่วน / โทร 1669)\n\n"
        "พิมพ์ 'เริ่มคัดกรอง' เพื่อเริ่มทำแบบประเมินได้เลยครับ"
    )
