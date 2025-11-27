# 🚀 คู่มือ Deploy บน Render (Step-by-Step)

## 📋 สิ่งที่ต้องตั้งค่าใน Render

### 1. **Basic Settings** (หน้าแรก)

✅ **Source Code**: `ddannyroberts / LicensePlate` (auto-detect แล้ว)
✅ **Service Type**: `Web Service` (auto-select แล้ว)
✅ **Name**: `LicensePlate` หรือ `license-plate-system`
✅ **Language**: `Python 3` (auto-detect แล้ว)
✅ **Branch**: `main` (auto-detect แล้ว)
✅ **Region**: `Singapore (Southeast Asia)` (แนะนำ)

---

### 2. **Root Directory** ⚠️ สำคัญ!

**ต้องตั้งค่านี้!** เพราะ Django project อยู่ใน `license_plate_system/` folder

```
license_plate_system
```

**วิธีตั้งค่า:**
- Scroll ลงไปหา "Advanced" section
- คลิก "> Advanced" เพื่อขยาย
- ในช่อง **"Root Directory"** ใส่: `license_plate_system`

---

### 3. **Build Command**

**ถ้า Root Directory ตั้งเป็น `license_plate_system` แล้ว:**
```
pip install -r ../requirements.txt && python manage.py collectstatic --noinput
```

**หรือถ้า Root Directory ไม่ได้ตั้ง (ใช้ root):**
```
cd license_plate_system && pip install -r ../requirements.txt && python manage.py collectstatic --noinput
```

**วิธีที่ง่ายที่สุด (แนะนำ):**
ตั้ง Root Directory = `license_plate_system` แล้วใช้:
```
pip install -r ../requirements.txt && python manage.py collectstatic --noinput
```

---

### 4. **Start Command**

**ถ้า Root Directory ตั้งเป็น `license_plate_system` แล้ว:**
```
python manage.py migrate && gunicorn license_plate_system.wsgi:application --timeout 120 --workers 2
```

**หรือถ้า Root Directory ไม่ได้ตั้ง:**
```
cd license_plate_system && python manage.py migrate && gunicorn license_plate_system.wsgi:application --timeout 120 --workers 2
```

**วิธีที่ง่ายที่สุด (แนะนำ):**
ตั้ง Root Directory = `license_plate_system` แล้วใช้:
```
python manage.py migrate && gunicorn license_plate_system.wsgi:application --timeout 120 --workers 2
```

**หมายเหตุ:** `migrate` จะรันทุกครั้งที่ start เพื่อให้แน่ใจว่า database schema ถูกต้อง

---

### 5. **Environment Variables** 🔐

คลิก "Add Environment Variable" แล้วเพิ่ม:

| Name | Value | หมายเหตุ |
|------|-------|----------|
| `SECRET_KEY` | (คลิก Generate เพื่อสร้างใหม่) | **สำคัญ!** ต้องสร้างใหม่ |
| `DEBUG` | `False` | ปิด debug mode |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | เปลี่ยนเป็นชื่อ app ของคุณ |
| `PYTHON_VERSION` | `3.13.5` | Python version |

**วิธีสร้าง SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### 6. **Instance Type**

เลือก **Free** ($0/month) สำหรับเริ่มต้น
- 512 MB RAM
- 0.1 CPU
- ⚠️ จะ sleep หลัง idle 15 นาที (wake up ช้า)

---

### 7. **Database (PostgreSQL)** 🗄️

**ต้องสร้าง Database แยก:**

1. ใน Render Dashboard → คลิก **"New"** → **"PostgreSQL"**
2. ตั้งชื่อ: `license-plate-db`
3. Plan: **Free**
4. Region: เลือกเดียวกับ Web Service
5. Render จะสร้าง `DATABASE_URL` อัตโนมัติ
6. Copy `DATABASE_URL` ไปใส่ใน Environment Variables ของ Web Service

---

## ✅ Checklist ก่อน Deploy

- [ ] ตั้งค่า **Root Directory** = `license_plate_system`
- [ ] ตั้งค่า **Build Command**
- [ ] ตั้งค่า **Start Command**
- [ ] เพิ่ม **SECRET_KEY** (Generate ใหม่)
- [ ] เพิ่ม **DEBUG** = `False`
- [ ] เพิ่ม **ALLOWED_HOSTS** = `your-app.onrender.com`
- [ ] สร้าง **PostgreSQL Database**
- [ ] เพิ่ม **DATABASE_URL** ใน Environment Variables
- [ ] เลือก **Instance Type** = Free

---

## 🎯 หลัง Deploy

1. **รอให้ Build เสร็จ** (ประมาณ 5-10 นาที)
2. **ตรวจสอบ Logs** ว่ามี error หรือไม่
3. **รัน Migrations:**
   - ไปที่ Render Dashboard → Web Service → Shell
   - รัน: `python manage.py migrate`
4. **สร้าง Superuser:**
   - รัน: `python manage.py createsuperuser`
5. **ทดสอบ:** เปิด URL ที่ Render ให้มา

---

## 🔧 Troubleshooting

### Error: "No module named 'dj_database_url'"
**แก้**: ตรวจสอบว่า `requirements.txt` มี `dj-database-url>=2.1.0`

### Error: "Static files not found"
**แก้**: ตรวจสอบว่า Build Command มี `collectstatic`

### Error: "Database connection failed"
**แก้**: ตรวจสอบ DATABASE_URL และ migrations

### Error: "ModuleNotFoundError"
**แก้**: ตรวจสอบ Root Directory และ requirements.txt

---

## 📝 หมายเหตุ

- **Free tier** จะ sleep หลัง idle → wake up ช้า (30-60 วินาที)
- **Media files** (รูปภาพ/วิดีโอ) จะหายเมื่อ restart → ควรใช้ cloud storage (S3, Cloudinary)
- **Database** ฟรีมีขนาดจำกัด → backup เป็นประจำ

---

## 🎉 เสร็จแล้ว!

หลังจากตั้งค่าทั้งหมดแล้ว คลิก **"Deploy Web Service"** และรอให้ deploy เสร็จ!

