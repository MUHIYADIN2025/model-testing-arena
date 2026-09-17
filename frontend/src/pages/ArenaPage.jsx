import { useEffect, useState } from "react";
import { AlertCircle } from "lucide-react";
import ModelSelector from "../components/ModelSelector";
import PromptInput from "../components/PromptInput";
import ArenaBattleView from "../components/ArenaBattleView";
import MetricComparison from "../components/MetricComparison";
import { listModels, runBattle } from "../services/api";

export default function ArenaPage() {
  const [models, setModels] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [battle, setBattle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    listModels()
      .then((data) => {
        setModels(data);
        setSelectedIds(data.slice(0, 2).map((m) => m.model_id));
      })
      .catch((err) => setError(err.message));
  }, []);

  const toggleModel = (modelId) => {
    setSelectedIds((prev) =>
      prev.includes(modelId) ? prev.filter((id) => id !== modelId) : [...prev, modelId]
    );
  };

  const handleBattle = async (prompt) => {
    setLoading(true);
    setError(null);
    setBattle(null);
    try {
      const result = await runBattle(prompt, selectedIds, true);
      setBattle(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-6 space-y-4">
      {error && (
        <div className="flex items-start gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3">
          <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
          {error}
        </div>
      )}

      <ModelSelector models={models} selectedIds={selectedIds} onToggle={toggleModel} />

      <PromptInput onSubmit={handleBattle} loading={loading} disabled={selectedIds.length < 2} />

      {selectedIds.length < 2 && (
        <p className="text-xs text-amber-600">Select at least 2 models to start a battle.</p>
      )}

      {battle && (
        <div className="space-y-4 pt-2">
          <ArenaBattleView battle={battle} />
          <MetricComparison results={battle.results} />
        </div>
      )}
    </div>
  );
}
