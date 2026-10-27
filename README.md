# Kunlik vazifalar rejalashtiruvchisi — Daily Planner

Odamlarning kundalik ishlarini rejalashtirishiga, vaqtini unumli boshqarishiga va samaradorligini oshirishiga yordam beradigan zamonaviy, chiroyli va to‘liq funksional SaaS uslubidagi web-ilova.

---

## 🛠 Texnologiyalar

- **Backend:** Python 3.11+, Django 5.x
- **Frontend:** HTML5, CSS3 (Modern CSS variables, Flexbox & Grid), Vanilla JavaScript (AJAX / Fetch API)
- **Database:** SQLite3 (Django ORM bilan)
- **Icons:** Font Awesome 6
- **Typography:** Google Fonts — Inter
- **Grafiklar:** Chart.js
- **Xavfsizlik:** CSRF himoyasi, Django Authentication, PBKDF2 Password Hashing, User Data Isolation.

---

## ✨ Imkoniyatlar va Funksiyalar

1. **Dashboard (Bosh sahifa):**
   - Vaqtga mos salomlashuv (“Xayrli tong”, “Xayrli kun”, “Xayrli kech”).
   - Bugungi sana va kun nomi.
   - Motivatsion shior.
   - Jami, bajarilgan, bajarilmagan vazifalar soni va avtomatik hisoblanuvchi Progress Bar.
   - Bugungi vazifalar ro‘yxati va tezkor qo‘shish imkoniyati.

2. **Vazifalarni to‘liq boshqarish (CRUD):**
   - Yangi vazifa yaratish (Modal oyna orqali).
   - Mavjud vazifani tahrirlash (AJAX orqali forma to‘ldiriladi).
   - Vazifani o‘chirish (Xavfsiz tasdiqlash modali bilan).
   - Vazifa holatini o‘zgartirish (Bajarildi/Bajarilmadi — sahifani yangilamasdan AJAX bilan).
   - Har bir vazifada: Nomi, Tavsifi, Sanasi, Boshlanish vaqti, Tugash vaqti, Davomiyligi (daqiqa), Muhimlik darajasi (Past, O‘rta, Yuqori), Kategoriya (Ish, O‘qish, Shaxsiy, Sog‘liq, Boshqa).

3. **Qidiruv, Filterlash va Saralash:**
   - Nomi va tavsifi bo‘yicha qidirish (`Q` parametri).
   - Sana bo‘yicha filter.
   - Kategoriya bo‘yicha filter.
   - Muhimlik darajasi bo‘yicha filter.
   - Bajarilgan va bajarilmagan holatlar bo‘yicha ajratish.
   - Saralash: Sana bo‘yicha (yangi/eski), vaqt bo‘yicha, muhimlik bo‘yicha, nomi bo‘yicha.

4. **Taqvim (Monthly Interactive Calendar):**
   - Oylik ko‘rinish, oldingi/keyingi oylarga o‘tish.
   - Har bir kun katagida shu kundagi vazifalar soni (badge).
   - Sanani bosganda yon paneldan shu kundagi vazifalar ro‘yxati ochilishi.
   - Bugungi kun vizual ajratilgan.

5. **Statistikalar (Analytics & Charts):**
   - Kunlik bajarilgan vazifalar (so‘nggi 7 kun — Bar chart).
   - Haftalik natijalar (so‘nggi 4 hafta — Line chart).
   - Oylik natijalar (so‘nggi 6 oy — Bar chart).
   - Kategoriyalar bo‘yicha taqsimot (Doughnut chart).
   - Umumiy bajarilish foizi va ko‘rsatkichlari.

6. **Dizayn va UX:**
   - Professional SaaS interfeysi, chiroyli burchaklar va nozik soyalar.
   - Light mode va Dark mode (mavzu brauzer xotirasida saqlanadi).
   - Responsive dizayn: Desktop, planshet va smartfonlarga moslashgan.
   - Barcha matnlar sof o‘zbek tilida (lotin yozuvida).

7. **Foydalanuvchi tizimi (Multi-user Isolation):**
   - Ro‘yxatdan o‘tish (Register).
   - Kirish va Chiqish (Login / Logout).
   - Har bir foydalanuvchi faqat o‘ziga tegishli vazifalarni ko‘radi va boshqaradi.
   - URL orqali boshqa foydalanuvchining maʼlumotiga kirish qatʼiy cheklangan (404 / Forbidden).

---

## 🚀 Loyihani kompyuterda ishga tushirish

### 1. Bog‘liqliklarni o‘rnatish:
Terminal yoki PowerShell orqali loyiha papkasiga kiring:
```bash
pip install -r requirements.txt
```

### 2. Maʼlumotlar bazasini tayyorlash (migratsiya):
```bash
python manage.py migrate
```

### 3. Superuser (admin) yaratish (ixtiyoriy):
```bash
python manage.py createsuperuser
```

### 4. Serverni ishga tushirish:
```bash
python manage.py runserver
```

Brauzerda quyidagi manzilni oching:
👉 **http://127.0.0.1:8000/**

Dastlab ro‘yxatdan o‘ting yoki admin hisobingiz bilan tizimga kiring.

---

## 🧪 Testlarni ishga tushirish

Loyiha uchun barcha asosiy talablar (CRUD, foydalanuvchilar maʼlumotlari ajratilishi, filterlar, autentifikatsiya, sahifalar yuklanishi) bo‘yicha avtomatik testlar yozilgan:

```bash
python manage.py test
```
Natija: `Ran 8 tests ... OK`
