-- ============================================================
-- EduPlatform Social Media Agent — Supabase Database Migration
-- Run this once in the Supabase SQL Editor.
-- Dashboard → SQL Editor → New Query → paste → Run
-- ============================================================

-- Enable UUID extension
create extension if not exists "pgcrypto";

-- ── Posts table ──────────────────────────────────────────────
create table if not exists posts (
  id                 uuid         primary key default gen_random_uuid(),
  post_type          text         not null,
  subject            text,
  class_level        text,
  topic              text,
  image_url          text,
  caption            text,
  hashtags           text,
  suggestions        text,
  fact_check_status  text         not null default 'unverified',
  status             text         not null default 'generated',
  created_at         timestamptz  not null default now(),
  approved_at        timestamptz,
  published_at       timestamptz,
  instagram_post_id  text,
  facebook_post_id   text,
  error_message      text,
  expires_at         timestamptz
);

-- ── Indexes ───────────────────────────────────────────────────
create index if not exists idx_posts_status
  on posts(status);

create index if not exists idx_posts_created_at
  on posts(created_at desc);

create index if not exists idx_posts_expires_at
  on posts(expires_at)
  where expires_at is not null;

-- ── Users table ──────────────────────────────────────────────
create table if not exists users (
  username       text primary key,
  password_hash  text not null,
  backup_codes   text,
  created_at     timestamptz not null default now()
);

-- ── Row-Level Security ────────────────────────────────────────
-- IMPORTANT: Supabase enables RLS by default on new projects.
-- Run the lines below to grant the anon key full access
-- so the backend can read/write posts and users.

alter table posts enable row level security;
alter table users enable row level security;

-- Allow anon key (used by the backend) to do everything on posts
drop policy if exists "Allow all for anon" on posts;
create policy "Allow all for anon"
  on posts
  for all
  to anon
  using (true)
  with check (true);

-- Allow anon key to do everything on users
drop policy if exists "Allow all for anon" on users;
create policy "Allow all for anon"
  on users
  for all
  to anon
  using (true)
  with check (true);

-- ── Verify ────────────────────────────────────────────────────
select 'Migration complete: tables and RLS policies created successfully' as result;

