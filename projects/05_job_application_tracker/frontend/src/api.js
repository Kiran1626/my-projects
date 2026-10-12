import axios from "axios";

const api = axios.create({ baseURL: "http://127.0.0.1:8000/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function login(username, password) {
  const { data } = await api.post("/token/", { username, password });
  localStorage.setItem("access", data.access);
  localStorage.setItem("refresh", data.refresh);
  return data;
}

export function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

export function isLoggedIn() {
  return !!localStorage.getItem("access");
}

export const getApplications = (params = {}) => api.get("/applications/", { params });
export const createApplication = (payload) => api.post("/applications/", payload);
export const updateApplication = (id, payload) => api.patch(`/applications/${id}/`, payload);
export const deleteApplication = (id) => api.delete(`/applications/${id}/`);
export const getStats = () => api.get("/applications/stats/");

export default api;
