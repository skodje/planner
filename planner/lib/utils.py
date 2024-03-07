import streamlit.components.v1 as components


def change_widget_font_size(label: str, font_size: str = "12px") -> None:
    """Change font size of widget label.

    This changes the font size of the label, but inserts a blank line in the
    document. It be nice to be able to avoid that blank line. Could also
    optimize this by allowing label to be a list so we don't need to iterate
    over everything every time this is called.
    """
    js_code = f"""
        <script>
        var elements = window.parent.document.querySelectorAll('*');
        for (var i = 0; i < elements.length; ++i) {{
            if (String(elements[i].innerText).startsWith('{label}')) {{
                elements[i].style.fontSize = '{font_size}';
            }}
        }}
        </script>
    """
    components.html(f"{js_code}", height=0, width=0)
