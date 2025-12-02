# คู่มือการใช้งาน Univer Report System

เอกสารนี้ให้คำแนะนำในการตั้งค่า (Setup), รัน (Run) และใช้งาน (Usage) โปรเจกต์ Univer Report System ทั้งส่วนของ Backend และ Frontend ที่ได้รับการปรับปรุงเพื่อแสดงผลไฟล์ Excel ผ่านเว็บ

---

## 1. การตั้งค่าและรัน Backend

Backend ใช้ FastAPI ในการทำงาน และมี Service สำหรับแปลงไฟล์ Excel เป็น Univer JSON

### 1.1. การเตรียมสภาพแวดล้อม (Environment Setup)

1.  **เข้าสู่ Directory ของ Backend:**
    ```bash
    cd /Users/seal/Documents/GitHub/univer/backend
    ```

2.  **สร้าง Virtual Environment (แนะนำ):**
    ```bash
    python3 -m venv venv
    ```

3.  **Activate Virtual Environment:**
    *   **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
    *   **Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate.ps1
        ```

4.  **ติดตั้ง Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **ตั้งค่า Environment Variables:**
    *   ตรวจสอบไฟล์ `.env.example` ใน directory เดียวกัน
    *   สร้างไฟล์ `.env` (ถ้ายังไม่มี) และคัดลอกเนื้อหาจาก `.env.example` มาวาง
    *   ปรับค่าตามต้องการ (เช่น `SECRET_KEY`, `DATABASE_URL` ถ้ามีการใช้งาน)
    *   **สำคัญ:** `API_BASE_URL` ใน Frontend ควรจะชี้มาที่ Backend นี้ (ปกติคือ `http://localhost:8000`)

### 1.2. การรัน Backend Application

หลังจากติดตั้ง Dependencies เรียบร้อยแล้ว ให้รัน Backend โดยใช้ Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*   `--host 0.0.0.0`: ทำให้ Backend สามารถเข้าถึงได้จากภายนอก (ถ้าจำเป็น)
*   `--port 8000`: กำหนด port ที่ Backend จะทำงาน
*   `--reload`: จะทำการโหลดโค้ดใหม่โดยอัตโนมัติเมื่อมีการเปลี่ยนแปลง (เหมาะสำหรับการพัฒนา)

เมื่อรันสำเร็จ คุณจะเห็นข้อความประมาณ `Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`

---

## 2. การตั้งค่าและรัน Frontend

Frontend ใช้ React, TypeScript และ Vite ในการทำงาน

### 2.1. การเตรียมสภาพแวดล้อม (Environment Setup)

1.  **เข้าสู่ Directory ของ Frontend:**
    ```bash
    cd /Users/seal/Documents/GitHub/univer/frontend
    ```

2.  **ติดตั้ง Dependencies:**
    ```bash
    npm install
    # หรือ
    # yarn install
    ```

3.  **ตั้งค่า Environment Variables (ถ้ามี):**
    *   ตรวจสอบไฟล์ `.env` ใน directory เดียวกัน
    *   ตรวจสอบให้แน่ใจว่า `VITE_API_BASE_URL` ชี้ไปยัง Backend ที่รันอยู่ (เช่น `VITE_API_BASE_URL=http://localhost:8000`)

### 2.2. การรัน Frontend Application

หลังจากติดตั้ง Dependencies เรียบร้อยแล้ว ให้รัน Frontend โดยใช้ Vite:

```bash
npm run dev
# หรือ
# yarn dev
```
เมื่อรันสำเร็จ คุณจะเห็นข้อความประมาณ `Local: http://localhost:5173/` (หรือ port อื่นๆ) ซึ่งเป็น URL สำหรับเข้าถึง Frontend

---

## 3. การใช้งาน Web Application (Frontend)

หลังจากรันทั้ง Backend และ Frontend แล้ว คุณสามารถเข้าใช้งานระบบได้ดังนี้:

1.  **เปิด Web Browser:** ไปที่ URL ของ Frontend (เช่น `http://localhost:5173/`)

2.  **เข้าสู่ระบบ (Login):**
    *   ระบบจะนำคุณไปยังหน้า Login (หากยังไม่ได้เข้าสู่ระบบ)
    *   ป้อน Email และคลิก "Request OTP"
    *   ป้อนรหัส OTP ที่ได้รับทาง Email และคลิก "Verify OTP"
    *   หากการยืนยันตัวตนสำเร็จ คุณจะเข้าสู่หน้าหลักของระบบ

3.  **ดูรายการรายงาน Excel:**
    *   เมื่อเข้าสู่ระบบสำเร็จ คุณจะเห็นหน้าจอแสดงรายการ **"Pre-generated Excel Reports"**
    *   หน้านี้จะแสดงรายชื่อไฟล์ Excel ทั้งหมด (`.xlsx`) ที่อยู่ในโฟลเดอร์ `/Users/seal/Documents/GitHub/univer/report_generator/output`
    *   ระบบจะแสดงสถานะ Loading ขณะดึงข้อมูลและข้อความ Error หากมีปัญหา

4.  **ดูรายงาน Excel:**
    *   เลือกไฟล์ Excel ที่ต้องการจากรายการ
    *   คลิกปุ่ม **"View"** ที่อยู่ถัดจากชื่อไฟล์
    *   ระบบจะสลับไปหน้า Report Viewer ซึ่งจะโหลดไฟล์ Excel นั้นมาแสดงผลในรูปแบบ Spreadsheet ที่โต้ตอบได้
    *   คุณจะเห็นตาราง Excel ที่มีข้อมูล, สไตล์, การรวมเซลล์, ความกว้างคอลัมน์ และความสูงแถว ตรงตามไฟล์ต้นฉบับ
    *   หากต้องการกลับไปหน้ารายการไฟล์ ให้คลิกปุ่ม **"Back to List"** หรือลูกศรย้อนกลับบน Page Header

5.  **ออกจากระบบ (Logout):**
    *   ที่ Header ด้านบนขวา จะมีข้อมูลอีเมลของคุณและปุ่ม **"ออกจากระบบ"**
    *   คลิกปุ่มนี้เพื่อออกจากระบบ

---
