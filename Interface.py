import curses
from Editor import Editor


def rawInput(scr, r, c, prompt_string):
    curses.echo()
    scr.addstr(r, c, prompt_string)
    scr.refresh()
    input = scr.getstr(r + 1, c, 20)
    return input  # ^^^^  reading input at next line


class Interface:
    path = []
    editors = []
    numOfEditor = 0

    def __init__(self, pathList):
        if len(pathList) == 0:
            self.path.append("README")
            self.editors.append(Editor("Readme.md"))
        for path_ in pathList:
            self.path.append(str(path_))
            self.editors.append(Editor(str(path_)))

    def draw(self, scr):
        padRenderX = 0
        padRenderY = 0
        key = 0
        while (key != 5):
            scr.clear()
            cursorY, cursorX = self.editors[self.numOfEditor].getCursor()
            pad = self.editors[self.numOfEditor].renderPad()
            maxY, maxX = scr.getmaxyx()
            pad.keypad(True)
            scr.keypad(False)
            scr.leaveok(False)
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)

            MenuLine = "F1 Menu (soon) | "
            scr.addstr(0, 0, MenuLine, curses.A_BOLD)

            s1 = ""
            for i in range(self.numOfEditor):
                s1 += self.path[i] + ' | '

            scr.addstr(0, len(MenuLine), s1)
            if len(MenuLine) + len(s1) < maxX:
                scr.addstr(0, len(MenuLine) + len(s1), self.path[self.numOfEditor], curses.A_REVERSE)
            s2 = ""
            for i in range(self.numOfEditor + 1, len(self.editors)):
                s2 += ' | ' + self.path[i]
            if len(MenuLine) + len(s1) + len(self.path[self.numOfEditor]) < maxX:
                scr.addstr(0, len(MenuLine) + len(s1) + len(self.path[self.numOfEditor]), s2)

            # scr.addstr(maxY - 1, 0, "Ctrl+E Exit | Ctrl+S Save | Ctrl+Q Close current file | Ctrl+Tab change current file |", curses.A_BOLD)
            scr.addstr(maxY - 1, 0, "Last pressed key: " + str(key) + ' ' + str(curses.keyname(key)), curses.A_BOLD)
            statusBarCursor = "Position: " + str(cursorX) + ':' + str(cursorY)
            scr.addstr(maxY - 1, maxX - len(statusBarCursor) - 1, statusBarCursor, curses.A_BOLD)

            if cursorX < padRenderX:
                padRenderX = cursorX
            if cursorX > padRenderX + maxX - 1:
                padRenderX = cursorX - maxX + 1
            if cursorY < padRenderY:
                padRenderY = cursorY
            if cursorY > padRenderY + maxY - 3:
                padRenderY = cursorY - maxY + 3
            scr.refresh()
            pad.refresh(padRenderY, padRenderX, 1, 0, maxY - 2, maxX - 1)
            key = pad.getch()
            if key == 482:  # Ctrl+Tab
                self.numOfEditor += 1
                self.numOfEditor %= len(self.editors)
            # elif key == 15: #Ctrl+O
            # todo
            elif key == 17:  # Ctrl+Q
                self.editors.pop(self.numOfEditor)
                self.path.pop(self.numOfEditor)
                if len(self.editors) == 0:
                    self.path.append("README")
                    self.editors.append(Editor("Readme.md"))
                self.numOfEditor %= len(self.editors)
            else:
                self.editors[self.numOfEditor].useKey(key)
