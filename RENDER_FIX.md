# 🔧 แก้ไข Build Error บน Render

## ❌ ปัญหาที่พบ

```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: '../requirements.txt'
```

## ✅ วิธีแก้ไข

### วิธีที่ 1: ตั้ง Root Directory (แนะนำ) ⭐

1. **ในหน้า Render Dashboard → Web Service Settings**
2. **Scroll ลงไปหา "Advanced" section**
3. **คลิก "> Advanced" เพื่อขยาย**
4. **ในช่อง "Root Directory" ใส่:**
   ```
   license_plate_system
   ```

5. **Build Command เปลี่ยนเป็น:**
   ```
   pip install -r ../requirements.txt && python manage.py collectstatic --noinput
   ```

6. **Start Command เปลี่ยนเป็น:**
   ```
   gunicorn license_plate_system.wsgi:application
   ```

---

### วิธีที่ 2: ไม่ตั้ง Root Directory

**Build Command:**
```
pip install -r requirements.txt && cd license_plate_system && python manage.py collectstatic --noinput
```

**Start Command:**
```
cd license_plate_system && gunicorn license_plate_system.wsgi:application
```

---

## 📋 สรุป Settings ที่ถูกต้อง

### ถ้า Root Directory = `license_plate_system` (แนะนำ)

| Field | Value |
|-------|-------|
| **Root Directory** | `license_plate_system` |
| **Build Command** | `pip install -r ../requirements.txt && python manage.py collectstatic --noinput` |
| **Start Command** | `gunicorn license_plate_system.wsgi:application` |

### ถ้า Root Directory = (ว่างเปล่า)

| Field | Value |
|-------|-------|
| **Root Directory** | (ว่างเปล่า) |
| **Build Command** | `pip install -r requirements.txt && cd license_plate_system && python manage.py collectstatic --noinput` |
| **Start Command** | `cd license_plate_system && gunicorn license_plate_system.wsgi:application` |

---

## 🎯 ขั้นตอนแก้ไข

1. ไปที่ Render Dashboard → Web Service ของคุณ
2. คลิก **"Settings"** (หรือ "Manual Deploy")
3. ตั้งค่า **Root Directory** = `license_plate_system`
4. เปลี่ยน **Build Command** ตามด้านบน
5. เปลี่ยน **Start Command** ตามด้านบน
6. **Save Changes**
7. คลิก **"Manual Deploy"** → **"Deploy latest commit"**

---

## ✅ ตรวจสอบ

หลังจากแก้ไขแล้ว Build ควรจะ:
- ✅ หา requirements.txt เจอ
- ✅ Install dependencies สำเร็จ
- ✅ Collect static files สำเร็จ
- ✅ Deploy สำเร็จ

---

## 🔍 ถ้ายังมี Error

ตรวจสอบ:
- [ ] Root Directory ตั้งถูกต้องหรือไม่
- [ ] Build Command ใช้ path ถูกต้องหรือไม่
- [ ] requirements.txt อยู่ใน root directory หรือไม่
- [ ] manage.py อยู่ใน license_plate_system/ หรือไม่


