## การติดตั้ง Python บน Windows

ดาวน์โหลด Python ล่าสุดจาก [https://www.python.org/downloads/]() เลือก Windows installer แล้วรันไฟล์. สำคัญคือติ๊ก "Add Python to PATH" ก่อนคลิก Install 

รอจนเสร็จแล้วตรวจสอบด้วยคำสั่ง `python --version` ใน Command Prompt. 

หากใช้ Miniconda แนะนำสำหรับ data science สร้าง virtual environment ด้วย `conda create -n myenv python=3.12`.[1][2][3]

## การติดตั้ง GitHub Desktop บน Windows

ดาวน์โหลดจาก [https://desktop.github.com/]() คลิก "Download for Windows (64-bit)" แล้วรันไฟล์ .exe ติดตั้งตามขั้นตอน. 

เปิดโปรแกรม สมัครหรือล็อกอิน GitHub account ตั้งค่า default storage directory ใน Tools > Options ได้. GitHub Desktop จะติดตั้ง Git อัตโนมัติสำหรับจัดการ repository.[4][5][6]

## ดึงโค้ดจาก GitHub มาใช้งาน (ตัวอย่าง https://github.com/kaebmoo/univer/)

เปิด GitHub Desktop คลิก "Clone a repository from the Internet" วาง URL `https://github.com/kaebmoo/univer/` เลือกโฟลเดอร์ปลายทางแล้วคลิก Clone. 

เปิด Command Prompt ในโฟลเดอร์นั้น พิมพ์ `cd univer` แล้ว `python -m venv venv` สร้าง virtual environment 

เปิดด้วย `venv\Scripts\activate`. 

ติดตั้ง dependencies ด้วย `pip install -r requirements.txt` ถ้ามี แล้วรัน `python main.py` หรือไฟล์หลัก.[7][5][4]

[1](https://devhub.in.th/blog/python-download-and-installation)
[2](https://www.youtube.com/watch?v=wodYroZ4_po)
[3](https://www.mindphp.com/%E0%B8%9A%E0%B8%97%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B8%AD%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%A5%E0%B8%99%E0%B9%8C/83-python/4876-installpython.html)
[4](https://www.interserver.net/tips/kb/how-to-install-and-use-git-desktop-in-windows/)
[5](https://stackoverflow.com/questions/13967353/clone-github-repo-to-specific-windows-folder)
[6](https://www.geeksforgeeks.org/git/github-desktop-download/)
[7](https://www.jcchouinard.com/clone-github-repository-on-windows/)
[8](https://www.youtube.com/watch?v=KdSXLAs_rbY)
[9](https://python-thailand.github.io/getting-python/install.html)
[10](https://www2.cs.science.cmu.ac.th/courses/204101/lib/exe/fetch.php?media=downloadandinstallpython382.pdf)