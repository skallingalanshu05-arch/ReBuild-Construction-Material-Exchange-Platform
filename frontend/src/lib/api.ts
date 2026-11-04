import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

/**
 * Backend base URL comes from VITE_API_BASE_URL (e.g. http://localhost:8000/api/v1).
 * When it is not set, the app runs in "not connected" mode: every page renders,
 * and data areas explain which endpoint they are waiting for.
 */
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";
export const isApiConfigured = API_BASE_URL.length > 0;

const ACCESS_KEY = "rebuild.access";
const REFRESH_KEY = "rebuild.refresh";

export const tokenStore = {
  get access() {
    return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_KEY) ?? sessionStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return typeof window === "undefined" ? null : localStorage.getItem(REFRESH_KEY) ?? sessionStorage.getItem(REFRESH_KEY);
  },
  set(access: string, refresh: string | undefined, remember: boolean) {
    const s = remember ? localStorage : sessionStorage;
    s.setItem(ACCESS_KEY, access);
    if (refresh) s.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    [localStorage, sessionStorage].forEach((s) => {
      s.removeItem(ACCESS_KEY);
      s.removeItem(REFRESH_KEY);
    });
  },
};

export class ApiNotConfiguredError extends Error {
  constructor() {
    super("Backend not connected (VITE_API_BASE_URL is not set).");
  }
}

export const api = axios.create({ baseURL: API_BASE_URL || undefined, withCredentials: true });

api.interceptors.request.use((config) => {
  if (!isApiConfigured) throw new ApiNotConfiguredError();
  const t = tokenStore.access;
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

let refreshing: Promise<string | null> | null = null;
export let onUnauthorized: () => void = () => {};
export const setUnauthorizedHandler = (fn: () => void) => (onUnauthorized = fn);

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (error.response?.status === 401 && original && !original._retry && !original.url?.includes("/auth/")) {
      original._retry = true;
      // ASSUMED endpoint: POST /auth/refresh { refresh_token } -> { access_token, refresh_token? }
      refreshing ??= axios
        .post(`${API_BASE_URL}/auth/refresh`, { refresh_token: tokenStore.refresh }, { withCredentials: true })
        .then((r) => {
          tokenStore.set(r.data.access_token, r.data.refresh_token, !!localStorage.getItem(ACCESS_KEY));
          return r.data.access_token as string;
        })
        .catch(() => null)
        .finally(() => (refreshing = null));
      const token = await refreshing;
      if (token) {
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      }
      tokenStore.clear();
      onUnauthorized();
    }
    return Promise.reject(error);
  },
);

export function errorMessage(e: unknown): string {
  if (e instanceof ApiNotConfiguredError) return e.message;
  if (axios.isAxiosError(e)) {
    const d = e.response?.data as { detail?: unknown } | undefined;
    if (typeof d?.detail === "string") return d.detail;
    if (Array.isArray(d?.detail)) return d.detail.map((x: { msg?: string }) => x.msg).join(", ");
    if (!e.response) return "Can't reach the server. Check your connection.";
    return `Request failed (${e.response.status}).`;
  }
  return e instanceof Error ? e.message : "Something went wrong.";
}

/** Normalise list responses: accepts arrays, {items}, {data}, {results}. */
export function asList<T = Record<string, unknown>>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  if (data && typeof data === "object") {
    for (const k of ["items", "data", "results"]) {
      const v = (data as Record<string, unknown>)[k];
      if (Array.isArray(v)) return v as T[];
    }
  }
  return [];
}
