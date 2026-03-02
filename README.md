# ⚡ EventHub — Multi-Club College Event Portal

A full-stack hackathon project: decentralized club management + centralized student event discovery.

**Stack**: Python FastAPI · Supabase (PostgreSQL) · HTML/CSS/JS · JWT Auth · `uv`

---

## Quick Start

### 1. Prerequisites
- [uv](https://docs.astral.sh/uv/) installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- A [Supabase](https://supabase.com) project (free tier works)

### 2. Database Setup
1. Open **Supabase → SQL Editor**
2. Paste and run `database/schema.sql` (creates all tables, indexes, atomic functions, and seed data)

### 3. Environment Variables
```bash
cp .env.example .env
# Fill in your values:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key
# JWT_SECRET=any-long-random-string
```

### 4. Install & Run
```bash
# From project root
uv sync

# Start the backend (serves frontend too)
cd backend
uv run uvicorn main:app --reload --port 3000
```

Open **http://localhost:3000** in your browser.

---

## Project Structure

```
event-portal/
├── backend/
│   ├── main.py               # FastAPI app, CORS, static files
│   ├── config.py             # Settings + Supabase client
│   ├── dependencies.py       # JWT middleware, role guards
│   ├── auth/                 # POST /auth/register|login, GET /auth/me
│   ├── events/               # GET/POST/PATCH/DELETE /events
│   ├── clubs/                # GET/POST/PATCH /clubs
│   └── registrations/        # GET/POST/DELETE /registrations
├── database/
│   └── schema.sql            # Tables, indexes, atomic Postgres functions
├── frontend/
│   ├── index.html            # Browse events (filterable)
│   ├── login.html
│   ├── register.html
│   ├── event-detail.html     # Register/cancel, seat bar
│   ├── student-dashboard.html
│   ├── admin-dashboard.html  # Event table, registrations modal, club manager
│   ├── create-event.html     # Create + edit event form
│   ├── css/style.css
│   └── js/
│       ├── api.js            # Typed API client, token helpers
│       └── ui.js             # Toast, formatDate, buildEventCard, nav
├── pyproject.toml            # uv dependencies
└── .env.example
```

---

## API Design

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Create student or admin account |
| POST | `/auth/login` | — | JWT login |
| GET  | `/auth/me` | JWT | Current user profile |
| GET  | `/events` | — | List events (filter: date, category, search, availability, club) |
| GET  | `/events/{id}` | — | Event detail |
| POST | `/events` | Admin | Create event |
| PATCH| `/events/{id}` | Admin | Update event |
| DELETE| `/events/{id}` | Admin | Deactivate event |
| GET  | `/clubs` | — | List clubs |
| POST | `/clubs` | Admin | Create club |
| PATCH| `/clubs/{id}` | Admin | Update club |
| GET  | `/registrations/me` | JWT | My registrations |
| POST | `/registrations` | JWT | Register for event (atomic) |
| DELETE| `/registrations/{id}` | JWT | Cancel registration (seat restored) |
| GET  | `/registrations/events/{id}` | Admin | All registrations for an event |

### Key Error Codes
| Code | HTTP | When |
|------|------|------|
| `EVENT_NOT_FOUND` | 404 | Event ID doesn't exist |
| `CLUB_NOT_FOUND` | 404 | Club ID doesn't exist |
| `REGISTRATION_NOT_FOUND` | 404 | Registration doesn't belong to user |
| `DUPLICATE_REGISTRATION` | 409 | Already registered |
| `NO_SEATS_AVAILABLE` | 409 | Event fully booked |
| `EVENT_INACTIVE` | 409 | Event deactivated |
| `EMAIL_EXISTS` | 409 | Email already registered |
| `FORBIDDEN` | 403 | Admin tries to manage another club's event |

---

## Race Condition Safety

Seat booking uses an atomic PostgreSQL stored procedure (`book_event_seat`) with `SELECT ... FOR UPDATE` row locking, ensuring no overbooking even under concurrent requests.

---

## Seed Accounts (password: `password123`)

| Email | Role |
|-------|------|
| admin1@college.edu | Admin (Coding Club) |
| admin2@college.edu | Admin (Robotics Club) |
| student1@college.edu | Student |
| student2@college.edu | Student |

---

## Docs

FastAPI auto-docs available at:
- **Swagger**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc
