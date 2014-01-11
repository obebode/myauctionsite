__author__ = 'obe'

import re
from django.utils.html import escape

def html_to_description(h):
    return escape(h)

def description_to_html(s):
    s= re.sub('\n','<br>\n',s)
    s= re.sub(
        r'\{\{\w+\}\}',
        (lambda n: '<a href="/auction/' + n.group(0)[2:-2] + '">' + n.group(0)[2:-2] + '</a>' ),
        s)
    return s
