# Beredskaqet Gaming Hub — CS2 Steam MM Stats Platform

Full-stack gaming statistics and progression tracking for Beredskaqet gaming club members.

## 🎮 Features

- **Personal Dashboard**: Track kills, K/D ratio, headshot %, ADR, and more
- **Progression Tracking**: 10-game rolling average trends with momentum tracking
- **Player Specialization**: CARRY / SUPPORT / LURKER / IGL classification
- **Head-to-Head**: Win/loss records against other players
- **Achievement Badges**: Unlock badges based on performance milestones
- **Dark Gaming Theme**: Responsive UI with theme toggle
- **Authentication**: Steam OpenID + JWT token management
- **Airtable Integration**: Direct data syncing from DEMO files

## 📁 Project Structure

```
steam-mm-dashboard/        # React frontend (Vite + TypeScript + Tailwind)
├── src/
│   ├── components/        # React components (Dashboard, Login, Charts)
│   ├── services/          # API client (airtable.ts)
│   ├── App.tsx            # Main app with auth
│   └── index.css          # Tailwind + custom styles
├── dist/                  # Production build
└── tailwind.config.js     # Tailwind configuration

steam-mm-pipeline/         # Python backend (FastAPI)
├── api.py                 # FastAPI server (9 endpoints)
├── auth.py                # Auth module (JWT + Steam integration)
├── demo_parser.py         # CS2 DEMO file parser
├── airtable_sync.py       # Airtable data sync
├── run_server.py          # Server launcher
└── requirements-api.txt   # Python dependencies
```

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js 16+ & npm
- Python 3.8+
- Airtable base (optional for testing)

### Backend Setup

```bash
cd steam-mm-pipeline
pip install -r requirements-api.txt
python run_server.py
# API runs at http://localhost:8000
```

**Test login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"steam_id":"76561198111111111"}'
```

### Frontend Setup

```bash
cd steam-mm-dashboard
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

**Demo users to login with:**
- Luffemann: `76561198111111111`
- Player2: `76561198222222222`
- Player3: `76561198333333333`

## 📊 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/auth/login` | Demo Steam login → JWT token |
| `POST` | `/api/auth/verify` | Verify token validity |
| `POST` | `/api/auth/logout` | Invalidate token |
| `GET` | `/api/health` | Server health check |
| `GET` | `/api/player/{name}` | Personal stats dashboard |
| `GET` | `/api/leaderboard` | Global top 50 rankings |
| `GET` | `/api/player/{name}/progression` | K/D trend over matches |
| `GET` | `/api/player/{name}/h2h` | Head-to-head records |
| `GET` | `/api/player/{name}/achievements` | Unlocked badges |
| `GET` | `/api/stats/weekly` | Weekly leaderboard aggregation |

**Swagger Docs:** `http://localhost:8000/docs`

## 🌐 Deployment

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Frontend (Vercel)
```bash
cd steam-mm-dashboard
npm run build
# Vercel auto-detects and deploys dist/
```

1. Push to GitHub
2. Link repo in [Vercel](https://vercel.com)
3. Set environment variable: `VITE_API_URL=https://api-domain.railway.app`
4. Deploy

#### Backend (Railway)
1. Create [Railway](https://railway.app) project
2. Connect GitHub repo
3. Add Python service pointing to `steam-mm-pipeline/`
4. Set environment variables:
   - `AIRTABLE_API_KEY=your-key`
   - `JWT_SECRET=your-secret`
   - `STEAM_API_KEY=your-key`
5. Deploy

### Option 2: Self-Hosted (Recommended for Hansikap)

**Frontend:**
```bash
npm run build
# Serve dist/ with nginx or http-server
npx http-server dist/ -p 3000
```

**Backend:**
```bash
python run_server.py
# Or with Gunicorn for production:
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000
```

## 🔐 Environment Variables

Create `.env` file in each directory:

**steam-mm-dashboard/.env**
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Beredskaqet Gaming Hub
```

**steam-mm-pipeline/.env**
```env
AIRTABLE_API_KEY=pat_xxxxx
AIRTABLE_BASE_ID=appZh8kPulBOY571R
JWT_SECRET=your-jwt-secret-change-in-production
STEAM_API_KEY=your-steam-api-key
```

## 📈 Performance

- **Frontend**: 340KB JS / 11.4KB CSS (minified)
- **API Caching**: LRU cache (128 items) for Airtable queries
- **Response Time**: <100ms average (cached)
- **Rate Limit**: 60 req/min per IP (configurable)

## 🛠 Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- D3.js (charts)
- Fetch API (HTTP client)

**Backend:**
- FastAPI (REST API)
- PyJWT (authentication)
- Airtable API (database)
- Uvicorn (ASGI server)

## 📋 Development Checklist

- [x] Authentication (Steam OpenID + JWT)
- [x] API endpoints (9 live)
- [x] React components (Dashboard, Login, Charts)
- [x] Production build
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Error tracking (Sentry)
- [ ] Analytics (Plausible)
- [ ] Custom domain
- [ ] SSL/HTTPS

## 🐛 Troubleshooting

**API returns 404 for endpoints:**
- Kill Python cache: `rm -rf __pycache__`
- Restart server: `python run_server.py`

**React build fails:**
- Reinstall deps: `rm -rf node_modules && npm install`
- Clear Tailwind cache: `npm install tailwindcss@3.4.1`

**CORS errors in browser:**
- Ensure API server runs on port 8000
- Check `.env` VITE_API_URL matches API server URL

## 📞 Support

For issues, contact Luffemann or check project logs in `PROJECT_STATUS.md`

## 📄 License

Private project for Beredskaqet gaming club. All rights reserved.

---

**Last Updated:** 2026-09-24  
**Deployed:** Not yet  
**Status:** Ready for production deployment
