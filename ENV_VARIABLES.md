# 🔐 Environment Variables สำหรับ Render

## 📋 Environment Variables ที่ต้องเพิ่ม

คลิก **"+ Add Environment Variable"** แล้วเพิ่มทีละตัว:

---

### 1. SECRET_KEY (สำคัญมาก!)

**Name:**
```
SECRET_KEY
```

**Value:**
```
n*d3!7+vv2($*=s9!unz+03r)y*$kd_nvv3!88$+c35e&t)ag)
```

**หรือคลิก "Generate" เพื่อสร้างใหม่** (แนะนำ)

---

### 2. DEBUG

**Name:**
```
DEBUG
```

**Value:**
```
False
```

---

### 3. ALLOWED_HOSTS

**Name:**
```
ALLOWED_HOSTS
```

**Value:**
```
127.0.0.1,localhost
```

**หมายเหตุ:** สำหรับ local development

---

### 4. RENDER_EXTERNAL_HOSTNAME (สำหรับ Render)

**Name:**
```
RENDER_EXTERNAL_HOSTNAME
```

**Value:**
```
license-plate-system-juq1.onrender.com
```

**หมายเหตุ:** 
- เปลี่ยนเป็น domain ที่ Render ให้คุณ (ดูได้จาก Render Dashboard → Web Service → URL)
- ตัวอย่าง: `license-plate-system-juq1.onrender.com`
- Django จะเพิ่ม domain นี้เข้าไปใน ALLOWED_HOSTS อัตโนมัติ

---

### 5. PYTHON_VERSION (Optional แต่แนะนำ)

**Name:**
```
PYTHON_VERSION
```

**Value:**
```
3.13.5
```

---

### 6. DATABASE_URL (หลังจากสร้าง PostgreSQL แล้ว)

**Name:**
```
DATABASE_URL
```

**Value:**
```
(จะได้จาก PostgreSQL database ที่สร้าง - Render จะสร้างให้อัตโนมัติ)
```

**วิธีหา:**
1. ไปที่ PostgreSQL database ที่สร้าง
2. คลิก "Connect" หรือ "Internal Database URL"
3. Copy connection string มาใส่

---

## 📝 ตัวอย่างหน้าจอที่ต้องกรอก

```
┌─────────────────────────────────────────┐
│ Environment Variables                    │
├─────────────────────────────────────────┤
│ NAME_OF_VARIABLE: SECRET_KEY            │
│ value: n*d3!7+vv2($*=s9!unz+03r)...     │
│                    [Generate] [🗑️]      │
├─────────────────────────────────────────┤
│ NAME_OF_VARIABLE: DEBUG                 │
│ value: False                             │
│                    [🗑️]                 │
├─────────────────────────────────────────┤
│ NAME_OF_VARIABLE: ALLOWED_HOSTS         │
│ value: license-plate-system.onrender.com│
│                    [🗑️]                 │
└─────────────────────────────────────────┘
```

---

## ✅ Checklist

- [ ] SECRET_KEY (Generate ใหม่หรือใช้ที่ให้มา)
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS = your-app-name.onrender.com
- [ ] DATABASE_URL (หลังจากสร้าง PostgreSQL แล้ว)

---

## ⚠️ หมายเหตุ

- **SECRET_KEY** ต้อง Generate ใหม่ ไม่ควรใช้ที่ให้มาใน production
- **ALLOWED_HOSTS** ต้องเปลี่ยนเป็นชื่อ app จริงของคุณ
- **DATABASE_URL** จะได้หลังจากสร้าง PostgreSQL database แล้ว

