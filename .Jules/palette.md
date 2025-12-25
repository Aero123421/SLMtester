## 2024-05-23 - [Clickable Form Labels]
**Learning:** In list-based forms (like checkbox lists), users often try to click the row text rather than the small input box. Wrapping the entire row content in a `<label>` element is a zero-JS way to significantly improve touch targets and accessibility.
**Action:** Always wrap checkbox/radio rows in `<label>` instead of `<div>`, ensuring the input is inside or properly associated via `for`/`id`.
## 2025-12-19 - [Accessible Table Sorting]
**Learning:** Native `<th>` elements are not focusable by default. To make them accessible for sorting, add `tabindex="0"` and `aria-sort`, and implement `keydown` handlers for Enter/Space. `role="button"` is sometimes redundant on headers if `aria-sort` is present, but keyboard support is mandatory.
**Action:** When implementing custom sortable tables, always couple `click` handlers with `keydown` handlers and dynamic `aria-sort` updates.
