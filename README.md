# SafeScan — Real-Time QR Fraud Detector

Live camera QR scanner that analyzes payment QR codes and links for fraud
signals *before* you act on them.

**Live demo**: _add your deployed Vercel URL here once deployed_

## Project structure

```
safescan/
├── backend/         FastAPI server + rule-based risk engine
│   ├── risk_engine.py    <- the actual fraud-detection logic
│   ├── main.py            <- API wrapper around the risk engine
│   └── requirements.txt   <- Python dependencies (for Render)
├── frontend/        React app with live camera QR scanning
│   └── src/App.jsx        <- main UI
├── render.yaml      Render deployment config (backend)
└── demo_qr_codes/   Sample QR images for testing/demoing
```

## Deploying it as a permanent website

This app has two parts that deploy separately: the **backend** (FastAPI,
the risk engine) goes on **Render**, and the **frontend** (React) goes on
**Vercel**. Both are free for this use case.

### Step 1 — Push to GitHub

```bash
cd safescan
git init
git add .
git commit -m "Initial commit"
```

Create a new repo on GitHub (no README/license — you already have files),
then:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

### Step 2 — Deploy the backend on Render

1. Go to [render.com](https://render.com) → sign in with GitHub
2. **New** → **Web Service** → select your repo
3. Render should auto-detect `render.yaml` and fill in settings. If not,
   set manually:
   - **Root directory**: `backend`
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Click **Create Web Service**
5. Wait for the build to finish — you'll get a URL like
   `https://safescan-backend-xxxx.onrender.com`
6. **Test it**: open that URL in a browser, you should see
   `{"status":"SafeScan API is running"}`

⚠️ **Free tier note**: Render's free plan spins the server down after
inactivity. The first request after idle time can take 20-30 seconds to
respond while it wakes up. For a live demo, open your deployed app and
make one scan a few minutes beforehand to "wake it up" so it's fast when
it matters.

### Step 3 — Point the frontend at your live backend

In `frontend/`, create a file named `.env.production`:

```
VITE_API_BASE=https://safescan-backend-xxxx.onrender.com
```

(Use your actual Render URL from Step 2, no trailing slash.)

Commit and push this file:

```bash
git add frontend/.env.production
git commit -m "Add production API URL"
git push
```

### Step 4 — Deploy the frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → sign in with GitHub
2. **Add New** → **Project** → select your repo
3. Set **Root Directory** to `frontend`
4. Vercel should auto-detect Vite settings from `vercel.json`. If not:
   - **Build command**: `npm run build`
   - **Output directory**: `dist`
5. Click **Deploy**
6. You'll get a permanent URL like `https://safescan-yourname.vercel.app`

That's it — this URL works from any phone, anywhere, no laptop required,
no local network needed. Camera access works automatically because Vercel
serves over real HTTPS.

### Updating after changes

Any time you `git push` to `main`, both Render and Vercel auto-redeploy.
No manual redeploy steps needed.

---

## Running it locally (for development/testing only)

### One-time setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

```bash
cd frontend
npm install
```

### Running

**Terminal 1:**
```bash
cd backend
venv\Scripts\activate        # or source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser. Camera access works on
`localhost` without needing HTTPS — that requirement only applies when
accessing via a network IP address, which the deployment path avoids
entirely.

## Testing the risk engine on its own (no servers needed)

```bash
cd backend
source venv/bin/activate   # or venv\Scripts\activate on Windows
python risk_engine.py
```

Runs a built-in set of test cases and prints what the engine detects for
each — useful for checking the logic still works after edits, without
needing the camera or UI at all.

## Known limitations (mention these proactively in your pitch)

- Detection is rule-based heuristics, not a trained ML model — by design,
  for reliability and explainability in a 15-hour build.
- No live database of verified merchant QR codes (future scope).
- No visual tampering detection (e.g. a fake sticker over a real QR) —
  this app only analyzes the *decoded payload*, not the QR image itself.
- Free-tier backend hosting has a cold-start delay after inactivity (see
  Step 2 above) — wake it up before a live demo.
