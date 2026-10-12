import { useCallback, useEffect, useState } from "react";
import {
  api,
  getTransactions,
  type CategoryBreakdown,
  type DailyTrend,
  type MonthlyBreakdown,
  type Summary,
  type TopMerchant,
  type TransactionRow,
} from "./services/api";
import { SummaryCards } from "./components/SummaryCards";
import { DashboardCharts } from "./components/DashboardCharts";
import { UploadPanel } from "./components/UploadPanel";
import { TransactionsTable } from "./components/TransactionsTable";
import { Chatbot } from "./components/chatbot";

function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [monthly, setMonthly] = useState<MonthlyBreakdown[]>([]);
  const [trends, setTrends] = useState<DailyTrend[]>([]);
  const [merchants, setMerchants] = useState<TopMerchant[]>([]);
  const [transactions, setTransactions] = useState<TransactionRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadAll = useCallback(async () => {
    try {
      const [s, c, m, t, mer, tx] = await Promise.all([
        api.getSummary(),
        api.getCategories(),
        api.getMonthly(),
        api.getTrends(),
        api.getTopMerchants(),
        getTransactions(),
      ]);
      setSummary(s);
      setCategories(c);
      setMonthly(m);
      setTrends(t);
      setMerchants(mer);
      setTransactions(tx);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  if (error) {
    return <div className="p-6 text-red-600">Error loading dashboard: {error}</div>;
  }

  if (loading || !summary) {
    return <div className="p-6 text-gray-500">Loading dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Personal Finance Intelligence</h1>
      <UploadPanel onDataChanged={loadAll} />
      <SummaryCards summary={summary} />
      <DashboardCharts categories={categories} monthly={monthly} trends={trends} merchants={merchants} />
      <TransactionsTable transactions={transactions} />
      <Chatbot />
    </div>
  );
}

export default App;