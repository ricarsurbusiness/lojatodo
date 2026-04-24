# 🛒 MultiVendor E-Commerce Platform

> A production-ready multi-vendor marketplace built with microservices architecture — like Mercado Libre or eBay.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?style=flat&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat&logo=docker)
![React](https://img.shields.io/badge/React-18+-blue?style=flat&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue?style=flat&logo=typescript)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Vendor Marketplace** | Multiple sellers can register, create products, and manage their own inventory |
| **Role-Based Access Control** | Three roles: `superAdmin`, `admin`, and `cliente` with specific permissions |
| **Product Ownership** | Sellers can only edit/delete their own products; customers can view all |
| **Shopping Cart** | Persistent cart using Redis caching |
| **Order Management** | Complete order flow: creation, status updates, cancellation |
| **Analytics Dashboard** | Real-time sales statistics for admins |

---

## 🏗️ Architecture

```
                                    ┌─────────────┐
                                    │    Kong    │
                                    │ API Gateway│
                                    └─────┬─────┘
                                          │
    ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
    │         │         │         │         │         │
┌───┐     ┌───┐     ┌───┐     ┌───┐     ┌───┐     ┌───┐
│Auth│     │Prod│     │Cart│     │Order│     │Pay │     │Inv │
└───┘     └───┘     └───┘     └───┘     └───┘     └───┘
    │         │         │         │         │         │
 PostgreSQL PostgreSQL Redis    PostgreSQL PostgreSQL ─┘
```

**Technologies:**
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Alembic
- **Databases:** PostgreSQL (data), Redis (cache/sessions)
- **Frontend:** React 18, TypeScript, TailwindCSS
- **API Gateway:** Kong
- **Container:** Docker, Docker Compose

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 4GB RAM minimum

### Run Everything

```bash
# Clone and start
git clone https://github.com/your-repo/ecommerce-microservices
cd ecommerce-microservices
docker-compose up -d
```

Access the application:
- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost:9000
- **Kong Dashboard:** http://localhost:8002

### Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@admin.com | admin123 |
| Admin | admin2@admin.com | admin123 |
| Cliente | cliente@cliente.com | cliente123 |

---

## 📡 API Services

| Service | Port | Description |
|---------|------|-------------|
| Kong Gateway | 9000 | Main entry point |
| auth-service | 8001 | Authentication & users |
| product-service | 8002 | Products & categories |
| cart-service | 8003 | Shopping cart |
| order-service | 8004 | Orders management |
| inventory-service | 8005 | Stock control |
| payment-service | 8006 | Payment processing |
| notification-service | 8007 | Email notifications |
| analytics-service | 8008 | Statistics & reports |
| admin-service | 8009 | Admin dashboard |

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **superAdmin** | Full system control, manage users, all products, all orders |
| **admin** | Manage products, categories, orders, view analytics |
| **cliente** | Browse products, manage cart, make purchases |

---

## 📁 Project Structure

```
ecommerce-microservices/
├── docker-compose.yml          # Orchestrates all services
├── frontend/                  # React frontend
│   └── ecommerce-web/
│       └── src/
│           ├── pages/        # Admin & Shop pages
│           ├── components/   # Reusable UI components
│           ├── services/   # API integrations
│           └── context/    # Auth & Cart state
└── services/                # 9 Microservices
    ├── auth-service/        # JWT auth, user management
    ├── product-service/     # Products, categories
    ├── cart-service/       # Redis-backed cart
    ├── order-service/     # Order processing
    ├── inventory-service/
    ├── payment-service/
    ├── notification-service/
    ├── analytics-service/
    └── admin-service/
```

---

## 🔧 Tech Decisions & Trade-offs

- **Why FastAPI?** Async-first, auto-generated OpenAPI docs, type safety
- **Why Postgres?** ACID compliance for transactions, relational data
- **Why Redis?** Fast session/cart caching, sub-millisecond lookups
- **Why Kong?** Proven API gateway, rate limiting, auth plugins
- **Trade-off:** Using single Docker host — for scale, would separate services across nodes

---

## 📦 Deployment

Ready for container orchestration:

- **Docker Compose** → Development & preview
- **Kubernetes** → Production (recommended: GKE, EKS, or AKS)
- **Cloud Run** → Serverlesscontainers

### Required Environment Variables

```env
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
JWT_SECRET=your-secret-key
KONG_URL=http://kong:8000
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License - Feel free to use this project for learning or as a portfolio base.

---

## 🙏 Acknowledgments

- Inspired by [Mercado Libre](https://www.mercadolibre.com/) marketplace model
- Architecture patterns from [Microsoft's eShop on Containers](https://github.com/dotnet-architecture/eShopOnContainers)

---

> ⭐ If this project helps you learn or build your portfolio, give it a star!