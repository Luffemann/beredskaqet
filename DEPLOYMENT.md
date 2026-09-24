# Beredskaqet Gaming Hub — Deployment Guide

Step-by-step guide to deploy the full stack to production.

## Prerequisites

- GitHub account (for code hosting)
- Vercel account (frontend hosting)
- Railway account (backend hosting)
- Airtable API key
- Steam API key (optional)

## 1️⃣ Prepare for Deployment

### 1.1 Create `.env.production` files

**steam-mm-dashboard/.env.production**
```env
VITE_API_URL=https://api.beredskaqet.railway.app
VITE_APP_NAME=Beredskaqet Gaming Hub
```

**steam-mm-pipeline/.env.production**
```env
AIRTABLE_API_KEY=pat_your_actual_key
AIRTABLE_BASE_ID=appZh8kPulBOY571R
JWT_SECRET=your-super-secret-jwt-key-change-this
STEAM_API_KEY=your_steam_api_key_optional
```

### 1.2 Update API CORS for production domain

Edit `steam-mm-pipeline/api.py` line 22-27:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://beredskaqet.vercel.app", "https://beredskaqet.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 2️⃣ Deploy Backend to Railway

### 2.1 Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "GitHub Repo"
4. Authorize GitHub and select your repo

### 2.2 Configure Railway Service

1. In Railway dashboard, select your project
2. Click "New Service" → "GitHub Repo"
3. Select branch: `main`
4. Set root directory: `steam-mm-pipeline`

### 2.3 Set Environment Variables

In Railway Dashboard → Variables:
- `AIRTABLE_API_KEY` = `pat_xxxx`
- `AIRTABLE_BASE_ID` = `appZh8kPulBOY571R`
- `JWT_SECRET` = `your-secret-key`
- `STEAM_API_KEY` = `your-steam-key` (optional)

### 2.4 Deploy

1. Click "Deploy"
2. Railway auto-detects Dockerfile
3. Wait for build to complete
4. Get domain: `https://api.beredskaqet.railway.app`

### 2.5 Test Backend

```bash
curl -X POST https://api.beredskaqet.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"steam_id":"76561198111111111"}'

# Should return JWT token
```

## 3️⃣ Deploy Frontend to Vercel

### 3.1 Create Vercel Project

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import GitHub repo
4. Select repository

### 3.2 Configure Build Settings

- **Framework:** Vite
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Root Directory:** `steam-mm-dashboard`

### 3.3 Set Environment Variables

In Vercel → Settings → Environment Variables:
- `VITE_API_URL` = `https://api.beredskaqet.railway.app`

### 3.4 Deploy

1. Click "Deploy"
2. Wait for build
3. Get URL: `https://beredskaqet.vercel.app`

### 3.5 Test Frontend

Open `https://beredskaqet.vercel.app` in browser:
1. Click "Luffemann" to login
2. Should redirect to dashboard
3. Try toggling theme (☀️/🌙 button)

## 4️⃣ Custom Domain (Optional)

### 4.1 Point Domain to Services

**For frontend (Vercel):**
1. Vercel → Settings → Domains
2. Add custom domain
3. Add CNAME record to DNS:
   - `beredskaqet.com` → `cname.vercel.com`

**For backend (Railway):**
1. Railway → Settings → Domains
2. Add custom domain
3. Add CNAME record:
   - `api.beredskaqet.com` → `api.beredskaqet.railway.app`

### 4.2 Enable HTTPS

Both Vercel and Railway auto-enable SSL. No additional setup needed.

## 5️⃣ Monitoring & Maintenance

### 5.1 Check Logs

**Railway logs:**
```bash
railway logs -s steam-mm-pipeline
```

**Vercel logs:**
- Dashboard → Deployments → click deployment → Logs

### 5.2 Monitor Uptime

1. Add health check: https://uptimerobot.com
2. Monitor: `https://api.beredskaqet.railway.app/api/health`
3. Alert on failure

### 5.3 Error Tracking (Optional)

Add [Sentry](https://sentry.io):

**Backend (api.py):**
```python
import sentry_sdk
sentry_sdk.init("https://your-sentry-key@sentry.io/xxxxx")
```

**Frontend (main.tsx):**
```typescript
import * as Sentry from "@sentry/react";
Sentry.init({
  dsn: "https://your-sentry-key@sentry.io/xxxxx",
});
```

## 6️⃣ Post-Deployment Checklist

- [ ] Frontend loads at https://beredskaqet.vercel.app
- [ ] Backend health check: https://api.beredskaqet.railway.app/api/health
- [ ] Login works with all demo users
- [ ] Dashboard displays stats
- [ ] Theme toggle works
- [ ] Logout clears session
- [ ] Auto-login on page reload works
- [ ] Swagger docs available at /docs
- [ ] CORS works (no errors in browser console)
- [ ] Mobile responsive (test on phone)

## 7️⃣ Rollback Plan

### If deployment breaks:

**Railway:**
```bash
railway logs -s steam-mm-pipeline
# Check for errors, fix .env or code
railway deploy
```

**Vercel:**
1. Dashboard → Deployments
2. Click previous working deployment
3. Click "Redeploy"

## 8️⃣ Update & Redeploy

### Push code changes:

```bash
git add .
git commit -m "your message"
git push origin main
```

Both Railway and Vercel will auto-deploy on push to `main` branch.

## 📞 Support

**Common Issues:**

| Issue | Solution |
|-------|----------|
| CORS errors | Check `allow_origins` in api.py matches frontend URL |
| 401 Unauthorized | Regenerate JWT_SECRET and redeploy |
| API timeouts | Check Airtable API key is valid |
| Frontend 404 | Check build succeeded in Vercel logs |
| Session not persisting | Check localStorage is enabled in browser |

---

**Estimated Deployment Time:** 10-15 minutes  
**Estimated Monthly Cost:** 
- Frontend (Vercel): Free  
- Backend (Railway): $5-10/mo (with free tier credits)  
- Total: **~$5-10/month**

**Last Updated:** 2026-09-24
