from __future__ import unicode_literals

from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label,
    TextArea,
    ValidationToolbar
)
from prompt_toolkit.shortcuts.dialogs import _return_none, _create_app

# Modified version of prompt toolkit input_dialog with additional default option
def input_dialog(
    title = "",
    text = "",
    ok_text: str = "OK",
    cancel_text: str = "Cancel",
    completer = None,
    validator = None,
    password = False,
    style = None,
    default = ""
):
    """
    Display a text input box.
    Return the given text, or None when cancelled.
    """

    def accept(buf) -> bool:
        get_app().layout.focus(ok_button)
        return True  # Keep text.

    def ok_handler() -> None:
        get_app().exit(result=textfield.text)

    ok_button = Button(text=ok_text, handler=ok_handler)
    cancel_button = Button(text=cancel_text, handler=_return_none)

    textfield = TextArea(
        multiline=False,
        text=default,
        password=password,
        completer=completer,
        accept_handler=accept,
    )

    dialog = Dialog(
        title=title,
        body=HSplit(
            [
                Label(text=text, dont_extend_height=True),
                textfield,
                ValidationToolbar(),
            ],
            padding=D(preferred=1, max=1),
        ),
        buttons=[ok_button, cancel_button],
        with_background=True,
    )

    return _create_app(dialog, style)