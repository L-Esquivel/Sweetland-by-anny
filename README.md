# Sweetland by Anny

A custom-built full-stack business management system for a pastry shop, featuring a Flask REST API, React admin panel, and MySQL database. 90% handcrafted logic.

![Status](https://img.shields.io/badge/Status-In%20Production-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

## 🚀 Live Links

- **Admin Panel**: [https://sweetland-by-anny.vercel.app](https://sweetland-by-anny.vercel.app)
- **Backend API**: [https://sweetland-by-anny-production.up.railway.app](https://sweetland-by-anny-production.up.railway.app)
- **Landing Page**: In progress (Vercel deployment coming soon)

## ✨ Features

- **Admin Panel** (React)
  - Product management
  - Ingredients and recipes with cost calculation
  - Orders and customers
  - Real-time cost analysis (ingredients + operational costs + profit margin)

- **Backend API** (Flask + MySQL)
  - User authentication
  - Advanced recipe costing engine
  - Order management
  - Packaging and inventory

- **Landing Page** (Static HTML/CSS/JS)
  - Public catalog
  - Shopping cart
  - Contact and about sections

## 🛠 Tech Stack

- **Backend**: Flask, Flask-Login, Flask-MySQLdb, Gunicorn
- **Frontend Admin**: React + Vite
- **Landing Page**: HTML5, CSS3, Vanilla JS
- **Database**: MySQL
- **Deployment**: Railway (Backend + DB), Vercel (Frontend)

## 📋 How to Test (Production)

1. Go to the [Admin Panel](https://sweetland-by-anny.vercel.app)
2. Login with admin credentials
3. Explore:
   - Products
   - Ingredients (already loaded)
   - Recipes
   - Orders

## 🏠 Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Admin Panel
cd admin-panel/mi-app
npm install
npm run dev

# Landing Page
cd landing-page
# Open index.html directly or serve with any static server

📁 Project Structure
Sweetland-by-anny/
├── backend/              # Flask API
├── admin-panel/          # React Admin Panel
├── landing-page/         # Static Landing Page
├── database/             # SQL scripts
├── shared-assets/        # Shared images
└── README.md

🚧 Current Status
Backend: Deployed & Running
Admin Panel: Deployed & Running
Landing Page: In Progress
Database: Populated with sample data

📝 Roadmap
Complete landing page deployment
Improve shopping cart and order flow
Add more analytics
Mobile responsiveness improvements

📄 License
MIT License - see LICENSE file.