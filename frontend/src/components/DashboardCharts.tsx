import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import type { CategoryBreakdown, MonthlyBreakdown, DailyTrend, TopMerchant } from "../services/api";

const COLORS = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];

interface Props {
  categories: CategoryBreakdown[];
  monthly: MonthlyBreakdown[];
  trends: DailyTrend[];
  merchants: TopMerchant[];
}

export function DashboardCharts({ categories, monthly, trends, merchants }: Props) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <div className="bg-white rounded-lg shadow p-4 border border-gray-100">
        <h2 className="text-lg font-semibold mb-4">Spending by Category</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={categories} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={100} label={(entry) => entry.category}>
              {categories.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg shadow p-4 border border-gray-100">
        <h2 className="text-lg font-semibold mb-4">Income vs Expenses (Monthly)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthly}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="income" fill="#10b981" name="Income" />
            <Bar dataKey="expenses" fill="#ef4444" name="Expenses" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg shadow p-4 border border-gray-100">
        <h2 className="text-lg font-semibold mb-4">Daily Spending Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="amount" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg shadow p-4 border border-gray-100">
        <h2 className="text-lg font-semibold mb-4">Top Merchants</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={merchants} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="merchant" type="category" width={80} />
            <Tooltip />
            <Bar dataKey="total_spent" fill="#8b5cf6" name="Total Spent" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}