"""Fixed-width Unicode box tables for CLI summaries (aligned columns, padded cells)."""

from __future__ import annotations

from typing import Sequence


def render_box_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    title: str | None = None,
    hpad: int = 1,
) -> str:
    """Render a box-drawn table sized to fit cell content.

    Uses ``┌─┬─┐`` borders and left-aligned text with horizontal padding.
    Long cell values are truncated with ``...`` to stay within column width.
    """
    if not headers:
        raise ValueError("headers must not be empty")
    n = len(headers)
    if any(len(row) != n for row in rows):
        raise ValueError("each row must have the same length as headers")

    body: list[tuple[str, ...]] = [tuple(str(h) for h in headers)]
    body.extend(tuple(str(c) for c in row) for row in rows)
    widths = [max(len(row[i]) for row in body) for i in range(n)]

    def cell(text: str, width: int) -> str:
        s = str(text)
        if len(s) > width:
            s = s[: max(0, width - 3)] + "..."
        return " " * hpad + s.ljust(width) + " " * hpad

    def border(left: str, mid: str, right: str, fill: str) -> str:
        parts = [fill * (w + hpad * 2) for w in widths]
        return left + mid.join(parts) + right

    lines: list[str] = []
    if title:
        lines.extend([title, ""])
    lines.append(border("┌", "┬", "┐", "─"))
    lines.append("│" + "│".join(cell(body[0][i], widths[i]) for i in range(n)) + "│")
    lines.append(border("├", "┼", "┤", "─"))
    for row in body[1:]:
        lines.append("│" + "│".join(cell(row[i], widths[i]) for i in range(n)) + "│")
    lines.append(border("└", "┴", "┘", "─"))
    return "\n".join(lines)
