# Nur & Garden Management System (NGMS)

Nur & Garden kompaniyasining kengayish strategiyasini boshqarish uchun yaratilgan web ilova.

## Texnologiyalar

- **Backend**: Python Flask
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens)
- **AI**: OpenAI API
- **Maps**: Mapbox (xarita integratsiyasi)

## O'rnatish

### 1. Loyihani klonlash

```bash
cd /Users/nurmuhammad/Desktop/NAGMS.apps
```

### 2. Virtual environment yaratish

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# yoki
venv\Scripts\activate  # Windows
```

### 3. Kerakli paketlarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. Environment variables sozlash

`.env.example` faylini `.env` ga nusxalang va quyidagilarni to'ldiring:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sizning_parolingiz
DB_NAME=ngms_db

JWT_SECRET_KEY=juda-xavfsiz-secret-key-yarating

OPENAI_API_KEY=sizning-openai-api-keyingiz

FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Database yaratish

**Variant 1: Python skripti orqali (tavsiya etiladi)**

```bash
python create_database.py
```

**Variant 2: MySQL da to'g'ridan-to'g'ri**

MySQL da yangi database yarating:

```sql
CREATE DATABASE ngms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Eslatma:** Agar `.env` faylida `DB_NAME=nagms_db` yozilgan bo'lsa, database nomini shunga mos qiling yoki `.env` faylida `DB_NAME=ngms_db` ga o'zgartiring.

### 6. Ilovani ishga tushirish

```bash
python run.py
```

Ilova `http://localhost:5000` da ishga tushadi.

## Foydalanish

### Birinchi admin foydalanuvchi yaratish

**Faqat bitta admin foydalanuvchi mavjud. Ro'yxatdan o'tish funksiyasi o'chirilgan.**

Admin yaratish uchun:

```bash
python create_admin.py
```

Skript sizdan username va kuchli parol so'raydi. Parol kamida 8 belgidan iborat bo'lishi kerak.

### Login

1. `/login.html` sahifasiga kiring
2. Username va password kiriting
3. Dashboard sahifasiga o'ting

## Asosiy Bo'limlar

### 1. Dashboard
- Kunlik, oylik, yillik savdo statistikasi
- O'sish dinamikasi grafiklari
- Eng ko'p sotilgan mahsulotlar
- AI tavsiyalari

### 2. Maqsadlar & Rejalar
- Maqsadlar yaratish va boshqarish
- Har bir maqsadga rejalar qo'shish
- Progress kuzatish

### 3. Mahsulotlar
- Mahsulotlar ro'yxati
- Kategoriyalar va brendlar
- Narx va marja hisoblash
- Assortiment tahlili

### 4. Ta'minotchilar
- Ta'minotchilar ro'yxati
- Ishonchlilik reytingi
- Tahlil: eng foydali va riskli ta'minotchilar

### 5. Do'konlar
- Do'konlar ro'yxati
- Hududga bog'lash
- Statistika: eng ko'p savdo qiladigan do'konlar

### 6. Hududlar & Xarita
- Xaritada hududlarni ko'rsatish
- Status: Egallangan (yashil), Jarayonda (sariq), Rejada (qizil)
- Hududlar ro'yxati

### 7. Savdo
- Savdo kiritish
- Statistika va grafiklar
- Online savdo kuzatuvi (Uzum Market, Yandex Market)

### 8. AI Tahlil
- Strategik savollar berish
- Hisobot yaratish (oylik, choraklik)
- Tavsiyalar olish

## API Endpoints

### Authentication
- `POST /api/auth/register` - Ro'yxatdan o'tish
- `POST /api/auth/login` - Kirish
- `GET /api/auth/me` - Joriy foydalanuvchi

### Dashboard
- `GET /api/dashboard/stats` - Umumiy statistika
- `GET /api/dashboard/growth-dynamics` - O'sish dinamikasi
- `GET /api/dashboard/top-products` - Eng ko'p sotilgan mahsulotlar

### Goals
- `GET /api/goals` - Barcha maqsadlar
- `POST /api/goals` - Yangi maqsad
- `PUT /api/goals/<id>` - Maqsadni yangilash
- `DELETE /api/goals/<id>` - Maqsadni o'chirish
- `GET /api/goals/<id>/plans` - Rejalar ro'yxati
- `POST /api/goals/<id>/plans` - Yangi reja

### Products
- `GET /api/products` - Barcha mahsulotlar
- `POST /api/products` - Yangi mahsulot
- `GET /api/products/categories` - Kategoriyalar
- `GET /api/products/brands` - Brendlar
- `GET /api/products/analysis/top-profitable` - Eng foydali mahsulotlar

### Suppliers
- `GET /api/suppliers` - Barcha ta'minotchilar
- `POST /api/suppliers` - Yangi ta'minotchi
- `GET /api/suppliers/analysis/most-profitable` - Eng foydali ta'minotchilar

### Shops
- `GET /api/shops` - Barcha do'konlar
- `POST /api/shops` - Yangi do'kon
- `GET /api/shops/analysis/top-shops` - Eng ko'p savdo qiladigan do'konlar

### Regions
- `GET /api/regions` - Barcha hududlar
- `POST /api/regions` - Yangi hudud
- `GET /api/regions/map-data` - Xarita ma'lumotlari

### Sales
- `GET /api/sales` - Barcha savdolar
- `POST /api/sales` - Yangi savdo
- `GET /api/sales/statistics` - Savdo statistikasi

### AI
- `POST /api/ai/ask` - AI ga savol berish
- `POST /api/ai/report` - Hisobot yaratish
- `GET /api/ai/recommendations` - Tavsiyalar

## Xavfsizlik

- Barcha API endpointlar JWT token talab qiladi (login va registerdan tashqari)
- Parollar hash qilinadi (Werkzeug security)
- CORS sozlanadi

## Keyingi Rivojlantirish

- [ ] Mobil ilova (React Native yoki Flutter)
- [ ] Multi-user support (Manager roli)
- [ ] Real-time notifications
- [ ] Export to Excel/PDF
- [ ] Advanced analytics
- [ ] API integratsiyalar (Uzum Market, Yandex Market)

## Muammo hal qilish

### Database xatosi
- MySQL server ishlamoqda ekanligini tekshiring
- `.env` faylida database ma'lumotlari to'g'ri ekanligini tekshiring

### OpenAI API xatosi
- `.env` faylida `OPENAI_API_KEY` to'g'ri ekanligini tekshiring
- API key aktivligini tekshiring

### Xarita API sozlash

**Variant 1: Mapbox (Professional)**
- [mapbox.com](https://www.mapbox.com/) ga kiring
- Access Token oling
- `regions.html` da `mapboxgl.accessToken` ni o'zgartiring

**Variant 2: Leaflet + OpenStreetMap (Bepul)**
- Hech qanday API key talab qilmaydi
- `/regions-leaflet.html` sahifasini ishlatishingiz mumkin
- To'liq bepul va ochiq manba

**Variant 3: Yandex Maps**
- [developer.tech.yandex.ru](https://developer.tech.yandex.ru/) dan API key oling
- O'zbekistonda yaxshi ishlaydi

Batafsil ma'lumot: `MAP_APIS.md` faylini ko'ring

## Muallif

Nur & Garden Management System

## Litsenziya

Private - Faqat Nur & Garden uchun

