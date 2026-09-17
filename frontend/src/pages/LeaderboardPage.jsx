import { useEffect, useState, useCallback } from "react";
import { Trophy, Loader2, Medal } from "lucide-react";
import { getLeaderboard } from "../services/api";

const RANK_COLOR = ["text-yellow-500", "text-slate-400", "text-amber-600"];

export default function LeaderboardPage() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getLeaderboard();
      setEntries(data);
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
      <div className="flex items-center gap-2 mb-1">
        <Trophy size={20} className="text-arena-600" />
        <h1 className="text-xl font-semibold text-slate-800">Elo Leaderboard</h1>
      </div>
      <p className="text-sm text-slate-500 mb-6">
        Rankings are built entirely from blind human votes on head-to-head battles — the same
        methodology as chess ratings and LMSYS's Chatbot Arena.
      </p>

      {error && (
        <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center gap-2 text-slate-400 py-16 text-sm">
          <Loader2 size={16} className="animate-spin" /> Loading...
        </div>
      ) : entries.length === 0 ? (
        <p className="text-slate-400 text-sm text-center py-16">
          No votes yet — run some battles and vote to populate the leaderboard.
        </p>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
              <tr>
                <th className="text-left px-5 py-2.5 w-12">Rank</th>
                <th className="text-left px-5 py-2.5">Model</th>
                <th className="text-left px-5 py-2.5">Elo Rating</th>
                <th className="text-left px-5 py-2.5">Win Rate</th>
                <th className="text-left px-5 py-2.5">Record (W-L-T)</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, idx) => (
                <tr key={entry.model_id} className="border-t border-slate-100">
                  <td className="px-5 py-3">
                    {idx < 3 ? (
                      <Medal size={16} className={RANK_COLOR[idx]} />
                    ) : (
                      <span className="text-slate-400">{idx + 1}</span>
                    )}
                  </td>
                  <td className="px-5 py-3 font-medium text-slate-800">
                    {entry.model_id.split(":")[1]}
                    <span className="text-xs text-slate-400 ml-1">
                      ({entry.model_id.split(":")[0]})
                    </span>
                  </td>
                  <td className="px-5 py-3 font-semibold text-arena-600">{entry.elo_rating}</td>
                  <td className="px-5 py-3 text-slate-600">{(entry.win_rate * 100).toFixed(0)}%</td>
                  <td className="px-5 py-3 text-slate-500">
                    {entry.wins}-{entry.losses}-{entry.ties}
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
