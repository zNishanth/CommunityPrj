import React, { useState } from "react";
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Loader2,
  Link2,
  ExternalLink,
  Database,
  Hash,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { usePhishCheck } from "@/hooks/usePhishCheck";
import HalftoneWordmarkFooter from "@/components/ui/halftone-wordmark-footer";

export default function Home() {
  const [url, setUrl] = useState("");
  const {
    loading, result, error,
    reporting, reportMsg,
    chainLoading, chainTx,
    check, report, recordOnChain,
  } = usePhishCheck();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) check(url.trim());
  };

  const isPhishing   = result?.verdict === "Phishing";
  const isLegitimate = result?.verdict === "Legitimate";

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-slate-950 to-slate-900 text-white">
      {/* ── NAV ─────────────────────────────────────────────────────── */}
      <nav className="border-b border-white/10 px-6 py-4 flex items-center gap-3">
        <Shield className="w-6 h-6 text-blue-400" />
        <span className="font-bold text-lg tracking-tight">catchPhish</span>
        <span className="ml-2 text-xs text-slate-400 font-mono uppercase tracking-widest">
          AI + Web3
        </span>
      </nav>

      {/* ── MAIN ────────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16 gap-10">

        {/* HERO */}
        <div className="text-center space-y-4 max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            Detect Phishing URLs
          </h1>
          <p className="text-slate-400 text-lg">
            Random Forest ML · 97.6 % accuracy · Blockchain reputation registry
          </p>
        </div>

        {/* SCAN FORM */}
        <form onSubmit={handleSubmit} className="w-full max-w-2xl flex gap-2">
          <div className="relative flex-1">
            <Link2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              className="pl-9 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 h-12"
              placeholder="https://example.com"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>
          <Button
            type="submit"
            disabled={loading}
            className="h-12 px-6 bg-blue-600 hover:bg-blue-500"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Analyze"}
          </Button>
        </form>

        {/* ERROR */}
        {error && (
          <div className="w-full max-w-2xl rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-red-300 text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {/* RESULT CARD */}
        {result && (
          <div className="w-full max-w-2xl space-y-4">
            <Card
              className={`border-2 ${
                isPhishing
                  ? "border-red-500/60 bg-red-950/30"
                  : isLegitimate
                  ? "border-green-500/60 bg-green-950/30"
                  : "border-slate-700 bg-slate-800/50"
              }`}
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  {isPhishing ? (
                    <AlertTriangle className="w-7 h-7 text-red-400" />
                  ) : (
                    <CheckCircle className="w-7 h-7 text-green-400" />
                  )}
                  <span className={isPhishing ? "text-red-400" : "text-green-400"}>
                    {result.verdict}
                  </span>
                  <Badge
                    variant={isPhishing ? "destructive" : "success"}
                    className="ml-auto"
                  >
                    {(result.confidence * 100).toFixed(1)}% confidence
                  </Badge>
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-4">
                <p className="text-slate-400 text-sm break-all font-mono">{url}</p>

                {/* FEATURE GRID */}
                {Object.keys(result.features).length > 0 && (
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">
                      Extracted Features
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {Object.entries(result.features).map(([k, v]) => (
                        <div
                          key={k}
                          className="bg-slate-800 rounded px-2 py-1.5 text-center"
                        >
                          <div className="text-xs text-slate-400 truncate">
                            {k.replace(/_/g, " ")}
                          </div>
                          <div
                            className={`text-sm font-mono font-bold ${
                              v === 1 ? "text-red-400" : "text-green-400"
                            }`}
                          >
                            {v}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ACTIONS */}
                <div className="flex flex-wrap gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-slate-600 text-slate-300 hover:bg-slate-700"
                    onClick={() => report(url)}
                    disabled={reporting}
                  >
                    {reporting ? (
                      <Loader2 className="w-3 h-3 animate-spin mr-1" />
                    ) : (
                      <Database className="w-3 h-3 mr-1" />
                    )}
                    {reporting ? "Reporting…" : "Community Report"}
                  </Button>

                  {isPhishing && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-orange-600 text-orange-300 hover:bg-orange-950"
                      onClick={() => recordOnChain(url)}
                      disabled={chainLoading}
                    >
                      {chainLoading ? (
                        <Loader2 className="w-3 h-3 animate-spin mr-1" />
                      ) : (
                        <Hash className="w-3 h-3 mr-1" />
                      )}
                      {chainLoading ? "Submitting…" : "Record On-Chain"}
                    </Button>
                  )}

                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:text-white"
                    onClick={() =>
                      window.open(url, "_blank", "noopener,noreferrer")
                    }
                  >
                    <ExternalLink className="w-3 h-3 mr-1" /> Open URL
                  </Button>
                </div>

                {reportMsg && (
                  <p className="text-xs text-blue-400">{reportMsg}</p>
                )}
                {chainTx && chainTx !== "error" && (
                  <p className="text-xs text-green-400 font-mono break-all">
                    ✓ On-chain tx: {chainTx}
                  </p>
                )}
                {chainTx === "error" && (
                  <p className="text-xs text-red-400">
                    Chain submission failed — check backend config.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* STAT ROW */}
        <div className="flex gap-10 text-center mt-4">
          {[
            { label: "ML Accuracy", value: "97.6%" },
            { label: "Features", value: "16" },
            { label: "On-Chain Registry", value: "Live" },
          ].map((s) => (
            <div key={s.label} className="space-y-1">
              <div className="text-2xl font-bold text-blue-400">{s.value}</div>
              <div className="text-xs text-slate-500 uppercase tracking-wider">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* ── FOOTER ──────────────────────────────────────────────────── */}
      <HalftoneWordmarkFooter
        preset="night"
        wordmark="catchphish"
        label="catchPhish"
        meta="©2026 · AI + Web3 Phishing Detection"
        height="420px"
      />
    </div>
  );
}
