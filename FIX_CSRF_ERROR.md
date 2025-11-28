# 🔧 แก้ไข CSRF Verification Failed Error (403)

## ❌ ปัญหา

```
CSRF verification failed. Request aborted.
Reason given for failure: CSRF token from POST incorrect.
```

## 🔍 สาเหตุ

1. **DEBUG = True** ใน production (ควรเป็น False)
2. **CSRF Cookie settings** ไม่เหมาะสมสำหรับ production
3. **Session Cookie settings** อาจต้องปรับ
4. **HTTPS/HTTP** mismatch

---

## ✅ วิธีแก้ไข

### 1. ตรวจสอบ Environment Variables ใน Render

ไปที่ **Render Dashboard → Web Service → Environment** ตรวจสอบ:

- ✅ `DEBUG` = `False` (ไม่ใช่ `True`)
- ✅ `SECRET_KEY` มีค่า
- ✅ `ALLOWED_HOSTS` ถูกต้อง

### 2. เพิ่ม CSRF Settings ใน settings.py

เพิ่มการตั้งค่า CSRF สำหรับ production:

```python
# CSRF Settings for Production
CSRF_COOKIE_SECURE = not DEBUG  # True in production (HTTPS only)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = []

# Session Cookie Settings
SESSION_COOKIE_SECURE = not DEBUG  # True in production (HTTPS only)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### 3. เพิ่ม Trusted Origins

```python
# Add Render domain to trusted origins
render_domain = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_domain:
    CSRF_TRUSTED_ORIGINS = [
        f'https://{render_domain}',
        f'http://{render_domain}',  # For development
    ]
```

---

## 🛠️ แก้ไข settings.py

เพิ่มการตั้งค่าต่อไปนี้ใน `settings.py`:

```python
# CSRF and Session Settings
CSRF_COOKIE_SECURE = not DEBUG  # True in production
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Session Cookie Settings
SESSION_COOKIE_SECURE = not DEBUG  # True in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = []

# Add Render domain to trusted origins
render_domain = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_domain:
    CSRF_TRUSTED_ORIGINS = [
        f'https://{render_domain}',
    ]
    # Also add to ALLOWED_HOSTS if not already
    if render_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(render_domain)
```

---

## 🔍 ตรวจสอบ Template

ตรวจสอบว่า template มี `{% csrf_token %}`:

```django
<form method="post" id="loginForm">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

---

## 📋 Checklist

- [ ] ตั้งค่า `DEBUG = False` ใน Render Environment Variables
- [ ] เพิ่ม CSRF settings ใน `settings.py`
- [ ] เพิ่ม `CSRF_TRUSTED_ORIGINS` สำหรับ Render domain
- [ ] ตรวจสอบว่า template มี `{% csrf_token %}`
- [ ] Deploy ใหม่
- [ ] ทดสอบ login

---

## 💡 Tips

1. **สำหรับ Production:**
   - `CSRF_COOKIE_SECURE = True` (HTTPS only)
   - `SESSION_COOKIE_SECURE = True` (HTTPS only)

2. **สำหรับ Development:**
   - `CSRF_COOKIE_SECURE = False`
   - `SESSION_COOKIE_SECURE = False`

3. **ตรวจสอบ Browser:**
   - เปิด Developer Tools → Application → Cookies
   - ตรวจสอบว่ามี `csrftoken` cookie

4. **Clear Browser Cache:**
   - ลบ cookies และ cache
   - ลอง login ใหม่

---

## 🔗 Related

- Django CSRF Documentation: https://docs.djangoproject.com/en/stable/ref/csrf/
- Render Deployment Guide

