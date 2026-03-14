# NEXUS — Multi-Agent AI Chat Room
### Tutorial Lengkap untuk Pemula

> Chat room di mana **Claude** (Anthropic) dan **ChatGPT** (OpenAI) bisa saling ngobrol, debat, dan assign tugas satu sama lain secara otomatis.

---

## 📋 DAFTAR ISI

1. [Apa Itu NEXUS?](#apa-itu-nexus)
2. [Struktur Folder](#struktur-folder)
3. [Persiapan: Install Software](#persiapan-install-software)
4. [Setup API Keys](#setup-api-keys)
5. [Cara Menjalankan Aplikasi](#cara-menjalankan-aplikasi)
6. [Cara Menggunakan Chat](#cara-menggunakan-chat)
7. [Troubleshooting](#troubleshooting)

---

## Apa Itu NEXUS?

NEXUS adalah chat room multi-agent di mana kamu bisa:

- **Tag** `@Claude` atau `@ChatGPT` untuk memanggil AI agent
- Agent bisa **tag satu sama lain** → otomatis lanjut diskusi
- **Debat, brainstorming, code review**, semua bisa dilakukan bersama 2 AI
- Berjalan **100% lokal** di komputer kamu
- **Open source** dan gratis (kecuali biaya API)

---

## 📁 STRUKTUR FOLDER

```
multi-agent-chat/                ← Folder utama project
│
├── backend/                     ← Server Node.js
│   ├── server.js                ← 🧠 Logika utama server & AI
│   ├── package.json             ← Daftar dependencies npm
│   ├── .env.example             ← Template environment variables
│   └── .env                     ← ⚠️ API keys kamu (BUAT SENDIRI!)
│
├── frontend/                    ← Tampilan website
│   └── index.html               ← 🎨 UI chat room (1 file)
│
└── README.md                    ← File ini
```

**Penjelasan singkat tiap file:**

| File | Fungsi |
|------|--------|
| `backend/server.js` | Server utama: menerima chat, kirim ke Claude/ChatGPT, broadcast ke browser |
| `backend/package.json` | Daftar library yang dibutuhkan (express, openai, dll) |
| `backend/.env` | Tempat menyimpan API keys (RAHASIA, jangan share!) |
| `frontend/index.html` | Tampilan chat room yang kamu lihat di browser |

---

## 🛠️ PERSIAPAN: INSTALL SOFTWARE

### 1. Install Node.js

Node.js adalah runtime JavaScript yang menjalankan server kita.

**Windows:**
1. Buka https://nodejs.org
2. Download versi **LTS** (recommended)
3. Jalankan installer, klik Next terus
4. Restart komputer setelah install

**Mac:**
```bash
# Jika sudah ada Homebrew:
brew install node

# Atau download dari https://nodejs.org
```

**Cek apakah berhasil:**
Buka Terminal / Command Prompt, ketik:
```bash
node --version
# Harus muncul: v20.x.x atau lebih baru

npm --version
# Harus muncul: 10.x.x atau lebih baru
```

### 2. Install VS Code

1. Buka https://code.visualstudio.com
2. Download dan install
3. Buka VS Code

### 3. Extension VS Code yang Berguna (Opsional)

Buka VS Code → Extensions (Ctrl+Shift+X) → Install:
- **ESLint** — cek error JavaScript
- **Prettier** — format kode otomatis
- **REST Client** — test API

---

## 🔑 SETUP API KEYS

Kamu butuh 2 API key: satu dari Anthropic (Claude), satu dari OpenAI (ChatGPT).

### Mendapatkan Anthropic API Key (Claude)

1. Buka https://console.anthropic.com
2. Daftar / login
3. Klik menu **API Keys** di sidebar
4. Klik **Create Key**
5. Beri nama, misalnya: `nexus-chat`
6. Copy API key-nya (mulai dengan `sk-ant-...`)
7. **SIMPAN BAIK-BAIK!** Key hanya ditampilkan sekali

> 💡 Anthropic memberi free credit untuk akun baru

### Mendapatkan OpenAI API Key (ChatGPT)

1. Buka https://platform.openai.com/api-keys
2. Daftar / login
3. Klik **Create new secret key**
4. Beri nama, misalnya: `nexus-chat`
5. Copy API key-nya (mulai dengan `sk-proj-...`)
6. **SIMPAN BAIK-BAIK!** Key hanya ditampilkan sekali

> 💡 OpenAI membutuhkan kredit berbayar untuk menggunakan API

### Membuat File .env

1. Buka folder `backend/` di project kamu
2. Copy file `.env.example` → rename jadi `.env`

   **Di Terminal:**
   ```bash
   cd backend
   cp .env.example .env
   ```

   **Di VS Code:**
   - Klik kanan `.env.example` → Copy
   - Paste di folder yang sama
   - Rename jadi `.env`

3. Buka file `.env` dan isi dengan API key kamu:
   ```
   ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXX_isi_dengan_key_kamu_XXXXXXXXXX
   OPENAI_API_KEY=sk-proj-XXXXXXXXXX_isi_dengan_key_kamu_XXXXXXXXXX
   PORT=3001
   ```

> ⚠️ **PENTING:** Jangan pernah upload atau share file `.env`!
> Jika pakai Git, pastikan `.env` ada di `.gitignore`

---

## 🚀 CARA MENJALANKAN APLIKASI

### Langkah 1: Buka Project di VS Code

1. Buka VS Code
2. Klik **File** → **Open Folder**
3. Pilih folder `multi-agent-chat`

### Langkah 2: Buka Terminal di VS Code

Klik **Terminal** → **New Terminal**
(atau tekan Ctrl+` / Cmd+`)

### Langkah 3: Masuk ke Folder Backend

```bash
cd backend
```

### Langkah 4: Install Dependencies

```bash
npm install
```

Tunggu sampai selesai. Akan muncul folder `node_modules/` (normal, ini berisi library).

### Langkah 5: Jalankan Server

```bash
node server.js
```

Jika berhasil, terminal akan menampilkan:
```
🚀 ================================
🚀  Multi-Agent Chat Server
🚀  Running on port 3001
🚀 ================================

📡 WebSocket: ws://localhost:3001
🌐 Frontend:  http://localhost:3001

🤖 Agents:
   @claude     → claude-opus-4-5
   @chatgpt    → gpt-4o

✅ Server ready!
```

### Langkah 6: Buka di Browser

Buka browser (Chrome/Firefox/Edge) dan pergi ke:
```
http://localhost:3001
```

**Selesai! 🎉** NEXUS sudah berjalan!

---

## 💬 CARA MENGGUNAKAN CHAT

### Memanggil Agent

Gunakan `@` untuk memanggil agent:

```
@Claude apa itu machine learning?
```

```
@ChatGPT buatkan function Python untuk sorting array
```

### Memanggil Dua Agent Sekaligus

```
@Claude dan @ChatGPT, mana lebih baik: Python atau JavaScript?
```

Kedua agent akan merespons, dan bisa saling balas!

### Auto-Chain (Agent Ngobrol Sendiri)

Jika Claude dalam responsnya menyebut `@ChatGPT`, ChatGPT akan otomatis merespons juga — dan begitu sebaliknya.

Contoh skenario menarik:
```
@Claude kamu adalah architect, dan @ChatGPT adalah developer. 
Diskusikan arsitektur terbaik untuk aplikasi e-commerce.
```

### Contoh Prompt Keren

```
@Claude review kode ini dan minta @ChatGPT untuk perbaiki: [paste kode]
```

```
@Claude dan @ChatGPT, debatkan: tabs vs spaces!
```

```
@ChatGPT buat roadmap belajar AI, lalu @Claude kasih pendapat kritisnya
```

### Keyboard Shortcuts

| Shortcut | Fungsi |
|----------|--------|
| `Enter` | Kirim pesan |
| `Shift+Enter` | Baris baru |

---

## 🔧 TROUBLESHOOTING

### ❌ "Cannot connect to server"

**Penyebab:** Server belum berjalan atau sudah mati

**Solusi:**
1. Pastikan terminal masih menjalankan `node server.js`
2. Cek apakah ada error di terminal
3. Coba refresh browser

---

### ❌ "Claude error: 401 Unauthorized"

**Penyebab:** API key Anthropic salah atau kosong

**Solusi:**
1. Buka file `backend/.env`
2. Pastikan `ANTHROPIC_API_KEY` diisi dengan benar
3. Restart server: Ctrl+C lalu `node server.js` lagi

---

### ❌ "ChatGPT error: Insufficient quota"

**Penyebab:** Saldo OpenAI habis

**Solusi:**
1. Login ke https://platform.openai.com/billing
2. Tambah kredit minimal $5

---

### ❌ Port 3001 already in use

**Penyebab:** Ada aplikasi lain yang pakai port 3001

**Solusi:**
Ubah di `backend/.env`:
```
PORT=3002
```
Lalu akses http://localhost:3002

---

### ❌ "npm install" gagal

**Penyebab:** Node.js belum terinstall atau versi terlalu lama

**Solusi:**
```bash
node --version  # Harus v18 atau lebih baru
npm --version   # Harus v8 atau lebih baru
```

Jika versi lama, update Node.js dari https://nodejs.org

---

## 📚 TEKNOLOGI YANG DIGUNAKAN

| Teknologi | Fungsi |
|-----------|--------|
| **Node.js** | Runtime JavaScript untuk server |
| **Express.js** | Web framework untuk HTTP server |
| **WebSocket (ws)** | Real-time komunikasi browser ↔ server |
| **Anthropic SDK** | Memanggil Claude API |
| **OpenAI SDK** | Memanggil ChatGPT API |
| **HTML/CSS/JS** | Frontend chat room (single file) |

---

## 💡 TIPS & TRIK

1. **Atur persona agent** — kasih sistem instruksi lewat prompt, misal:
   `@Claude kamu adalah senior engineer yang sangat kritis`

2. **Track tasks** — minta agent untuk assign dan track pekerjaan:
   `@Claude buat daftar task untuk project ini, assign ke @ChatGPT`

3. **Code review workflow** — workflow klasik:
   `@ChatGPT tulis kode untuk [task], lalu @Claude review dan optimalkan`

4. **Auto-loop limit** — ada batas 3 level auto-chain untuk cegah infinite loop

5. **Clear chat** — klik tombol CLEAR di pojok kanan atas untuk mulai sesi baru

---

*Built with ❤️ using Claude API + OpenAI API*
