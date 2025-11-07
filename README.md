# Emergent Account Generator

Generate akun Emergent.sh secara otomatis melalui Web Interface dan Telegram Bot.

## Fitur

### Web Interface
- 🎯 Generate akun dengan 1 klik
- ⏳ Loading indicator saat proses
- 📋 Tampilan email dan password yang dapat disalin
- 📊 Daftar semua akun yang sudah di-generate
- ✨ UI modern dan responsive

### Telegram Bot
- 🤖 Command `/start` untuk memulai
- 🎯 Tombol "Buat Akun" untuk generate akun baru
- 📋 Tombol "Daftar Akun" untuk melihat semua akun
- 📱 Format pesan yang dapat di-copy langsung
- 🔄 Generate akun baru tanpa restart bot

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Tailwind CSS + shadcn/ui
- **Storage**: JSON file (tidak perlu database)
- **Bot**: python-telegram-bot
- **Email**: mail.tm (temporary email service)

## Environment Variables

Buat file `.env` di folder `/app/backend/`:

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

## Deploy ke Koyeb Free Tier

### Persiapan

1. **Create Telegram Bot**
   - Bot Token Anda: `8202105040:AAGALkbC7XPS2CoKCB2tWTRryjOOxuC7br4`
   - Bot sudah siap digunakan

2. **Push ke GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO
   git push -u origin main
   ```

### Deploy di Koyeb

1. Login ke [Koyeb](https://koyeb.com)

2. **Create New Service**
   - Connect GitHub repository
   - Pilih repository Anda

3. **Important: Koyeb Configuration**
   
   Untuk deploy ke Koyeb free tier, Anda perlu membuat **single service** yang menjalankan backend dan frontend sekaligus. Buat file `start.sh`:
   
   ```bash
   #!/bin/bash
   # Install dependencies
   cd /app/backend && pip install -r requirements.txt
   cd /app/frontend && yarn install && yarn build
   
   # Start backend in background
   cd /app/backend && uvicorn server:app --host 0.0.0.0 --port 8001 &
   
   # Serve frontend with nginx or serve
   cd /app/frontend/build && npx serve -s . -l 8000
   ```

4. **Environment Variables di Koyeb**
   ```
   TELEGRAM_BOT_TOKEN=8202105040:AAGALkbC7XPS2CoKCB2tWTRryjOOxuC7br4
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=emergent_accounts
   CORS_ORIGINS=*
   PORT=8000
   ```

5. **Port Configuration**
   - Expose port: `8000`
   - Public port: `80` atau `443`

6. **Deploy**
   - Klik "Deploy"
   - Tunggu deployment selesai
   - Copy URL yang diberikan

## API Endpoints

### GET `/api/`
Health check endpoint.

### POST `/api/generate`
Generate akun baru (membutuhkan 30-60 detik).

### GET `/api/accounts`
Ambil semua akun yang sudah di-generate.

## Telegram Bot Commands

- `/start` - Mulai bot dan tampilkan menu utama
- Inline buttons:
  - 🎯 **Buat Akun** - Generate akun baru
  - 📋 **Daftar Akun** - Lihat semua akun (max 5 terakhir)
  - 🏠 **Menu Utama** - Kembali ke menu

## Testing

### Test Web Interface
1. Buka browser: `https://your-app-url.com`
2. Klik tombol "🎯 Generate Akun"
3. Tunggu 30-60 detik
4. Email dan password akan muncul
5. Klik icon copy untuk menyalin

### Test Telegram Bot
1. Buka Telegram
2. Search bot: `@your_bot_username`
3. Kirim `/start`
4. Klik "🎯 Buat Akun"
5. Tunggu hingga akun dibuat
6. Tap pada email/password untuk copy

## Struktur File

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI + Telegram bot
│   ├── utils/
│   │   └── account_generator.py  # Account generation logic
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   └── accounts.json          # Generated accounts (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   └── App.css           # Styles
│   └── package.json          # Node dependencies
│
└── README.md                 # This file
```

## Troubleshooting

### Bot Tidak Merespon
- Cek logs backend
- Pastikan bot token benar
- Restart service

### Generate Gagal
- mail.tm service mungkin down
- Coba lagi beberapa kali
- Cek koneksi internet

### Frontend Error
- Pastikan REACT_APP_BACKEND_URL sudah benar
- Check browser console untuk error
- Verify CORS settings

## Notes

- Setiap generate membutuhkan 30-60 detik
- Akun disimpan ke file JSON di `/app/backend/accounts.json`
- Bot Telegram dan Web Interface berbagi data yang sama
- Telegram bot berjalan di background bersamaan dengan API

## License

MIT
