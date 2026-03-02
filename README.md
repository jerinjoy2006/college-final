  ⚡ EventHub — Multi-Club College Event Portal


  EventHub is a high-performance, full-stack event management system designed for colleges. It provides a decentralized
  platform where multiple clubs can independently manage their events while offering students a centralized
  "discovery-to-registration" experience.


  !FastAPI (https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
  !Supabase (https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
  !PostgreSQL (https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
  !JavaScript (https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

  ---

  🚀 Key Features


  For Students
   * Event Discovery: Browse, search, and filter events by category (Coding, Robotics, Design, etc.), date, or club.
   * Real-time Seat Tracking: Visual "seat bars" show exactly how many spots are left before you register.
   * One-Click Registration: Instant registration with automatic conflict checks.
   * Personal Dashboard: Manage your upcoming events and cancel registrations to free up seats for others.


  For Club Admins
   * Event Management: Create, edit, and deactivate events for your specific club.
   * Attendee Tracking: Export or view a real-time list of students registered for your events.
   * Club Customization: Manage your club's profile, logo, and description.
   * Permission Control: Secure JWT-based access ensures admins can only modify their own club's data.

  ---

  🛠️ Tech Stack


   * Backend: FastAPI (https://fastapi.tiangolo.com/) (Python) — Chosen for its speed and automatic Swagger
     documentation.
   * Database: Supabase (https://supabase.com/) (PostgreSQL) — Powers the data layer with robust relational integrity.
   * Auth: JWT (JSON Web Tokens) — Secure, stateless authentication for students and admins.
   * Frontend: Vanilla HTML5, CSS3, and Modern JavaScript (ES6+). No heavy frameworks, just clean, fast code.
   * Package Management: uv (https://docs.astral.sh/uv/) — Extremely fast Python package installer and resolver.

  ---

  🏗️ Project Structure


    1 ├── backend/
    2 │   ├── auth/           # JWT Login, Registration & Middleware
    3 │   ├── events/         # Event CRUD & Filtering logic
    4 │   ├── clubs/          # Club profile management
    5 │   ├── registrations/  # Seat booking & Cancellation logic
    6 │   ├── main.py         # App entry point & static file routing
    7 │   └── config.py       # Supabase & Environment configuration
    8 ├── database/
    9 │   └── schema.sql      # Database tables & Atomic Stored Procedures
   10 ├── frontend/
   11 │   ├── js/
   12 │   │   ├── api.js      # Centralized API client (Fetch wrapper)
   13 │   │   └── ui.js       # Reusable UI components (Toasts, Cards)
   14 │   ├── css/            # Modern, responsive styling
   15 │   └── *.html          # Semantic HTML templates
   16 └── pyproject.toml      # Dependency management

  ---

  ⚡ Technical Highlight: Race Condition Safety


  One of the project's most critical features is the Atomic Seat Booking. In high-traffic scenarios (e.g., a popular
  Hackathon), multiple users might try to book the last remaining seat at the exact same millisecond.


  EventHub solves this using a PostgreSQL Stored Procedure (book_event_seat):
   1. It uses SELECT ... FOR UPDATE to lock the event row during the transaction.
   2. It verifies seat availability and duplicate registration in one atomic step.
   3. If successful, it decrements the seat count and creates the registration record simultaneously.
  Result: Zero overbooking, zero data corruption.

  ---

  🏁 Getting Started


  1. Prerequisites
   * Python 3.12+ (https://www.python.org/)
   * uv (https://docs.astral.sh/uv/install/) (recommended) or pip
   * A Supabase (https://supabase.com/) account.


  2. Database Setup
   1. Create a new project in Supabase.
   2. Go to the SQL Editor in the Supabase dashboard.
   3. Paste the contents of database/schema.sql and run it. This creates the tables, indexes, and atomic functions.

  3. Environment Configuration
  Create a .env file in the backend/ directory:


   1 SUPABASE_URL=your_supabase_project_url
   2 SUPABASE_KEY=your_supabase_anon_key
   3 JWT_SECRET=your_random_secret_string

  4. Installation & Run


   1 # Install dependencies
   2 uv sync
   3
   4 # Run the server
   5 cd backend
   6 uv run uvicorn main:app --reload --port 3000
  Visit http://localhost:3000 to see the app!

  ---

  📖 API Documentation


  Once the backend is running, you can explore the fully interactive API documentation:
   * Swagger UI: http://localhost:3000/docs
   * ReDoc: http://localhost:3000/redoc

  ---


  🤝 Seed Accounts
  For testing purposes, you can use these accounts (Password: password123):
   * Admin: admin@college.edu (Coding Club)
   * Student: student1@college.edu

