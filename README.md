# Personal Finance Intelligence

*Automated transaction analysis with a grounded AI assistant.*

Upload your bank or UPI transactions (CSV or Excel), and the app cleans them, sorts them into categories, shows a dashboard of your spending, and lets you ask an AI assistant questions about your money. The AI only explains numbers that the backend has already calculated. It is never asked to do the financial calculations itself.

> This is a budgeting and analysis tool, not financial advice.

## Features

- **File upload**: `.csv` and `.xlsx`, with checks on file type, size, and required columns
- **Data cleaning**: detects missing values, invalid dates, invalid amounts, and duplicates. Rejected rows are shown with the reason, and every fix is logged. Nothing is silently deleted.
- **Categorization**: keyword rules first (e.g. Swiggy → Food), then a small machine learning model (TF-IDF + Logistic Regression) for merchants the rules do not recognize
- **Analytics engine**: totals, savings rate, spending by category, monthly income vs expenses, daily trend, and top merchants, all calculated in Python with pandas
- **Dashboard**: summary cards, charts, and a recent transactions table
- **AI chat assistant**: answers questions about your spending using only your real figures
- **Reset button**: clears all data for a clean demo

## How the AI is kept honest

```text
Database  ->  Analytics (Python/pandas)  ->  Facts  ->  LLM  ->  Explanation
```

1. The backend calculates every number from the stored transactions.
2. Those facts are given to the LLM as context, with instructions to use only the supplied figures and to say so when the answer is not in the data.
3. The LLM turns the facts into a plain-language answer.

This reduces the chance of invented numbers, but it is enforced through prompt instructions, not by code that checks the answer. See *Limitations*.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS, Recharts |
| Backend | Python, FastAPI, SQLAlchemy |
| Data processing | pandas, openpyxl |
| Database | SQLite |
| ML categorization | scikit-learn |
| LLM | Google Gemini (via the `google-genai` SDK) |

## Project structure

```text
personal-finance-intelligence/
├── backend/
│   ├── app/
│   │   ├── api/          API routes (uploads, analytics, chat, data)
│   │   ├── ai/           LLM client
│   │   ├── analytics/    Financial calculations
│   │   ├── models/       Database tables
│   │   ├── services/     Ingestion, cleaning, categorization
│   │   ├── config.py     Settings read from .env
│   │   ├── database.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   └── src/              React app (components, services)
├── data/                 Sample files for testing
├── .env.example
└── README.md
```

## Installation

You need Python 3.11 or newer, Node.js 20 or newer, and Git.

### 1. Get the code

```powershell
git clone <your-repository-url>
cd personal-finance-intelligence
```

### 2. Set up the backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Add your API key

Create a file named `.env` inside the `backend` folder:

```text
LLM_PROVIDER=gemini
LLM_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-2.0-flash
DATABASE_URL=sqlite:///./finance.db
```

You can get a free Gemini key at https://aistudio.google.com/apikey. The `.env` file is listed in `.gitignore` and must never be committed.

### 4. Build the frontend

```powershell
cd ..\frontend
npm install
npm run build
```

## Running the app

From the `backend` folder, with the virtual environment active:

```powershell
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/**. The backend serves the built frontend, so the whole app runs from one address.

| Address | What it is |
|---|---|
| http://127.0.0.1:8000/ | The app (dashboard and chat) |
| http://127.0.0.1:8000/docs | Interactive API documentation |

### Development mode (optional)

To work on the frontend with live reloading, run the backend as above, then in a second terminal:

```powershell
cd frontend
npm run dev
```

and open http://localhost:5173/.

If you change frontend code and want the single-address version updated, run `npm run build` again.

## Using the app

1. Click **Reset data** if you want a clean start.
2. Choose a `.csv` or `.xlsx` file with the upload button.
3. Check the line under the button: it shows how many rows were accepted and rejected, and why any were rejected.
4. Explore the dashboard and the transactions table.
5. Ask the chat assistant, for example:
   - "How much did I spend on food?"
   - "What was my biggest expense category?"
   - "Compare my income and expenses by month."

### File format

| Column | Required | Notes |
|---|---|---|
| `date` | Yes | e.g. `2026-09-01` (Excel date cells also work) |
| `description` | Yes | Merchant or payment description |
| `amount` | Yes | A number |
| `type` | Recommended | `income` or `expense`. If missing, the sign of the amount is used, so include this column. |
| `payment_method` | No | Stored if present |

Maximum file size is 5 MB. For Excel files, only the first sheet is read.

Sample files are in the `data/` folder: `demo_transactions.csv` (two clean months), `test_messy.csv` (contains deliberately bad rows to show the cleaning), and `test_transactions.csv` (a tiny file).

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/uploads` | Upload and process a CSV or Excel file |
| GET | `/api/transactions` | Recent transactions |
| DELETE | `/api/data` | Delete all stored data |
| GET | `/api/analytics/summary` | Income, expenses, savings, savings rate, average daily spend |
| GET | `/api/analytics/categories` | Spending by category |
| GET | `/api/analytics/monthly` | Income vs expenses per month |
| GET | `/api/analytics/trends` | Daily spending |
| GET | `/api/analytics/merchants` | Top merchants |
| POST | `/api/chat` | Ask the AI assistant a question |
| GET | `/api/health` | Health check |

Duplicate rows are flagged and excluded from the analytics.

## Screenshots

*Add screenshots here: the dashboard, the upload result with rejected rows, and the chat assistant.*

## Limitations

- **Grounding is prompt-based.** The assistant is told to use only the supplied figures, but the code does not verify its answers against the data. It has not been formally evaluated for accuracy or hallucination rate; it was checked manually on a small number of questions.
- **The assistant sees summaries only.** It receives overall totals, category totals, monthly totals, and the top five merchants, so it cannot answer questions about individual transactions or specific days.
- **No automated tests.**
- **Small ML training set.** The fallback categorizer is trained on about 20 examples, so it will misclassify unfamiliar merchants. The keyword rules cover a limited list of merchants.
- **No user accounts.** All data lives in one shared database.
- **SQLite and floating-point amounts.** Fine for a demo; a production system would use PostgreSQL and store money as integers or decimals.
- **Limited input formats.** CSV and `.xlsx` only, not PDF statements or older `.xls` files.
- **Basic security.** File type and size checks only, with no rate limiting or authentication.

## Future work

- What-if simulator (for example, "what if I cut food spending by 20%?")
- Anomaly detection for unusual transactions
- Recurring payment and subscription detection
- A knowledge base for general finance questions (RAG)
- A formal evaluation of categorization accuracy and answer groundedness
- User accounts and a production database

## Author

*Your name, course, and college.*
