import { Cpu, Cloud, Check } from "lucide-react";

export default function ModelSelector({ models, selectedIds, onToggle, maxSelect = 4 }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-slate-700 mb-3">
        Select Models to Compare ({selectedIds.length}/{maxSelect})
      </h3>
      <div className="flex flex-wrap gap-2">
        {models.map((model) => {
          const isSelected = selectedIds.includes(model.model_id);
          const isDisabled = !isSelected && selectedIds.length >= maxSelect;
          const Icon = model.provider === "ollama" ? Cpu : Cloud;

          return (
            <button
              key={model.model_id}
              onClick={() => onToggle(model.model_id)}
              disabled={isDisabled}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border transition-colors ${
                isSelected
                  ? "bg-arena-600 text-white border-arena-600"
                  : isDisabled
                  ? "bg-slate-50 text-slate-300 border-slate-200 cursor-not-allowed"
                  : "bg-white text-slate-600 border-slate-300 hover:border-arena-400"
              }`}
            >
              {isSelected ? <Check size={13} /> : <Icon size={13} />}
              {model.display_name}
              <span className="text-xs opacity-70">
                {model.provider === "ollama" ? "(free)" : "(paid)"}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
