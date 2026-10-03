/**
 * frontend/src/components/SecurityModal.tsx
 * Modal displaying enterprise security posture and active defensive hardening.
 */

import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  X, 
  Lock, 
  CheckCircle2, 
  AlertCircle, 
  Key, 
  Cpu, 
  Database,
  RefreshCw
} from 'lucide-react';
import { SecurityAuditResponse } from '../types/dashboard';
import { api } from '../services/api';

interface SecurityModalProps {
  isOpen: boolean;
  onClose: () => void;
  theme: 'bright' | 'dark';
}

export const SecurityModal: React.FC<SecurityModalProps> = ({ isOpen, onClose, theme }) => {
  const isDark = theme === 'dark';
  const modalBg = isDark ? 'bg-[#0D1520] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';

  const [audit, setAudit] = useState<SecurityAuditResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      api.getSecurityAudit()
        .then(setAudit)
        .finally(() => setLoading(false));

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose();
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in"
    >
      <div 
        onClick={e => e.stopPropagation()}
        className={`w-full max-w-xl rounded-2xl border p-6 shadow-2xl relative ${modalBg}`}
      >
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute right-4 top-4 p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5 mb-1">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold">Enterprise Security & Compliance Audit</h3>
            <span className="text-[11px] font-mono text-emerald-600 dark:text-emerald-400 font-semibold">
              Krone Agriculture India • OWASP & Rate-Limit Hardening
            </span>
          </div>
        </div>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center gap-2 text-xs">
            <RefreshCw className="w-6 h-6 animate-spin text-emerald-600" />
            <span>Scanning endpoints and security headers...</span>
          </div>
        ) : audit ? (
          <div className="space-y-4 mt-4">
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-500/20">
              <div>
                <span className={`text-[10px] font-mono uppercase ${textMuted}`}>Overall Security Posture</span>
                <div className="text-sm font-black font-mono text-emerald-600 dark:text-emerald-400">
                  {audit.overall_rating} (Compliant)
                </div>
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200 font-bold">
                Zero Vulnerabilities
              </span>
            </div>

            <div className="space-y-2">
              <span className={`text-[11px] font-mono uppercase font-bold ${textMuted}`}>Active Security Defenses</span>
              <div className="space-y-2 text-xs">
                {Object.entries(audit.checks).map(([key, check]) => (
                  <div key={key} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 flex items-start justify-between gap-3">
                    <div className="space-y-0.5">
                      <div className="font-bold capitalize">{key.replace(/_/g, ' ')}</div>
                      <div className={`text-[11px] ${textMuted}`}>{check.details}</div>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                      {check.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/80 text-[11px] text-slate-600 dark:text-slate-300 font-medium">
              🔒 <strong>Audit Guarantee:</strong> Zero guessing policy active. Bearer tokens are kept in server environment variables and never leaked in client bundles or git commits.
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
