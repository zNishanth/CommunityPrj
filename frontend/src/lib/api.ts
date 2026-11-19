import axios from "axios";

const BASE = "/api";

export interface DetectResult {
  verdict: "Phishing" | "Legitimate" | "Unknown";
  confidence: number;
  features: Record<string, number>;
  error?: string;
}

export interface ChainReportResult {
  url_hash: string;
  tx_hash: string;
}

const api = axios.create({ baseURL: BASE });

// Attach JWT token if stored
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function detectURL(url: string): Promise<DetectResult> {
  const { data } = await api.post<DetectResult>("/detect/", { url });
  return data;
}

export async function reportURL(url: string): Promise<{ msg: string }> {
  const { data } = await api.post<{ msg: string }>("/report/", { url });
  return data;
}

export async function chainReport(url: string): Promise<ChainReportResult> {
  const { data } = await api.post<ChainReportResult>("/chain-report/", { url });
  return data;
}

export async function login(email: string, password: string): Promise<void> {
  const { data } = await api.post<{ access: string; refresh: string }>("/token/", { email, password });
  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
}

export async function signup(email: string, username: string, password: string): Promise<void> {
  await api.post("/signup/", { email, username, password });
}
