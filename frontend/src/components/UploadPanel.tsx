import { useRef, useState } from "react";
import { resetData, uploadFile, type UploadResult } from "../services/api";

export function UploadPanel({ onDataChanged }: { onDataChanged: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const uploaded = await uploadFile(file);
      setResult(uploaded);
      onDataChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  async function handleReset() {
    if (!window.confirm("This deletes ALL uploaded transactions. Continue?")) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      await resetData();
      onDataChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 border border-gray-100 mb-6">
      <div className="flex flex-wrap items-center gap-3">
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx"         
          disabled={busy}
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          className="text-sm"
        />
        <button
          onClick={handleReset}
          disabled={busy}
          className="ml-auto text-sm px-3 py-1 rounded border border-red-300 text-red-600 hover:bg-red-50 disabled:opacity-50"
        >
          Reset data
        </button>
      </div>
      <p className="text-xs text-gray-500 mt-2">Upload a .csv or .xlsx with columns: date, description, amount, type (optional).</p>

      {busy && <p className="text-sm text-gray-500 mt-3">Working...</p>}
      {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
      {result && (
        <div className="text-sm mt-3 text-gray-700">
          <p>
            <strong>{result.filename}</strong>: {result.rows_accepted} accepted, {result.rows_rejected} rejected,{" "}
            {result.duplicates_flagged} duplicates flagged, {result.fixes_applied} fixes logged.
          </p>
          {result.rejected_rows.length > 0 && (
            <ul className="list-disc ml-5 mt-1 text-red-600">
              {result.rejected_rows.map((r) => (
                <li key={r.row_number}>
                  Row {r.row_number}: {r.reason}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}