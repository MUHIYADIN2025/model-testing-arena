import { useEffect, useState, useCallback } from "react";
import { Loader2 } from "lucide-react";
import { listBattles } from "../services/api";

export default function HistoryPage() {
  const [battles, setBattles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await listBattles();
      setBattles(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-6">
      <h1 className="text-xl font-semibold text-slate-800 mb-1">Battle History</h1>
      <p className="text-sm text-slate-500 mb-6">Past prompts and the models compared.</p>

      {error && (
        <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center gap-2 text-slate-400 py-16 text-sm">
          <Loader2 size={16} className="animate-spin" /> Loading...
        </div>
      ) : battles.length === 0 ? (
        <p className="text-slate-400 text-sm text-center py-16">No battles run yet.</p>
      ) : (
        <ul className="space-y-2">
          {battles.map((battle) => (
            <li key={battle.id} className="bg-white border border-slate-200 rounded-xl p-4">
              <p className="text-sm font-medium text-slate-800 mb-1.5 line-clamp-2">
                {battle.prompt}
              </p>
              <div className="flex items-center gap-2 flex-wrap">
                {battle.model_ids.map((id) => (
                  <span key={id} className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">
                    {id.split(":")[1]}
                  </span>
                ))}
                <span className="text-xs text-slate-400 ml-auto">
                  {new Date(battle.created_at).toLocaleString()}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
