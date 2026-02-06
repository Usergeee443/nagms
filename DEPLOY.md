# NGMS — Render'ga deploy qilish

## 1. Tayyorgarlik

- GitHub/GitLab da repozitoriyangiz bo‘lishi kerak.
- [Render](https://render.com) da hisob oching.

## 2. PostgreSQL bazani yaratish

1. Render Dashboard → **New** → **PostgreSQL**.
2. **Name**: `ngms-db`, **Region**: Singapore (yoki yaqin).
3. **Create Database**.
4. Yaratilgach, **Connect** → **Internal Database URL** ni nusxalang (bu sizning `DATABASE_URL`).

## 3. Web Service yaratish

1. **New** → **Web Service**.
2. Repozitoriyani ulang (GitHub/GitLab).
3. Sozlamalar:
   - **Name**: `ngms`
   - **Region**: Singapore (yoki PostgreSQL bilan bir xil)
   - **Branch**: `main` (yoki asosiy branch)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 1 --threads 2`

## 4. Environment variables

Web Service → **Environment** da qo‘shing:

| Key | Value |
|-----|--------|
| `DATABASE_URL` | PostgreSQL Internal URL (2-qismda nusxalangan) |
| `JWT_SECRET_KEY` | Istalgan uzun, xavfsiz tasodifiy satr (generator ishlatishingiz mumkin) |
| `OPENAI_API_KEY` | OpenAI API kaliti (AI bo‘limi uchun, ixtiyoriy) |

**Eslatma:** `DATABASE_URL` Render tomonidan beriladi, format: `postgres://...` — ilova ichida avtomatik ravishda `postgresql://` ga o‘giriladi.

## 5. Deploy

**Save Changes** / **Deploy** bosilgach, build va deploy jarayoni boshlanadi. Birinchi marta jadvalar `db.create_all()` orqali yaratiladi.

## 6. Admin foydalanuvchi yaratish

Birinchi deploy dan keyin admin yaratish kerak:

1. Render Dashboard → sizning **ngms** Web Service → **Shell**.
2. Shell da:
   ```bash
   python create_admin.py admin SizningXavfsizParolingiz
   ```
3. Keyin brauzerda `https://your-app.onrender.com/login.html` ga kiring va shu login/parol bilan kiring.

## 7. Blueprint (ixtiyoriy)

Agar loyihada `render.yaml` bo‘lsa, Render **Blueprint** orqali bitta marta Web Service va Database ni yaratish mumkin. Keyin **Environment** da `DATABASE_URL` va `JWT_SECRET_KEY` ni o‘zingiz qo‘yasiz (PostgreSQL yaratilgach uning Internal URL ini `DATABASE_URL` ga nusxalang).

---

## Muammolarni bartaraf etish

- **Build xatosi**: `requirements.txt` dagi barcha paketlar o‘rnatilayotganini tekshiring; Python 3.10+ ishlatilayotgan bo‘lsin.
- **Database xatosi**: `DATABASE_URL` to‘g‘ri qo‘yilganini va PostgreSQL ishlayotganini tekshiring.
- **502 Bad Gateway**: Start command `gunicorn run:app --bind 0.0.0.0:$PORT` ekanligini tekshiring; `$PORT` Render tomonidan beriladi.
- **Static fayllar**: Ilova `static/` papkasidagi HTML/CSS/JS ni Flask orqali xizmat qiladi; maxsus sozlash shart emas.
