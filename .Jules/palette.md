## 2024-05-23 - [Clickable Form Labels]
**Learning:** In list-based forms (like checkbox lists), users often try to click the row text rather than the small input box. Wrapping the entire row content in a `<label>` element is a zero-JS way to significantly improve touch targets and accessibility.
**Action:** Always wrap checkbox/radio rows in `<label>` instead of `<div>`, ensuring the input is inside or properly associated via `for`/`id`.

## 2025-05-24 - [Modal Focus Management]
**Learning:** Vanilla JS modals often neglect focus management. Without it, keyboard users get trapped or lost. Implementing a simple focus trap (tab cycle) and restoring focus on close makes the app usable for keyboard-only users.
**Action:** Always implement `trapFocus` and `restoreFocus` logic when building or modifying custom modals.
