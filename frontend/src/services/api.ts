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
};