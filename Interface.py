import curses
import json
from Editor import Editor
from Cursor import Cursor


class Interface:
    path = []
    editors = []
    num_of_editor = 0

    def __init__(self, pathList):
        self.config = json.load(open("config.json", "r"))
        if len(pathList) == 0:
            self.path.append("file")
            self.editors.append(Editor("file"))
        for path_ in pathList:
            self.path.append(str(path_))
            self.editors.append(Editor(str(path_)))

    def render_menu_lines(self, scr, max_y, max_x, cursor):
        """Method adds top and down menu lines"""
        menu_line = "{} files opened | ".format(len(self.editors))
        scr.addstr(0, 0, menu_line, curses.A_BOLD)

        s1 = ' | '.join(self.path[0:self.num_of_editor])
        if not len(s1) == 0:
            s1 += ' | '

        s2 = ' | '.join(self.path[self.num_of_editor + 1:len(self.editors)])
        s2 = ' | ' + s2
        if not len(s2) == 3:
            s2 += ' | '

        scr.addstr(0, len(menu_line), s1)
        if len(menu_line) + len(s1) < max_x:
            scr.addstr(0, len(menu_line) + len(s1), self.path[self.num_of_editor], curses.A_REVERSE)
            if len(menu_line) + len(s1) + len(self.path[self.num_of_editor]) < max_x:
                scr.addstr(0, len(menu_line) + len(s1) + len(self.path[self.num_of_editor]), s2)

        scr.addstr(max_y - 1, 0,
                   "Ctrl+E Exit | Ctrl+S Save | Ctrl+Q Close current file | Ctrl+Tab change current file |",
                   curses.A_BOLD)
        status_bar_cursor = "Position: {}:{}".format(str(cursor.x), str(cursor.y))
        scr.addstr(max_y - 1, max_x - len(status_bar_cursor) - 1, status_bar_cursor, curses.A_BOLD)

    def use_key(self, key):
        """If key is menu key code then make changes else call editor use_key function"""
        if key in self.config['key_codes']['KEY_CTL_TAB']:
            self.num_of_editor += 1
            self.num_of_editor %= len(self.editors)
        elif key in self.config['key_codes']['KEY_CTL_Q']:
            self.editors.pop(self.num_of_editor)
            self.path.pop(self.num_of_editor)
            if len(self.editors) == 0:
                self.path.append("file")
                self.editors.append(Editor("file"))
            self.num_of_editor %= len(self.editors)
        else:
            self.editors[self.num_of_editor].use_key(key)

    def draw(self, scr):
        """Draws redactor"""
        pad_render = Cursor(0, 0)
        key = 0
        while key not in self.config['key_codes']['KEY_CTL_E']:
            scr.clear()
            cursor = self.editors[self.num_of_editor].get_cursor()
            pad = self.editors[self.num_of_editor].render_pad()
            max_y, max_x = scr.getmaxyx()
            pad.keypad(True)
            scr.keypad(False)
            scr.leaveok(False)
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)

            self.render_menu_lines(scr, max_y, max_x, cursor)
            # scr.addstr(max_y - 1, 0, "Last pressed key: {} {}".format(str(key), str(curses.keyname(key))),
            #            curses.A_BOLD)

            pad_render = Cursor(min(cursor.x, pad_render.x), min(cursor.y, pad_render.y))
            pad_render = Cursor(max(cursor.x - max_x + 1, pad_render.x), max(cursor.y - max_y + 3, pad_render.y))

            scr.refresh()
            pad.refresh(pad_render.y, pad_render.x, 1, 0, max_y - 2, max_x - 1)
            key = pad.getch()
            self.use_key(key)
