## 2024-05-23 - [Clickable Form Labels]
**Learning:** In list-based forms (like checkbox lists), users often try to click the row text rather than the small input box. Wrapping the entire row content in a `<label>` element is a zero-JS way to significantly improve touch targets and accessibility.
**Action:** Always wrap checkbox/radio rows in `<label>` instead of `<div>`, ensuring the input is inside or properly associated via `for`/`id`.
