import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { normaliseQueryParams } from "./backend-map";

/**
 * Backend base URL: set VITE_API_BASE_URL (e.g. http://localhost:8000/api/v1).
 * In dev, defaults to /api/v1 and Vite proxies to the FastAPI server.
 */
const envBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
export const API_BASE_URL =
  envBase && envBase.length > 0 ? envBase : import.meta.env.DEV ? "/api/v1" : "";
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

type ApiEnvelope<T = unknown> = { success?: boolean; message?: string; data?: T };

function unwrapEnvelope<T>(body: unknown): T {
  if (body && typeof body === "object" && "success" in body && "data" in body) {
    return (body as ApiEnvelope<T>).data as T;
  }
  return body as T;
}

export const api = axios.create({ baseURL: API_BASE_URL || undefined, withCredentials: true });

api.interceptors.request.use((config) => {
  if (!isApiConfigured) throw new ApiNotConfiguredError();
  if (config.params && typeof config.params === "object") {
    config.params = normaliseQueryParams(config.params as Record<string, unknown>);
  }
  const t = tokenStore.access;
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

api.interceptors.response.use((response) => {
  response.data = unwrapEnvelope(response.data);
  return response;
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
      refreshing ??= axios
        .post(`${API_BASE_URL}/auth/refresh`, { refresh_token: tokenStore.refresh }, { withCredentials: true })
        .then((r) => {
          const tokens = unwrapEnvelope<{ access_token: string; refresh_token?: string }>(r.data);
          tokenStore.set(tokens.access_token, tokens.refresh_token, !!localStorage.getItem(ACCESS_KEY));
          return tokens.access_token;
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
    const d = e.response?.data as { message?: string; detail?: unknown; errors?: { msg?: string }[] } | undefined;
    if (typeof d?.message === "string" && d.message) return d.message;
    if (typeof d?.detail === "string") return d.detail;
    if (Array.isArray(d?.detail)) return d.detail.map((x: { msg?: string }) => x.msg).join(", ");
    if (Array.isArray(d?.errors) && d.errors.length) {
      return d.errors.map((x) => x.msg ?? JSON.stringify(x)).join(", ");
    }
    if (!e.response) return "Can't reach the server. Check your connection and that the API is running.";
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
