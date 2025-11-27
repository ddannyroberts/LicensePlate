# 🚀 Deploy ใหม่บน Render

## ✅ ขั้นตอน Deploy ใหม่

### 1. ตรวจสอบ Code บน GitHub

ตรวจสอบว่า code ถูก push ขึ้น GitHub แล้ว:
- ✅ Commit ล่าสุด: `e3be14b` - Fix: Add migrate command to render.yaml
- ✅ ไฟล์ `render.yaml` มี `migrate` ใน startCommand แล้ว

---

### 2. ไปที่ Render Dashboard

1. **เปิด**: https://dashboard.render.com
2. **เลือก**: Web Service ของคุณ (`license-plate-system`)
3. **คลิก**: "Manual Deploy" (หรือ "Deploy" button)
4. **เลือก**: "Deploy latest commit"

---

### 3. ตรวจสอบ Settings ก่อน Deploy

ไปที่ **Settings** และตรวจสอบ:

#### ✅ Root Directory
```
license_plate_system
```

#### ✅ Build Command
```
pip install -r ../requirements.txt && python manage.py collectstatic --noinput
```

#### ✅ Start Command (สำคัญ!)
```
python manage.py migrate && gunicorn license_plate_system.wsgi:application --timeout 120 --workers 2
```

**หมายเหตุ:** ต้องมี `python manage.py migrate &&` ด้านหน้า

---

### 4. ตรวจสอบ Environment Variables

ตรวจสอบว่ามี Environment Variables เหล่านี้:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | (ตั้งค่าแล้ว) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` |
| `RENDER_EXTERNAL_HOSTNAME` | `license-plate-system-juq1.onrender.com` |
| `DATABASE_URL` | (จาก PostgreSQL database) |

---

### 5. รอให้ Deploy เสร็จ

1. **ดู Logs** ขณะ deploy
2. **ตรวจสอบว่า:**
   - ✅ Build สำเร็จ
   - ✅ `collectstatic` สำเร็จ
   - ✅ `migrate` รันและสำเร็จ
   - ✅ Gunicorn start สำเร็จ

---

### 6. ตรวจสอบหลัง Deploy

1. **เปิด URL**: `https://license-plate-system-juq1.onrender.com`
2. **ควรเห็นหน้า Login** (ไม่ใช่ error)
3. **ถ้ายังมี error** → ดู Logs

---

## 🔍 ถ้ายังมี Error

### Error: "no such table: auth_user"

**แก้ไข:**
1. ตรวจสอบว่า Start Command มี `migrate` หรือไม่
2. ไปที่ Shell → รัน `python manage.py migrate` เอง

### Error: "Blank page"

**แก้ไข:**
1. เปลี่ยน `DEBUG` = `True` ชั่วคราว
2. ดู error message
3. แก้ไข error
4. เปลี่ยน `DEBUG` = `False` กลับ

### Error: "Module not found"

**แก้ไข:**
1. ตรวจสอบ `requirements.txt`
2. ตรวจสอบ Build Logs
3. ดูว่า dependencies install สำเร็จหรือไม่

---

## 📋 Checklist ก่อน Deploy

- [ ] Code ถูก push ขึ้น GitHub แล้ว
- [ ] Root Directory = `license_plate_system`
- [ ] Build Command ถูกต้อง
- [ ] Start Command มี `migrate`
- [ ] Environment Variables ครบ
- [ ] DATABASE_URL ถูกต้อง

---

## 🎯 หลัง Deploy สำเร็จ

1. **สร้าง Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Login และทดสอบ:**
   - เปิด `/auth/login/`
   - Login ด้วย superuser
   - ทดสอบฟีเจอร์ต่างๆ

---

## 💡 Tips

- **ดู Logs** เป็นสิ่งแรกที่ควรทำเมื่อมีปัญหา
- **ตรวจสอบ Start Command** ให้แน่ใจว่ามี `migrate`
- **รอให้ Deploy เสร็จ** ก่อนทดสอบ (ประมาณ 3-5 นาที)

---

## 🎉 เสร็จแล้ว!

หลังจาก deploy สำเร็จ ควรเห็นหน้า Login และสามารถใช้งานได้ปกติ!

