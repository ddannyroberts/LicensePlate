# 🚀 คู่มือ Deploy License Plate Detection System แบบฟรี

## 📋 ตัวเลือก Platform ฟรี

### 1. **Railway** (แนะนำ - ง่ายที่สุด) ⭐
- **ฟรี**: $5 credit/เดือน (พอใช้สำหรับ project เล็ก)
- **ข้อดี**: ง่าย, auto-deploy จาก GitHub, รองรับ Django ดี
- **URL**: https://railway.app

### 2. **Render** (แนะนำ - ฟรีจริงๆ)
- **ฟรี**: Free tier (ช้าเมื่อ idle แต่ฟรีจริงๆ)
- **ข้อดี**: ฟรี, auto-deploy, รองรับ Django
- **URL**: https://render.com

### 3. **PythonAnywhere**
- **ฟรี**: Free tier (จำกัด)
- **ข้อดี**: ฟรี, ง่าย, เหมาะกับ Django
- **URL**: https://www.pythonanywhere.com

---

## 🎯 วิธี Deploy บน Railway (แนะนำ)

### ขั้นตอนที่ 1: เตรียม Project

1. **Push code ขึ้น GitHub**
   ```bash
   cd /Users/dannyroberts/Documents/DG/LicensePlate
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/license-plate-system.git
   git push -u origin main
   ```

### ขั้นตอนที่ 2: สร้างไฟล์สำหรับ Railway

ไฟล์ที่สร้างแล้ว:
- ✅ `Procfile` - บอก Railway วิธีรัน app
- ✅ `runtime.txt` - ระบุ Python version
- ✅ `requirements.txt` - dependencies

### ขั้นตอนที่ 3: Deploy บน Railway

1. **ไปที่**: https://railway.app
2. **Sign up** ด้วย GitHub account
3. **New Project** → **Deploy from GitHub repo**
4. **เลือก repository** ของคุณ
5. **Railway จะ auto-detect** Django และ deploy อัตโนมัติ

### ขั้นตอนที่ 4: ตั้งค่า Environment Variables

ใน Railway Dashboard → Variables → เพิ่ม:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app
```

### ขั้นตอนที่ 5: ตั้งค่า Database

Railway มี PostgreSQL ฟรี:
1. **New** → **Database** → **Add PostgreSQL**
2. Railway จะสร้าง DATABASE_URL อัตโนมัติ
3. Django จะใช้ DATABASE_URL นี้

### ขั้นตอนที่ 6: รัน Migrations

ใน Railway → Deployments → View Logs → Run Command:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🎯 วิธี Deploy บน Render (ฟรีจริงๆ)

### ขั้นตอนที่ 1: เตรียม Project (เหมือน Railway)

### ขั้นตอนที่ 2: Deploy บน Render

1. **ไปที่**: https://render.com
2. **Sign up** ฟรี
3. **New** → **Web Service**
4. **Connect GitHub** → เลือก repository
5. **ตั้งค่า**:
   - **Name**: license-plate-system
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn license_plate_system.wsgi:application`
   - **Plan**: Free

### ขั้นตอนที่ 3: ตั้งค่า Environment Variables

ใน Render Dashboard → Environment → เพิ่ม:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
```

### ขั้นตอนที่ 4: ตั้งค่า Database

1. **New** → **PostgreSQL**
2. **Plan**: Free
3. Render จะสร้าง DATABASE_URL อัตโนมัติ

---

## ⚙️ ปรับ Settings สำหรับ Production

ไฟล์ `settings.py` จะถูกปรับให้รองรับ environment variables อัตโนมัติ

---

## 📝 Checklist ก่อน Deploy

- [ ] Push code ขึ้น GitHub
- [ ] ตั้งค่า SECRET_KEY (ใช้ environment variable)
- [ ] ตั้งค่า DEBUG=False
- [ ] ตั้งค่า ALLOWED_HOSTS
- [ ] ตั้งค่า Database (PostgreSQL)
- [ ] รัน migrations
- [ ] สร้าง superuser
- [ ] ทดสอบ upload images/videos

---

## 🔧 Troubleshooting

### ปัญหา: Static files ไม่แสดง
**แก้**: ตรวจสอบว่า `collectstatic` รันแล้ว

### ปัญหา: Database error
**แก้**: ตรวจสอบ DATABASE_URL และ migrations

### ปัญหา: Media files ไม่แสดง
**แก้**: ใช้ cloud storage (AWS S3, Cloudinary) สำหรับ production

---

## 💡 Tips

1. **ใช้ Cloud Storage** สำหรับ media files (แนะนำ Cloudinary ฟรี)
2. **ตั้งค่า SECRET_KEY** ให้ปลอดภัย
3. **Backup database** เป็นประจำ
4. **Monitor logs** ใน dashboard

---

## 📞 ต้องการความช่วยเหลือ?

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

