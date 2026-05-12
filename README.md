# Precivox - SaaS Costing & Business Intelligence

**Precivox** is a Software-as-a-Service (SaaS) application designed to help small businesses (from bakeries to service-based models) to perform detailed product costing, manage operations, and gain financial insights through a powerful dashboard.

## 🚀 Live Demo

*   **Admin Panel:** [https://sweetland-admin.vercel.app/](https://sweetland-admin.vercel.app/)
*   **Public Landing Page:** [https://sweetlandbyanny.vercel.app/](https://sweetlandbyanny.vercel.app/)

> **Note:** The landing page is a functional demo for a specific client use case ("Sweetland by Anny"), while the admin panel represents the core Precivox SaaS product.

## ✨ Key Features

*   **Product & Inventory Management:** Catalog products, ingredients, and packaging.
*   **Advanced Costing Engine:** Automatically calculate production costs, suggested sale prices based on desired profit margins, and operational overheads.
*   **Order Management:** Track customer orders from creation to completion.
*   **Business Intelligence Dashboard:** An interactive dashboard with date-range filtering to visualize key metrics like Sales, Expenses, Waste, and **Real Net Profit**.
*   **Expense Management:** A dedicated module to register and track fixed and operational business costs.
*   **Waste (Merma) Management:** A module to record product or ingredient losses, providing a more accurate profitability analysis.
*   **User & Role Management:** Secure access control with different user roles (Admin, Employee).
*   **Secure Authentication:** Traditional email/password login, OAuth 2.0 with Google, and secure password recovery.
 
## 🛠️ Tech Stack

*   **Backend:**
    *   **Framework:** Flask (Python)
    *   **Database:** MySQL (via PyMySQL)
    *   **Authentication:** Flask-Login
    *   **Security:** Flask-Limiter (Rate Limiting), Flask-CORS
*   **Frontend (Admin Panel):**
    *   **Framework:** React
    *   **Styling:** Bootstrap
    *   **Charting:** Recharts
*   **Deployment:**
    *   **Backend:** Railway
    *   **Frontend (Admin):** Vercel
    *   **Frontend (Landing):** Vercel
    *   **Image Storage:** Cloudinary

## ⚙️ Getting Started (Local Development)

### Prerequisites

*   Python 3.10+
*   Node.js & npm
*   A local MySQL database instance.

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
    ```env
    # Flask
    SECRET_KEY=your_super_secret_key
    FLASK_ENV=development

    # Database
    MYSQL_HOST=localhost
    MYSQL_USER=your_db_user
    MYSQL_PASSWORD=your_db_password
    MYSQL_DB=your_db_name
    MYSQL_PORT=3306

    # Google OAuth
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret

    # Cloudinary
    CLOUDINARY_CLOUD_NAME=your_cloudinary_name
    CLOUDINARY_API_KEY=your_cloudinary_api_key
    CLOUDINARY_API_SECRET=your_cloudinary_api_secret

    # Email (for password recovery)
    MAIL_USERNAME=your_gmail_address@gmail.com
    MAIL_PASSWORD=your_gmail_app_password
    ```
5.  Run the backend server:
    ```bash
    flask run
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
    ```env
    VITE_API_URL=http://127.0.0.1:5000
    ```
4.  Run the frontend development server:
    ```bash
    npm run dev
    ```

## 🗺️ Project Roadmap

The project is currently evolving from an MVP to a full-fledged multi-tenant SaaS application. Key development phases include:

1.  **Identity & Access:** Finalizing secure user authentication and recovery flows.
2.  **SaaS-ification:** Implementing a multi-tenant architecture for data isolation.
3.  **Security Hardening:** Advanced audit logs, security headers (CSP), and input sanitization.
4.  **Business Intelligence:** Expanding the BI module with features like report exporting (PDF/Excel).
5.  **DevOps & Quality:** API documentation (Swagger), containerization (Docker), and unit testing.