#!/usr/bin/env python3

from __future__ import unicode_literals
import sqlite3
import sys
from styles import mystyle
from pygments.lexers.sql import SqlLexer
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.application.current import get_app
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import button_dialog, yes_no_dialog
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import ProgressBar

style = mystyle()

multiline_bool = yes_no_dialog(
    title=HTML('<style bg="blue" fg="white"> Multiline Input </style>'),
    text='Do you want to enable multiline input?\n If you do, [Enter] will create a new line,\n and you will need to type [Escape-Enter] to run.',
    style=style).run()

case_bool = button_dialog(
    title=HTML('<style bg="blue" fg="white"> Auto-completion Case </style>'),
    text='Should the auto-completions be in lower or upper case?',
    buttons=[
        ('Lowercase', True),
        ('Uppercase', False)
    ],
    style=style).run()

completer = [
    'abort', 'action', 'add', 'after', 'all', 'alter', 'analyze', 'and',
    'as', 'asc', 'attach', 'autoincrement', 'before', 'begin', 'between',
    'by', 'cascade', 'case', 'cast', 'check', 'collate', 'column',
    'commit', 'conflict', 'constraint', 'create', 'cross', 'current_date',
    'current_time', 'current_timestamp', 'database', 'default',
    'deferrable', 'deferred', 'delete', 'desc', 'detach', 'distinct',
    'drop', 'each', 'else', 'end', 'escape', 'except', 'exclusive',
    'exists', 'explain', 'fail', 'for', 'foreign', 'from', 'full', 'glob',
    'group', 'having', 'if', 'ignore', 'immediate', 'in', 'index',
    'indexed', 'initially', 'inner', 'insert', 'instead', 'intersect',
    'into', 'is', 'isnull', 'join', 'key', 'left', 'like', 'limit',
    'match', 'natural', 'no', 'not', 'notnull', 'null', 'of', 'offset',
    'on', 'or', 'order', 'outer', 'plan', 'pragma', 'primary', 'query',
    'raise', 'recursive', 'references', 'regexp', 'reindex', 'release',
    'rename', 'replace', 'restrict', 'right', 'rollback', 'row',
    'savepoint', 'select', 'set', 'table', 'temp', 'temporary', 'then',
    'to', 'transaction', 'trigger', 'union', 'unique', 'update', 'using',
    'vacuum', 'values', 'view', 'virtual', 'when', 'where', 'with',
    'without']
if case_bool == False:
    completer = [c.upper() for c in completer]

sql_completer = WordCompleter(completer, ignore_case=True)

# Keybindings
bindings = KeyBindings()

@bindings.add('f4')
def _(event):
    " Toggle between Emacs and Vi mode. "
    app = event.app
    if app.editing_mode == EditingMode.VI:
        app.editing_mode = EditingMode.EMACS
    else:
        app.editing_mode = EditingMode.VI


@bindings.add('c-space')
def _(event):
    " Initialize autocompletion, or select the next completion. "
    buff = event.app.current_buffer
    if buff.complete_state:
        buff.complete_next()
    else:
        buff.start_completion(select_first=False)


def bottom_toolbar():
    " Display the current input mode. "
    editing_mode = 'Vi' if get_app().editing_mode == EditingMode.VI else 'Emacs'
    multiline_commands = '[Enter] Run' if multiline_bool == 0 else '[Enter] New line | [Escape-Enter] Run'
    return [
        ('class:toolbar', '[F4] ' + editing_mode +
         ' | [C-Space] Autocomplete | ' + multiline_commands + ' | [C-c] Abort command | [C-d] Quit')
    ]

# Main


def main(database):
    print('\nWelcome to Sqshell, an SQL REPL!\n')
    connection = sqlite3.connect(database)
    session = PromptSession(
        lexer=PygmentsLexer(SqlLexer),
        completer=sql_completer,
        history=FileHistory('.sqshell_history'),
        auto_suggest=AutoSuggestFromHistory(),
        complete_in_thread=True,
        key_bindings=bindings,
        multiline=multiline_bool,
        mouse_support=True,
        bottom_toolbar=bottom_toolbar,
        style=style)

    while True:
        try:
            message = [
                ('class:language', 'SQL'),
                ('class:arrow', ' \u279C '),
            ]
            text = session.prompt(message, style=style)
        except KeyboardInterrupt:
            continue  # Control-C pressed. Try again.
        except EOFError:
            break  # Control-D pressed.

        with connection:
            try:
                messages = connection.execute(text)
            except Exception as e:
                print(repr(e))
            else:
                for message in messages:
                    print(message)

    print('Goodbye!')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        db = ':memory:'
    else:
        db = sys.argv[1]

    main(db)
