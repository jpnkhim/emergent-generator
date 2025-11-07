# 🚀 Deploy ke Render Free Tier

## ✅ Keuntungan Render vs Koyeb
- ✅ **750 jam gratis per bulan** (cukup untuk 1 aplikasi 24/7)
- ✅ **Global CDN** (lebih cepat)
- ✅ **Auto-deploy** dari GitHub
- ✅ **SSL otomatis** (HTTPS)
- ✅ **Lebih stabil** untuk free tier

---

## 📋 Langkah-Langkah Deploy

### 1️⃣ Push ke GitHub (Sudah Selesai ✅)
Repository Anda sudah ada di: https://github.com/jpnkhim/emergent-generator

### 2️⃣ Login ke Render
1. Buka: https://render.com
2. Klik **"Get Started"** atau **"Sign Up"**
3. Login dengan **GitHub account** Anda

### 3️⃣ Connect Repository
1. Di dashboard Render, klik **"New +"**
2. Pilih **"Web Service"**
3. Klik **"Connect GitHub"** (authorize Render)
4. Pilih repository: **`emergent-generator`**
5. Klik **"Connect"**

### 4️⃣ Konfigurasi Service

**Basic Settings:**
- **Name**: `emergent-generator` (atau nama lain)
- **Region**: Pilih yang terdekat:
  - 🇸🇬 **Singapore** (paling dekat untuk Indonesia)
  - 🇺🇸 Oregon
  - 🇪🇺 Frankfurt
- **Branch**: `main`
- **Root Directory**: (kosongkan)
- **Environment**: **Docker** ✅
- **Dockerfile Path**: `./Dockerfile`

### 5️⃣ Instance Type
- **Plan**: **Free** ✅
- RAM: 512 MB
- CPU: Shared
- **Note**: Free tier akan sleep setelah 15 menit tidak ada traffic

### 6️⃣ Environment Variables
Klik **"Add Environment Variable"** dan tambahkan:

```
TELEGRAM_BOT_TOKEN = 8202105040:AAGALkbC7XPS2CoKCB2tWTRryjOOxuC7br4
MONGO_URL = mongodb://localhost:27017
DB_NAME = emergent_accounts
CORS_ORIGINS = *
```

**Cara menambahkan:**
1. Klik **"Advanced"**
2. Scroll ke **"Environment Variables"**
3. Klik **"Add Environment Variable"**
4. Masukkan key dan value
5. Ulangi untuk semua variables

### 7️⃣ Deploy!
1. Scroll ke bawah
2. Klik **"Create Web Service"**
3. Tunggu 5-10 menit untuk build pertama kali
4. Anda akan mendapat URL: `https://emergent-generator.onrender.com`

---

## 📊 Monitor Deployment

**Status build bisa dilihat di:**
- **Logs tab**: Real-time build & runtime logs
- **Events tab**: History deployment
- **Metrics tab**: CPU & Memory usage

**Build Steps:**
1. ✅ Cloning repository
2. ✅ Building frontend (React)
3. ✅ Building backend (Python)
4. ✅ Installing dependencies
5. ✅ Starting services (nginx + uvicorn + telegram bot)
6. ✅ Service live!

---

## 🎯 Testing Aplikasi

### Test Web Interface
1. Buka URL Render Anda: `https://your-app.onrender.com`
2. Klik **"🎯 Generate Akun"**
3. Tunggu 30-60 detik
4. Email dan password akan muncul

### Test Telegram Bot
1. Buka Telegram
2. Search: `@your_bot_username`
3. Kirim `/start`
4. Klik **"🎯 Buat Akun"**
5. Tunggu hingga akun dibuat

---

## 🔄 Auto-Deploy (Bonus)

Render akan **otomatis deploy** setiap kali Anda push ke GitHub:

```bash
# Update code
git add .
git commit -m "Update feature"
git push origin main
```

Render akan otomatis detect perubahan dan re-deploy! 🎉

---

## ⚠️ Limitasi Free Tier

1. **Sleep after inactivity**:
   - Service sleep setelah 15 menit tidak ada traffic
   - Wake up otomatis saat ada request (30-60 detik)
   - Telegram bot tetap jalan di background

2. **750 jam per bulan**:
   - Cukup untuk 1 aplikasi running 24/7
   - Jika lebih dari 1 app, akan dibagi

3. **Build time**:
   - Free tier: ~10 menit build time
   - Paid tier: ~3 menit

---

## 🆙 Upgrade (Opsional)

Jika aplikasi Anda ramai, upgrade ke **Starter Plan** ($7/bulan):
- ✅ No sleep
- ✅ Faster build
- ✅ More resources
- ✅ Priority support

---

## 🐛 Troubleshooting

### Build Failed?
- Cek **Logs tab** untuk error message
- Pastikan semua dependencies ada di `requirements.txt` dan `package.json`
- Cek Dockerfile syntax

### Service Crash?
- Cek **Runtime logs**
- Pastikan environment variables benar
- Cek TELEGRAM_BOT_TOKEN valid

### Telegram Bot Tidak Respond?
- Pastikan token benar
- Cek logs: `grep "telegram" logs`
- Restart service di Render dashboard

---

## 📱 URL Final

Setelah deploy berhasil, Anda akan mendapat:
- **Web Interface**: `https://emergent-generator.onrender.com`
- **API Endpoint**: `https://emergent-generator.onrender.com/api`
- **Health Check**: `https://emergent-generator.onrender.com/api/`

Update URL ini di Telegram bot webhook jika diperlukan!

---

## ✅ Checklist Deploy

- [ ] Repository sudah di GitHub
- [ ] Login ke Render dengan GitHub
- [ ] Connect repository
- [ ] Set environment variables
- [ ] Pilih region & plan (Free)
- [ ] Klik "Create Web Service"
- [ ] Tunggu build selesai
- [ ] Test web interface
- [ ] Test Telegram bot
- [ ] Selesai! 🎉

---

**Good luck!** 🚀

Jika ada masalah, cek logs di Render dashboard atau Telegram bot logs.
