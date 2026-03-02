-- =============================================================
-- Multi-Club College Event Portal — Database Schema
-- Run this ONCE in the Supabase SQL Editor
-- =============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================
-- ENUM TYPES
-- =============================================================
DO $$ BEGIN
  CREATE TYPE user_role AS ENUM ('student', 'admin');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
  CREATE TYPE event_category AS ENUM (
    'Coding', 'Robotics', 'Design', 'Music', 'Sports',
    'Cultural', 'Science', 'Business', 'Workshop', 'Other'
  );
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- =============================================================
-- USERS TABLE
-- =============================================================
CREATE TABLE IF NOT EXISTS users (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email         TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  full_name     TEXT NOT NULL,
  role          user_role NOT NULL DEFAULT 'student',
  branch        TEXT,
  semester      INT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- CLUBS TABLE
-- =============================================================
CREATE TABLE IF NOT EXISTS clubs (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        TEXT NOT NULL UNIQUE,
  description TEXT,
  logo_url    TEXT,
  admin_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- EVENTS TABLE
-- =============================================================
CREATE TABLE IF NOT EXISTS events (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  club_id          UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
  title            TEXT NOT NULL,
  description      TEXT,
  category         event_category NOT NULL DEFAULT 'Other',
  event_date       TIMESTAMPTZ NOT NULL,
  venue            TEXT,
  total_seats      INT NOT NULL CHECK (total_seats > 0),
  available_seats  INT NOT NULL CHECK (available_seats >= 0),
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT seats_check CHECK (available_seats <= total_seats)
);

-- Indexes for efficient filtering
CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_club_id ON events(club_id);
CREATE INDEX IF NOT EXISTS idx_events_available_seats ON events(available_seats);

-- =============================================================
-- REGISTRATIONS TABLE
-- =============================================================
CREATE TABLE IF NOT EXISTS registrations (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  event_id      UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT unique_registration UNIQUE (user_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_registrations_user_id ON registrations(user_id);
CREATE INDEX IF NOT EXISTS idx_registrations_event_id ON registrations(event_id);

-- =============================================================
-- ATOMIC SEAT BOOKING FUNCTION
-- Prevents race conditions when multiple users book simultaneously
-- =============================================================
CREATE OR REPLACE FUNCTION book_event_seat(p_event_id UUID, p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_reg registrations;
  v_event events;
BEGIN
  -- Check if event exists and is active
  SELECT * INTO v_event FROM events WHERE id = p_event_id FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'EVENT_NOT_FOUND' USING DETAIL = 'Event does not exist';
  END IF;

  IF NOT v_event.is_active THEN
    RAISE EXCEPTION 'EVENT_INACTIVE' USING DETAIL = 'Event is no longer active';
  END IF;

  -- Check for duplicate registration
  IF EXISTS (
    SELECT 1 FROM registrations
    WHERE user_id = p_user_id AND event_id = p_event_id
  ) THEN
    RAISE EXCEPTION 'DUPLICATE_REGISTRATION'
      USING DETAIL = 'You are already registered for this event';
  END IF;

  -- Check seat availability (atomic with FOR UPDATE lock above)
  IF v_event.available_seats <= 0 THEN
    RAISE EXCEPTION 'NO_SEATS_AVAILABLE'
      USING DETAIL = 'This event is fully booked';
  END IF;

  -- Decrement seat count
  UPDATE events
    SET available_seats = available_seats - 1
    WHERE id = p_event_id;

  -- Insert registration record
  INSERT INTO registrations (user_id, event_id)
    VALUES (p_user_id, p_event_id)
    RETURNING * INTO v_reg;

  RETURN json_build_object(
    'id', v_reg.id,
    'user_id', v_reg.user_id,
    'event_id', v_reg.event_id,
    'registered_at', v_reg.registered_at
  );
END;
$$ LANGUAGE plpgsql;

-- =============================================================
-- CANCEL REGISTRATION FUNCTION
-- Restores seat atomically
-- =============================================================
CREATE OR REPLACE FUNCTION cancel_event_registration(p_registration_id UUID, p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_reg registrations;
BEGIN
  -- Find the registration (only owner can cancel)
  SELECT * INTO v_reg FROM registrations
    WHERE id = p_registration_id AND user_id = p_user_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'REGISTRATION_NOT_FOUND'
      USING DETAIL = 'Registration not found or does not belong to you';
  END IF;

  -- Restore the seat
  UPDATE events
    SET available_seats = available_seats + 1
    WHERE id = v_reg.event_id;

  -- Delete the registration
  DELETE FROM registrations WHERE id = p_registration_id;

  RETURN json_build_object(
    'cancelled_registration_id', p_registration_id,
    'event_id', v_reg.event_id
  );
END;
$$ LANGUAGE plpgsql;

-- =============================================================
-- SAMPLE SEED DATA
-- =============================================================
-- Passwords below are bcrypt hashes of "password123"
INSERT INTO users (id, email, password_hash, full_name, role, branch, semester) VALUES
  ('a0000000-0000-0000-0000-000000000001', 'admin@college.edu',
   '$2b$12$OHlxq880nFSSvK0GxHWabefvTkkHF.VWu9lSQyfO6aOprVj2yz07O', 'Admin User', 'admin', NULL, NULL),
  ('a0000000-0000-0000-0000-000000000002', 'admin2@college.edu',
   '$2b$12$OHlxq880nFSSvK0GxHWabefvTkkHF.VWu9lSQyfO6aOprVj2yz07O', 'Bob Admin', 'admin', NULL, NULL),
  ('a0000000-0000-0000-0000-000000000003', 'student1@college.edu',
   '$2b$12$OHlxq880nFSSvK0GxHWabefvTkkHF.VWu9lSQyfO6aOprVj2yz07O', 'Charlie Student', 'student', 'Computer Science', 4),
  ('a0000000-0000-0000-0000-000000000004', 'student2@college.edu',
   '$2b$12$OHlxq880nFSSvK0GxHWabefvTkkHF.VWu9lSQyfO6aOprVj2yz07O', 'Diana Student', 'student', 'Electronics', 6)
ON CONFLICT DO NOTHING;

INSERT INTO clubs (id, name, description, admin_id) VALUES
  ('b0000000-0000-0000-0000-000000000001', 'Coding Club',
   'Building the next generation of developers.', 'a0000000-0000-0000-0000-000000000001'),
  ('b0000000-0000-0000-0000-000000000002', 'Robotics Club',
   'Innovating with hardware and AI systems.', 'a0000000-0000-0000-0000-000000000002')
ON CONFLICT DO NOTHING;

INSERT INTO events (id, club_id, title, description, category, event_date, venue, total_seats, available_seats) VALUES
  ('c0000000-0000-0000-0000-000000000001',
   'b0000000-0000-0000-0000-000000000001',
   'Hackathon 2026',
   'A 24-hour coding competition. Build anything and win prizes!',
   'Coding', NOW() + INTERVAL '7 days', 'CS Block Auditorium', 50, 50),
  ('c0000000-0000-0000-0000-000000000002',
   'b0000000-0000-0000-0000-000000000001',
   'Web Dev Workshop',
   'Hands-on React + FastAPI workshop for beginners.',
   'Workshop', NOW() + INTERVAL '3 days', 'Lab 301', 30, 30),
  ('c0000000-0000-0000-0000-000000000003',
   'b0000000-0000-0000-0000-000000000002',
   'Robo Wars 2026',
   'Battle bots in an arena. Register your robot and compete!',
   'Robotics', NOW() + INTERVAL '14 days', 'Engineering Ground', 20, 20)
ON CONFLICT DO NOTHING;
