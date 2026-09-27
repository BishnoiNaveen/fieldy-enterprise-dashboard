/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        krone: {
          emerald: "#059669",
          "emerald-light": "#10B981",
          "emerald-dark": "#022C22",
          "emerald-glow": "rgba(5, 150, 105, 0.25)",
          obsidian: "#0B121E",
          "obsidian-dark": "#060A11",
          "obsidian-card": "#0F172A",
          "obsidian-border": "#1E293B",
          gold: "#F59E0B",
          "gold-light": "#FBBF24",
          "gold-dark": "#B45309",
          slate: "#334155",
          "slate-muted": "#64748B",
          "slate-light": "#94A3B8",
        },
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'aura-emerald': '0 8px 30px -4px rgba(5, 150, 105, 0.25)',
        'aura-card': '0 20px 50px rgba(0, 0, 0, 0.6)',
        'aura-gold': '0 8px 30px -4px rgba(245, 158, 11, 0.25)',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
