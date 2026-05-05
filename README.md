# 🎂 Sweetland by Anny | Full-Stack ERP & E-Commerce Solution

![Backend](https://img.shields.io/badge/Backend-Railway-blue?style=flat-square)
![Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Production-brightgreen?style=flat-square)

A bespoke business management platform tailored for a professional pastry business. This project integrates a robust ERP (Enterprise Resource Planning) system for internal operations with a dynamic e-commerce funnel for end customers.

---

## 🚀 Live Environment

| Service | URL |
|---|---|
| Customer Landing Page | [sweetlandbyanny.vercel.app](https://sweetlandbyanny.vercel.app) |
| Administrative Panel | [sweetland-by-anny.vercel.app](https://sweetland-by-anny.vercel.app) |
| RESTful API | [sweetland-by-anny-production.up.railway.app](https://sweetland-by-anny-production.up.railway.app) |

---

## 🛠 Tech Stack & Architecture

The system follows a decoupled, three-tier architecture:

- **Backend:** Python 3.12 / Flask (REST API)
- **Database:** MySQL 8.0 (Managed via Railway)
- **Internal Admin Panel:** React 18 / Vite / Chart.js / Bootstrap 5
- **Public Landing Page:** Dynamic HTML5 / CSS3 / Vanilla JavaScript
- **Storage:** Cloudinary API (Persistent Cloud Media Management)
- **DevOps:** GitHub Actions (CI/CD), Railway (Production Backend), Vercel (Production Frontend)

---

## 🌟 Key Features

### 📊 Business Intelligence & Costing Engine

A custom-built financial algorithm that manages product pricing through a real-time 8-step logic:

- **Dynamic Costing:** Automatically calculates Suggested Retail Price (SRP) based on base ingredient costs + 35% Operating Expenses + 10% Market Depreciation + 5% Equipment Depreciation + Packaging.
- **Automated Stock Control:** Real-time inventory deduction triggered by order fulfillment, distinguishing between stockable items and custom-made products.
- **Financial Dashboard:** Visual analytics and KPIs providing real-time data on daily/monthly revenue and top-selling products.
- **Supply Chain Management:** A unified "Insumos" module to track inventory and prices for both raw ingredients and packaging materials.

### 🛍️ Sales Funnel & Order Management

- **Public Catalog:** Dynamically fetched from the MySQL database via REST API.
- **Atomic Checkout:** Orders are created as complete transactions in the backend and then pushed to the owner via WhatsApp API Integration.
- **Customer Portal:** Secure login for clients to track their order history, status, and account details in real-time.

### 🔒 Security Implementation (IT Focus)

Designed with a security-first mindset, implementing measures to mitigate common vulnerabilities:

**Vulnerability Mitigation:**
- **SQL Injection (SQLi):** Enforced Parameterized Queries (Prepared Statements) across all database interactions.
- **Brute-Force Protection:** Implemented Rate-Limiting via `Flask-Limiter` on all authentication endpoints.
- **Cross-Site Scripting (XSS):** Implemented `HttpOnly` and `Secure` cookie flags to prevent session hijacking.

**Secure Access & Identity:**
- **RBAC (Role-Based Access Control):** Granular permission system (Admin, Employee, Customer) enforced via custom Flask decorators and conditional UI rendering.
- **Password Hashing:** Industry-standard PBKDF2 hashing with salt (Werkzeug) for all user credentials.
- **Secure Session Management:** `SameSite=None` and `Secure=True` configuration for cross-domain cookie compatibility.

**Network Security:**
- **CORS:** Strict whitelist-based policy allowing only authorized production domains to communicate with the API.
- **Force HTTPS:** Global redirect logic to ensure all traffic is encrypted in transit.

---

## 📁 Project Structure
Sweetland-by-anny/
├── backend/              # Flask REST API (Controllers, Blueprints, Models, Utils)
│   └── static/images/    # Managed product assets (Hybrid local/cloud storage)
├── admin-panel/          # React SPA for internal business management
├── landing-page/         # Client-facing dynamic website
├── database/             # Relational schema and SQL seeding scripts
└── shared-assets/        # Branding and raw design resources

---

## 🛠 Local Development

**1. Clone & Install Backend:**
```bash
cd backend
pip install -r requirements.txt
# Configure .env with MYSQL_URL, SECRET_KEY, MAIL_PASSWORD, and CLOUDINARY_URL
python app.py
2. Run Admin Panel:
bash
Copy
cd admin-panel/mi-app
npm install
npm run dev
⚠️ Open the landing page using Live Server (VS Code extension) to avoid CORS restrictions from the file:// protocol.


Developed by Luis Esquivel as part of a commitment to building secure, scalable, and business-oriented software.
