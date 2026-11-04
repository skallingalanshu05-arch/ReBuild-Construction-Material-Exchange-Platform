import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, isApiConfigured, setUnauthorizedHandler, tokenStore } from "./api";

export type User = {
  id?: string;
  full_name?: string;
  email?: string;
  role?: string;
  roles?: string[];
  company_name?: string;
  [k: string]: unknown;
};

type AuthCtx = {
  user: User | null;
  ready: boolean;
  login: (email: string, password: string, remember: boolean) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  isAdmin: boolean;
};

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  const refreshUser = async () => {
    // ASSUMED endpoint: GET /auth/me
    const { data } = await api.get("/auth/me");
    setUser(data);
  };

  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null));
    if (!isApiConfigured || !tokenStore.access) {
      setReady(true);
      return;
    }
    refreshUser()
      .catch(() => tokenStore.clear())
      .finally(() => setReady(true));
  }, []);

  const login = async (email: string, password: string, remember: boolean) => {
    // ASSUMED endpoint: POST /auth/login { email, password } -> { access_token, refresh_token }
    const { data } = await api.post("/auth/login", { email, password });
    tokenStore.set(data.access_token, data.refresh_token, remember);
    if (data.user) setUser(data.user);
    else await refreshUser();
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout", { refresh_token: tokenStore.refresh });
    } catch {
      /* ignore */
    }
    tokenStore.clear();
    setUser(null);
  };

  const isAdmin = user?.role === "admin" || !!user?.roles?.includes("admin");

  return <Ctx.Provider value={{ user, ready, login, logout, refreshUser, isAdmin }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const c = useContext(Ctx);
  if (!c) throw new Error("useAuth must be used inside AuthProvider");
  return c;
}
