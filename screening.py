"""
เกณฑ์การคัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง
(Stroke Risk Screening in Chronic Disease Patients)
สามารถแก้ไขคำถาม คะแนน และเกณฑ์การประเมินได้ในไฟล์นี้
"""

from typing import Any, Dict, List, Optional

# รายการคำถามคัดกรองภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง 9 ข้อ
SCREENING_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "age",
        "step": 1,
        "title": "ข้อที่ 1/9: ช่วงอายุของผู้ป่วย",
        "question": "ปัจจุบันผู้ป่วยมีอายุอยู่ในช่วงใด?",
        "choices": [
            {"key": "1", "label": "ต่ำกว่า 45 ปี", "text": "อายุต่ำกว่า 45 ปี", "score": 0},
            {"key": "2", "label": "45 - 59 ปี", "text": "อายุ 45 - 59 ปี", "score": 1},
            {"key": "3", "label": "60 ปีขึ้นไป", "text": "อายุ 60 ปีขึ้นไป", "score": 2},
        ],
    },
    {
        "id": "chronic_disease",
        "step": 2,
        "title": "ข้อที่ 2/9: โรคประจำตัวเรื้อรังที่เป็นอยู่",
        "question": "ผู้ป่วยมีโรคประจำตัวเรื้อรังในกลุ่มใดต่อไปนี้?",
        "choices": [
            {
                "key": "1",
                "label": "มี 1 โรคเรื้อรัง",
                "text": "มีโรคเรื้อรัง 1 โรค (เช่น ความดันสูง หรือเบาหวาน หรือไขมันสูง)",
                "score": 1,
            },
            {
                "key": "2",
                "label": "มี 2 โรคขึ้นไป",
                "text": "มีโรคเรื้อรังร่วมกันตั้งแต่ 2 โรคขึ้นไป (เช่น ความดันสูง+เบาหวาน/ไขมัน/โรคไต)",
                "score": 2,
            },
            {
                "key": "3",
                "label": "โรคหัวใจ/เคยเป็นสโตรก",
                "text": "มีภาวะหัวใจเต้นผิดจังหวะ (AF) โรคหัวใจ หรือเคยเป็นอัมพฤกษ์-อัมพาตมาก่อน",
                "score": 4,
            },
        ],
    },
    {
        "id": "bp_control",
        "step": 3,
        "title": "ข้อที่ 3/9: การควบคุมระดับความดันโลหิต",
        "question": "ในช่วงที่ผ่านมา ค่าความดันโลหิตของผู้ป่วยอยู่ในเกณฑ์ใด?",
        "choices": [
            {
                "key": "1",
                "label": "คุมได้ดี (<140/90)",
                "text": "ควบคุมได้ดี (< 140/90 mmHg)",
                "score": 0,
            },
            {
                "key": "2",
                "label": "สูงบางครั้ง/ไม่ได้วัด",
                "text": "สูงเป็นบางครั้ง (140/90 - 159/99 mmHg) หรือไม่ได้วัดสม่ำเสมอ",
                "score": 2,
            },
            {
                "key": "3",
                "label": "สูงมาก (>=160/100)",
                "text": "ความดันสูงมาก (>= 160/100 mmHg) หรือควบคุมไม่ได้",
                "score": 3,
            },
        ],
    },
    {
        "id": "sugar_lipid",
        "step": 4,
        "title": "ข้อที่ 4/9: การควบคุมระดับน้ำตาลและไขมันในเลือด",
        "question": "ผลตรวจระดับน้ำตาลในเลือด (หรือ HbA1c) และไขมันในเลือด (LDL) ล่าสุดเป็นอย่างไร?",
        "choices": [
            {
                "key": "1",
                "label": "อยู่ในเกณฑ์ปกติ",
                "text": "ผลเลือดอยู่ในเกณฑ์เป้าหมายตามที่แพทย์กำหนด",
                "score": 0,
            },
            {
                "key": "2",
                "label": "สูงกว่าเกณฑ์เล็กน้อย",
                "text": "น้ำตาลหรือไขมันในเลือดสูงกว่าเกณฑ์เล็กน้อย หรือไม่ทราบผลล่าสุด",
                "score": 1,
            },
            {
                "key": "3",
                "label": "น้ำตาล/ไขมันสูงมาก",
                "text": "น้ำตาลในเลือดสูงมาก (FBS >= 180 หรือ HbA1c >= 8%) หรือไขมันสูงมากคุมไม่ได้",
                "score": 2,
            },
        ],
    },
    {
        "id": "med_adherence",
        "step": 5,
        "title": "ข้อที่ 5/9: ความสม่ำเสมอในการรับประทานยา",
        "question": "ผู้ป่วยรับประทานยาโรคประจำตัวและไปพบแพทย์ตามนัดสม่ำเสมอหรือไม่?",
        "choices": [
            {
                "key": "1",
                "label": "ทานยาครบทุกวัน",
                "text": "ทานยาสม่ำเสมอทุกวันและไปตามนัดแพทย์ทุกครั้ง",
                "score": 0,
            },
            {
                "key": "2",
                "label": "ลืมทานยาบางครั้ง",
                "text": "ลืมทานยาเป็นบางครั้ง (1-2 ครั้ง/สัปดาห์)",
                "score": 1,
            },
            {
                "key": "3",
                "label": "ขาดยาบ่อย/หยุดยาเอง",
                "text": "ขาดยาบ่อย หยุดยาเอง หรือขาดนัดแพทย์",
                "score": 3,
            },
        ],
    },
    {
        "id": "smoking_alcohol",
        "step": 6,
        "title": "ข้อที่ 6/9: การสูบบุหรี่และดื่มแอลกอฮอล์",
        "question": "ผู้ป่วยมีพฤติกรรมการสูบบุหรี่ (หรือได้รับควันบุหรี่) และดื่มแอลกอฮอล์หรือไม่?",
        "choices": [
            {
                "key": "1",
                "label": "ไม่สูบและไม่ดื่ม",
                "text": "ไม่สูบบุหรี่ และไม่ดื่มแอลกอฮอล์",
                "score": 0,
            },
            {
                "key": "2",
                "label": "เคยสูบ/ดื่มครั้งคราว",
                "text": "เคยสูบบุหรี่ หรือดื่มแอลกอฮอล์เป็นครั้งคราว",
                "score": 1,
            },
            {
                "key": "3",
                "label": "สูบประจำ/ดื่มบ่อย",
                "text": "สูบบุหรี่เป็นประจำ หรือดื่มแอลกอฮอล์บ่อย",
                "score": 3,
            },
        ],
    },
    {
        "id": "bmi_exercise",
        "step": 7,
        "title": "ข้อที่ 7/9: รูปร่าง น้ำหนักตัว และการออกกำลังกาย",
        "question": "รูปร่าง (BMI/รอบเอว) และกิจกรรมทางกายของผู้ป่วยเป็นอย่างไร?",
        "choices": [
            {
                "key": "1",
                "label": "สมส่วน+ออกกำลังกาย",
                "text": "น้ำหนักปกติ และออกกำลังกายสม่ำเสมอ (>= 3 ครั้ง/สัปดาห์)",
                "score": 0,
            },
            {
                "key": "2",
                "label": "ท้วม/ออกกำลังน้อย",
                "text": "น้ำหนักเกินเล็กน้อย หรือออกกำลังกายนานๆ ครั้ง",
                "score": 1,
            },
            {
                "key": "3",
                "label": "อ้วนลงพุง+ไม่ออกกำลัง",
                "text": "อ้วนลงพุง (BMI >= 25) และแทบไม่ได้ออกกำลังกาย",
                "score": 2,
            },
        ],
    },
    {
        "id": "family_stroke",
        "step": 8,
        "title": "ข้อที่ 8/9: ประวัติครอบครัวเป็นโรคหลอดเลือดสมอง",
        "question": "มีคนในครอบครัวสายตรง (พ่อ, แม่, พี่น้อง) เคยป่วยเป็นโรคหลอดเลือดสมอง (อัมพฤกษ์/อัมพาต) หรือไม่?",
        "choices": [
            {
                "key": "1",
                "label": "ไม่มี",
                "text": "ไม่มีประวัติในครอบครัว",
                "score": 0,
            },
            {
                "key": "2",
                "label": "ไม่แน่ใจ",
                "text": "ไม่แน่ใจ",
                "score": 1,
            },
            {
                "key": "3",
                "label": "มี (พ่อ/แม่/พี่น้อง)",
                "text": "มีประวัติคนในครอบครัวสายตรงเป็นโรคหลอดเลือดสมอง",
                "score": 2,
            },
        ],
    },
    {
        "id": "befast_symptoms",
        "step": 9,
        "title": "ข้อที่ 9/9: อาการเตือนโรคหลอดเลือดสมอง (B.E.F.A.S.T.)",
        "question": "ผู้ป่วยเคยมีอาการเตือนเหล่านี้หรือไม่? (แม้เป็นชั่วคราวแล้วหายเอง)\n• เดินเซ เวียนศีรษะบ้านหมุนฉับพลัน (Balance)\n• ตาพร่ามัว มองเห็นภาพซ้อนฉับพลัน (Eyes)\n• หน้าเบี้ยว ปากเบี้ยว มุมปากตก (Face)\n• แขนขาอ่อนแรงหรือชาครึ่งซีก (Arms)\n• พูดไม่ชัด ลิ้นแข็ง นึกคำพูดไม่ออก (Speech)",
        "choices": [
            {
                "key": "1",
                "label": "ไม่มีอาการเลย",
                "text": "ไม่มีอาการผิดปกติ",
                "score": 0,
            },
            {
                "key": "2",
                "label": "มึนศีรษะ/ชาปลายมือเท้า",
                "text": "มีอาการมึนศีรษะ หรือชาปลายมือปลายเท้าเป็นบางครั้ง",
                "score": 2,
            },
            {
                "key": "3",
                "label": "มีอาการ B.E.F.A.S.T.",
                "text": "มีอาการเตือน B.E.F.A.S.T. (ปากเบี้ยว/แขนขาอ่อนแรงครึ่งซีก/พูดไม่ชัด/เดินเซ/ตาพร่าฉับพลัน)",
                "score": 6,
            },
        ],
    },
]

# เกณฑ์การแบ่งระดับความเสี่ยงภาวะโรคหลอดเลือดสมอง 4 ระดับ พร้อมคำแนะนำสำหรับผู้ป่วยโรคเรื้อรัง
RISK_LEVELS: List[Dict[str, Any]] = [
    {
        "level_id": 1,
        "min_score": 0,
        "max_score": 4,
        "name": "ระดับที่ 1: ความเสี่ยงต่ำ (Low Stroke Risk)",
        "short_name": "ความเสี่ยงต่ำ",
        "probability": "ความเสี่ยงต่อภาวะโรคหลอดเลือดสมองอยู่ในเกณฑ์ต่ำ (< 10%)",
        "color": "#2E7D32",  # สีเขียว
        "badge_bg": "#E8F5E9",
        "summary": "ผู้ป่วยควบคุมโรคประจำตัวเรื้อรังและพฤติกรรมสุขภาพได้ดี มีปัจจัยเสี่ยงต่อโรคหลอดเลือดสมองน้อย",
        "recommendations": [
            "รับประทานยาโรคประจำตัวต่อเนื่องทุกวันตามแพทย์สั่ง ห้ามหยุดยาหรือปรับลดยาเอง",
            "ควบคุมความดันโลหิตให้ต่ำกว่า 130/80 mmHg และรักษาระดับน้ำตาล/ไขมันให้อยู่ในเกณฑ์ปกติ",
            "รับประทานอาหารลดหวาน-มัน-เค็ม เน้นผักผลไม้ และออกกำลังกายสม่ำเสมออย่างน้อย 150 นาที/สัปดาห์",
            "หมั่นสังเกตสัญญาณเตือน B.E.F.A.S.T. (เดินเซ ตาพร่า หน้าเบี้ยว แขนอ่อนแรง พูดไม่ชัด) และไปพบแพทย์ตามนัดทุกครั้ง",
        ],
    },
    {
        "level_id": 2,
        "min_score": 5,
        "max_score": 9,
        "name": "ระดับที่ 2: ความเสี่ยงปานกลาง (Moderate Stroke Risk)",
        "short_name": "ความเสี่ยงปานกลาง",
        "probability": "เริ่มมีปัจจัยเสี่ยงสะสมต่อภาวะหลอดเลือดสมองตีบ/แตก (20% - 40%)",
        "color": "#EF6C00",  # สีส้มเหลือง
        "badge_bg": "#FFF3E0",
        "summary": "ผู้ป่วยมีปัจจัยเสี่ยงจากโรคเรื้อรังหรือพฤติกรรมบางส่วนที่ยังควบคุมได้ไม่เต็มที่",
        "recommendations": [
            "เคร่งครัดในการทานยาโรคประจำตัวให้ตรงเวลาทุกวัน หากลืมทานยาบ่อยควรตั้งนาฬิกาเตือนหรือใช้กล่องจัดยา",
            "ตรวจวัดความดันโลหิตที่บ้านอย่างน้อยสัปดาห์ละ 2-3 ครั้ง และจดบันทึกไปให้แพทย์ดูเมื่อถึงวันนัด",
            "ลดอาหารเค็มจัด อาหารมัน และของหวาน งดสูบบุหรี่และหลีกเลี่ยงเครื่องดื่มแอลกอฮอล์",
            "ควบคุมน้ำหนักตัวและรอบเอว พร้อมออกกำลังกายเบาๆ เช่น เดินเร็ว แกว่งแขน อย่างน้อย 30 นาที/วัน",
        ],
    },
    {
        "level_id": 3,
        "min_score": 10,
        "max_score": 14,
        "name": "ระดับที่ 3: ความเสี่ยงสูง (High Stroke Risk)",
        "short_name": "ความเสี่ยงสูง",
        "probability": "มีความเสี่ยงสูงต่อการเกิดภาวะโรคหลอดเลือดสมอง (50% - 75%)",
        "color": "#D84315",  # สีส้มอมแดง
        "badge_bg": "#FBE9E7",
        "summary": "ผู้ป่วยมีปัจจัยเสี่ยงสะสมหลายด้าน เช่น โรคเรื้อรังหลายโรค การคุมความดัน/น้ำตาลยังไม่ดี หรือขาดยา",
        "recommendations": [
            "แนะนำให้ปรึกษาแพทย์ประจำตัวเพื่อประเมินความเสี่ยงโรคหลอดเลือดสมองและปรับแผนการใช้ยาควบคุมโรคเรื้อรัง",
            "วัดความดันโลหิตทุกวัน (เช้าหลังตื่นนอน และก่อนนอน) หากสูงเกิน 140/90 mmHg ต่อเนื่องควรพบแพทย์ก่อนนัด",
            "งดสูบบุหรี่และงดเครื่องดื่มแอลกอฮอล์โดยเด็ดขาด เพราะเป็นตัวเร่งให้หลอดเลือดสมองตีบและแตกได้ง่าย",
            "ผู้ป่วยและคนใกล้ชิดต้องจดจำอาการ B.E.F.A.S.T. หากมีอาการเพียงข้อใดข้อหนึ่ง ต้องรีบไปโรงพยาบาลทันที",
        ],
    },
    {
        "level_id": 4,
        "min_score": 15,
        "max_score": 999,
        "name": "ระดับที่ 4: ความเสี่ยงสูงมาก / มีสัญญาณเตือน (Very High Stroke Risk)",
        "short_name": "ความเสี่ยงสูงมาก (ควรพบแพทย์ด่วน)",
        "probability": "มีความเสี่ยงสูงมากต่อการเกิดโรคหลอดเลือดสมองเฉียบพลัน (> 80%) หรือมีอาการเตือนสำคัญ",
        "color": "#C62828",  # สีแดงเข้ม
        "badge_bg": "#FFEBEE",
        "summary": "พบปัจจัยเสี่ยงรุนแรง หรือมีสัญญาณเตือนของภาวะสมองขาดเลือดชั่วคราว (TIA) / โรคหลอดเลือดสมอง",
        "recommendations": [
            "🚨 หากกำลังมีอาการ ปากเบี้ยว แขนขาอ่อนแรงครึ่งซีก พูดไม่ชัด เดินเซ หรือตาพร่ามัวฉับพลัน ให้โทร 1669 หรือไปโรงพยาบาลทันที (ภายใน 4.5 ชั่วโมง / Stroke Fast Track)",
            "หากอาการเตือนเป็นชั่วคราวแล้วหายเอง (TIA) ห้ามนิ่งนอนใจเด็ดขาด ต้องรีบไปพบแพทย์เพื่อตรวจสมองและหลอดเลือดโดยเร็วที่สุด",
            "รับประทานยาควบคุมความดัน เบาหวาน ไขมัน หรือยาต้านเกล็ดเลือด/ยาละลายลิ่มเลือดตามแพทย์สั่งอย่างเคร่งครัด ห้ามขาดยาแม้แต่วันเดียว",
            "ต้องมีผู้ดูแลหรือคนในครอบครัวคอยเฝ้าระวังอาการอย่างใกล้ชิด และจัดเตรียมเบอร์ฉุกเฉิน 1669 ไว้ให้พร้อมเสมอ",
        ],
    },
]


def get_question(step: int) -> Optional[Dict[str, Any]]:
    """ดึงข้อมูลคำถามตามลำดับข้อ (1 ถึง 9)"""
    for q in SCREENING_QUESTIONS:
        if q["step"] == step:
            return q
    return None


def parse_answer(question: Dict[str, Any], user_input: str) -> Optional[Dict[str, Any]]:
    """
    ตรวจสอบคำตอบของผู้ใช้กับตัวเลือกของคำถามนั้นๆ
    รองรับทั้งการกดปุ่ม Quick Reply (เช่น '1', '2', 'ans:1:2') หรือพิมพ์ข้อความตัวเลือก
    """
    cleaned = user_input.strip()

    if cleaned.startswith("ans:"):
        parts = cleaned.split(":")
        if len(parts) == 3:
            cleaned = parts[2]

    for choice in question["choices"]:
        if (
            cleaned == choice["key"]
            or cleaned == choice["label"]
            or cleaned == choice["text"]
            or cleaned.startswith(f"{choice['key']}.")
        ):
            return choice
    return None


def evaluate_risk(answers: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    คำนวณคะแนนรวมและประเมินระดับความเสี่ยงภาวะโรคหลอดเลือดสมองจากคำตอบทั้ง 9 ข้อ
    """
    total_score = sum(item.get("score", 0) for item in answers.values())

    # กรณีพิเศษ: หากผู้ป่วยมีอาการเตือน B.E.F.A.S.T. (ข้อ 9 ตอบตัวเลือก 3)
    # ให้จัดอยู่ในระดับที่ 4 (ความเสี่ยงสูงมาก / มีสัญญาณเตือนอันตราย) ทันที
    befast_answer = answers.get("befast_symptoms", {})
    force_very_high = befast_answer.get("key") == "3"

    selected_level = RISK_LEVELS[-1]
    for level in RISK_LEVELS:
        if level["min_score"] <= total_score <= level["max_score"]:
            selected_level = level
            break

    if force_very_high and selected_level["level_id"] < 4:
        selected_level = RISK_LEVELS[3]

    risk_factors = []
    for q in SCREENING_QUESTIONS:
        qid = q["id"]
        ans = answers.get(qid)
        if ans and ans.get("score", 0) > 0:
            risk_factors.append(f"{ans['text']} (+{ans['score']} คะแนน)")

    return {
        "total_score": total_score,
        "max_possible_score": 25,
        "level_id": selected_level["level_id"],
        "risk_level": selected_level["name"],
        "short_name": selected_level["short_name"],
        "probability": selected_level["probability"],
        "color": selected_level["color"],
        "badge_bg": selected_level["badge_bg"],
        "summary": selected_level["summary"],
        "recommendations": selected_level["recommendations"],
        "risk_factors": risk_factors,
    }


def _start_step_1_for_known_patient(
    user_id: str, display_name: str, patient_name: str, database: Any, is_returning: bool = True
) -> Dict[str, Any]:
    """เริ่มคำถามข้อที่ 1 ทันทีเมื่อทราบชื่อ-นามสกุลของผู้ป่วยแล้ว"""
    from flex_templates import build_question_text_and_choices

    database.start_session(
        user_id=user_id,
        display_name=display_name,
        patient_name=patient_name,
        initial_step=1,
    )
    q1 = get_question(1)
    q_payload = build_question_text_and_choices(q1)

    if is_returning:
        greeting = (
            f"👋 ยินดีต้อนรับกลับมาครับ\n"
            f"👤 ผู้รับการคัดกรอง: คุณ{patient_name}\n"
            f"(ระบบจดจำชื่อ-นามสกุลของคุณไว้แล้ว หากต้องการเปลี่ยนชื่อผู้ป่วย กดปุ่ม '✏️ เปลี่ยนชื่อผู้ป่วย' ด้านล่างได้ครับ)\n\n"
        )
    else:
        greeting = (
            f"✅ บันทึกชื่อ-นามสกุลผู้ป่วย: คุณ{patient_name} เรียบร้อยแล้วครับ\n"
            f"(ครั้งต่อไปที่ใช้ LINE นี้ ระบบจะจดจำชื่อให้โดยอัตโนมัติครับ)\n\n"
        )

    quick_replies = list(q_payload["quick_replies"])
    quick_replies.insert(-1, {"label": "✏️ เปลี่ยนชื่อผู้ป่วย", "text": "เปลี่ยนชื่อ"})

    return {
        "type": "question",
        "text": (
            f"{greeting}"
            f"🧠 เริ่มการคัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง (9 ข้อ)\n\n"
            f"{q_payload['text']}"
        ),
        "quick_replies": quick_replies,
        "step": 1,
        "patient_name": patient_name,
    }


def process_user_message(
    user_id: str, display_name: str, user_text: str, database: Any
) -> Dict[str, Any]:
    """
    ประมวลผลข้อความจากผู้ใช้ และคืนค่าข้อความตอบกลับพร้อมปุ่มตัวเลือกหรือ Flex Card
    รองรับการถามชื่อ-นามสกุลผู้ป่วยก่อนเริ่มทำแบบประเมิน และจดจำชื่ออัตโนมัติสำหรับ User เดิม
    """
    from flex_templates import (
        build_criteria_text,
        build_question_text_and_choices,
        build_result_flex,
        build_welcome_flex,
    )

    text = user_text.strip()

    # 1. คำสั่งเปลี่ยนชื่อ-นามสกุลผู้ป่วย
    if text in ("เปลี่ยนชื่อ", "เปลี่ยนชื่อผู้ป่วย", "แก้ไขชื่อ"):
        database.start_session(
            user_id=user_id,
            display_name=display_name,
            patient_name="",
            initial_step=0,
        )
        return {
            "type": "ask_name",
            "text": (
                "📝 กรุณาพิมพ์ **ชื่อ-นามสกุล** ใหม่ของผู้ป่วยที่ต้องการคัดกรองครับ\n"
                "(ตัวอย่างเช่น: สมชาย ใจดี)"
            ),
            "quick_replies": [
                {"label": "❌ ยกเลิก", "text": "ยกเลิก"},
            ],
            "step": 0,
        }

    # 2. คำสั่งเริ่มทำแบบคัดกรองใหม่
    if text in ("เริ่ม", "เริ่มคัดกรอง", "คัดกรอง", "ประเมิน", "ทำแบบประเมิน", "start"):
        remembered_name = database.get_patient_name(user_id)
        if remembered_name:
            # กรณี User เดิมที่เคยลงทะเบียนชื่อ-นามสกุลไว้แล้ว -> จดจำชื่อและเริ่มข้อ 1 ทันที
            return _start_step_1_for_known_patient(
                user_id=user_id,
                display_name=display_name,
                patient_name=remembered_name,
                database=database,
                is_returning=True,
            )
        else:
            # กรณี User ใหม่ -> ถามชื่อ-นามสกุลก่อน (Step 0)
            database.start_session(
                user_id=user_id,
                display_name=display_name,
                patient_name="",
                initial_step=0,
            )
            return {
                "type": "ask_name",
                "text": (
                    "📝 ก่อนเริ่มทำแบบคัดกรองภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง\n\n"
                    "กรุณาพิมพ์ **ชื่อ-นามสกุล** ของผู้ป่วยครับ\n"
                    "(ตัวอย่างเช่น: สมชาย ใจดี)\n\n"
                    "💡 ระบบจะจดจำชื่อ-นามสกุลไว้สำหรับบัญชี LINE ของคุณ เพื่อความสะดวกในการใช้งานครั้งต่อไปครับ"
                ),
                "quick_replies": [
                    {"label": "❌ ยกเลิก", "text": "ยกเลิก"},
                ],
                "step": 0,
            }

    # 3. คำสั่งยกเลิกการทำแบบคัดกรอง
    if text in ("ยกเลิก", "cancel", "หยุด"):
        database.clear_session(user_id)
        return {
            "type": "text",
            "text": "ยกเลิกการทำแบบคัดกรองปัจจุบันแล้วครับ หากต้องการเริ่มใหม่ กดปุ่ม 'เริ่มคัดกรอง' ได้ทุกเมื่อครับ",
            "quick_replies": [
                {"label": "🧠 เริ่มคัดกรองใหม่", "text": "เริ่มคัดกรอง"},
                {"label": "✏️ เปลี่ยนชื่อผู้ป่วย", "text": "เปลี่ยนชื่อ"},
                {"label": "📊 เกณฑ์การประเมิน", "text": "เกณฑ์การประเมิน"},
                {"label": "📋 ดูประวัติล่าสุด", "text": "ประวัติ"},
            ],
        }

    # 4. คำสั่งดูเกณฑ์การให้คะแนน
    if text in ("เกณฑ์", "เกณฑ์การประเมิน", "ความรู้", "criteria"):
        return {
            "type": "text",
            "text": build_criteria_text(),
            "quick_replies": [
                {"label": "🧠 เริ่มคัดกรอง", "text": "เริ่มคัดกรอง"},
                {"label": "📋 ดูประวัติล่าสุด", "text": "ประวัติ"},
            ],
        }

    # 5. คำสั่งดูประวัติผลการคัดกรองล่าสุดของผู้ใช้
    if text in ("ประวัติ", "ดูประวัติ", "ผลล่าสุด", "history"):
        latest = database.get_latest_record(user_id)
        if not latest:
            return {
                "type": "text",
                "text": "ยังไม่มีประวัติการคัดกรองของคุณในระบบครับ กดปุ่ม 'เริ่มคัดกรอง' ด้านล่างเพื่อประเมินได้เลย",
                "quick_replies": [
                    {"label": "🧠 เริ่มคัดกรอง", "text": "เริ่มคัดกรอง"},
                    {"label": "📊 เกณฑ์การประเมิน", "text": "เกณฑ์การประเมิน"},
                ],
            }
        patient_label = latest.get("patient_name") or latest.get("display_name") or "-"
        history_msg = (
            f"📋 ประวัติการคัดกรองภาวะโรคหลอดเลือดสมองล่าสุด\n"
            f"👤 ชื่อ-นามสกุลผู้ป่วย: {patient_label}\n"
            f"🕒 วันที่: {latest['timestamp']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"• ผลการประเมิน: {latest['risk_level']}\n"
            f"• คะแนนรวม: {latest['total_score']} คะแนน\n"
            f"• โอกาสเกิดโรค: {latest['probability']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 คำแนะนำ:\n- " + latest["recommendations"].replace(" | ", "\n- ")
        )
        return {
            "type": "text",
            "text": history_msg,
            "quick_replies": [
                {"label": "🧠 ทำแบบคัดกรองใหม่", "text": "เริ่มคัดกรอง"},
                {"label": "✏️ เปลี่ยนชื่อผู้ป่วย", "text": "เปลี่ยนชื่อ"},
                {"label": "📊 เกณฑ์การประเมิน", "text": "เกณฑ์การประเมิน"},
            ],
        }

    # 6. ตรวจสอบว่าผู้ใช้อยู่ระหว่างทำแบบคัดกรองหรือไม่
    session = database.get_session(user_id)
    if session:
        current_step = session["current_step"]

        # Step 0: ผู้ใช้กำลังพิมพ์ชื่อ-นามสกุลของผู้ป่วย
        if current_step == 0:
            cleaned_name = " ".join(text.split())
            # ตรวจสอบความถูกต้องเบื้องต้นของชื่อ-นามสกุล
            if len(cleaned_name) < 2 or cleaned_name.isdigit():
                return {
                    "type": "ask_name",
                    "text": (
                        "⚠️ กรุณาพิมพ์ **ชื่อ-นามสกุล** ของผู้ป่วยเป็นตัวอักษรให้ถูกต้องครับ\n"
                        "(ตัวอย่างเช่น: สมชาย ใจดี)"
                    ),
                    "quick_replies": [
                        {"label": "❌ ยกเลิก", "text": "ยกเลิก"},
                    ],
                    "step": 0,
                }

            # บันทึกชื่อ-นามสกุลลงฐานข้อมูลเพื่อจดจำไว้สำหรับ User ID นี้
            database.save_patient_name(
                user_id=user_id,
                patient_name=cleaned_name,
                display_name=display_name,
            )
            return _start_step_1_for_known_patient(
                user_id=user_id,
                display_name=display_name,
                patient_name=cleaned_name,
                database=database,
                is_returning=False,
            )

        # Step 1 - 9: ผู้ใช้กำลังตอบคำถามข้อ 1 - 9
        question = get_question(current_step)
        if question:
            matched_choice = parse_answer(question, text)
            if not matched_choice:
                q_payload = build_question_text_and_choices(question)
                return {
                    "type": "question",
                    "text": (
                        f"⚠️ กรุณาเลือกคำตอบด้วยหมายเลข 1 - {len(question['choices'])} "
                        f"หรือกดปุ่มตัวเลือกด้านล่างครับ\n\n{q_payload['text']}"
                    ),
                    "quick_replies": q_payload["quick_replies"],
                    "step": current_step,
                }

            answers = session["answers"]
            answers[question["id"]] = {
                "key": matched_choice["key"],
                "text": matched_choice["text"],
                "score": matched_choice["score"],
            }

            total_questions = len(SCREENING_QUESTIONS)
            if current_step < total_questions:
                next_step = current_step + 1
                database.update_session(user_id, next_step, answers)
                next_q = get_question(next_step)
                q_payload = build_question_text_and_choices(next_q)
                return {
                    "type": "question",
                    "text": f"✅ บันทึกข้อ {current_step} แล้ว: {matched_choice['text']}\n\n{q_payload['text']}",
                    "quick_replies": q_payload["quick_replies"],
                    "step": next_step,
                }
            else:
                patient_name = (
                    session.get("patient_name")
                    or database.get_patient_name(user_id)
                    or display_name
                )
                evaluation = evaluate_risk(answers)
                saved_info = database.save_screening_result(
                    user_id=user_id,
                    display_name=session.get("display_name") or display_name,
                    patient_name=patient_name,
                    answers=answers,
                    evaluation=evaluation,
                )
                database.clear_session(user_id)

                flex_bubble = build_result_flex(
                    patient_name=patient_name,
                    evaluation=evaluation,
                    saved_info=saved_info,
                )

                rec_bullets = "\n".join(
                    f"  {i}. {r}" for i, r in enumerate(evaluation["recommendations"], 1)
                )
                summary_text = (
                    f"📊 ผลการคัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง\n"
                    f"👤 ชื่อ-นามสกุลผู้ป่วย: {patient_name}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 ผลลัพธ์: {evaluation['risk_level']}\n"
                    f"🔢 คะแนนรวม: {evaluation['total_score']} คะแนน\n"
                    f"📈 {evaluation['probability']}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"💡 คำแนะนำการปฏิบัติตัว:\n{rec_bullets}"
                )

                return {
                    "type": "result",
                    "text": summary_text,
                    "flex": flex_bubble,
                    "evaluation": evaluation,
                    "saved_info": saved_info,
                    "patient_name": patient_name,
                    "quick_replies": [
                        {"label": "🧠 คัดกรองอีกครั้ง", "text": "เริ่มคัดกรอง"},
                        {"label": "✏️ เปลี่ยนชื่อผู้ป่วย", "text": "เปลี่ยนชื่อ"},
                        {"label": "📋 ดูประวัติล่าสุด", "text": "ประวัติ"},
                        {"label": "📊 เกณฑ์การประเมิน", "text": "เกณฑ์การประเมิน"},
                    ],
                }

    # 7. กรณีไม่ได้อยู่ใน Session การคัดกรอง -> ส่งการ์ดต้อนรับพร้อมแสดงชื่อผู้ป่วยหากจำได้
    remembered_name = database.get_patient_name(user_id)
    welcome_note = (
        f"\n👤 ผู้ป่วยที่บันทึกไว้: คุณ{remembered_name}" if remembered_name else ""
    )
    quick_replies = [
        {"label": "🧠 เริ่มคัดกรอง (9 ข้อ)", "text": "เริ่มคัดกรอง"},
        {"label": "📊 เกณฑ์การประเมิน", "text": "เกณฑ์การประเมิน"},
        {"label": "📋 ดูประวัติล่าสุด", "text": "ประวัติ"},
    ]
    if remembered_name:
        quick_replies.insert(1, {"label": "✏️ เปลี่ยนชื่อผู้ป่วย", "text": "เปลี่ยนชื่อ"})

    return {
        "type": "welcome",
        "text": (
            f"สวัสดีครับ 🙏 ยินดีต้อนรับสู่ระบบคัดกรองความเสี่ยงภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง{welcome_note}\n"
            f"กดปุ่ม 'เริ่มทำแบบคัดกรอง' ด้านล่างเพื่อเริ่มประเมินความเสี่ยง 9 ข้อได้เลยครับ"
        ),
        "flex": build_welcome_flex(remembered_name=remembered_name),
        "quick_replies": quick_replies,
    }
