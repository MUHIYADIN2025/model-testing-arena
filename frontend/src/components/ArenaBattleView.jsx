import { useState } from "react";
import { Trophy, Equal, ThumbsDown, Eye, EyeOff, Clock, Coins, Hash, Sparkles } from "lucide-react";
import { submitVote } from "../services/api";

const PROVIDER_LABEL = { ollama: "Local", openai: "Cloud" };

function ResponseCard({ result, label, revealed, isWinner }) {
  const displayName = result.model_id.split(":")[1];

  return (
    <div
      className={`bg-white border rounded-xl p-4 flex flex-col ${
        isWinner ? "border-arena-500 ring-1 ring-arena-200" : "border-slate-200"
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold bg-slate-100 text-slate-500 px-2 py-0.5 rounded">
          {label}
        </span>
        {revealed && (
          <span className="text-xs font-medium text-slate-600">
            {displayName} <span className="text-slate-400">({PROVIDER_LABEL[result.model_id.split(":")[0]]})</span>
          </span>
        )}
      </div>

      <div className="flex-1 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto">
        {result.status === "error" ? (
          <span className="text-red-600 italic">Error: {result.error}</span>
        ) : (
          result.text
        )}
      </div>

      {result.status === "success" && (
        <div className="flex items-center gap-3 mt-3 pt-3 border-t border-slate-100 text-xs text-slate-500">
          <span className="flex items-center gap-1"><Clock size={12} /> {result.latency_ms}ms</span>
          <span className="flex items-center gap-1"><Hash size={12} /> {result.tokens_out} tok</span>
          <span className="flex items-center gap-1">
            <Coins size={12} /> {result.estimated_cost_usd > 0 ? `$${result.estimated_cost_usd.toFixed(5)}` : "Free"}
          </span>
          {result.judge_score != null && (
            <span className="flex items-center gap-1 ml-auto text-arena-600 font-medium">
              <Sparkles size={12} /> {result.judge_score}/10
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default function ArenaBattleView({ battle }) {
  const [revealed, setRevealed] = useState(false);
  const [voted, setVoted] = useState(false);
  const [winnerId, setWinnerId] = useState(null);
  const [voting, setVoting] = useState(false);
  const [error, setError] = useState(null);

  const labels = ["A", "B", "C", "D", "E", "F"];

  const handleVote = async (outcome, winnerModelId = null) => {
    if (voting) return;
    setVoting(true);
    setError(null);

    const loserIds = battle.results
      .map((r) => r.model_id)
      .filter((id) => id !== winnerModelId);

    try {
      await submitVote(battle.battle_id, outcome, winnerModelId, loserIds);
      setVoted(true);
      setWinnerId(winnerModelId);
      setRevealed(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setVoting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          Prompt: <span className="font-medium text-slate-700">&ldquo;{battle.prompt}&rdquo;</span>
        </p>
        <button
          onClick={() => setRevealed((r) => !r)}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700"
        >
          {revealed ? <EyeOff size={13} /> : <Eye size={13} />}
          {revealed ? "Hide model names" : "Reveal model names"}
        </button>
      </div>

      <div className={`grid gap-4 ${battle.results.length <= 2 ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"}`}>
        {battle.results.map((result, idx) => (
          <ResponseCard
            key={result.model_id}
            result={result}
            label={labels[idx]}
            revealed={revealed}
            isWinner={voted && result.model_id === winnerId}
          />
        ))}
      </div>

      {error && <p className="text-xs text-red-600">{error}</p>}

      {!voted ? (
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <p className="text-xs text-slate-500 mb-2.5">Which response was better?</p>
          <div className="flex flex-wrap gap-2">
            {battle.results.map((result, idx) => (
              <button
                key={result.model_id}
                onClick={() => handleVote("win", result.model_id)}
                disabled={voting || result.status === "error"}
                className="flex items-center gap-1.5 text-sm bg-arena-50 text-arena-700 border border-arena-200 hover:bg-arena-100 disabled:opacity-40 rounded-lg px-3 py-1.5"
              >
                <Trophy size={13} /> {labels[idx]} is better
              </button>
            ))}
            <button
              onClick={() => handleVote("tie")}
              disabled={voting}
              className="flex items-center gap-1.5 text-sm bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100 rounded-lg px-3 py-1.5"
            >
              <Equal size={13} /> Tie
            </button>
            <button
              onClick={() => handleVote("both_bad")}
              disabled={voting}
              className="flex items-center gap-1.5 text-sm bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100 rounded-lg px-3 py-1.5"
            >
              <ThumbsDown size={13} /> Both bad
            </button>
          </div>
        </div>
      ) : (
        <p className="text-xs text-emerald-600 font-medium">
          ✓ Vote recorded — leaderboard updated.
        </p>
      )}
    </div>
  );
}
