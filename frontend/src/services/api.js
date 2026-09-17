import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 90000, // battles across multiple local models can take a while
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "Something went wrong.";
    return Promise.reject(new Error(message));
  }
);

export const listModels = async () => {
  const { data } = await api.get("/models");
  return data;
};

export const runBattle = async (prompt, modelIds, useJudge = true) => {
  const { data } = await api.post("/battle", { prompt, model_ids: modelIds, use_judge: useJudge });
  return data;
};

export const submitVote = async (battleId, outcome, winnerModelId, loserModelIds) => {
  const { data } = await api.post("/vote", {
    battle_id: battleId,
    outcome,
    winner_model_id: winnerModelId,
    loser_model_ids: loserModelIds,
  });
  return data;
};

export const getLeaderboard = async () => {
  const { data } = await api.get("/leaderboard");
  return data;
};

export const listBattles = async (limit = 50) => {
  const { data } = await api.get(`/battles?limit=${limit}`);
  return data;
};

export default api;
