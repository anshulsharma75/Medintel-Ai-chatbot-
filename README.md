"""Shared helpers for MedIntel Streamlit app."""


def card_html(content: str, variant: str = "default") -> str:
    """Wrap content in a styled card div."""
    border_map = {
        "default": "#1a3347",
        "accent":  "rgba(0,229,195,0.3)",
        "warn":    "rgba(245,158,11,0.3)",
        "danger":  "rgba(255,107,74,0.3)",
    }
    left_border = {
        "default": "none",
        "accent":  "3px solid #00e5c3",
        "warn":    "3px solid #f59e0b",
        "danger":  "3px solid #ff6b4a",
    }
    return f"""
    <div style='
        background:#0b1f2e;
        border:1px solid {border_map.get(variant, border_map["default"])};
        border-left:{left_border.get(variant, "none")};
        border-radius:12px;
        padding:16px;
        margin-bottom:12px;
    '>{content}</div>
    """


def tag_html(text: str, color: str = "green") -> str:
    """Inline tag badge."""
    styles = {
        "green":  ("rgba(0,229,195,0.1)",  "#00e5c3", "rgba(0,229,195,0.3)"),
        "orange": ("rgba(245,158,11,0.1)", "#f59e0b", "rgba(245,158,11,0.3)"),
        "red":    ("rgba(255,107,74,0.1)", "#ff6b4a", "rgba(255,107,74,0.3)"),
        "purple": ("rgba(167,139,250,0.1)","#a78bfa", "rgba(167,139,250,0.3)"),
    }
    bg, fg, border = styles.get(color, styles["green"])
    return (
        f"<span style='display:inline-block;background:{bg};color:{fg};"
        f"border:1px solid {border};border-radius:4px;"
        f"font-family:monospace;font-size:11px;padding:3px 10px;"
        f"margin-right:6px;letter-spacing:0.04em;'>{text}</span>"
    )


def metric_delta(value: float, baseline: float, unit: str = "") -> str:
    """Format a delta string with sign and unit."""
    diff = value - baseline
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.1f}{unit}"
