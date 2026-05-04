🎂 Sweetland by Anny | Full-Stack ERP & E-Commerce Solution
![alt text](https://img.shields.io/badge/Backend-Railway-blue?style=flat-square)

![alt text](https://img.shields.io/badge/Frontend-Vercel-black?style=flat-square)

![alt text](https://img.shields.io/badge/Status-In%20Production-brightgreen?style=flat-square)
A bespoke business management platform tailored for a professional pastry business. This project integrates a robust ERP (Enterprise Resource Planning) system for internal operations with a dynamic e-commerce funnel for end customers.
🚀 Live Environment
Customer Landing Page: sweetlandbyanny.vercel.app
Administrative Panel: sweetland-by-anny.vercel.app
RESTful API: Documentation/Base URL
🛠 Tech Stack & Architecture
The system follows a decoupled, three-tier architecture:
Backend: Python 3.12 / Flask (REST API).
Database: MySQL 8.0 (Managed via Railway).
Internal Admin Panel: React 18 / Vite / Bootstrap 5.
Public Landing Page: Dynamic HTML5 / CSS3 / Vanilla JavaScript.
DevOps: GitHub Actions (CI/CD), Railway (Production Backend), Vercel (Production Frontend).
🌟 Key Features
📊 Business Intelligence & Costing Engine
A custom-built financial algorithm that manages product pricing through a real-time 8-step logic:
Dynamic Costing: Automatically calculates Suggested Retail Price (SRP) based on base ingredient costs + 35% Operating Expenses + 10% Market Depreciation + 5% Equipment Depreciation + Packaging.
Supply Chain Management: A unified "Insumos" (Supplies) module to track inventory and prices for both raw ingredients and packaging materials.
🛍️ Sales Funnel & Order Management
Public Catalog: Dynamically fetched from the MySQL database via REST API.
Atomic Checkout: Orders are created in the backend with a unique ID and then pushed to the owner via WhatsApp API Integration for final fulfillment.
Customer Portal: Secure login for clients to track their order history and status in real-time.
🔒 Security Implementation (IT Focus)
Designed with a security-first mindset, implementing measures to mitigate common vulnerabilities:
Vulnerability Mitigation:
SQL Injection (SQLi): Enforced Parameterized Queries (Prepared Statements) across all database interactions.
Cross-Site Scripting (XSS): Implemented HttpOnly and Secure cookie flags to prevent session hijacking.
Secure Session Management:
SameSite=None and Secure=True configuration for cross-domain cookie compatibility between Vercel and Railway.
Unauthorized access prevention using Flask-Login and session-based authentication.
Network Security:
CORS (Cross-Origin Resource Sharing): Strict whitelist-based policy allowing only authorized production domains to communicate with the API.
Force HTTPS: Global redirect logic to ensure all traffic is encrypted in transit.
📁 Project Structure
code
Text
Sweetland-by-anny/
├── backend/              # Flask REST API (Controllers, Blueprints, Models)
│   └── static/images/    # Managed product assets
├── admin-panel/          # React SPA for internal business management
├── landing-page/         # Client-facing dynamic website
├── database/             # Relational schema and SQL seeding scripts
└── shared-assets/        # Branding and raw design resources
🛠 Local Development
Clone & Install Backend:
code
Bash
cd backend
pip install -r requirements.txt
# Configure .env with MYSQL_URL, SECRET_KEY, and ALLOWED_ORIGINS
python app.py
Run Admin Panel:
code
Bash
cd admin-panel/mi-app
npm install
npm run dev
Developed by L-Esquivel as part of a commitment to building secure, scalable, and business-oriented software.
