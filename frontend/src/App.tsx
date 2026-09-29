import { useEffect, useState } from "react";
import { api, type Summary } from "./services/api";

function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getSummary()
      .then(setSummary)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <div style={{ padding: 20 }}>Error: {error}</div>;
  if (!summary) return <div style={{ padding: 20 }}>Loading...</div>;

  return (
    <div style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1 className="text-4xl font-bold text-blue-600">Personal Finance Intelligence</h1>
      <p>Total Income: {summary.total_income}</p>
      <p>Total Expenses: {summary.total_expenses}</p>
      <p>Total Savings: {summary.total_savings}</p>
      <p>Savings Rate: {(summary.savings_rate * 100).toFixed(1)}%</p>
    </div>
  );
}

export default App;