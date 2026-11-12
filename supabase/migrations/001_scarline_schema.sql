-- =====================================================================
-- SCARLINE — skema database (Supabase / PostgreSQL)
-- Jalankan file ini di Supabase Dashboard → SQL Editor, lalu jalankan
-- supabase/seed.sql untuk mengisi materi, soal, game, dan lencana.
-- =====================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- profiles
create table if not exists public.profiles (
  id          uuid primary key references auth.users (id) on delete cascade,
  full_name   text not null check (char_length(full_name) between 3 and 60),
  username    text not null unique check (username ~ '^[a-z0-9_]{3,20}$'),
  email       text not null,
  class_name  text not null check (char_length(class_name) between 1 and 20),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------- katalog
create table if not exists public.lessons (
  slug        text primary key,
  mission_no  int  not null unique,
  region      text not null,
  title       text not null,
  xp_reward   int  not null default 100,
  created_at  timestamptz not null default now()
);

create table if not exists public.quizzes (
  slug        text primary key,
  title       text not null,
  kind        text not null check (kind in ('lesson', 'training', 'daily', 'final')),
  level       int,
  lesson_slug text references public.lessons (slug) on delete cascade,
  created_at  timestamptz not null default now()
);

create table if not exists public.quiz_questions (
  id          text primary key,
  quiz_slug   text not null references public.quizzes (slug) on delete cascade,
  qtype       text not null check (qtype in ('mc', 'tf', 'num', 'point', 'line', 'match')),
  topic       text not null,
  prompt      text not null,
  payload     jsonb not null default '{}'::jsonb,   -- opsi, grafik, item
  answer      jsonb not null,                        -- kunci (TIDAK bisa dibaca siswa)
  explanation text not null default '',
  position    int  not null default 0,
  created_at  timestamptz not null default now()
);
create index if not exists quiz_questions_quiz_idx on public.quiz_questions (quiz_slug, position);

create table if not exists public.games (
  slug        text primary key,
  title       text not null,
  tagline     text not null,
  mechanic    text not null,
  description text not null,
  created_at  timestamptz not null default now()
);

create table if not exists public.achievements (
  slug        text primary key,
  title       text not null,
  description text not null,
  icon        text not null,
  xp_bonus    int  not null default 0,
  sort_order  int  not null default 0,
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------- data siswa
create table if not exists public.lesson_progress (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references public.profiles (id) on delete cascade,
  lesson_slug  text not null references public.lessons (slug) on delete cascade,
  status       text not null default 'in_progress' check (status in ('in_progress', 'completed')),
  quiz_score   int  check (quiz_score between 0 and 100),
  completed_at timestamptz,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  unique (user_id, lesson_slug)
);

create table if not exists public.quiz_attempts (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid not null references public.profiles (id) on delete cascade,
  quiz_slug        text not null references public.quizzes (slug) on delete cascade,
  kind             text not null check (kind in ('lesson', 'training', 'daily', 'final')),
  score            int  not null check (score between 0 and 100),
  correct          int  not null check (correct >= 0),
  total            int  not null check (total > 0),
  stars            int  not null default 0 check (stars between 0 and 3),
  xp_awarded       int  not null default 0 check (xp_awarded >= 0),
  duration_seconds int  not null default 0,
  answers          jsonb not null default '[]'::jsonb,
  created_at       timestamptz not null default now()
);
create index if not exists quiz_attempts_user_idx on public.quiz_attempts (user_id, quiz_slug, score desc);

create table if not exists public.game_attempts (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid not null references public.profiles (id) on delete cascade,
  game_slug        text not null references public.games (slug) on delete cascade,
  difficulty       text not null check (difficulty in ('easy', 'medium', 'hard')),
  score            int  not null check (score >= 0),
  max_score        int  not null check (max_score > 0),
  percent          numeric(5, 1) not null check (percent between 0 and 100),
  stars            int  not null default 0 check (stars between 0 and 3),
  xp_awarded       int  not null default 0 check (xp_awarded >= 0),
  rounds_correct   int  not null default 0,
  rounds_total     int  not null default 0,
  duration_seconds int  not null default 0,
  created_at       timestamptz not null default now()
);
create index if not exists game_attempts_user_idx on public.game_attempts (user_id, game_slug);

create table if not exists public.user_stats (
  user_id            uuid primary key references public.profiles (id) on delete cascade,
  total_xp           int not null default 0 check (total_xp >= 0),
  level              int not null default 1 check (level >= 1),
  missions_completed int not null default 0,
  games_played       int not null default 0,
  quizzes_taken      int not null default 0,
  finals_taken       int not null default 0,
  best_final_score   int not null default 0,
  updated_at         timestamptz not null default now()
);

create table if not exists public.user_achievements (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid not null references public.profiles (id) on delete cascade,
  achievement_slug text not null references public.achievements (slug) on delete cascade,
  earned_at        timestamptz not null default now(),
  unique (user_id, achievement_slug)
);

create table if not exists public.activity_logs (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references public.profiles (id) on delete cascade,
  activity_type text not null,
  title         text not null,
  ref           text,
  score         int,
  status        text,
  xp_awarded    int not null default 0,
  meta          jsonb not null default '{}'::jsonb,
  created_at    timestamptz not null default now()
);
create index if not exists activity_logs_user_idx on public.activity_logs (user_id, created_at desc);

-- Tantangan harian: maksimal satu klaim XP per siswa per hari.
create table if not exists public.daily_claims (
  user_id    uuid not null references public.profiles (id) on delete cascade,
  claim_date date not null,
  correct    int  not null default 0,
  total      int  not null default 3,
  xp_awarded int  not null default 0,
  created_at timestamptz not null default now(),
  primary key (user_id, claim_date)
);

-- ---------------------------------------------------------------- trigger akun baru
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  meta jsonb := coalesce(new.raw_user_meta_data, '{}'::jsonb);
begin
  insert into public.profiles (id, full_name, username, email, class_name)
  values (
    new.id,
    coalesce(nullif(meta ->> 'full_name', ''), split_part(new.email, '@', 1)),
    lower(coalesce(nullif(meta ->> 'username', ''), 'explorer_' || substr(replace(new.id::text, '-', ''), 1, 8))),
    new.email,
    coalesce(nullif(meta ->> 'class_name', ''), 'VIII')
  );
  insert into public.user_stats (user_id) values (new.id) on conflict do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------- Row Level Security
alter table public.profiles          enable row level security;
alter table public.lessons           enable row level security;
alter table public.quizzes           enable row level security;
alter table public.quiz_questions    enable row level security;
alter table public.games             enable row level security;
alter table public.achievements      enable row level security;
alter table public.lesson_progress   enable row level security;
alter table public.quiz_attempts     enable row level security;
alter table public.game_attempts     enable row level security;
alter table public.user_stats        enable row level security;
alter table public.user_achievements enable row level security;
alter table public.activity_logs     enable row level security;
alter table public.daily_claims      enable row level security;

-- Katalog: boleh dibaca siapa saja (tanpa kunci jawaban).
drop policy if exists "catalog lessons read" on public.lessons;
create policy "catalog lessons read" on public.lessons for select using (true);
drop policy if exists "catalog quizzes read" on public.quizzes;
create policy "catalog quizzes read" on public.quizzes for select using (true);
drop policy if exists "catalog games read" on public.games;
create policy "catalog games read" on public.games for select using (true);
drop policy if exists "catalog achievements read" on public.achievements;
create policy "catalog achievements read" on public.achievements for select using (true);
-- quiz_questions sengaja TANPA policy: kunci jawaban hanya bisa dibaca server (service role).

-- Profil: siswa hanya membaca & mengubah profilnya sendiri (kolom nama dan kelas saja).
drop policy if exists "own profile read" on public.profiles;
create policy "own profile read" on public.profiles for select to authenticated using (auth.uid() = id);
drop policy if exists "own profile update" on public.profiles;
create policy "own profile update" on public.profiles for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);
revoke insert, update, delete on public.profiles from anon, authenticated;
grant update (full_name, class_name, updated_at) on public.profiles to authenticated;

-- Data belajar: siswa hanya bisa MEMBACA miliknya sendiri.
-- Penulisan skor/XP hanya lewat server (service role), sehingga skor tidak bisa dimanipulasi dari browser.
do $$
declare t text;
begin
  foreach t in array array['lesson_progress', 'quiz_attempts', 'game_attempts', 'user_stats', 'user_achievements', 'activity_logs', 'daily_claims']
  loop
    execute format('drop policy if exists "own rows read" on public.%I', t);
    execute format('create policy "own rows read" on public.%I for select to authenticated using (auth.uid() = user_id)', t);
    execute format('revoke insert, update, delete on public.%I from anon, authenticated', t);
  end loop;
end $$;

revoke all on public.quiz_questions from anon, authenticated;
