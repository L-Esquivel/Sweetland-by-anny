# 🎂 Sweetland by Anny — Full Stack Business Management System

> A complete business solution for a Colombian pastry shop — connecting a public-facing storefront with a powerful admin panel through a shared REST API.

---

## 📌 Overview

**Sweetland by Anny** is a full-stack web application built to support the real operational needs of a small pastry business. It consists of three integrated layers:

- A **customer-facing landing page** where clients can browse products, add them to a cart, and place orders via WhatsApp — with optional account creation to track order history.
- An **admin panel** (React + Vite) where the business owner can manage products, ingredients, recipes, users, and orders.
- A **Flask REST API** that connects both frontends to a shared MySQL database.

---

## 🗂️ Project Structure

```
Sweetland-by-anny/
├── backend/               # Flask REST API
│   ├── app.py             # App factory, CORS, session config
│   ├── db.py              # MySQL connection helper
│   ├── models.py          # User model (Flask-Login)
│   ├── login.py           # Auth blueprint (/auth)
│   ├── productos.py       # Products blueprint + image upload
│   ├── pedidos.py         # Orders blueprint (admin + public)
│   ├── detalle_pedidos.py # Order details blueprint
│   ├── ingredientes.py    # Ingredients blueprint
│   ├── recetas.py         # Recipes blueprint
│   ├── usuarios.py        # Users blueprint
│   ├── extensions.py      # Flask-MySQLdb init
│   └── .env               # Environment variables (not committed)
│
├── admin-panel/           # React + Vite admin dashboard
│   └── mi-app/
│       └── src/
│           ├── components/
│           │   ├── productos/     # Product management (CRUD + image upload)
│           │   ├── pedidos/       # Order management + status updates
│           │   ├── ingredientes/  # Ingredient stock management
│           │   ├── recetas/       # Recipe management (ingredients per product)
│           │   └── usuarios/      # User management
│           ├── services/          # API service layer
│           └── context/           # Auth context (session state)
│
├── landing-page/          # Static HTML customer storefront
│   ├── index.html         # Homepage with product slider
│   ├── tortas.html        # Cakes catalog (dynamic from API)
│   ├── postres.html       # Desserts catalog (dynamic from API)
│   ├── detalles.html      # Details/decorations catalog
│   ├── carrito.html       # Shopping cart
│   ├── mi-cuenta.html     # Client login, registration & order history
│   ├── aboutus.html       # About page
│   ├── contactenos.html   # Contact page
│   ├── carrito.js         # Cart logic + order saving + session management
│   └── estilos.css        # Global styles
│
├── shared-assets/
│   └── images/            # All product images served by Flask
│
└── database/
    └── scripts/
        └── sweetland_db_v1.sql   # Full database schema
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Flask 2.3, Flask-Login, Flask-CORS, Flask-MySQLdb |
| Database | MySQL 8.0 |
| Admin Frontend | React 18, Vite, Bootstrap 5 |
| Customer Frontend | Vanilla HTML, CSS, JavaScript |
| Auth | Session-based (Flask-Login + secure cookies) |
| Password security | Werkzeug `generate_password_hash` / `check_password_hash` |
| Image storage | Local filesystem (`shared-assets/images/`) served by Flask |

---

## 🗄️ Database Schema

The database `sweetland_by_anny` contains 6 tables:

```
usuarios        → Customers and admins (role-based)
productos       → Products with category, price, image, and production cost
ingredientes    → Ingredient inventory with unit cost
recetas         → Recipe table (ingredients per product with required quantity)
pedidos         → Orders (linked to users or anonymous)
detalle_pedidos → Order line items (product, quantity, subtotal)
```

**Key relationships:**
- `recetas` links `productos` ↔ `ingredientes` — used to auto-calculate production cost
- `pedidos.usuario_id` is nullable — supports anonymous orders from the landing page
- `detalle_pedidos` links orders to specific products with quantities and subtotals

---

## 🔐 Authentication & Security

The system uses **two separate authentication contexts**:

### Admin Panel
- Session-based login via Flask-Login
- Only users with `rol = 'admin'` can access the panel
- All admin endpoints protected with `@login_required`
- Passwords hashed with Werkzeug PBKDF2

### Customer (Landing Page)
- Optional login/registration via `/pedidos/public/login` and `/pedidos/public/registro`
- Accounts created from the landing page are always assigned `rol = 'cliente'`
- Logged-in customers can view their full order history at `/mi-cuenta.html`
- Anonymous orders are fully supported — `usuario_id` is stored as `NULL`

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8.0
- VS Code with Live Server extension (for landing page)

### 1. Database Setup

```bash
mysql -u root -p < database/scripts/sweetland_db_v1.sql
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in `/backend`:

```env
SECRET_KEY=your_secret_key_here
```

Start the Flask server:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### 3. Admin Panel Setup

```bash
cd admin-panel/mi-app
npm install
npm run dev
```

The admin panel will be available at `http://localhost:5173`

### 4. Landing Page

Open `landing-page/index.html` with **Live Server** (VS Code extension) to serve it at `http://127.0.0.1:5500`.

> ⚠️ Do not open HTML files directly as `file://` — the browser will block API requests due to CORS restrictions.

---

## 🌐 API Reference

### Public Endpoints (no authentication required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/productos/public` | Get all products for the storefront |
| GET | `/static/images/<filename>` | Serve product images |
| POST | `/pedidos/public` | Save an order from the cart |
| POST | `/pedidos/public/login` | Customer login |
| POST | `/pedidos/public/registro` | Customer registration |
| POST | `/pedidos/public/logout` | Customer logout |
| GET | `/pedidos/public/mis-pedidos` | Get order history (requires customer session) |

### Admin Endpoints (session required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Admin login |
| POST | `/auth/logout` | Admin logout |
| GET/POST | `/productos/` | List / create products |
| PUT/DELETE | `/productos/<id>` | Update / delete product |
| POST | `/productos/upload-image` | Upload product image |
| GET/POST | `/pedidos/` | List / create orders |
| PUT | `/pedidos/<id>/estado` | Update order status |
| GET/POST | `/ingredientes/` | List / create ingredients |
| GET/POST | `/recetas/` | List / create recipes |
| GET/POST | `/usuarios/` | List / create users |

---

## ✨ Key Features

- **Dynamic product catalog** — products added in the admin panel appear automatically on the landing page
- **Image upload from admin** — upload product images directly from the browser; stored in `shared-assets/images/` and served by Flask
- **Shopping cart** — persistent cart using `localStorage`; supports quantity tracking and WhatsApp checkout
- **Order registration** — every WhatsApp order is also saved to the database with full line-item detail
- **Customer accounts** — optional registration/login for customers to track their order history
- **Recipe & cost engine** — each product has a recipe (ingredients + quantities); production cost is auto-calculated and updated whenever a recipe changes
- **Role-based access** — admins manage everything; customers only see their own data
- **Order status workflow** — orders move through: `pendiente → confirmado → en_preparacion → completado → cancelado`

---

### 📸 Screenshots

| 🛒 Customer Storefront (Landing Page) | ⚙️ Admin Management Panel (React) |
| :---: | :---: |
| ![Landing Page](evidence/landing-page-products.png) | ![Admin Panel](evidence/admin-panel-products.png) |
| *Dynamic product catalog connected to Flask API.* | *Inventory, order tracking, and production cost management.* ||

---

## 🛣️ Roadmap

- [ ] Ingredient stock deduction on order placement
- [ ] Google OAuth for customer login
- [ ] Sales dashboard with revenue and top products
- [ ] Order notifications (email or WhatsApp Business API)
- [ ] Mobile-responsive admin panel

---


🔨 Development & Authorship
This project is 90% custom-developed, showcasing my ability to architect and implement a full-stack solution from the ground up.

Original Architecture: Designed the entire database schema and the communication flow between the Flask API and multiple frontends.

Handcrafted Logic: Developed all backend routes, authentication systems, and the custom recipe/cost engine.

End-to-End Implementation: From the initial SQL scripts to the final React components and Vanilla JS integration.


## 👨‍💻 Author

**Luis Esquivel**
[GitHub](https://github.com/L-Esquivel)

---

## 📄 License

This project was developed as a real-world solution for a small business. All rights reserved.
