import type { Summary } from "../services/api";

function formatCurrency(value: number): string {
  return `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

export function SummaryCards({ summary }: { summary: Summary }) {
  const cards = [
    { label: "Total Income", value: formatCurrency(summary.total_income), color: "text-green-600" },
    { label: "Total Expenses", value: formatCurrency(summary.total_expenses), color: "text-red-600" },
    { label: "Total Savings", value: formatCurrency(summary.total_savings), color: "text-blue-600" },
    { label: "Savings Rate", value: `${(summary.savings_rate * 100).toFixed(1)}%`, color: "text-purple-600" },
    { label: "Avg Daily Spending", value: formatCurrency(summary.avg_daily_spending), color: "text-orange-600" },
    { label: "Transactions", value: summary.transaction_count.toString(), color: "text-gray-700" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card) => (
        <div key={card.label} className="bg-white rounded-lg shadow p-4 border border-gray-100">
          <p className="text-sm text-gray-500">{card.label}</p>
          <p className={`text-2xl font-bold mt-1 ${card.color}`}>{card.value}</p>
        </div>
      ))}
    </div>
  );
}