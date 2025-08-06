# notes/templatetags/note_extras.py

import re
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
import markdown2
# REMOVE THIS LINE: from notes.views import nm

register = template.Library()

@register.filter(name='markdown_and_links')
def markdown_and_links(text):
    """
    Renders Markdown text, finds [[Note Title]] links, and converts them
    to internal Django URLs. Also enables syntax highlighting.
    """
    # ADD THE IMPORT HERE INSTEAD
    from notes.views import nm

    if not text:
        return ""

    # 1. Find all [[Note Title]] style links
    def replace_link(match):
        title = match.group(1)
        manager = nm()
        linked_note = manager.find_by_title(title.strip())
        
        if linked_note:
            url = reverse('note_detail', args=[str(linked_note['_id'])])
            return f'<a href="{url}" class="internal-link">{title}</a>'
        else:
            return f'<span class="broken-link">{title}</span>'

    linked_text = re.sub(r'\[\[(.*?)\]\]', replace_link, text)

    # 2. Render the result as Markdown with extras
    html = markdown2.markdown(
        linked_text,
        extras=['fenced-code-blocks', 'code-friendly', 'tables', 'cuddled-lists', 'strikethrough']
    )
    return mark_safe(html)

