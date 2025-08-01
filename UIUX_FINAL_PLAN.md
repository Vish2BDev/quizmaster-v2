
# 🎨 Quiz Master V2 – UI/UX Uplift Plan (From 8.5 → 10/10)

This document balances performance, precision, and polish while **preserving existing high-value components**. It merges TRAE insights with the Perplexity roadmap and your own dark-mode vision — into one actionable UI/UX strategy.

---

## ✅ STRENGTHS TO PRESERVE

| Category | Keep As-Is (Unless Design Language Evolves) |
|---------|---------------------------------------------|
| 🎯 UX Flow | Confidence-building quiz intro, celebration on finish |
| 🎨 Theme | Existing `_qm-theme.scss`, spacing, shadows, font hierarchy |
| 📊 Visuals | Chart.js stats integration, progress ring, hover states |
| 🧠 Info Arch | Logical quiz-user-admin navigation structure |
| ⚡ Animations | `transform`, `opacity`, `shimmer`, skeleton loaders |
| 📱 Responsive Grid | Mobile-first layout using Bootstrap 5 grid |

---

## 🔧 HIGH-IMPACT IMPROVEMENTS

### 1. 🎨 Visual & Component Refinement

- ✅ **Unify all buttons** into `qm-btn` system (`primary`, `ghost`, `danger`, `success`)
- ✅ Replace Font Awesome with **SVG Icon Set** (Heroicons subset + custom badges)
- ✅ Add **dark-mode tokens**: `--qm-bg-surface-900`, `--qm-text-50`, etc.

### 2. 🧩 Modular Component Architecture (Atomic Design)

| Layer       | Refactor Examples                  |
|-------------|------------------------------------|
| **Atoms**   | `qm-btn`, `qm-input`, `qm-icon`, `qm-chip` |
| **Molecules** | `QuizCard`, `ScoreStat`, `QuizTimer`, `AnswerOption` |
| **Organisms** | `QuizListView`, `LeaderboardTable`, `AdminSidebar`, `QuizAttemptPage` |

- Move Vue files to `/components/atoms|molecules|organisms`
- Export via `index.ts` barrel for clarity

---

## 🌘 DARK MODE STRATEGY (Color Psychology Backed)

| Element              | HEX        | Meaning |
|----------------------|------------|---------|
| Primary Background   | `#121212`  | Deep focus, avoids eye strain |
| Surface/Card BG      | `#1E1E1E`  | Contrast layering |
| Primary Text         | `#F5F5F5`  | High readability |
| Secondary Text       | `#AFAFAF`  | Subdued metadata |
| Accent (CTA buttons) | `#3F88C5`  | Trust, focus, clarity (academic blue) |
| Highlight (Correct)  | `#4CAF50`  | Growth, success |
| Highlight (Wrong)    | `#EF5350`  | Attention, correction |
| Warning/Error        | `#FF7043`  | Friendly urgency |

- Automatically adapts via `[data-theme="dark"]`
- User-toggle in Settings → Appearance, default to `prefers-color-scheme`

---

## 🧠 MICRO-UX POLISH

| Interaction | Enhancement |
|-------------|-------------|
| Hover Cards | Slight lift + background tint + ripple on click |
| Form Focus  | 2px blue outline with 2px offset |
| Transitions | Fade-slide using `<router-view v-slot:transition>` |
| Dialogs     | Slot-based `<QmDialog>` with header/body/footer slots |
| Toasts      | Uniform `QmToast` for info/success/warning/error feedback |
| Emoji Rating | Show post-quiz; POSTs to `/feedback` |
| Streak Logic | Celebratory confetti for 3-day streaks |

---

## 🔍 ACCESSIBILITY & FEEDBACK

- Implement **ARIA live regions** for timers, score changes
- Add **skip-to-content** link for screen reader users
- Use **VeeValidate** for inline animated error messages
- Global `<ErrorView>` boundary with retry + fail whale illustration

---

## 📦 TIMELINE (Agile-Ready)

| Week | Focus Area |
|------|------------|
| 1    | Button/icon unification, dark-mode SCSS, dialog/toast abstraction |
| 2    | Atomic refactor, skeleton loaders, Framer-style quiz card transitions |
| 3    | a11y upgrades, error boundary, keyboard navigation paths |
| 4    | Gamification layer, achievement view, streak logic, emoji feedback |

---

## ✅ METRICS OF SUCCESS

| Metric | Target |
|--------|--------|
| Accessibility Score (axe-core) | ≥ 95 |
| Quiz Completion Rate | +12% |
| CSAT Rating (Emoji) | ≥ 4.5★ |
| Page Load (LCP) | < 2.5 s (3G mobile) |
| Mobile Usability | 100% Google Lighthouse score |

---

## 💬 FINAL NOTE

> “Design is not just what it looks like and feels like. Design is how it works.” — Steve Jobs

This UI/UX roadmap is your bridge from a great product to an **exceptional learning experience**. By iterating smartly (not redoing unnecessarily), you'll craft a platform worthy of top-tier edtech status.
