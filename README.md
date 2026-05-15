# Precivox - Business Intelligence SaaS Platform

Precivox is a Multi-Tenant Software as a Service (SaaS) platform engineered to serve as the business intelligence core for small and medium-sized enterprises (SMEs). The platform's flagship feature is its Advanced Costing Engine, which replaces fragmented spreadsheets with a unified, data-driven ecosystem for precise recipe costing, inventory management, and real-time profitability analysis.

## 💎 Core Value: The Advanced Costing Engine
The heart of Precivox is a sophisticated mathematical engine designed to provide 100% visibility into production costs and profit margins:

- **Granular Recipe Costing**: Automatically calculates the total cost of products by aggregating individual ingredient and packaging costs.

- **Operational Expense Integration**: Factors in indirect costs such as labor, utilities, and operational expenses to provide a true "cost to produce".

- **Asset Depreciation Tracking**: Includes equipment depreciation in the costing logic, ensuring long-term business sustainability.

- **Dynamic Profit Margin Analysis**: Allows owners to set desired profit margins and instantly see the recommended selling price vs. actual costs.

- **Forensic Waste (Merma) Management**: Implements specialized logic where ingredient waste is calculated by cost, while finished product waste is calculated by sale price to measure lost revenue potential.

## 🏗️ System Architecture & Tech Stack
The project utilizes a decoupled architecture consisting of a robust RESTful API and a modern administrative frontend.

### Backend (REST API)
- **Language/Framework**: Python 3.9+ with Flask.

- **Database**: PostgreSQL, chosen for its relational integrity and complex aggregations required for the costing engine.

- **Multi-Tenancy**: Implements logical data isolation where every query is strictly scoped via a `tenant_id`.

- **Services**: Cloudinary (Image Storage) and SendGrid (Transactional Emails).

### Frontend (Admin Panel)
- **Library/Framework**: React 18+ powered by Vite.

- **UI/UX**: Bootstrap 5 and custom CSS, featuring responsive dashboards.

- **BI Visualization**: Interactive charts for cost vs. sales trends using Recharts.

## 👥 User Roles & Access Control
- **Super Admin (Platform Owner)**: Manages the tenant lifecycle, global statistics, and verified payment history through a dedicated `tenant_payments` API.

- **Admin (Tenant/Business Owner)**: Operates within a completely isolated workspace to manage the entire supply chain, from raw ingredients to final sales orders.

## 🛠️ Engineering & Debugging Log (Stabilization Phase)
The platform recently underwent a comprehensive engineering sprint to ensure the reliability of the Costing Engine and core infrastructure:

1.  **Costing Engine Optimization**
    - **SQL Precision**: Implemented `COALESCE` logic in backend queries to prevent `$ NaN` errors in pricing displays when data is missing.
    - **Formula Standardization**: Standardized fields like `costo_por_unidad` and `unidad_medida` across the stack to ensure calculation accuracy between the React frontend and Flask backend.
    - **Waste Logic Refactoring**: Corrected a critical bug in ingredient waste calculation (previously defaulting to $0) to ensure accurate loss tracking.

2.  **Infrastructure & Security**
    - **URL Sanitization**: Implemented custom middleware in `app.py` to handle malformed URLs and prevent broken redirect chains during API calls.
    - **CORS & Auth**: Unified the security layer and resolved persistent "Failed to fetch" errors by standardizing `@admin_required` decorators.
    - **Data Serialization**: Standardized JSON conversion for all modules to ensure seamless data flow to the frontend dashboards.

## ⚙️ Setup and Installation

### Prerequisites

- Node.js (v18+ recommended)
- Python (v3.9+ recommended)
- A running PostgreSQL server

### 1. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file in the `backend` directory and populate it with your credentials. You can use `.env.example` as a template. Key variables include:
    - `DATABASE_URL`
    - `SECRET_KEY`
    - `SENDGRID_API_KEY`
    - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
    - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
    - `SUPPORT_EMAIL_ADDRESS`

5.  Initialize the database by running the SQL commands in `schema.sql` against your PostgreSQL instance.

### 2. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd admin-panel/mi-app
    ```
2.  Install the required Node.js packages:
    ```bash
    npm install
    ```
3.  Create a `.env` file in the `admin-panel/mi-app` directory and add the following line, pointing to your running backend server:
    ```
    VITE_API_URL=http://127.0.0.1:5000
    ```

## 🚀 Running the Application

1.  **Start the Backend Server**:
    In the `backend` directory, run:
    ```bash
    python app.py
    ```
    The API will be available at `http://127.0.0.1:5000`.

2.  **Start the Frontend Development Server**:
    In a new terminal, navigate to the `admin-panel/mi-app` directory and run:
    ```bash
    npm run dev
    ```
    The admin panel will be accessible at `http://localhost:5173`.

## 🗺️ Development Roadmap
- **Multi-Tenant Landing Pages**: Dynamic, customizable public-facing pages for individual tenants.
- **Internationalization**: Full codebase and UI migration to English standards.
- **Security Audit**: End-to-end forensic audit of data isolation and RBAC.
- **Dockerization**: Full containerization for scalable deployment on environments like Render.

```
├── admin-panel/        # React frontend application
│   └── mi-app/
├── backend/            # Flask backend API
├── landing-page/       # Public-facing static website
└── README.md           # You are here
```

## ⚙️ Setup and Installation

### Prerequisites

- Node.js (v18+ recommended)
- Python (v3.9+ recommended)
- A running PostgreSQL server

### 1. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file in the `backend` directory and populate it with your credentials. You can use `.env.example` as a template. Key variables include:
    - `DATABASE_URL`
    - `SECRET_KEY`
    - `SENDGRID_API_KEY`
    - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
    - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
    - `SUPPORT_EMAIL_ADDRESS`

5.  Initialize the database by running the SQL commands in `schema.sql` against your PostgreSQL instance.

### 2. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd admin-panel/mi-app
    ```
2.  Install the required Node.js packages:
    ```bash
    npm install
    ```
3.  Create a `.env` file in the `admin-panel/mi-app` directory and add the following line, pointing to your running backend server:
    ```
    VITE_API_URL=http://127.0.0.1:5000
    ```

## 🚀 Running the Application

1.  **Start the Backend Server**:
    In the `backend` directory, run:
    ```bash
    python app.py
    ```
    The API will be available at `http://127.0.0.1:5000`.

2.  **Start the Frontend Development Server**:
    In a new terminal, navigate to the `admin-panel/mi-app` directory and run:
    ```bash
    npm run dev
    ```
    The admin panel will be accessible at `http://localhost:5173`.