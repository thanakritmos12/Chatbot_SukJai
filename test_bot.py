"""
ไฟล์ทดสอบการทำงานของบอทคัดกรองภาวะโรคหลอดเลือดสมองในผู้ป่วยโรคเรื้อรัง
ทดสอบ:
1. การถามชื่อ-นามสกุลผู้ป่วยเมื่อเข้าใช้งานครั้งแรก
2. การประเมินความเสี่ยงทั้ง 9 ข้อ และการแปลผล
3. การจดจำชื่อ-นามสกุลอัตโนมัติเมื่อ User เดิมกลับมาทำแบบประเมินซ้ำ
4. การเปลี่ยนชื่อผู้ป่วยด้วยคำสั่ง 'เปลี่ยนชื่อ'
"""

import os
from unittest.mock import patch
from database import DatabaseManager
from screening import process_user_message


def run_tests():
    test_db_path = "test_stroke_screening.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    test_db = DatabaseManager(sqlite_path=test_db_path)

    # ปิดการยิงข้อมูลขึ้น Google Sheet จริงระหว่างรัน Unit Test
    with patch.object(DatabaseManager, "_get_google_worksheet", return_value=None):
        print("1. ทดสอบผู้ใช้ใหม่กด 'เริ่มคัดกรอง' -> ระบบต้องถามชื่อ-นามสกุลก่อน (Step 0)...")
        res = process_user_message("U_USER_01", "LINE_Sommai", "เริ่มคัดกรอง", database=test_db)
        assert res["type"] == "ask_name"
        assert res["step"] == 0

        print("2. ทดสอบพิมพ์ชื่อ-นามสกุล 'สมหมาย ใจดี' -> ระบบบันทึกชื่อและเริ่มข้อที่ 1/9 ทันที...")
        res = process_user_message("U_USER_01", "LINE_Sommai", "สมหมาย ใจดี", database=test_db)
        assert res["type"] == "question"
        assert res["step"] == 1
        assert res["patient_name"] == "สมหมาย ใจดี"
        assert test_db.get_patient_name("U_USER_01") == "สมหมาย ใจดี"

        print("3. ทดสอบตอบคำถามครบ 9 ข้อ (กรณีความเสี่ยงต่ำ - ระดับ 1)...")
        for step in range(1, 10):
            res = process_user_message("U_USER_01", "LINE_Sommai", "1", database=test_db)
            if step < 9:
                assert res["type"] == "question"
                assert res["step"] == step + 1
            else:
                assert res["type"] == "result"
                assert res["evaluation"]["level_id"] == 1
                assert res["patient_name"] == "สมหมาย ใจดี"
                print(
                    f"   -> ผลลัพธ์ครั้งที่ 1 ({res['patient_name']}): {res['evaluation']['risk_level']} "
                    f"(คะแนน {res['evaluation']['total_score']})"
                )

        print("4. ทดสอบ User เดิม ('U_USER_01') กด 'เริ่มคัดกรอง' อีกครั้ง -> ต้องจดจำชื่อ 'สมหมาย ใจดี' และข้ามไปข้อ 1 ทันที...")
        res_again = process_user_message("U_USER_01", "LINE_Sommai", "เริ่มคัดกรอง", database=test_db)
        assert res_again["type"] == "question"
        assert res_again["step"] == 1
        assert res_again["patient_name"] == "สมหมาย ใจดี"
        assert "ยินดีต้อนรับกลับมาครับ" in res_again["text"]
        print("   -> จดจำชื่อผู้ป่วยเดิมสำเร็จ ไม่ต้องกรอกชื่อซ้ำ!")

        # ตอบแบบความเสี่ยงสูงมาก (ระดับ 4)
        for _ in range(1, 10):
            res_high = process_user_message("U_USER_01", "LINE_Sommai", "3", database=test_db)
        assert res_high["type"] == "result"
        assert res_high["evaluation"]["level_id"] == 4
        print(
            f"   -> ผลลัพธ์ครั้งที่ 2 ({res_high['patient_name']}): {res_high['evaluation']['risk_level']} "
            f"(คะแนน {res_high['evaluation']['total_score']})"
        )

        print("5. ทดสอบคำสั่ง 'เปลี่ยนชื่อ' กรณีต้องการเปลี่ยนชื่อผู้ป่วย...")
        res_change = process_user_message("U_USER_01", "LINE_Sommai", "เปลี่ยนชื่อ", database=test_db)
        assert res_change["type"] == "ask_name"
        res_new_name = process_user_message("U_USER_01", "LINE_Sommai", "สมศรี ใจงาม", database=test_db)
        assert res_new_name["step"] == 1
        assert test_db.get_patient_name("U_USER_01") == "สมศรี ใจงาม"
        print("   -> เปลี่ยนชื่อผู้ป่วยเป็น 'สมศรี ใจงาม' สำเร็จ!")

    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    print("\n✅ การทดสอบทั้งหมดผ่านสมบูรณ์!")


if __name__ == "__main__":
    run_tests()
