/**
 * frontend/src/utils/formatters.ts
 * Utility formatting helpers for Krone Agriculture India Dashboard.
 */

export const formatHours = (hours?: number | null): string => {
  if (hours === undefined || hours === null || isNaN(hours)) return '0.0h';
  return `${hours.toFixed(1)}h`;
};

export const formatMinutesToHours = (minutes?: number | null): string => {
  if (!minutes) return '0h 0m';
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return `${h}h ${m}m`;
};

export const formatCurrencyINR = (amount?: number | null): string => {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatTimestamp = (isoString?: string | null): string => {
  if (!isoString) return 'N/A';
  try {
    const d = new Date(isoString);
    return d.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
  } catch {
    return isoString;
  }
};

export const formatDate = (isoString?: string | null): string => {
  if (!isoString) return 'N/A';
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return isoString;
  }
};

export const getStatusColor = (status: string): string => {
  const s = status.toLowerCase();
  if (s.includes('progress')) return '#059669'; // Emerald
  if (s.includes('completed')) return '#10B981'; // Green
  if (s.includes('travel')) return '#0284C7'; // Sky
  if (s.includes('hold')) return '#F59E0B'; // Amber
  if (s.includes('cancel')) return '#EF4444'; // Red
  return '#64748B'; // Slate
};
