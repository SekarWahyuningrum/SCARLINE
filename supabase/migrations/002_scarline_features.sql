-- =====================================================================
-- SCARLINE — migrasi 002: pre-test/post-test, Mistake Notebook, SCAR's Diary,
-- preferensi pengguna, Secret Mission & Real-Life Challenge, lencana & game baru.
--
-- AMAN dijalankan pada database yang sudah berisi data:
--   * hanya MENAMBAH tabel baru (create table if not exists),
--   * TIDAK mengubah / menghapus tabel lama maupun datanya,
--   * baris katalog baru memakai "on conflict do nothing",
--   * boleh dijalankan ulang (idempotent).
-- Jalankan di Supabase Dashboard → SQL Editor setelah 001_scarline_schema.sql.
-- =====================================================================

-- ---------------------------------------------------------------- pre-test & post-test
create table if not exists public.assessment_attempts (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid not null references public.profiles (id) on delete cascade,
  kind             text not null check (kind in ('pretest', 'posttest')),
  score            int  not null check (score between 0 and 100),
  correct          int  not null check (correct >= 0),
  total            int  not null check (total > 0),
  duration_seconds int  not null default 0,
  topic_scores     jsonb not null default '{}'::jsonb,   -- {topik: {"correct": n, "total": n}}
  answers          jsonb not null default '[]'::jsonb,
  created_at       timestamptz not null default now()
);
create index if not exists assessment_attempts_user_idx on public.assessment_attempts (user_id, kind, created_at desc);

-- ---------------------------------------------------------------- Mistake Notebook
create table if not exists public.mistakes (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references public.profiles (id) on delete cascade,
  question_id    text not null,
  source         text not null,                 -- misi, latihan, harian, final, pretest, posttest, rahasia, kehidupan
  topic          text not null,
  prompt         text not null,
  your_answer    text not null default '',
  correct_answer text not null default '',
  explanation    text not null default '',
  status         text not null default 'perlu-latihan' check (status in ('perlu-latihan', 'dikuasai')),
  times_wrong    int  not null default 1,
  mastered_at    timestamptz,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  unique (user_id, question_id)
);
create index if not exists mistakes_user_idx on public.mistakes (user_id, status, updated_at desc);

-- ---------------------------------------------------------------- SCAR's Diary
create table if not exists public.diary_notes (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references public.profiles (id) on delete cascade,
  title       text not null check (char_length(title) between 1 and 80),
  body        text not null default '' check (char_length(body) <= 4000),
  lesson_slug text references public.lessons (slug) on delete set null,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create index if not exists diary_notes_user_idx on public.diary_notes (user_id, updated_at desc);

-- ---------------------------------------------------------------- preferensi & bookmark
create table if not exists public.user_preferences (
  user_id       uuid primary key references public.profiles (id) on delete cascade,
  theme         text not null default 'light' check (theme in ('light', 'dark', 'system')),
  music         boolean not null default false,
  sfx           boolean not null default true,
  reduce_motion boolean not null default false,
  avatar        text not null default 'explorer',
  bookmarks     jsonb not null default '[]'::jsonb,   -- slug misi yang ditandai
  favorites     jsonb not null default '[]'::jsonb,   -- slug misi favorit
  reminder_time text,                                  -- "HH:MM" pengingat belajar harian
  updated_at    timestamptz not null default now()
);

-- ---------------------------------------------------------------- Secret Mission & Real-Life Challenge
create table if not exists public.challenge_progress (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references public.profiles (id) on delete cascade,
  kind         text not null check (kind in ('secret', 'reallife')),
  ref          text not null,
  best_score   int  not null default 0 check (best_score between 0 and 100),
  points       int  not null default 0,
  completed    boolean not null default false,
  attempts     int  not null default 0,
  xp_awarded   int  not null default 0,
  completed_at timestamptz,
  updated_at   timestamptz not null default now(),
  unique (user_id, kind, ref)
);

-- ---------------------------------------------------------------- RLS: siswa hanya membaca miliknya
alter table public.assessment_attempts enable row level security;
alter table public.mistakes            enable row level security;
alter table public.diary_notes         enable row level security;
alter table public.user_preferences    enable row level security;
alter table public.challenge_progress  enable row level security;

do $$
declare t text;
begin
  foreach t in array array['assessment_attempts', 'mistakes', 'diary_notes', 'user_preferences', 'challenge_progress']
  loop
    execute format('drop policy if exists "own rows read" on public.%I', t);
    execute format('create policy "own rows read" on public.%I for select to authenticated using (auth.uid() = user_id)', t);
    -- Penulisan hanya lewat server (service role) yang selalu memfilter user_id siswa yang login.
    execute format('revoke insert, update, delete on public.%I from anon, authenticated', t);
  end loop;
end $$;

-- ---------------------------------------------------------------- katalog: game & lencana baru
insert into public.games (slug, title, tagline, mechanic, description) values
  ('line-detective', 'Line Detective', 'Menyelidiki Garis Tersangka', 'Klik garis yang cocok di grafik',
   'Beberapa garis tersangka tergambar di bidang koordinat. Baca petunjuk persamaannya, lalu tunjuk garis pelakunya.'),
  ('parallel-perpendicular', 'Parallel or Perpendicular?', 'Memilah Pasangan Garis', 'Seret kartu ke portal sejajar / tegak lurus / berpotongan',
   'Kartu pasangan persamaan garis datang satu per satu. Tentukan hubungannya dan seret ke portal yang benar.')
on conflict (slug) do nothing;

insert into public.achievements (slug, title, description, icon, xp_bonus, sort_order) values
  ('coordinate-explorer', 'Coordinate Explorer', 'Mengerjakan pre-test dan menyelesaikan Coordinate City.', 'compass', 30, 10),
  ('equation-solver', 'Equation Solver', 'Menyelesaikan semua Real-Life Mathematics Challenge.', 'calc', 60, 11),
  ('graph-architect', 'Graph Architect', 'Meraih ≥ 70% di Line Builder dan Gradient Rush.', 'ruler', 50, 12),
  ('line-detective', 'Line Detective', 'Meraih ≥ 70% di game Line Detective.', 'search', 40, 13),
  ('daily-streak', 'Daily Streak', 'Belajar 3 hari berturut-turut.', 'flame', 40, 14),
  ('rising-line', 'Rising Line', 'Nilai post-test lebih tinggi daripada nilai pre-test.', 'growth', 60, 15),
  ('master-of-straight-lines', 'Master of Straight Lines', 'Menuntaskan seluruh SCAR''s Secret Mission.', 'crown', 120, 16)
on conflict (slug) do nothing;
