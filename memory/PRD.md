# Creatools — Product Requirements Document

## Original Problem Statement
Creatools is an all-in-one platform for TikTok Live streamers (Brazilian market, PT-BR primary). Feature roadmap inspired by public capabilities of tools like bettertok.app / tikscan.live, with heavy emphasis on:
- Overlays and Scoreboards / Leaderboards / Minigames
- Granular plan limits (per-day/per-month enforcement, per-user overrides)
- AI Assistant (Claude Sonnet 4.5) + AI Video Generation (Sora 2) → Emergent Object Storage
- TikTok account linking with verified profile data

## Architecture (Feb 2026)
- **Backend proxy**: FastAPI at `:8001` (supervisor `backend`) — loads `EMERGENT_LLM_KEY` + `TIKTOOLS_API_KEY` from `/app/backend/.env`, spawns Node child + serves AI routes natively.
- **Node backend**: Express (TypeScript ESM) at `:8081` — main REST API (auth, plans, tiktok, overlays, events, layouts, gifts, admin).
- **Frontend**: Vite + React (TypeScript) at `:3000` (supervisor `frontend`), wraps monorepo at `/app/tiks/artifacts/creatools`.
- **Database**: PostgreSQL 15 (creatools/creatools@127.0.0.1:5432) with Drizzle ORM. Schema at `/app/tiks/lib/db/src/schema`.

### API Domains
- `/api/auth/*`, `/api/tiktok/*`, `/api/plans`, `/api/admin/plans/*` — Node
- `/api/ai/chat/stream`, `/api/ai/chat/usage`, `/api/ai/video/*`, `/api/ai/videos` — Python (FastAPI ai_router.py, mounted BEFORE Node proxy)
- All other `/api/*` — proxied to Node

## Completed
- 2026-02-07 · **Fase 1**: Overlay Studio (dual vertical/horizontal preview + `?demo=1`).
- 2026-02-07 · **Env fixes**: PostgreSQL install/seed, Vite proxy → 127.0.0.1:8081, frontend launcher uses vite directly.
- 2026-02-07 · **Fase 3**: Granular plan limits — schema fields `maxLiveHoursPerDay`, `maxActiveOverlays`, `maxActiveScoreboards`, `maxActiveMinigames`, `maxAiChatMessagesPerDay`, `maxAiVideoGenerationsPerMonth` + admin UI editor + PATCH endpoint + `users.limitsOverride` for per-user overrides. Public `GET /api/plans` endpoint.
- 2026-02-07 · **TikTok bug fix**: verify-username now uses TikTok's PUBLIC oEmbed API + HTML scrape for avatar/follower/verified (works without paid tier). Fallback to tik.tools live_status. Tested with real TikTok users (mrbeast 129M followers, charlidamelio 159M).
- 2026-02-07 · **Fase 4**: AI Assistant (Claude Sonnet 4.5 streaming SSE) + AI Video Generator (Sora 2 with vertical 1024x1792 default + 4/8/12s durations) + Emergent Object Storage integration + plan limit enforcement + sidebar entry.

## Roadmap (Prioritized)
### P0 — Next Session
- **Fase 2** — Scoreboards / Leaderboards / Minigames redesign with dual vertical/horizontal preview and theme presets (currently pages exist but layout could be refined).
- Migrate AI chat/video usage tracking from in-memory dict → PostgreSQL (`ai_usage` table).
- Persist AI video registry (`ai_videos` table) so records survive backend restart.

### P1
- **Actions & Events polish**: expand `/events` triggers (17+ types) and actions (7+ types) inspired by bettertok public feature list.
- **Sound Alerts / TTS Tester**: page exists (`/sound-alerts`); add 100+ voices via ElevenLabs or OpenAI TTS.
- **VIP Tracker** dashboard: highlight top gifters/loyal viewers over time windows.
- **Trade Calculator** for gift value estimation.
- **Spotify song requests**: OAuth + queue overlay (needs user creds).

### P2 (Backlog)
- Discord bot (needs Discord app creation by user).
- Chrome extension.
- Desktop app (Electron/Tauri).
- Elgato Stream Deck plugin.
- Multi-account / role delegation.

## Integrations Active
- **Emergent Universal Key** (`sk-emergent-58aE90c0611153c902` — /app/backend/.env)
  - Claude Sonnet 4.5 for chat (`anthropic/claude-sonnet-4-5-20250929`)
  - Sora 2 for video (`sora-2` default, `sora-2-pro` optional)
  - Emergent Object Storage (`creatools/ai-videos/{user_id}/{uuid}.mp4`)
- **Stripe** (test key `sk_test_emergent`)
- **tik.tools** (`tk_dc6acbf11dcaca519aeded1c794bf0b2eb41ee13bad540b5` — free tier, fallback only)
- **TikTok oEmbed** (public, no key)

## Test Credentials
See `/app/memory/test_credentials.md`.

## Testing Status
- iteration_1.json: Overlay Studio (Fase 1) — PASS.
- iteration_2.json: TikTok verify + granular plan limits — PASS 100% (11/11 backend, all frontend).
- iteration_3.json: AI Assistant + AI Videos + full regression — pending (this session).

## Files of Reference
- `/app/backend/ai_router.py` — Python AI routes
- `/app/backend/server.py` — FastAPI proxy + Node spawner + ai_router mount
- `/app/tiks/artifacts/api-server/src/routes/tiktok.ts` — TikTok verify (oEmbed)
- `/app/tiks/artifacts/api-server/src/routes/plans.ts` — public + admin plans
- `/app/tiks/lib/db/src/schema/plans.ts`, `users.ts` — DB schema
- `/app/tiks/artifacts/creatools/src/pages/ai-assistant.tsx`, `ai-videos.tsx` — AI UI
- `/app/tiks/artifacts/creatools/src/components/layout/app-layout.tsx` — sidebar with `ia-section`
