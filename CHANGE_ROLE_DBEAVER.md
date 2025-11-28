# 🔐 เปลี่ยน User Role ผ่าน DBeaver

## 📌 ข้อมูลเบื้องต้น

**Table:** `auth_user`  
**Columns ที่สำคัญ:**
- `username` - ชื่อผู้ใช้
- `is_staff` - สิทธิ์ admin (1 = มีสิทธิ์, 0 = ไม่มี)
- `is_superuser` - สิทธิ์ superuser (1 = มีสิทธิ์, 0 = ไม่มี)
- `is_active` - เปิด/ปิดใช้งาน (1 = เปิด, 0 = ปิด)

---

## 🔌 เชื่อมต่อ Database

### สำหรับ SQLite (Development):
1. เปิด DBeaver
2. **New Database Connection** → **SQLite**
3. **Path:** เลือกไฟล์ `db.sqlite3` ในโฟลเดอร์ `license_plate_system/`
   - Path: `/Users/dannyroberts/Documents/DG/LicensePlate/license_plate_system/db.sqlite3`

### สำหรับ PostgreSQL (Production/Render):
1. เปิด DBeaver
2. **New Database Connection** → **PostgreSQL**
3. **Host:** จาก `DATABASE_URL` ใน Render
4. **Port:** 5432 (default)
5. **Database:** `license_plate_db`
6. **Username:** `license_plate_user`
7. **Password:** จาก `DATABASE_URL`

---

## 📊 ดู Users ทั้งหมด

### SQL Query:
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

**หรือดูแบบสั้น:**
```sql
SELECT username, is_staff, is_superuser, is_active 
FROM auth_user;
```

---

## ✅ ทำให้ User เป็น Admin

### วิธีที่ 1: Admin เต็ม (Staff + Superuser)
```sql
UPDATE auth_user 
SET is_staff = 1, 
    is_superuser = 1 
WHERE username = 'john';
```

### วิธีที่ 2: Staff เท่านั้น (ไม่ใช่ Superuser)
```sql
UPDATE auth_user 
SET is_staff = 1, 
    is_superuser = 0 
WHERE username = 'john';
```

### วิธีที่ 3: Superuser เท่านั้น
```sql
UPDATE auth_user 
SET is_staff = 0, 
    is_superuser = 1 
WHERE username = 'john';
```

---

## ❌ ลบ Admin Privileges

```sql
UPDATE auth_user 
SET is_staff = 0, 
    is_superuser = 0 
WHERE username = 'john';
```

---

## 🔄 เปิด/ปิดใช้งาน Account

### เปิดใช้งาน:
```sql
UPDATE auth_user 
SET is_active = 1 
WHERE username = 'john';
```

### ปิดใช้งาน:
```sql
UPDATE auth_user 
SET is_active = 0 
WHERE username = 'john';
```

---

## 🎯 ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: ทำให้ user หลายคนเป็น admin
```sql
UPDATE auth_user 
SET is_staff = 1, 
    is_superuser = 1 
WHERE username IN ('john', 'jane', 'bob');
```

### ตัวอย่างที่ 2: ทำให้ user ทั้งหมดเป็น staff
```sql
UPDATE auth_user 
SET is_staff = 1;
```

### ตัวอย่างที่ 3: ลบ admin จาก user ที่ไม่ใช่ superuser
```sql
UPDATE auth_user 
SET is_staff = 0 
WHERE is_superuser = 0;
```

### ตัวอย่างที่ 4: ปิดใช้งาน users ที่ไม่ active มากกว่า 90 วัน
```sql
UPDATE auth_user 
SET is_active = 0 
WHERE last_login < datetime('now', '-90 days')
  AND is_staff = 0;
```

---

## 🔍 ตรวจสอบ Role

### ตรวจสอบว่า user เป็น admin หรือไม่:
```sql
SELECT username, 
       CASE 
           WHEN is_staff = 1 OR is_superuser = 1 THEN 'Admin'
           ELSE 'User'
       END AS role
FROM auth_user
WHERE username = 'john';
```

### ดู admin users ทั้งหมด:
```sql
SELECT username, email, is_staff, is_superuser 
FROM auth_user 
WHERE is_staff = 1 OR is_superuser = 1;
```

### ดู regular users:
```sql
SELECT username, email 
FROM auth_user 
WHERE is_staff = 0 AND is_superuser = 0;
```

---

## 📝 Step-by-Step Guide

### ขั้นตอนที่ 1: เปิด DBeaver และเชื่อมต่อ Database

1. เปิด DBeaver
2. คลิก **New Database Connection**
3. เลือก **SQLite** (สำหรับ local) หรือ **PostgreSQL** (สำหรับ production)
4. ใส่ข้อมูล connection
5. **Test Connection** → **Finish**

### ขั้นตอนที่ 2: เปิด SQL Editor

1. คลิกขวาที่ Database → **SQL Editor** → **New SQL Script**
2. หรือกด `Ctrl+Enter` (Windows/Linux) หรือ `Cmd+Enter` (Mac)

### ขั้นตอนที่ 3: ดู Users ก่อน

```sql
SELECT username, is_staff, is_superuser, is_active 
FROM auth_user;
```

### ขั้นตอนที่ 4: แก้ไข Role

```sql
-- ตัวอย่าง: ทำให้ user 'john' เป็น admin
UPDATE auth_user 
SET is_staff = 1, 
    is_superuser = 1 
WHERE username = 'john';
```

### ขั้นตอนที่ 5: Execute Query

- กด **Execute** หรือ `Ctrl+Enter` / `Cmd+Enter`
- ตรวจสอบว่า "1 row affected" หรือ "1 row updated"

### ขั้นตอนที่ 6: ตรวจสอบผลลัพธ์

```sql
SELECT username, is_staff, is_superuser, is_active 
FROM auth_user 
WHERE username = 'john';
```

---

## ⚠️ ข้อควรระวัง

### 1. สำหรับ SQLite (Development):
- ใช้ `1` และ `0` สำหรับ boolean values
- ใช้ `datetime('now')` สำหรับ timestamp

### 2. สำหรับ PostgreSQL (Production):
- ใช้ `true` และ `false` สำหรับ boolean values
- ใช้ `NOW()` สำหรับ timestamp
- ต้องระวัง case sensitivity ของ username

### 3. ตรวจสอบก่อนแก้:
```sql
-- ดู user ก่อนแก้
SELECT * FROM auth_user WHERE username = 'john';
```

### 4. Backup ก่อนแก้:
- Export table `auth_user` เป็น CSV หรือ SQL
- หรือใช้ DBeaver: คลิกขวาที่ table → **Export Data**

---

## 🔄 SQL สำหรับ PostgreSQL (Production)

### ดู Users:
```sql
SELECT username, is_staff, is_superuser, is_active 
FROM auth_user;
```

### ทำให้เป็น Admin:
```sql
UPDATE auth_user 
SET is_staff = true, 
    is_superuser = true 
WHERE username = 'john';
```

### ลบ Admin:
```sql
UPDATE auth_user 
SET is_staff = false, 
    is_superuser = false 
WHERE username = 'john';
```

### เปิด/ปิดใช้งาน:
```sql
-- เปิด
UPDATE auth_user 
SET is_active = true 
WHERE username = 'john';

-- ปิด
UPDATE auth_user 
SET is_active = false 
WHERE username = 'john';
```

---

## 🎯 Quick Reference

| Action | SQLite | PostgreSQL |
|--------|--------|------------|
| Admin | `is_staff = 1, is_superuser = 1` | `is_staff = true, is_superuser = true` |
| Staff Only | `is_staff = 1, is_superuser = 0` | `is_staff = true, is_superuser = false` |
| Remove Admin | `is_staff = 0, is_superuser = 0` | `is_staff = false, is_superuser = false` |
| Activate | `is_active = 1` | `is_active = true` |
| Deactivate | `is_active = 0` | `is_active = false` |

---

## 💡 Tips

1. **ใช้ Transaction** - เริ่ม transaction ก่อนแก้ แล้ว commit หลังแก้
2. **ตรวจสอบก่อน** - ใช้ SELECT ก่อน UPDATE เสมอ
3. **Backup** - Export table ก่อนแก้ไข
4. **Test** - ทดสอบ login หลังแก้ role
5. **Case Sensitive** - PostgreSQL username อาจ case sensitive

---

## 🔗 Related

- `MANAGE_ROLES.md` - จัดการ roles ผ่าน Python script
- `CREATE_ADMIN.md` - สร้าง admin user
- Django Admin Panel - จัดการผ่าน web interface

---

## 📸 Screenshots Guide

### 1. เชื่อมต่อ SQLite:
```
DBeaver → New Connection → SQLite
→ Path: /path/to/db.sqlite3
→ Test Connection → Finish
```

### 2. เปิด SQL Editor:
```
Database → SQL Editor → New SQL Script
```

### 3. Run Query:
```
Type SQL → Execute (Ctrl+Enter / Cmd+Enter)
```

---

**หมายเหตุ:** หลังแก้ role ใน database ควร logout และ login ใหม่เพื่อให้ role ใหม่มีผล

