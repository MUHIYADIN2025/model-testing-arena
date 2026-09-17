import { NavLink } from "react-router-dom";
import { Swords, Trophy, History } from "lucide-react";

export default function Nav() {
  return (
    <header className="bg-white border-b border-slate-200 px-4 md:px-8 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="bg-arena-600 text-white p-2 rounded-lg">
          <Swords size={20} />
        </div>
        <div>
          <p className="font-semibold text-sm leading-tight">Model Testing Arena</p>
          <p className="text-xs text-slate-500">Blind LLM comparison &amp; Elo leaderboard</p>
        </div>
      </div>

      <nav className="flex gap-1">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isActive ? "bg-arena-50 text-arena-700" : "text-slate-600 hover:bg-slate-100"
            }`
          }
        >
          Arena
        </NavLink>
        <NavLink
          to="/leaderboard"
          className={({ isActive }) =>
            `px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-1.5 transition-colors ${
              isActive ? "bg-arena-50 text-arena-700" : "text-slate-600 hover:bg-slate-100"
            }`
          }
        >
          <Trophy size={15} />
          Leaderboard
        </NavLink>
        <NavLink
          to="/history"
          className={({ isActive }) =>
            `px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-1.5 transition-colors ${
              isActive ? "bg-arena-50 text-arena-700" : "text-slate-600 hover:bg-slate-100"
            }`
          }
        >
          <History size={15} />
          History
        </NavLink>
      </nav>
    </header>
  );
}
