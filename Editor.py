import curses
import pyperclip
import json
from Cursor import Cursor


class Editor:
    pad_width = 1000
    path = str
    content = []
    cursor = Cursor(0, 0)
    selection = Cursor(0, 0)

    def __init__(self, path_):
        self.config = json.load(open("config.json", "r"))
        self.path = path_
        file = open(self.path, "r")
        self.content = (file.read()).split('\n')
        if len(self.content) == 0:
            self.content.append("")
        self.set_size()

    def set_size(self):
        max_str_len = 1000
        for s in self.content:
            max_str_len = max(max_str_len, len(s))
        self.pad_width = max_str_len

    def render_pad(self):
        pad = curses.newpad(len(self.content), self.pad_width)
        cursor = self.cursor
        selection = self.selection

        selection, cursor = min(selection, cursor), max(selection, cursor)
        for i in range(selection.y):
            pad.addstr(i, 0, self.content[i])
        pad.addstr(selection.y, 0, self.content[selection.y][0:selection.x])

        pad.attron(curses.A_REVERSE)
        if selection.y == cursor.y:
            if not selection.x == cursor.x:
                pad.addstr(selection.y, selection.x, self.content[selection.y][selection.x:cursor.x])
        else:
            pad.addstr(selection.y, selection.x, self.content[selection.y][selection.x:len(self.content[selection.y])])
            for i in range(selection.y + 1, cursor.y):
                pad.addstr(i, 0, self.content[i])
            pad.addstr(cursor.y, 0, self.content[cursor.y][0:cursor.x])
        pad.attroff(curses.A_REVERSE)

        pad.addstr(cursor.y, cursor.x, self.content[cursor.y][cursor.x:len(self.content[cursor.y])])
        for i in range(cursor.y + 1, len(self.content)):
            pad.addstr(i, 0, self.content[i])
        pad.move(self.cursor.y, self.cursor.x)
        return pad

    def get_cursor(self):
        return self.cursor

    def keyRight(self):
        if self.cursor.y == len(self.content) - 1 and self.cursor.x == len(self.content[self.cursor.y]):
            return
        if not self.cursor.y == len(self.content) - 1 and self.cursor.x == len(self.content[self.cursor.y]):
            self.cursor.y += 1
            self.cursor.x = 0
        else:
            self.cursor.x += 1
            self.cursor.x = min(self.cursor.x, len(self.content[self.cursor.y]))

    def keyLeft(self):
        if not self.cursor.y == 0 and self.cursor.x == 0:
            self.cursor.y -= 1
            self.cursor.x = len(self.content[self.cursor.y])
        else:
            self.cursor.x -= 1
            self.cursor.x = max(self.cursor.x, 0)

    def paste(self, otherContent):
        start, end = min(self.selection, self.cursor), max(self.selection, self.cursor)
        self.cursor.y = start.y + len(otherContent) - 1
        if len(otherContent) > 1:
            self.cursor.x = len(otherContent[len(otherContent) - 1])
        else:
            self.cursor.x = start.x + len(otherContent[len(otherContent) - 1])

        otherContent[len(otherContent) - 1] += self.content[end.y][end.x:len(self.content[end.y]) - 1]
        for i in range(start.y + 1, end.y + 1):
            self.content.pop(i)
        self.content[start.y] = self.content[start.y][0:start.x]
        self.content[start.y] += otherContent[0]
        for i in range(1, len(otherContent)):
            self.content.insert(start.y + i, otherContent[i])
        self.set_size()

    def backspace(self):
        if self.selection.x != self.cursor.x or self.selection.y != self.cursor.y:
            self.paste([""])
            return
        if self.cursor.x == 0:
            if self.cursor.y > 0:
                self.cursor.x = len(self.content[self.cursor.y - 1])
                self.content[self.cursor.y - 1] += self.content[self.cursor.y]
                self.content.pop(self.cursor.y)
                self.cursor.y -= 1
        else:
            self.content[self.cursor.y] = self.content[self.cursor.y][0:self.cursor.x - 1] + \
                                          self.content[self.cursor.y][self.cursor.x:len(self.content[self.cursor.y])]
            self.cursor.x -= 1
            self.cursor.x = max(self.cursor.x, 0)
            self.selection.y, self.selection.x = self.cursor.y, self.cursor.x

    def use_key(self, key):

        if key in self.config['key_codes']['KEY_UP']:
            self.cursor.y -= 1
            self.cursor = Cursor(max(self.cursor.y, 0), min(self.cursor.x, len(self.content[self.cursor.y])))
        elif key in self.config['key_codes']['KEY_DOWN']:
            self.cursor.y += 1
            self.cursor.y = min(self.cursor.y, len(self.content) - 1)
            self.cursor.x = min(self.cursor.x, len(self.content[self.cursor.y]))
        elif key in self.config['key_codes']['KEY_RIGHT']:
            self.keyRight()
        elif key in self.config['key_codes']['KEY_LEFT']:
            self.keyLeft()
        elif key in self.config['key_codes']['KEY_END']:
            self.cursor.x = len(self.content[self.cursor.y])
        elif key in self.config['key_codes']['KEY_HOME']:
            self.cursor.x = 0
        elif key in self.config['key_codes']['KEY_CTL_RIGHT']:
            while self.cursor.x < len(self.content[self.cursor.y]) and self.content[self.cursor.y][
                self.cursor.x] == ' ':
                self.cursor.x += 1
            self.keyRight()
            while self.cursor.x < len(self.content[self.cursor.y]) and self.content[self.cursor.y][
                self.cursor.x] != ' ':
                self.keyRight()
        elif key in self.config['key_codes']['KEY_CTL_LEFT']:
            while self.cursor.x > 0 and self.content[self.cursor.y][self.cursor.x - 1] == ' ':
                self.keyLeft()
            self.keyLeft()
            while self.cursor.x > 0 and self.content[self.cursor.y][self.cursor.x - 1] != ' ':
                self.keyLeft()
        elif key in self.config['key_codes']['KEY_CTL_C']:
            if self.cursor.y == self.selection.y:
                if self.cursor.x == self.selection.x:
                    return
                else:
                    pyperclip.copy(
                        self.content[self.cursor.y][
                        min(self.selection.x, self.cursor.x):max(self.selection.x, self.cursor.x)])
            else:
                start, end = min(self.selection, self.cursor), max(self.selection, self.cursor)
                s = '\n'.join([self.content[start.y][start.x:len(self.content[start.y])],
                               '\n'.join(self.content[start.y + 1:end.y]), self.content[end.y][0:end.x]])
                pyperclip.copy(s)
        elif key in self.config['key_codes']['KEY_CTL_V']:
            self.paste((str(pyperclip.paste())).split('\n'))
        elif key in self.config['key_codes']['KEY_CTL_S']:
            file = open(self.path, 'w')
            for s in self.content:
                file.write(s)
                file.write('\n')
        elif key in self.config['key_codes']['KEY_ENTER']:
            self.content.insert(self.cursor.y + 1,
                                self.content[self.cursor.y][self.cursor.x:len(self.content[self.cursor.y])])
            self.content[self.cursor.y] = self.content[self.cursor.y][0:self.cursor.x]
            self.cursor.y += 1
            self.cursor.x = 0
        elif key == curses.KEY_RESIZE:
            return
        elif key in self.config['key_codes']['KEY_BACKSPACE']:
            self.backspace()
        elif key in self.config['key_codes']['KEY_CTL_BACKSPACE']:
            while self.cursor.x > 0 and self.content[self.cursor.y][self.cursor.x - 1] == ' ':
                self.backspace()
            self.backspace()
            while self.cursor.x > 0 and self.content[self.cursor.y][self.cursor.x - 1] != ' ':
                self.backspace()
            self.backspace()
        elif key in range(curses.KEY_F0, curses.KEY_F12):  # F1 - F12
            return
        elif key in range(32, 127):
            if self.cursor == self.selection:
                self.content[self.cursor.y] = self.content[self.cursor.y][0:self.cursor.x] + chr(key) + \
                                              self.content[self.cursor.y][
                                              self.cursor.x:len(self.content[self.cursor.y])]
                self.cursor.x += 1
            else:
                self.paste([str(chr(key))])
            self.selection.y, self.selection.x = self.cursor.y, self.cursor.x

        if not key in self.config['s_key_codes']:
            self.selection.y, self.selection.x = self.cursor.y, self.cursor.x
