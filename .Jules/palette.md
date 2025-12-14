## 2024-05-23 - [Interactive Cards & Accessibility]
**Learning:**
I discovered a pattern where `div` elements were used as interactive "cards" for displaying benchmark results (`.result-card`). While they had `cursor: pointer` and a click handler, they completely lacked keyboard accessibility (tabindex, role) and screen reader support (aria-label). This effectively excluded keyboard-only and screen reader users from accessing detailed results.

**Action:**
In the future, whenever I see a `click` listener on a non-interactive element like a `div`, I must immediately ensure it has:
1. `role="button"` to identify it as a button.
2. `tabindex="0"` to make it focusable.
3. A `keydown` listener to handle `Enter` and `Space` keys.
4. An appropriate `aria-label` if the visible text is complex or structured layout.

This converts a "mouse-only" feature into a universally accessible one with minimal code changes.
