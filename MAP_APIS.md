# Xarita API Variantlari

O'zbekiston uchun xarita yaratish uchun quyidagi API'lardan foydalanishingiz mumkin:

## 1. Mapbox (Tavsiya etiladi) ⭐

**Afzalliklari:**
- Professional va zamonaviy
- Yaxshi performance
- Vector tiles (tez yuklanadi)
- Custom styling
- Bepul: 50,000 so'rov/oy

**Qanday olish:**
1. [mapbox.com](https://www.mapbox.com/) ga kiring
2. Ro'yxatdan o'ting
3. Access Token oling
4. `.env` faylida: `MAPBOX_TOKEN=your-token-here`

**Narxi:** Bepul (50K so'rov/oy), keyin $5/1000 so'rov

---

## 2. Leaflet + OpenStreetMap (Bepul) 🆓

**Afzalliklari:**
- To'liq bepul
- Ochiq manba
- Hech qanday API key talab qilmaydi
- O'zbekiston uchun yaxshi ishlaydi

**Qo'shish:**
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

**Narxi:** To'liq bepul

---

## 3. Yandex Maps API 🇺🇿    

**Afzalliklari:**
- O'zbekistonda yaxshi ishlaydi
- O'zbek tilida qo'llab-quvvatlash
- Bepul: 25,000 so'rov/kun

**Qanday olish:**
1. [developer.tech.yandex.ru](https://developer.tech.yandex.ru/) ga kiring
2. API key oling
3. `.env` faylida: `YANDEX_MAPS_API_KEY=your-key`

**Narxi:** Bepul (25K so'rov/kun)

---

## 4. Google Maps API

**Afzalliklari:**
- Eng mashhur
- Keng funksiyalar
- Yaxshi dokumentatsiya

**Kamchiliklari:**
- Narxi qimmat ($200/kredit)
- O'zbekistonda ba'zi cheklovlar

**Narxi:** $200 kredit bepul, keyin to'lov

---

## Tavsiya

**O'zbekiston uchun eng yaxshi variantlar:**

1. **Mapbox** - Professional loyihalar uchun (tavsiya etiladi)
2. **Leaflet + OpenStreetMap** - Bepul va ochiq manba
3. **Yandex Maps** - O'zbekistonda yaxshi ishlaydi

---

## Qanday o'rnatish

### Mapbox o'rnatish:

1. `regions.html` faylida:
```javascript
mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN';
```

2. `.env` faylida:
```
MAPBOX_TOKEN=your-token-here
```

### Leaflet o'rnatish:

1. `regions.html` faylida Mapbox o'rniga Leaflet qo'shing
2. Hech qanday API key talab qilmaydi

### Yandex Maps o'rnatish:

1. `regions.html` faylida Yandex Maps script qo'shing
2. API key sozlang

---

## Qo'shimcha ma'lumotlar

- **OpenStreetMap** - O'zbekiston uchun to'liq ma'lumotlar mavjud
- **GeoJSON** - Viloyat, tuman, qishloq chegaralari uchun
- **Nominatim** - Geocoding uchun (bepul)

