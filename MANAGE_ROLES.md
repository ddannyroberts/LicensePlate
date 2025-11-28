# 🔐 จัดการ User Roles ผ่าน Database

## 📌 Role System ใน Django

ระบบใช้ Django's built-in User model ซึ่งมี:
- **is_staff** - เข้าถึง admin panel และ admin features
- **is_superuser** - มีสิทธิ์เต็ม (superuser)
- **is_active** - เปิด/ปิดใช้งาน account

---

## 🛠️ วิธีที่ 1: ใช้สคริปต์ (แนะนำ) ⭐

### ติดตั้งสคริปต์:
```bash
cd /Users/dannyroberts/Documents/DG/LicensePlate/license_plate_system
chmod +x manage_roles.py
```

### คำสั่งที่ใช้ได้:

**1. ดูรายชื่อ users ทั้งหมด:**
```bash
python manage_roles.py list
```

**2. ทำให้ user เป็น admin:**
```bash
python manage_roles.py admin [username]
```
ตัวอย่าง: `python manage_roles.py admin john`

**3. ลบ admin privileges:**
```bash
python manage_roles.py remove-admin [username]
```

**4. ทำให้ user เป็น staff (แต่ไม่ใช่ superuser):**
```bash
python manage_roles.py staff [username]
```

**5. ลบ staff status:**
```bash
python manage_roles.py remove-staff [username]
```

**6. เปิดใช้งาน account:**
```bash
python manage_roles.py activate [username]
```

**7. ปิดใช้งาน account:**
```bash
python manage_roles.py deactivate [username]
```

---

## 🛠️ วิธีที่ 2: ใช้ Django Shell

### เปิด Django Shell:
```bash
cd /Users/dannyroberts/Documents/DG/LicensePlate/license_plate_system
python manage.py shell
```

### คำสั่งที่ใช้ได้:

**1. ดูรายชื่อ users:**
```python
from django.contrib.auth.models import User

# ดูทั้งหมด
users = User.objects.all()
for user in users:
    print(f"{user.username} - Staff: {user.is_staff}, Superuser: {user.is_superuser}, Active: {user.is_active}")
```

**2. ทำให้ user เป็น admin:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='john')
user.is_staff = True
user.is_superuser = True
user.save()
print(f"✅ {user.username} is now admin")
```

**3. ลบ admin privileges:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='john')
user.is_staff = False
user.is_superuser = False
user.save()
print(f"✅ Admin privileges removed from {user.username}")
```

**4. ทำให้ user เป็น staff เท่านั้น:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='john')
user.is_staff = True
user.is_superuser = False  # ไม่ใช่ superuser
user.save()
print(f"✅ {user.username} is now staff")
```

**5. เปิด/ปิดใช้งาน account:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='john')
user.is_active = True  # หรือ False เพื่อปิด
user.save()
print(f"✅ {user.username} is now {'active' if user.is_active else 'inactive'}")
```

**6. สร้าง admin user ใหม่:**
```python
from django.contrib.auth.models import User

User.objects.create_superuser(
    username='newadmin',
    email='admin@example.com',
    password='password123'
)
print("✅ Admin user created")
```

---

## 🛠️ วิธีที่ 3: ใช้ Django Admin Panel

1. **Login เข้า admin panel:** `http://127.0.0.1:8000/admin/`
2. **ไปที่:** Users → เลือก user ที่ต้องการ
3. **แก้ไข:**
   - ✅ Staff status = ให้สิทธิ์ admin
   - ✅ Superuser status = ให้สิทธิ์เต็ม
   - ✅ Active = เปิด/ปิดใช้งาน
4. **Save**

---

## 🛠️ วิธีที่ 4: ใช้ SQL โดยตรง (สำหรับ Production)

### สำหรับ SQLite (Development):
```bash
sqlite3 db.sqlite3
```

```sql
-- ดู users
SELECT username, is_staff, is_superuser, is_active FROM auth_user;

-- ทำให้ user เป็น admin
UPDATE auth_user 
SET is_staff = 1, is_superuser = 1 
WHERE username = 'john';

-- ลบ admin
UPDATE auth_user 
SET is_staff = 0, is_superuser = 0 
WHERE username = 'john';
```

### สำหรับ PostgreSQL (Production):
```bash
# ผ่าน Render Shell หรือ psql
psql $DATABASE_URL
```

```sql
-- ดู users
SELECT username, is_staff, is_superuser, is_active FROM auth_user;

-- ทำให้ user เป็น admin
UPDATE auth_user 
SET is_staff = true, is_superuser = true 
WHERE username = 'john';

-- ลบ admin
UPDATE auth_user 
SET is_staff = false, is_superuser = false 
WHERE username = 'john';
```

---

## 📊 Role Types

### 1. **Superuser** (`is_superuser = True`)
- ✅ เข้าถึง Django admin panel
- ✅ เข้าถึง admin features ทั้งหมด
- ✅ มีสิทธิ์เต็มในระบบ
- ✅ สามารถจัดการ users อื่นๆ

### 2. **Staff** (`is_staff = True`, `is_superuser = False`)
- ✅ เข้าถึง Django admin panel
- ✅ เข้าถึง admin features (ตาม permissions)
- ❌ ไม่มีสิทธิ์จัดการ users

### 3. **Regular User** (`is_staff = False`, `is_superuser = False`)
- ❌ ไม่สามารถเข้าถึง admin panel
- ✅ เข้าถึง user features เท่านั้น
- ✅ ลงทะเบียนป้ายทะเบียน
- ✅ ดูประวัติของตัวเอง

### 4. **Inactive User** (`is_active = False`)
- ❌ ไม่สามารถ login ได้
- ❌ Account ถูกปิดใช้งาน

---

## 🎯 ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: ทำให้ user หลายคนเป็น admin
```python
from django.contrib.auth.models import User

usernames = ['john', 'jane', 'bob']
for username in usernames:
    try:
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ {username} is now admin")
    except User.DoesNotExist:
        print(f"❌ {username} not found")
```

### ตัวอย่างที่ 2: ดู admin users ทั้งหมด
```python
from django.contrib.auth.models import User

admins = User.objects.filter(is_staff=True)
print(f"Total admins: {admins.count()}")
for admin in admins:
    print(f"- {admin.username} ({admin.email})")
```

### ตัวอย่างที่ 3: ปิดใช้งาน users ที่ไม่ active
```python
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# ปิดใช้งาน users ที่ไม่ login มากกว่า 90 วัน
cutoff_date = timezone.now() - timedelta(days=90)
inactive_users = User.objects.filter(
    last_login__lt=cutoff_date,
    is_staff=False
)
count = inactive_users.update(is_active=False)
print(f"✅ Deactivated {count} users")
```

---

## ⚠️ ข้อควรระวัง

1. **อย่าลบ superuser ทั้งหมด** - จะทำให้เข้า admin panel ไม่ได้
2. **ตรวจสอบก่อนลบ admin** - ต้องมี admin อย่างน้อย 1 คน
3. **Backup database** - ก่อนทำการเปลี่ยนแปลงใหญ่
4. **ใช้ใน Production ระวัง** - ตรวจสอบ username ให้ถูกต้อง

---

## 🔍 ตรวจสอบ Role

### ตรวจสอบว่า user เป็น admin หรือไม่:
```python
from django.contrib.auth.models import User

user = User.objects.get(username='john')
if user.is_staff or user.is_superuser:
    print("✅ User is admin")
else:
    print("❌ User is not admin")
```

### ตรวจสอบใน Template:
```django
{% if user.is_staff %}
    <!-- แสดง admin features -->
{% endif %}

{% if user.is_superuser %}
    <!-- แสดง superuser features -->
{% endif %}
```

---

## 📝 Checklist

- [ ] ตรวจสอบ users ทั้งหมด (`python manage_roles.py list`)
- [ ] สร้าง admin user (`python manage_roles.py admin [username]`)
- [ ] ทดสอบ login ด้วย admin account
- [ ] ตรวจสอบว่า admin features ทำงานได้
- [ ] Backup database (ถ้าทำใน production)

---

## 💡 Tips

1. **ใช้สคริปต์** - ง่ายและปลอดภัยที่สุด
2. **ตรวจสอบก่อนแก้** - ใช้ `list` command ก่อน
3. **บันทึกการเปลี่ยนแปลง** - จดบันทึกว่าแก้ user ไหนบ้าง
4. **ทดสอบหลังแก้** - Login ทดสอบว่า role ถูกต้อง

---

## 🔗 Related Files

- `manage_roles.py` - สคริปต์จัดการ roles
- `create_admin.py` - สคริปต์สร้าง admin user
- `authentication/views.py` - Login logic
- `dashboard/views.py` - Admin dashboard

