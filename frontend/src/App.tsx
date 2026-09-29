import { useEffect, useState } from "react";
import { api, type Summary, type CategoryBreakdown, type MonthlyBreakdown, type DailyTrend, type TopMerchant } from "./services/api";
import { SummaryCards } from "./components/SummaryCards";
import { DashboardCharts } from "./components/DashboardCharts";
import { Chatbot } from "./components/Chatbot";

function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [monthly, setMonthly] = useState<MonthlyBreakdown[]>([]);
  const [trends, setTrends] = useState<DailyTrend[]>([]);
  const [merchants, setMerchants] = useState<TopMerchant[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getSummary(),
      api.getCategories(),
      api.getMonthly(),
      api.getTrends(),
      api.getTopMerchants(),
    ])
      .then(([summaryData, categoriesData, monthlyData, trendsData, merchantsData]) => {
        setSummary(summaryData);
        setCategories(categoriesData);
        setMonthly(monthlyData);
        setTrends(trendsData);
        setMerchants(merchantsData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (error) {
    return <div className="p-6 text-red-600">Error loading dashboard: {error}</div>;
  }

  if (loading || !summary) {
    return <div className="p-6 text-gray-500">Loading dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Personal Finance Intelligence</h1>
      <SummaryCards summary={summary} />
      <DashboardCharts categories={categories} monthly={monthly} trends={trends} merchants={merchants} />
     <Chatbot />    
    </div>
  );
}

export default App;