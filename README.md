# catchPhish — AI + Web3 Phishing Detector

A full-stack phishing detection system combining Machine Learning with blockchain-based community reporting.

## Features
- **ML Detection** — Random Forest classifier with 16 URL features, 97%+ accuracy
- **Community Reporting** — authenticated users flag suspicious URLs
- **On-Chain Registry** — confirmed phishing hashes recorded on Ethereum via smart contract
- **React Dashboard** — real-time URL scanning with feature breakdown and confidence score

---

## Project Structure
```
catchphish-web3/
├── backend/              Django REST API + ML engine
│   ├── api/              endpoints, models, serializers
│   ├── ml/               feature extraction + model inference
│   │   ├── feature_extraction.py
│   │   ├── predictor.py
│   │   └── models/       ← place phishing_rf_model.pkl here after training
│   └── catchphish/       Django settings & URLs
├── contracts/            Hardhat + Solidity smart contract
│   ├── contracts/PhishRegistry.sol
│   └── scripts/deploy.js
├── colab/                ML training notebook
│   └── catchphish_training.ipynb
├── frontend/             React 18 + TypeScript + Tailwind + shadcn/ui
│   └── src/
│       ├── pages/Home.tsx
│       ├── components/ui/
│       └── hooks/usePhishCheck.ts
└── data/                 Dataset (phishing URL CSV, 11055 records)
    └── phishing_dataset.csv
```

---

## Quick Start

### Step 1 — Train ML Model (Google Colab)
1. Open `colab/catchphish_training.ipynb` in [Google Colab](https://colab.research.google.com/)
2. Click **Runtime → Run All**
3. After training completes, the notebook **auto-downloads** `phishing_rf_model.pkl`
4. Place the downloaded file at `backend/ml/models/phishing_rf_model.pkl`

**Graphs & outputs you will see in Colab:**
| Cell | Output |
|------|--------|
| Cell 3 | Dataset shape, first 5 rows, class distribution |
| Cell 5 | Random Forest accuracy + confusion matrix heatmap |
| Cell 6 | Classification report (precision, recall, F1) for all 3 models |
| Cell 7 | Feature importance bar chart (top 16 features) |
| Cell 8 | Saves `phishing_rf_model.pkl` and `phishing_rf_model.joblib` |
| Cell 9 | Auto-downloads the `.pkl` file to your computer |

---

### Step 2 — Backend (Django REST)
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
mkdir ml\models
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver
```
Backend runs at → **http://127.0.0.1:8000**

---

### Step 3 — Smart Contract (Hardhat) — 2 terminals
```cmd
# Terminal A
cd contracts
npm install
npx hardhat node

# Terminal B (after Terminal A is running)
cd contracts
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
```
Copy the printed contract address into `backend/.env` as `CONTRACT_ADDRESS=0x...`

---

### Step 4 — Frontend (React + Vite)
```cmd
cd frontend
npm install
npm run dev
```
Frontend runs at → **http://localhost:5173**

---

## Dataset

The dataset is included at `data/phishing_dataset.csv`.

| Property | Value |
|----------|-------|
| Total records | 11,055 |
| Phishing URLs | 4,898 |
| Legitimate URLs | 6,157 |
| Features | 16 URL-based features |
| Label | 1 = Phishing, 0 = Legitimate |

**Feature List:**
`Have_IP`, `Have_At`, `URL_Length`, `URL_Depth`, `Redirection`, `https_Domain`, `TinyURL`, `Prefix_Suffix`, `DNS_Record`, `Web_Traffic`, `Domain_Age`, `Domain_End`, `iFrame`, `Mouse_Over`, `Right_Click`, `Web_Forwards`

---

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/detect/` | POST | No | ML phishing detection |
| `/api/report/` | POST | JWT | Community report a URL |
| `/api/chain-report/` | POST | JWT | Record URL hash on-chain |
| `/api/token/` | POST | No | Login → get JWT tokens |
| `/api/token/refresh/` | POST | No | Refresh JWT |
| `/api/signup/` | POST | No | Register new account |

**Example detect request:**
```json
POST /api/detect/
{ "url": "https://suspicious-site.tk/login" }
```
**Response:**
```json
{
  "verdict": "Phishing",
  "confidence": 0.94,
  "features": {
    "Have_IP": 0, "Have_At": 0, "URL_Length": 1,
    "TinyURL": 0, "Prefix_Suffix": 0, ...
  }
}
```

---

## Stack
| Layer | Technology |
|-------|-----------|
| ML Engine | scikit-learn · Random Forest · XGBoost · 16 features |
| Backend | Django 4.2 · Django REST Framework · JWT · web3.py |
| Blockchain | Solidity 0.8 · Hardhat · PhishRegistry smart contract |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS · shadcn/ui |
