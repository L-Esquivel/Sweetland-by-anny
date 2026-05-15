# Precivox - SaaS Costing & Business Intelligence

**Precivox** is a high-precision financial intelligence engine and multi-tenant SaaS platform designed to automate cost analysis and optimize profitability for small to medium-sized businesses.

**Key Achievement:** Reduced operational calculation time by 95% through a custom-built dynamic pricing engine.

## 🚀 Live Demo

*   **Admin Panel:** [https://precivox.vercel.app/](https://precivox.vercel.app/)
*   **Public Landing Page:** [https://sweetlandbyanny.vercel.app/](https://sweetlandbyanny.vercel.app/)

> **Note:** The landing page is a functional demo for a specific client use case ("Sweetland by Anny"), while the admin panel represents the core Precivox SaaS product.

## ✨ Key Features

*   **Product & Inventory Management:** Catalog products, ingredients, and packaging.
*   **Multi-Tenant Architecture:** Full data isolation between different organizations (tenants), managed by a Super Admin.
*   **Modular System:** Ability to enable or disable specific features (e.g., 'Pedidos', 'Recetas') for each tenant.
*   **Advanced Costing Engine:** Automatically calculate production costs, suggested sale prices based on desired profit margins, and operational overheads.
*   **Order Management:** Track customer orders from creation to completion.
*   **Business Intelligence Dashboard:** An interactive dashboard with date-range filtering to visualize key metrics like Sales, Expenses, Waste, and **Real Net Profit**.
*   **Expense Management:** A dedicated module to register and track fixed and operational business costs.
*   **Waste (Merma) Management:** A module to record product or ingredient losses, providing a more accurate profitability analysis.
*   **User & Role Management:** Secure access control with different user roles (Admin, Employee).
*   **Secure Authentication:** Traditional email/password login, OAuth 2.0 with Google, and secure password recovery.
 
## 🛠️ Tech Stack

*   **Backend:**
    *   **Framework:** Flask (Python) with Gunicorn
    *   **Database:** PostgreSQL
    *   **Authentication:** Flask-Login
    *   **Security:** Flask-Limiter (Rate Limiting), Flask-CORS
*   **Frontend (Admin Panel):**
    *   **Framework:** React (Vite)
    *   **Styling:** Bootstrap
    *   **Charting:** Recharts
*   **Deployment:**
    *   **Backend & Database:** Render
    *   **Frontend (Admin):** Vercel
    *   **Frontend (Landing):** Vercel
    *   **Image Storage:** Cloudinary

## ⚙️ Getting Started (Local Development)

### Prerequisites

*   Python 3.10+
*   Node.js & npm
*   A local PostgreSQL database instance.

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file in the `backend` directory and add the following environment variables:
    ```dotenv
    # Flask
    SECRET_KEY=your_super_secret_key
    FLASK_ENV=development

    # Database
    DATABASE_URL=postgresql://user:password@host:port/dbname

    # Google OAuth
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret

    # Cloudinary
    CLOUDINARY_CLOUD_NAME=your_cloudinary_name
    CLOUDINARY_API_KEY=your_cloudinary_api_key
    CLOUDINARY_API_SECRET=your_cloudinary_api_secret

    # Email (SendGrid for password recovery & support)
    SENDGRID_API_KEY=your_sendgrid_api_key
    SENDER_EMAIL=verified_sender@example.com
    SUPPORT_EMAIL_ADDRESS=your_support_email@example.com

    # SaaS Configuration
    FRONTEND_URL=http://localhost:5173
    PUBLIC_TENANT_ID=1
    ```
5.  Initialize the database by running the `schema.sql` script on your PostgreSQL instance.
6.  Run the backend server:
    ```bash
    python app.py
    ```

### Frontend (Admin Panel) Setup

1.  Navigate to the `admin-panel/mi-app` directory:
    ```bash
    cd admin-panel/mi-app
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Create a `.env.local` file in the `admin-panel/mi-app` directory and add the backend URL:
    ```dotenv
    VITE_API_URL=http://127.0.0.1:5000
    ```
4.  Run the frontend development server:
    ```bash
    npm run dev
    ```

## 🗺️ Project Roadmap

The project is currently evolving from an MVP to a full-fledged multi-tenant SaaS application. Key development phases include:

1.  **✅ Identity & Access:** Finalizing secure user authentication and recovery flows.
    *   *Status: Completed. OAuth 2.0 (Google) and secure password recovery via SendGrid are implemented.*

2.  **✅ SaaS-ification:** Implementing a multi-tenant architecture for data isolation.
    *   *Status: Completed. The database schema and backend logic support full data isolation, a Super Admin role, and modular features per tenant.*

3.  **✅ Deployment & CI/CD:** Migrated to a professional-grade stack (PostgreSQL on Render, Vercel).
    *   *Status: Completed.*

4.  **Security Hardening:** Advanced audit logs, security headers (CSP), and input sanitization.
    *   *Status: In Progress.*

5.  **DevOps & Quality:** API documentation (e.g., Swagger), containerization (Docker), and unit testing.