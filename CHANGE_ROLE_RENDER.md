# 🔐 เปลี่ยน User Role ใน Database บน Render (PostgreSQL)

## 📌 ข้อมูลเบื้องต้น

**Database:** PostgreSQL บน Render.com  
**Table:** `auth_user`  
**Columns:**
- `username` - ชื่อผู้ใช้
- `is_staff` - สิทธิ์ admin (true/false)
- `is_superuser` - สิทธิ์ superuser (true/false)
- `is_active` - เปิด/ปิดใช้งาน (true/false)

---

## 🛠️ วิธีที่ 1: ใช้ Render Shell (แนะนำ) ⭐

### ขั้นตอน:

1. **ไปที่ Render Dashboard**
   - https://dashboard.render.com
   - Login เข้าระบบ

2. **เปิด Web Service**
   - คลิกที่ Web Service `license-plate-system`

3. **เปิด Shell**
   - คลิกแท็บ **"Shell"** (ด้านบน)
   - หรือไปที่ **"Shell"** ในเมนู

4. **เชื่อมต่อ Database**
   ```bash
   psql $DATABASE_URL
   ```

5. **รัน SQL Commands**

---

## 📝 SQL Commands สำหรับ PostgreSQL

### 1. ดู Users ทั้งหมด:
```sql
SELECT username, email, is_staff, is_superuser, is_active 
FROM auth_user
ORDER BY username;
```

### 2. ทำให้ User เป็น Admin (Staff + Superuser):
```sql
UPDATE auth_user 
SET is_staff = true, 
    is_superuser = true 
WHERE username = 'john';
```

### 3. ทำให้ User เป็น Staff เท่านั้น (ไม่ใช่ Superuser):
```sql
UPDATE auth_user 
SET is_staff = true, 
    is_superuser = false 
WHERE username = 'john';
```

### 4. ลบ Admin Privileges:
```sql
UPDATE auth_user 
SET is_staff = false, 
    is_superuser = false 
WHERE username = 'john';
```

### 5. เปิด/ปิดใช้งาน Account:
```sql
-- เปิดใช้งาน
UPDATE auth_user 
SET is_active = true 
WHERE username = 'john';

-- ปิดใช้งาน
UPDATE auth_user 
SET is_active = false 
WHERE username = 'john';
```

### 6. ออกจาก psql:
```sql
\q
```

---

## 🛠️ วิธีที่ 2: ใช้ Django Shell ใน Render

### ขั้นตอน:

1. **เปิด Render Shell** (เหมือนวิธีที่ 1)

2. **รัน Django Shell:**
   ```bash
   python manage.py shell
   ```

3. **รัน Python Code:**
   ```python
   from django.contrib.auth.models import User
   
   # ดู users
   users = User.objects.all()
   for user in users:
       print(f"{user.username} - Staff: {user.is_staff}, Superuser: {user.is_superuser}")
   
   # ทำให้ user เป็น admin
   user = User.objects.get(username='john')
   user.is_staff = True
   user.is_superuser = True
   user.save()
   print(f"✅ {user.username} is now admin")
   
   # ออกจาก shell
   exit()
   ```

---

## 🛠️ วิธีที่ 3: ใช้ DBeaver เชื่อมต่อ PostgreSQL

### ขั้นตอนที่ 1: ดู Connection String

1. **ไปที่ Render Dashboard**
2. **คลิกที่ PostgreSQL database** `license-plate-db`
3. **ดู "Internal Database URL"** หรือ **"Connection Info"**
4. **Copy connection string**

### ขั้นตอนที่ 2: เชื่อมต่อ DBeaver

1. **เปิด DBeaver**
2. **New Database Connection** → **PostgreSQL**
3. **ใส่ข้อมูล:**
   - **Host:** จาก connection string (เช่น `dpg-xxxxx-a.singapore-postgres.render.com`)
   - **Port:** 5432 (default)
   - **Database:** `license_plate_db`
   - **Username:** `license_plate_user`
   - **Password:** จาก connection string
4. **Test Connection** → **Finish**

### ขั้นตอนที่ 3: รัน SQL

1. **เปิด SQL Editor**
2. **รัน SQL commands** (เหมือนวิธีที่ 1)

---

## 🛠️ วิธีที่ 4: ใช้ Python Script ใน Render Shell

### สร้างไฟล์ชั่วคราว:

1. **เปิด Render Shell**

2. **สร้างไฟล์:**
   ```bash
   cat > change_role.py << 'EOF'
   import os
   import django
   
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'license_plate_system.settings')
   django.setup()
   
   from django.contrib.auth.models import User
   
   username = 'john'  # เปลี่ยนเป็น username ที่ต้องการ
   
   try:
       user = User.objects.get(username=username)
       user.is_staff = True
       user.is_superuser = True
       user.save()
       print(f"✅ {username} is now admin")
   except User.DoesNotExist:
       print(f"❌ User '{username}' not found!")
   EOF
   ```

3. **รัน Script:**
   ```bash
   python change_role.py
   ```

---

## 📊 ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: ดู Users ทั้งหมด
```sql
SELECT 
    id,
    username,
    email,
    is_staff,
    is_superuser,
    is_active,
    date_joined,
    last_login
FROM auth_user
ORDER BY username;
```

### ตัวอย่างที่ 2: ทำให้ User หลายคนเป็น Admin
```sql
UPDATE auth_user 
SET is_staff = true, 
    is_superuser = true 
WHERE username IN ('john', 'jane', 'bob');
```

### ตัวอย่างที่ 3: ดู Admin Users ทั้งหมด
```sql
SELECT username, email 
FROM auth_user 
WHERE is_staff = true OR is_superuser = true;
```

### ตัวอย่างที่ 4: ตรวจสอบ Role ของ User
```sql
SELECT username, 
       CASE 
           WHEN is_staff = true OR is_superuser = true THEN 'Admin'
           ELSE 'User'
       END AS role,
       is_active AS active
FROM auth_user
WHERE username = 'john';
```

---

## 🎯 Step-by-Step Guide (Render Shell)

### ขั้นตอนที่ 1: เปิด Render Shell
1. ไปที่ https://dashboard.render.com
2. Login
3. คลิก Web Service `license-plate-system`
4. คลิกแท็บ **"Shell"**

### ขั้นตอนที่ 2: เชื่อมต่อ Database
```bash
psql $DATABASE_URL
```

### ขั้นตอนที่ 3: ดู Users ก่อน
```sql
SELECT username, is_staff, is_superuser, is_active FROM auth_user;
```

### ขั้นตอนที่ 4: แก้ไข Role
```sql
-- ตัวอย่าง: ทำให้ user 'john' เป็น admin
UPDATE auth_user 
SET is_staff = true, 
    is_superuser = true 
WHERE username = 'john';
```

### ขั้นตอนที่ 5: ตรวจสอบผลลัพธ์
```sql
SELECT username, is_staff, is_superuser, is_active 
FROM auth_user 
WHERE username = 'john';
```

### ขั้นตอนที่ 6: ออกจาก psql
```sql
\q
```

---

## ⚠️ ข้อควรระวัง

### 1. Case Sensitivity
PostgreSQL อาจ case sensitive กับ username:
```sql
-- ใช้ LOWER() เพื่อไม่สนใจ case
UPDATE auth_user 
SET is_staff = true 
WHERE LOWER(username) = LOWER('John');
```

### 2. ตรวจสอบก่อนแก้
```sql
-- ดู user ก่อนแก้
SELECT * FROM auth_user WHERE username = 'john';
```

### 3. Backup ก่อนแก้
```sql
-- Export table
\copy auth_user TO '/tmp/auth_user_backup.csv' CSV HEADER;
```

### 4. Transaction
```sql
-- เริ่ม transaction
BEGIN;

-- แก้ไข
UPDATE auth_user SET is_staff = true WHERE username = 'john';

-- ตรวจสอบ
SELECT * FROM auth_user WHERE username = 'john';

-- Commit หรือ Rollback
COMMIT;  -- หรือ ROLLBACK;
```

---

## 🔍 Troubleshooting

### ปัญหา: "relation auth_user does not exist"
**แก้:** รัน migrations ก่อน:
```bash
python manage.py migrate
```

### ปัญหา: "permission denied"
**แก้:** ตรวจสอบว่าใช้ user ที่มีสิทธิ์ (license_plate_user)

### ปัญหา: "could not connect"
**แก้:** ตรวจสอบ DATABASE_URL และ network connection

---

## 📋 Quick Reference

| Action | SQL Command |
|--------|-------------|
| **ดู Users** | `SELECT username, is_staff, is_superuser FROM auth_user;` |
| **Admin** | `UPDATE auth_user SET is_staff = true, is_superuser = true WHERE username = 'john';` |
| **Staff Only** | `UPDATE auth_user SET is_staff = true, is_superuser = false WHERE username = 'john';` |
| **Remove Admin** | `UPDATE auth_user SET is_staff = false, is_superuser = false WHERE username = 'john';` |
| **Activate** | `UPDATE auth_user SET is_active = true WHERE username = 'john';` |
| **Deactivate** | `UPDATE auth_user SET is_active = false WHERE username = 'john';` |

---

## 💡 Tips

1. **ใช้ Render Shell** - ง่ายและปลอดภัยที่สุด
2. **ตรวจสอบก่อนแก้** - ใช้ SELECT ก่อน UPDATE
3. **บันทึกการเปลี่ยนแปลง** - จดบันทึกว่าแก้ user ไหนบ้าง
4. **ทดสอบหลังแก้** - Login ทดสอบว่า role ถูกต้อง
5. **Logout/Login ใหม่** - หลังแก้ role ควร logout และ login ใหม่

---

## 🔗 Related Files

- `CHANGE_ROLE_DBEAVER.md` - เปลี่ยน role ผ่าน DBeaver
- `MANAGE_ROLES.md` - จัดการ roles ผ่าน Python script
- `CREATE_ADMIN.md` - สร้าง admin user

---

**หมายเหตุ:** หลังแก้ role ใน database ควร logout และ login ใหม่เพื่อให้ role ใหม่มีผล

