# 🔧 แก้ไขปัญหา "no such table: auth_user"

## ❌ ปัญหาที่พบ

```
Error in login_view: no such table: auth_user
```

## 🔍 สาเหตุ

Database ยังไม่ได้ migrate - Django tables ยังไม่ได้ถูกสร้าง

## ✅ วิธีแก้ไข

### วิธีที่ 1: แก้ไขใน Render Dashboard (แนะนำ) ⭐

1. **ไปที่ Render Dashboard → Web Service → Settings**
2. **หา "Start Command"**
3. **เปลี่ยนเป็น:**
   ```
   python manage.py migrate && gunicorn license_plate_system.wsgi:application --timeout 120 --workers 2
   ```
4. **Save Changes**
5. **Manual Deploy** → **Deploy latest commit**

---

### วิธีที่ 2: รัน Migrate ผ่าน Shell (ชั่วคราว)

1. **ไปที่ Render Dashboard → Web Service → Shell**
2. **รันคำสั่ง:**
   ```bash
   python manage.py migrate
   ```
3. **รอให้ migrate เสร็จ**
4. **Refresh หน้าเว็บ**

---

### วิธีที่ 3: สร้าง Superuser (หลังจาก migrate)

1. **ไปที่ Render Dashboard → Web Service → Shell**
2. **รันคำสั่ง:**
   ```bash
   python manage.py createsuperuser
   ```
3. **ใส่ข้อมูล:**
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: (ใส่ password ที่ต้องการ)

---

## 📋 Checklist

- [ ] แก้ไข Start Command ให้มี `migrate`
- [ ] Save และ Deploy ใหม่
- [ ] ตรวจสอบ Logs ว่า migrate สำเร็จ
- [ ] สร้าง Superuser
- [ ] ทดสอบ login

---

## 🎯 Start Command ที่ถูกต้อง

```
python manage.py migrate && gunicorn license_plate_system.wsgi:application --timeout 120 --workers 2
```

**หมายเหตุ:**
- `migrate` จะรันทุกครั้งที่ start
- ใช้เวลาเพิ่มขึ้นเล็กน้อย แต่ทำให้แน่ใจว่า database schema ถูกต้อง
- ถ้า migrate แล้วจะ skip อัตโนมัติ

---

## 💡 Tips

- **ตรวจสอบ Logs** หลัง deploy ว่ามี "Applying migrations" หรือไม่
- **ถ้า migrate สำเร็จ** จะเห็น "Operations to perform: Apply all migrations"
- **ถ้ามี error** จะแสดงใน Logs

---

## 🔗 Links

- [Django Migrations](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [Render Shell](https://render.com/docs/shell)


