import type { TransactionRow } from "../services/api";

export function TransactionsTable({ transactions }: { transactions: TransactionRow[] }) {
  return (
    <div className="bg-white rounded-lg shadow p-4 border border-gray-100 mt-6">
      <h2 className="text-lg font-semibold mb-4">Recent Transactions</h2>
      {transactions.length === 0 ? (
        <p className="text-sm text-gray-500">No transactions yet. Upload a file above to get started.</p>
      ) : (
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-gray-500 border-b sticky top-0 bg-white">
              <tr>
                <th className="py-2 pr-4">Date</th>
                <th className="py-2 pr-4">Merchant</th>
                <th className="py-2 pr-4">Category</th>
                <th className="py-2 pr-4">Method</th>
                <th className="py-2 pr-4 text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.id} className="border-b border-gray-50">
                  <td className="py-2 pr-4">{t.date}</td>
                  <td className="py-2 pr-4">
                    {t.merchant}
                    {t.is_duplicate && <span className="ml-2 text-xs text-orange-600">(duplicate)</span>}
                  </td>
                  <td className="py-2 pr-4">{t.category}</td>
                  <td className="py-2 pr-4 text-gray-500">{t.category_source}</td>
                  <td className={`py-2 pr-4 text-right font-medium ${t.type === "income" ? "text-green-600" : "text-red-600"}`}>
                    {t.type === "income" ? "+" : "-"}₹{t.amount.toLocaleString("en-IN")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}