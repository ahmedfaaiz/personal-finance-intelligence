const API_BASE_URL = "http://127.0.0.1:8000/api";

export interface Summary {
  total_income: number;
  total_expenses: number;
  total_savings: number;
  savings_rate: number;
  avg_daily_spending: number;
  transaction_count: number;
}

export interface CategoryBreakdown {
  category: string;
  amount: number;
  percentage: number;
}

export interface MonthlyBreakdown {
  month: string;
  income: number;
  expenses: number;
  savings: number;
}

export interface DailyTrend {
  date: string;
  amount: number;
}

export interface TopMerchant {
  merchant: string;
  total_spent: number;
  transaction_count: number;
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  getSummary: () => fetchJson<Summary>("/analytics/summary"),
  getCategories: () => fetchJson<CategoryBreakdown[]>("/analytics/categories"),
  getMonthly: () => fetchJson<MonthlyBreakdown[]>("/analytics/monthly"),
  getTrends: () => fetchJson<DailyTrend[]>("/analytics/trends"),
  getTopMerchants: () => fetchJson<TopMerchant[]>("/analytics/merchants"),
  
  chat: async (message: string): Promise<{ response: string }> => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed with status ${response.status}`);
    }

    return response.json();
  },

};
export interface TransactionRow {
  id: number;
  date: string;
  merchant: string;
  amount: number;
  type: string;
  category: string;
  category_source: string;
  is_duplicate: boolean;
}

export interface UploadResult {
  upload_id: number;
  filename: string;
  rows_total: number;
  rows_accepted: number;
  rows_rejected: number;
  duplicates_flagged: number;
  fixes_applied: number;
  rejected_rows: { row_number: number; reason: string }[];
}

export async function uploadFile(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/uploads`, { method: "POST", body: formData });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail ?? "Upload failed");
  }
  return body as UploadResult;
}

export async function getTransactions(): Promise<TransactionRow[]> {
  const response = await fetch(`${API_BASE_URL}/transactions?limit=100`);
  if (!response.ok) throw new Error("Could not load transactions");
  return response.json();
}

export async function resetData(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/data`, { method: "DELETE" });
  if (!response.ok) throw new Error("Could not reset data");
}