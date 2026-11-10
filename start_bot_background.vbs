Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
CurrentDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = CurrentDir
WshShell.Run "python start_bot.py", 0, False
MsgBox "เปิดระบบ LINE Chatbot + ngrok ในโหมดเบื้องหลัง (Background) เรียบร้อยแล้ว!" & vbCrLf & "คุณสามารถปิดหน้าต่างโปรแกรมอื่นๆ ได้เลย (หากต้องการหยุดบอท ให้ดับเบิลคลิก stop_bot.bat)", 64, "Stroke Screening Bot"
