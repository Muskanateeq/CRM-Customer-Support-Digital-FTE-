"""Tests for safe channel-aware response formatting."""

from src.utils.message_formatting import markdown_to_html, markdown_to_plain_text


def test_markdown_to_html_formats_without_exposing_markers() -> None:
    source = """## Routine

1. **Cleanser** - Use gently
2. **Sunscreen** - Apply daily

[View products](https://example.com/products)
"""

    result = markdown_to_html(source)

    assert "<h3>Routine</h3>" in result
    assert "<strong>Cleanser</strong>" in result
    assert "<ol>" in result
    assert '<a href="https://example.com/products">View products</a>' in result
    assert "**" not in result


def test_markdown_to_html_escapes_untrusted_html() -> None:
    result = markdown_to_html("**Important** <script>alert(1)</script>")

    assert "<strong>Important</strong>" in result
    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_markdown_to_plain_text_removes_control_characters() -> None:
    result = markdown_to_plain_text("## **Important**\n*Use daily*")

    assert result == "Important\nUse daily"
