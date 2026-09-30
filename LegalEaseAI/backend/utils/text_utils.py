import html


def format_html_preview(text: str) -> str:
    """Convert generated text into a simple HTML preview."""
    if not text:
        return "<p>No document content available.</p>"

    escaped = html.escape(text)

    paragraphs = escaped.split("\n\n")

    return "".join(
        f"<p>{p.replace(chr(10), '<br>')}</p>"
        for p in paragraphs
        if p.strip()
    )