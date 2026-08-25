"""Safe formatting helpers for agent responses sent outside the API."""

import html
import re
from typing import List

_INLINE_TOKEN = re.compile(
    r"(\*\*.+?\*\*|\*[^*\n]+?\*|\[[^\]\n]+\]\([^)\n]+\))"
)


def _inline_html(text: str) -> str:
    """Render a small, safe Markdown subset without allowing raw HTML."""
    rendered: List[str] = []
    position = 0

    for match in _INLINE_TOKEN.finditer(text):
        rendered.append(html.escape(text[position:match.start()]))
        token = match.group(0)

        if token.startswith("**"):
            rendered.append(f"<strong>{html.escape(token[2:-2])}</strong>")
        elif token.startswith("*"):
            rendered.append(f"<em>{html.escape(token[1:-1])}</em>")
        else:
            label, url = re.match(r"\[([^]]+)\]\(([^)]+)\)", token).groups()
            if url.startswith(("https://", "http://")):
                rendered.append(
                    f'<a href="{html.escape(url, quote=True)}">'
                    f"{html.escape(label)}</a>"
                )
            else:
                rendered.append(html.escape(label))

        position = match.end()

    rendered.append(html.escape(text[position:]))
    return "".join(rendered).replace("**", "").replace("*", "")


def markdown_to_html(text: str) -> str:
    """Convert agent Markdown into email-safe HTML."""
    output: List[str] = []
    active_list = None

    def close_list() -> None:
        nonlocal active_list
        if active_list:
            output.append(f"</{active_list}>")
            active_list = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            close_list()
            continue

        heading = re.match(r"^#{1,6}\s+(.+)$", line)
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        numbered = re.match(r"^\d+[.)]\s+(.+)$", line)

        if heading:
            close_list()
            output.append(f"<h3>{_inline_html(heading.group(1))}</h3>")
        elif bullet or numbered:
            list_type = "ul" if bullet else "ol"
            if active_list != list_type:
                close_list()
                output.append(f"<{list_type}>")
                active_list = list_type
            content = (bullet or numbered).group(1)
            output.append(f"<li>{_inline_html(content)}</li>")
        else:
            close_list()
            output.append(f"<p>{_inline_html(line)}</p>")

    close_list()
    return "\n".join(output)


def markdown_to_plain_text(text: str) -> str:
    """Remove Markdown control characters for plain-text email clients."""
    result = re.sub(
        r"\[([^]]+)\]\((https?://[^)]+)\)",
        r"\1 (\2)",
        text,
    )
    result = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", result)
    result = re.sub(r"^#{1,6}\s+", "", result, flags=re.MULTILINE)
    result = result.replace("**", "").replace("*", "")
    return result.strip()
