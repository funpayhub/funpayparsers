from __future__ import annotations

from funpayparsers.parsers.utils import serialize_form


form_html = """
<form>
  <input type="text" name="text1" value="hello">
  <input type="password" name="pass" value="secret">
  <input type="checkbox" name="check1" checked>
  <input type="checkbox" name="check2">
  <input type="radio" name="radio" value="a" checked>
  <input type="radio" name="radio" value="b">
  <textarea name="comment">Some text here</textarea>
  <select name="select1">
    <option value="1">One</option>
    <option value="2" selected>Two</option>
    <option value="3">Three</option>
  </select>
  <select name="select2">
    <option>Default</option>
  </select>
</form>
"""

result = {
    'text1': 'hello',
    'pass': 'secret',
    'check1': 'on',
    'check2': '',
    'radio': 'a',
    'comment': 'Some text here',
    'select1': '2',
    'select2': '',
}


def test_form_serializer():
    assert serialize_form(form_html) == result