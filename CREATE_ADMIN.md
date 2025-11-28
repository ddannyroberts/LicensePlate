# 🔐 สร้าง Admin Account (Superuser)

## ❌ ปัญหา: Login ไม่ได้ด้วย admin/admin123

**สาเหตุ:** ยังไม่ได้สร้าง superuser ในระบบ

---

## ✅ วิธีแก้ไข

### วิธีที่ 1: สร้าง Superuser ผ่าน Terminal (Local)

1. **เปิด Terminal**
2. **ไปที่โฟลเดอร์โปรเจกต์:**
   ```bash
   cd /Users/dannyroberts/Documents/DG/LicensePlate/license_plate_system
   ```

3. **รันคำสั่ง:**
   ```bash
   python manage.py createsuperuser
   ```

4. **ใส่ข้อมูล:**
   ```
   Username: admin
   Email address: admin@example.com
   Password: admin123
   Password (again): admin123
   ```

5. **กด Enter** - จะเห็น "Superuser created successfully."

6. **ลอง Login ใหม่** ด้วย:
   - Username: `admin`
   - Password: `admin123`

---

### วิธีที่ 2: สร้าง Superuser ผ่าน Django Shell (Local)

1. **เปิด Django Shell:**
   ```bash
   cd /Users/dannyroberts/Documents/DG/LicensePlate/license_plate_system
   python manage.py shell
   ```

2. **รันโค้ดนี้:**
   ```python
   from django.contrib.auth.models import User
   
   # สร้าง superuser
   User.objects.create_superuser(
       username='admin',
       email='admin@example.com',
       password='admin123'
   )
   
   # ออกจาก shell
   exit()
   ```

3. **ลอง Login ใหม่**

---

### วิธีที่ 3: สร้าง Superuser บน Render (Production)

1. **ไปที่ Render Dashboard → Web Service → Shell**

2. **รันคำสั่ง:**
   ```bash
   python manage.py createsuperuser
   ```

3. **ใส่ข้อมูล:**
   ```
   Username: admin
   Email address: admin@example.com
   Password: admin123
   Password (again): admin123
   ```

4. **ลอง Login ใหม่**

---

## 🔍 ตรวจสอบว่า Superuser มีอยู่แล้วหรือไม่

### ผ่าน Django Shell:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# ตรวจสอบว่ามี admin user หรือไม่
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print(f"Found admin user: {admin_user.username}")
    print(f"Is superuser: {admin_user.is_superuser}")
    print(f"Is staff: {admin_user.is_staff}")
else:
    print("Admin user not found - need to create superuser")
```

---

## 🔄 Reset Password (ถ้าลืมรหัสผ่าน)

### วิธีที่ 1: เปลี่ยนรหัสผ่านผ่าน Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# หา user
user = User.objects.get(username='admin')

# เปลี่ยนรหัสผ่าน
user.set_password('admin123')
user.save()

print("Password changed successfully!")
exit()
```

### วิธีที่ 2: ใช้ Django Management Command

```bash
python manage.py changepassword admin
```

---

## ✅ Checklist

- [ ] รัน migrations (`python manage.py migrate`)
- [ ] สร้าง superuser (`python manage.py createsuperuser`)
- [ ] ตรวจสอบว่า superuser ถูกสร้างแล้ว
- [ ] ลอง login ด้วย username/password ที่สร้าง

---

## 🎯 ข้อมูล Login ที่ถูกต้อง

หลังจากสร้าง superuser แล้ว:

- **Username:** `admin`
- **Password:** `admin123` (หรือรหัสที่คุณตั้ง)
- **URL:** `http://127.0.0.1:8000/auth/login/` (local)
- **Admin Panel:** `http://127.0.0.1:8000/admin/` (local)

---

## 💡 Tips

1. **ถ้า login ไม่ได้** - ตรวจสอบว่า:
   - Database migrations รันแล้ว (`python manage.py migrate`)
   - Superuser ถูกสร้างแล้ว
   - Username และ password ถูกต้อง

2. **ถ้ายัง login ไม่ได้** - ลอง:
   - ตรวจสอบ error message ใน browser console
   - ตรวจสอบ Django logs
   - ลองสร้าง superuser ใหม่

3. **สำหรับ Production (Render):**
   - ใช้ Shell ใน Render Dashboard
   - ตรวจสอบว่า DATABASE_URL ถูกต้อง
   - ตรวจสอบ Logs ว่ามี error หรือไม่

