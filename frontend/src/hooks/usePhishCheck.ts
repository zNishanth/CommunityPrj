import { useState } from "react";
import { detectURL, reportURL, chainReport, type DetectResult } from "@/lib/api";

interface PhishCheckState {
  loading: boolean;
  result: DetectResult | null;
  error: string | null;
  reporting: boolean;
  reportMsg: string | null;
  chainLoading: boolean;
  chainTx: string | null;
}

export function usePhishCheck() {
  const [state, setState] = useState<PhishCheckState>({
    loading: false,
    result: null,
    error: null,
    reporting: false,
    reportMsg: null,
    chainLoading: false,
    chainTx: null,
  });

  async function check(url: string) {
    setState((s) => ({ ...s, loading: true, error: null, result: null }));
    try {
      const result = await detectURL(url);
      setState((s) => ({ ...s, loading: false, result }));
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Detection failed";
      setState((s) => ({ ...s, loading: false, error: msg }));
    }
  }

  async function report(url: string) {
    setState((s) => ({ ...s, reporting: true, reportMsg: null }));
    try {
      const res = await reportURL(url);
      setState((s) => ({ ...s, reporting: false, reportMsg: res.msg }));
    } catch {
      setState((s) => ({ ...s, reporting: false, reportMsg: "Report failed — are you logged in?" }));
    }
  }

  async function recordOnChain(url: string) {
    setState((s) => ({ ...s, chainLoading: true, chainTx: null }));
    try {
      const res = await chainReport(url);
      setState((s) => ({ ...s, chainLoading: false, chainTx: res.tx_hash }));
    } catch {
      setState((s) => ({ ...s, chainLoading: false, chainTx: "error" }));
    }
  }

  return { ...state, check, report, recordOnChain };
}
