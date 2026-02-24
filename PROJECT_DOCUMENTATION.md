# Hospital Management System - Project Documentation

## 1. Project Overview

The Hospital Management System is a scalable backend application built with Django and Django REST Framework.
It includes JWT authentication, role-based access, appointment booking, prescriptions, billing, analytics, caching, and deployment-ready configuration.

## 2. Technology Stack

- Backend: Django, Django REST Framework
- Database: PostgreSQL
- Cache: Redis
- Server: Gunicorn
- Static Handling: Whitenoise
- Containerization: Docker, Docker Compose
- Deployment: Render

## 3. Core Features

- JWT Authentication (`/api/auth/token/`, `/api/auth/token/refresh/`)
- Role-based access control (`ADMIN`, `DOCTOR`, `PATIENT`)
- Doctor and Patient profile management
- Appointment booking and status tracking
- Prescription module linked to appointments
- Billing and invoice tracking
- Dashboard analytics endpoint with Redis caching

## 4. Database Design

- `User` (custom auth model with role)
- `Doctor` (One-to-One with `User`)
- `Patient` (One-to-One with `User`)
- `Appointment` (FK to `Doctor` and `Patient`)
- `Prescription` (One-to-One with `Appointment`)
- `Invoice` (One-to-One with `Appointment`)

## 5. Performance Optimization

- Redis caching for dashboard statistics (`/api/accounts/dashboard/`)
- `select_related()` in queryset-heavy APIs
- Revenue aggregation with Django ORM (`Sum`, `Count`)

## 6. Security Features

- Environment-based settings (`.env`)
- JWT-based authentication via DRF SimpleJWT
- `DEBUG=False` for production
- Secure cookie toggles in production mode
- PostgreSQL configuration via environment variables

## 7. Deployment Process

- Push source to GitHub
- Provision PostgreSQL and Redis services on Render
- Use `render.yaml` blueprint for service provisioning
- Run Gunicorn (`HMS.wsgi:application`) for production serving
- Whitenoise serves static files

## 8. Future Scope Plan

- Load balancing
- Database read replicas
- Redis clustering
- Celery for asynchronous tasks
- CDN integration for static content
