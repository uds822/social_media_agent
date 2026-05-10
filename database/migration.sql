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

-- ── Row-Level Security (optional but recommended) ─────────────
-- alter table posts enable row level security;

-- ── Verify ────────────────────────────────────────────────────
select 'posts table created successfully' as result;
