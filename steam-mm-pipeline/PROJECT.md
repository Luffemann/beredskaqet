# Beredskaqet Gaming Hub — Master Project Plan

**Projekt:** CS2 Valve Matchmaking → Personalized Gaming Platform  
**Start:** 2026-09-23  
**Status:** Phase D Complete, Phase B Pending

---

## Formål
Bygge en privat medlem-portal hvor Beredskaqet-spillere kan se deres egne stats, progression, head-to-head data, fun-facts, achievements og specialization tags. Platform skal føles personlig og give ejerfølelse.

---

## 🎯 FASE OVERVIEW

| Fase | Navn | Status | Depends On |
|------|------|--------|-----------|
| A | Dashboard Mockup | ✅ DONE | — |
| B | Airtable Formler | ⏳ IN PROGRESS | A |
| D | Parser Expansion | ✅ DONE | — |
| C | React Frontend | ⏳ PENDING | B |
| E | Backend API | ⏳ PENDING | D, B |
| F | Steam Login | ⏳ PENDING | E |
| G | Deployment | ⏳ PENDING | C, E, F |
| H | Team Systems & Tournaments | ⏳ PENDING | B, C |

---

## FASE A: Dashboard Mockup & Design
**Status:** ✅ COMPLETE  
**Repo:** `beredskaqet-dashboard.html` (Artifact)  
**Owner:** Claude

### A1. Login Screen Design
- ✅ Steam OAuth button
- ✅ Branding (Beredskaqet logo)
- ✅ Visual theme (dark gaming theme)

### A2. Dashboard Main View
- ✅ Quick stats cards (kills, K/D, HS%, ADR)
- ✅ Fun facts section
- ✅ Specialization display
- ✅ Badge system

### A3. Tabbed Navigation
- ✅ Overview tab (dashboard + specialization)
- ✅ Progression tab (K/D trend, HS% climb)
- ✅ Head-to-Head tab (vs other players)
- ✅ Achievements tab (badges + milestones)

### A4. Responsive Design
- ✅ Mobile-friendly layout
- ✅ Dark mode compatibility
- ✅ Smooth transitions

---

## FASE D: Parser Expansion & Data Pipeline
**Status:** ✅ COMPLETE (tested 2026-09-24)  
**Files Modified:** `demo_parser.py`, `airtable_sync.py`  
**Owner:** Claude

### D1. Multi-Kill Detection
- ✅ Track 2k, 3k, 4k, 5k per round
- ✅ Count multi-kills per player per match
- ✅ Upload to Airtable

### D2. Specialization Classification
- ✅ Algorithm: CARRY (high kills/K/D) → Score
- ✅ Algorithm: SUPPORT (high assists/utility) → Score
- ✅ Algorithm: LURKER (entry frags, selective deaths) → Score
- ✅ Algorithm: IGL (MVPs, balanced, consistent) → Score
- ✅ Tag assigned per match to each player
- ✅ Stored in player_stats dict (ready for dashboard)

### D3. Progression Tracking
- ✅ Read previous records from Airtable
- ✅ Calculate K/D trend (current vs average)
- ✅ Calculate HS% trend
- ✅ Count total matches per player
- ✅ Display progression in sync logs

### D4. Map-Specific Stats (Partial)
- ✅ Store map name with match data
- ⏳ Full map-split views pending Airtable schema

### D5. Testing
- ✅ run_full_test.py: 3 matches, 6 players, all uploaded
- ✅ Progression tracking shows 4→5→6 kampe for Luffemann
- ✅ Multi-kills counted correctly
- ✅ No Airtable errors

---

## FASE B: Airtable Formulas & Backend Scoring
**Status:** ⏳ PENDING (next task)  
**Files to Modify:** Airtable base structure, `airtable_sync.py` (if needed)  
**Owner:** Claude (pending)

### B1. Head-to-Head Formulas
- ⏳ Create H2H table in Airtable
- ⏳ Formula: Win/loss record per player pair
- ⏳ Formula: Momentum tracking (last 3 matches)
- ⏳ Formula: Avg stats vs each opponent
- ⏳ Link from player profile dashboard

### B2. Progression Dashboard
- ⏳ Create Progression table
- ⏳ Formula: K/D trend line (5 match rolling avg)
- ⏳ Formula: HS% improvement tracking
- ⏳ Formula: Rank change over time
- ⏳ Milestone detection (100 kills, 60% HS, etc)

### B3. Specialization Badges
- ✅ Create Achievements table (tblmdcjyF7qmvRMK2)
- ✅ Formula: Award CARRY badge (if K/D > 2.0)
- ✅ Formula: Award SUPPORT badge (if assists > 8)
- ✅ Formula: Award LURKER badge (if entry frags > 40% of kills)
- ✅ Formula: Award IGL badge (if MVPs >= 3 per match)
- ✅ All_Badges formula combines all badges earned
- ✅ Tested and verified with run_full_test.py

### B4. Leaderboard Rankings
- ✅ Leaderboard table exists (tblmGtXMzrXVgUdMH)
- ✅ D-sync score verified: "Endelig Score" (fld0vuxsPpHI4xx9z)
- ✅ Role-based scores: CARRY_Score, SUPPORT_Score added
- ⏳ Weekly rankings (backend SQL required)
- ⏳ Map-specific rankings (backend aggregation required)
- ✅ Tested and working

### B5. Fun Facts Engine
- ✅ Fun_Facts AI text field added (fldEBYsw5D5mfDuTf)
- ✅ Python generator: peak performance, HS insights, K/D trends
- ✅ Career-high detection (>25 kills)
- ✅ Precision tracking (>55% HS)
- ✅ Progression trending (K/D vs rolling avg)
- ✅ Team player detection (>10 assists)
- ✅ Tested and working

---

## FASE C: React Frontend Build
**Status:** ⏳ PENDING (after B)  
**Tech:** React + TypeScript + Tailwind  
**Owner:** Claude (pending)

### C1. Project Setup
- ⏳ Create React app (Vite)
- ⏳ Install dependencies (React, Axios, D3 for charts)
- ⏳ Setup TypeScript
- ⏳ Configure Tailwind CSS

### C2. Authentication
- ⏳ Steam OAuth integration (redirect flow)
- ⏳ JWT token storage
- ⏳ Protected routes

### C3. Dashboard Components
- ⏳ Header (user info, logout)
- ⏳ Quick stats cards
- ⏳ Fun facts carousel
- ⏳ Tabs (Overview, Progression, H2H, Achievements)

### C4. Visualizations
- ⏳ K/D trend chart (D3 line chart)
- ⏳ HS% progress bar
- ⏳ Head-to-head record display
- ⏳ Achievement badges grid
- ⏳ Map-specific stats breakdown

### C5. Responsive UI
- ⏳ Mobile layouts
- ⏳ Dark/light theme toggle
- ⏳ Performance optimization

---

## FASE E: Backend API
**Status:** ⏳ PENDING (after D+B)  
**Tech:** Node.js (Express) or Python (FastAPI)  
**Owner:** Claude (pending)

### E1. Data Service
- ⏳ Airtable API wrapper (read player data)
- ⏳ Cache layer (Redis or in-memory)
- ⏳ Pagination for large datasets

### E2. Endpoints
- ⏳ GET /api/player/:steamId (personal dashboard)
- ⏳ GET /api/player/:steamId/progression (trend data)
- ⏳ GET /api/player/:steamId/h2h (head-to-head)
- ⏳ GET /api/player/:steamId/achievements (badges)
- ⏳ GET /api/leaderboard (global rankings)
- ⏳ GET /api/fun-facts (daily insights)

### E3. Real-time Updates
- ⏳ WebSocket connection (new match uploads)
- ⏳ Push notifications (new badges, overscoret, etc)

### E4. Data Aggregation
- ⏳ Weekly stat summaries
- ⏳ Monthly progression reports
- ⏳ Seasonal leaderboards

---

## FASE F: Steam Authentication
**Status:** ⏳ PENDING (after E)  
**Integration:** Steam OpenID  
**Owner:** Claude (pending)

### F1. Steam OAuth Setup
- ⏳ Register app with Valve
- ⏳ Configure redirect URI
- ⏳ Implement login flow

### F2. Session Management
- ⏳ JWT token generation
- ⏳ Token refresh logic
- ⏳ Logout handler

### F3. User Profile Sync
- ⏳ Fetch Steam profile on login
- ⏳ Map Steam ID to Airtable records
- ⏳ Update user last-seen timestamp

---

## FASE G: Deployment & Live
**Status:** ⏳ PENDING (final)  
**Platforms:** TBD (Vercel for frontend, Heroku/Railway for backend)  
**Owner:** Claude (pending)

### G1. Frontend Deployment
- ⏳ Build React app
- ⏳ Deploy to Vercel/Netlify
- ⏳ Configure custom domain

### G2. Backend Deployment
- ⏳ Deploy API to Heroku/Railway
- ⏳ Setup environment variables
- ⏳ Configure CORS for frontend

### G3. Database & Caching
- ⏳ Setup Redis (if using caching)
- ⏳ Configure Airtable API rate limiting
- ⏳ Monitor API usage

### G4. Monitoring & Logging
- ⏳ Setup error tracking (Sentry)
- ⏳ Configure log aggregation
- ⏳ Alert on failures

### G5. Go Live
- ⏳ User testing
- ⏳ Documentation (README, API docs)
- ⏳ Launch announcement

---

## FASE H: Team Systems & Tournaments
**Status:** ⏳ PENDING (after B+C)  
**Integration:** Airtable + React frontend  
**Owner:** Claude (pending)

### H1. Teams Table & Management
- ⏳ Create Teams table (team_name, members, type: 2v2/3v3/5v5)
- ⏳ Link to Player records (multipleRecordLinks)
- ⏳ Team leaderboard (win/loss, avg rating)
- ⏳ Team metadata (founded date, region, city)

### H2. Geographic Tournaments
- ⏳ Tournament generator (by region/city)
- ⏳ Bracket system (single-elim, round-robin)
- ⏳ Seeding based on team ratings
- ⏳ Match scheduling

### H3. Team Match Tracking
- ⏳ Create TeamMatches table
- ⏳ Track team-vs-team results
- ⏳ Aggregate stats per team
- ⏳ Team-level K/D, HS%, ADR

### H4. Team Leaderboards
- ⏳ Regional leaderboards (by city/region)
- ⏳ Global team rankings
- ⏳ Format-specific (2v2, 3v3, 5v5 separate)
- ⏳ Monthly/seasonal resets

### H5. Tournament Display
- ⏳ Website: Active tournaments page
- ⏳ Bracket visualization (D3)
- ⏳ Team profiles + roster
- ⏳ Match results + replays
- ⏳ Prize/achievement tracking

---

## 📋 CURRENT STATUS SUMMARY

| Phase | Item | Status | Blocker | Next |
|-------|------|--------|---------|------|
| A | Mockup | ✅ | — | B |
| D | Parser | ✅ | — | B |
| B | Formulas | ⏳ IN PROGRESS | None | Start B1 |
| C | React | ⏳ | B | After B done |
| E | Backend | ⏳ | B, D | After B done |
| F | Steam Auth | ⏳ | E | After E done |
| G | Deploy | ⏳ | E, C, F | After all done |
| H | Teams & Tournaments | ⏳ | B, C | After C done |

---

## 🚀 NEXT IMMEDIATE STEP

**Decision Point:** FASE B (Airtable formulas) vs Fast-track to Website?

**Option 1: FASE B First**
- Build solid data layer in Airtable
- Then React frontend reads clean data
- Slower but more scalable

**Option 2: Fast-track React**
- Skip Airtable formulas for now
- React queries raw data + calculates client-side
- Faster to live but less maintainable

**Recommendation:** FASE B (more professional, cleaner separation)

**Decision made:** ⏳ Waiting for user input

---

## 📝 NOTES FOR FUTURE SESSIONS

- Specialization classification works (CARRY/SUPPORT/LURKER/IGL)
- Multi-kill detection works (2k, 3k, 4k, 5k)
- Progression tracking reads Airtable history
- Test data: Luffemann tracked across 6 matches successfully
- New Airtable fields needed: Specialization, Kills_Trend, Total_Matches (for Phase B)
- Dashboard mockup includes all planned features (ready for React implementation)
- Steam API limitation: DEMOs must be downloaded manually (documented in README)

---

**Last Updated:** 2026-09-24 by Claude  
**Next Review:** Before Phase B starts
