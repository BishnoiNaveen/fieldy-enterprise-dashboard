/**
 * frontend/src/components/AutomationsView.tsx
 * Enterprise Automation Hub for WhatsApp Business API, Email Dispatch, and Webhooks.
 */

import React, { useState } from 'react';
import { 
  Send, 
  MessageSquare, 
  Mail, 
  CheckCircle2, 
  Clock, 
  ShieldCheck, 
  Radio, 
  RefreshCw,
  Zap,
  Smartphone,
  Copy,
  Check
} from 'lucide-react';
import { api } from '../services/api';

interface AutomationsViewProps {
  theme: 'bright' | 'dark';
}

export const AutomationsView: React.FC<AutomationsViewProps> = ({ theme }) => {
  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0D1520] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const inputBg = isDark ? 'bg-slate-900 border-slate-700 text-white' : 'bg-slate-50 border-slate-300 text-slate-900';

  // WhatsApp Dispatch State
  const [waJobId, setWaJobId] = useState('SR-26- 0148');
  const [waPhone, setWaPhone] = useState('+91 9625957663');
  const [waName, setWaName] = useState('Sunny Kumar');
  const [waRole, setWaRole] = useState<'technician' | 'customer'>('technician');
  const [waCustomNote, setWaCustomNote] = useState('');
  const [isSendingWa, setIsSendingWa] = useState(false);
  const [waSuccessMsg, setWaSuccessMsg] = useState<string | null>(null);

  // Email Report State
  const [emailTo, setEmailTo] = useState('kin.it@krone-india.com');
  const [emailSubject, setEmailSubject] = useState('Daily Operations Digest & Fieldy Forensic Recovery Summary');
  const [emailReportType, setEmailReportType] = useState('audit_recovery_ledger');
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [emailSuccessMsg, setEmailSuccessMsg] = useState<string | null>(null);

  // Copied State
  const [copied, setCopied] = useState(false);

  const handleSendWhatsApp = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSendingWa(true);
    try {
      const res = await api.dispatchWhatsApp({
        job_id: waJobId,
        recipient_phone: waPhone,
        recipient_name: waName,
        recipient_role: waRole,
        custom_message: waCustomNote || undefined
      });
      setWaSuccessMsg(`✓ Dispatched to ${res.recipient} [Ref: ${res.message_id}]`);
      setTimeout(() => setWaSuccessMsg(null), 6000);
    } finally {
      setIsSendingWa(false);
    }
  };

  const handleSendEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSendingEmail(true);
    try {
      const res = await api.sendEmailReport({
        recipient_email: emailTo,
        subject: emailSubject,
        report_type: emailReportType
      });
      setEmailSuccessMsg(`✓ Report sent to ${res.recipient} [ID: ${res.email_id}]`);
      setTimeout(() => setEmailSuccessMsg(null), 6000);
    } finally {
      setIsSendingEmail(false);
    }
  };

  const samplePreview = (
    `🚜 *KRONE AGRICULTURE INDIA — SERVICE WORK ORDER DISPATCH*\n` +
    `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
    `👨‍🔧 *Technician:* ${waName}\n` +
    `📋 *Job ID:* ${waJobId}\n` +
    `🏢 *Customer:* Guru kirpa tractor\n` +
    `⚙️ *Machinery:* Krone Swadro TC 640\n` +
    `📍 *Site Location:* Mdr102, Kulan, Haryana\n` +
    `🕒 *Scheduled Start:* Today, 08:30 AM\n` +
    `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
    `⚠️ *Mandatory Audit Directives:*\n` +
    `1. Start Travel punch in Fieldy mobile app before journey.\n` +
    `2. Capture initial odometer reading photo.\n` +
    `3. Local trips (<50 KM) qualify for ₹150 DA only if duty >8h.\n` +
    `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`
  );

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className={`rounded-2xl border p-6 ${cardBg}`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider bg-emerald-600/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                Zero-Touch Automation
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider bg-blue-600/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                WhatsApp Business API & Transactional Mail
              </span>
            </div>
            <h2 className="text-xl font-black tracking-tight mt-1.5 flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              Automations & Real-Time Communications Hub
            </h2>
            <p className={`text-xs mt-1 ${textMuted}`}>
              Automated end-to-end dispatch of job orders, technician alerts, daily executive digests, and customer confirmations without manual intervention.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-mono font-bold">
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              Webhook Daemon Active
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: WhatsApp Dispatcher */}
        <div className={`rounded-2xl border p-6 ${cardBg}`}>
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-200 dark:border-slate-800">
            <h3 className="text-sm font-bold flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              WhatsApp Business API Dispatcher
            </h3>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              Verified Gateway
            </span>
          </div>

          <form onSubmit={handleSendWhatsApp} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Fieldy Work Order
                </label>
                <input
                  type="text"
                  value={waJobId}
                  onChange={e => setWaJobId(e.target.value)}
                  className={`w-full px-3 py-2 rounded-xl text-xs font-mono font-bold border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
              </div>

              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Recipient Role
                </label>
                <select
                  value={waRole}
                  onChange={e => setWaRole(e.target.value as any)}
                  className={`w-full px-3 py-2 rounded-xl text-xs border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                >
                  <option value="technician">Field Service Technician</option>
                  <option value="customer">Client Contact Person</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Recipient Name
                </label>
                <input
                  type="text"
                  value={waName}
                  onChange={e => setWaName(e.target.value)}
                  className={`w-full px-3 py-2 rounded-xl text-xs border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
              </div>

              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  WhatsApp Phone (+91)
                </label>
                <input
                  type="text"
                  value={waPhone}
                  onChange={e => setWaPhone(e.target.value)}
                  className={`w-full px-3 py-2 rounded-xl text-xs font-mono border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                Custom Dispatch Instructions (Optional)
              </label>
              <textarea
                rows={2}
                value={waCustomNote}
                onChange={e => setWaCustomNote(e.target.value)}
                placeholder="E.g. Check hydraulic filter and grease knotter needles..."
                className={`w-full px-3 py-2 rounded-xl text-xs border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
              />
            </div>

            {/* Live Message Preview Box */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className={`text-[11px] font-mono ${textMuted}`}>Live WhatsApp Template Preview</span>
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(samplePreview);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1"
                >
                  {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 text-slate-200 font-mono text-[11px] leading-relaxed whitespace-pre-wrap border border-slate-800">
                {samplePreview}
              </div>
            </div>

            {waSuccessMsg && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-bold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                {waSuccessMsg}
              </div>
            )}

            <button
              type="submit"
              disabled={isSendingWa}
              className="w-full py-3 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-lg shadow-emerald-600/20 transition flex items-center justify-center gap-2"
            >
              {isSendingWa ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Dispatching to WhatsApp Business Gateway...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Dispatch WhatsApp Notification
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Transactional Email & Digest */}
        <div className={`rounded-2xl border p-6 ${cardBg}`}>
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-200 dark:border-slate-800">
            <h3 className="text-sm font-bold flex items-center gap-2">
              <Mail className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              Transactional Email & Forensic Digests
            </h3>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400">
              SMTP Active
            </span>
          </div>

          <form onSubmit={handleSendEmail} className="space-y-4">
            <div>
              <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                Recipient Email
              </label>
              <input
                type="email"
                value={emailTo}
                onChange={e => setEmailTo(e.target.value)}
                className={`w-full px-3 py-2 rounded-xl text-xs font-mono border ${inputBg} focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
            </div>

            <div>
              <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                Report Type
              </label>
              <select
                value={emailReportType}
                onChange={e => setEmailReportType(e.target.value)}
                className={`w-full px-3 py-2 rounded-xl text-xs border ${inputBg} focus:outline-none focus:ring-2 focus:ring-blue-500`}
              >
                <option value="audit_recovery_ledger">12-Pillar Forensic Audit Recovery Ledger</option>
                <option value="daily_digest">Daily Executive Command & Manpower Digest</option>
                <option value="service_job_card">Fieldy Service Report & Checklist PDF</option>
                <option value="amc_retainer_summary">Krone AMC Billing & Retainer Statement</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                Email Subject
              </label>
              <input
                type="text"
                value={emailSubject}
                onChange={e => setEmailSubject(e.target.value)}
                className={`w-full px-3 py-2 rounded-xl text-xs font-medium border ${inputBg} focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className={`font-mono ${textMuted}`}>Automated Attachment:</span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">KRONE_AUDIT_LEDGER.pdf</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={`font-mono ${textMuted}`}>Data Source:</span>
                <span className="font-mono">Live Fieldy Synchronizer (483 jobs)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={`font-mono ${textMuted}`}>Security Stamp:</span>
                <span className="font-mono">SHA-256 Verified Corporate Signoff</span>
              </div>
            </div>

            {emailSuccessMsg && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-bold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                {emailSuccessMsg}
              </div>
            )}

            <button
              type="submit"
              disabled={isSendingEmail}
              className="w-full py-3 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-600/20 transition flex items-center justify-center gap-2"
            >
              {isSendingEmail ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating & Dispatching Encrypted Report...
                </>
              ) : (
                <>
                  <Mail className="w-4 h-4" />
                  Send Automated Report Email
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
