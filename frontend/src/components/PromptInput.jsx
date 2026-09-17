import { useState } from "react";
import { Swords, Loader2 } from "lucide-react";

const SAMPLE_PROMPTS = [
  "Explain quantum entanglement to a 10-year-old.",
  "Write a haiku about debugging code at 2am.",
  "What's the time complexity of quicksort, and why?",
];

export default function PromptInput({ onSubmit, loading, disabled }) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || loading || disabled) return;
    onSubmit(prompt.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-4">
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter a prompt to send to every selected model..."
        rows={3}
        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-arena-500"
      />

      <div className="flex items-center justify-between mt-3">
        <div className="flex gap-1.5 flex-wrap">
          {SAMPLE_PROMPTS.map((sample) => (
            <button
              key={sample}
              type="button"
              onClick={() => setPrompt(sample)}
              className="text-xs bg-slate-50 text-slate-500 hover:text-slate-700 px-2 py-1 rounded-full border border-slate-200"
            >
              {sample.length > 40 ? sample.slice(0, 40) + "…" : sample}
            </button>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading || disabled || !prompt.trim()}
          className="flex items-center gap-2 bg-arena-600 hover:bg-arena-700 disabled:bg-slate-300 text-white text-sm font-medium rounded-lg px-4 py-2 flex-shrink-0"
        >
          {loading ? <Loader2 size={15} className="animate-spin" /> : <Swords size={15} />}
          {loading ? "Battling..." : "Start Battle"}
        </button>
      </div>
    </form>
  );
}
