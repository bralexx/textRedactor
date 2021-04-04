import curses
import pyperclip


class Editor:
    padWidth = 1000
    path = str
    content = []
    cursorX = 0
    cursorY = 0
    selectionX = 0
    selectionY = 0

    def setSize(self):
        maxStrLen = 1000
        for str in self.content:
            maxStrLen = max(maxStrLen, len(str))
        self.padWidth = maxStrLen

    def __init__(self, path_):
        self.path = path_
        file = open(self.path, "r")
        self.content = (file.read()).split('\n')
        if len(self.content) == 0:
            self.content.append("")
        self.setSize()

    def renderPad(self):
        pad = curses.newpad(len(self.content), self.padWidth)
        cursorX = self.cursorX
        cursorY = self.cursorY
        selectionX = self.selectionX
        selectionY = self.selectionY
        [selectionY, selectionX], [cursorY, cursorX] = \
            min([selectionY, selectionX], [cursorY, cursorX]), max([selectionY, selectionX], [cursorY, cursorX])
        for i in range(selectionY):
            pad.addstr(i, 0, self.content[i])
        pad.addstr(selectionY, 0, self.content[selectionY][0:selectionX])

        pad.attron(curses.A_REVERSE)
        if selectionY == cursorY:
            if not selectionX == cursorX:
                pad.addstr(selectionY, selectionX, self.content[selectionY][selectionX:cursorX])
        else:
            pad.addstr(selectionY, selectionX, self.content[selectionY][selectionX:len(self.content[selectionY])])
            for i in range(selectionY + 1, cursorY):
                pad.addstr(i, 0, self.content[i])
            pad.addstr(cursorY, 0, self.content[cursorY][0:cursorX])
        pad.attroff(curses.A_REVERSE)

        pad.addstr(cursorY, cursorX, self.content[cursorY][cursorX:len(self.content[cursorY])])
        for i in range(cursorY + 1, len(self.content)):
            pad.addstr(i, 0, self.content[i])
        pad.move(self.cursorY, self.cursorX)
        return pad

    def getCursor(self):
        return self.cursorY, self.cursorX

    def paste(self, otherContent):
        [startY, startX], [endY, endX] = min([self.selectionY, self.selectionX], [self.cursorY, self.cursorX]), \
                                         max([self.selectionY, self.selectionX], [self.cursorY, self.cursorX])
        self.cursorY = startY + len(otherContent) - 1
        if len(otherContent) > 1:
            self.cursorX = len(otherContent[len(otherContent) - 1])
        else:
            self.cursorX = startX + len(otherContent[len(otherContent) - 1])

        otherContent[len(otherContent) - 1] += self.content[endY][endX:len(self.content[endY]) - 1]
        for i in range(startY + 1, endY + 1):
            self.content.pop(i)
        self.content[startY] = self.content[startY][0:startX]
        self.content[startY] += otherContent[0]
        for i in range(1, len(otherContent)):
            self.content.insert(startY + i, otherContent[i])
        self.setSize()

    def keyUp(self):
        self.cursorY -= 1
        self.cursorY = max(self.cursorY, 0)
        self.cursorX = min(self.cursorX, len(self.content[self.cursorY]))

    def keyDown(self):
        self.cursorY += 1
        self.cursorY = min(self.cursorY, len(self.content) - 1)
        self.cursorX = min(self.cursorX, len(self.content[self.cursorY]))

    def keyRight(self):
        if self.cursorY == len(self.content) - 1 and self.cursorX == len(self.content[self.cursorY]):
            return
        if not self.cursorY == len(self.content) - 1 and self.cursorX == len(self.content[self.cursorY]):
            self.cursorY += 1
            self.cursorX = 0
        else:
            self.cursorX += 1
            self.cursorX = min(self.cursorX, len(self.content[self.cursorY]))

    def keyLeft(self):
        if not self.cursorY == 0 and self.cursorX == 0:
            self.cursorY -= 1
            self.cursorX = len(self.content[self.cursorY])
        else:
            self.cursorX -= 1
            self.cursorX = max(self.cursorX, 0)

    def backspace(self):
        if self.selectionX != self.cursorX or self.selectionY != self.cursorY:
            self.paste([""])
            return
        if self.cursorX == 0:
            if self.cursorY > 0:
                self.cursorX = len(self.content[self.cursorY - 1])
                self.content[self.cursorY - 1] += self.content[self.cursorY]
                self.content.pop(self.cursorY)
                self.cursorY -= 1
        else:
            self.content[self.cursorY] = self.content[self.cursorY][0:self.cursorX - 1] + \
                                         self.content[self.cursorY][self.cursorX:len(self.content[self.cursorY])]
            self.cursorX -= 1
            self.cursorX = max(self.cursorX, 0)
            self.selectionY, self.selectionX = self.cursorY, self.cursorX

    def ctrlC(self):
        if self.cursorY == self.selectionY:
            if self.cursorX == self.selectionX:
                return
            else:
                pyperclip.copy(
                    self.content[self.cursorY][min(self.selectionX, self.cursorX):max(self.selectionX, self.cursorX)])
        else:
            [startY, startX], [endY, endX] = min([self.selectionY, self.selectionX], [self.cursorY, self.cursorX]), \
                                             max([self.selectionY, self.selectionX], [self.cursorY, self.cursorX])
            s = self.content[startY][startX:len(self.content[startY])] + '\n'
            for i in range(startY + 1, endY):
                s += self.content[i] + '\n'
            s += self.content[endY][0:endY]
            pyperclip.copy(s)

    def ctrlRight(self):
        while self.cursorX < len(self.content[self.cursorY]) and self.content[self.cursorY][self.cursorX] == ' ':
            self.keyRight()
        self.keyRight()
        while self.cursorX < len(self.content[self.cursorY]) and self.content[self.cursorY][self.cursorX] != ' ':
            self.keyRight()

    def ctrlLeft(self):
        while self.cursorX > 0 and self.content[self.cursorY][self.cursorX - 1] == ' ':
            self.keyLeft()
        self.keyLeft()
        while self.cursorX > 0 and self.content[self.cursorY][self.cursorX - 1] != ' ':
            self.keyLeft()

    def ctrlBackSpace(self):
        while self.cursorX > 0 and self.content[self.cursorY][self.cursorX - 1] == ' ':
            self.backspace()
        self.backspace()
        while self.cursorX > 0 and self.content[self.cursorY][self.cursorX - 1] != ' ':
            self.backspace()
        self.backspace()

    def useKey(self, key):

        if key == curses.KEY_UP or key == 547:
            self.keyUp()
        elif key == curses.KEY_DOWN or key == 548:
            self.keyDown()
        elif key == curses.KEY_RIGHT or key == curses.KEY_SRIGHT:
            self.keyRight()
        elif key == curses.KEY_END or key == curses.KEY_SEND:
            self.cursorX = len(self.content[self.cursorY])
        elif key == curses.KEY_HOME or key == curses.KEY_SHOME:
            self.cursorX = 0
        elif key == 444:  # Ctrl + Right
            self.ctrlRight()
        elif key == curses.KEY_LEFT or key == curses.KEY_SLEFT:
            self.keyLeft()
        elif key == 443:  # Ctrl + Left
            self.ctrlLeft()
        elif key == 3:  # Ctrl + C
            self.ctrlC()
        elif key == 22:  # Ctrl + V
            self.paste((str(pyperclip.paste())).split('\n'))
        elif key == 19:  # Ctrl + S
            file = open(self.path, 'w')
            for s in self.content:
                file.write(s)
                file.write('\n')
        elif key == 10 or key == curses.KEY_ENTER:
            self.content.insert(self.cursorY + 1,
                                self.content[self.cursorY][self.cursorX:len(self.content[self.cursorY])])
            self.content[self.cursorY] = self.content[self.cursorY][0:self.cursorX]
            self.cursorY += 1
            self.cursorX = 0
        elif key == curses.KEY_RESIZE:
            return
        elif key == 8 or key == curses.KEY_BACKSPACE:
            self.backspace()
        elif key == 127:
            self.ctrlBackSpace()
        elif key in range(curses.KEY_F0, curses.KEY_F12):  # F1 - F12
            return
        elif key in range(32, 127) and (chr(key).isprintable() or chr(key).isdigit() or key == 32 or chr(key) == ' '):
            if self.cursorY == self.selectionY and self.cursorX == self.selectionX:
                self.content[self.cursorY] = self.content[self.cursorY][0:self.cursorX] + chr(key) + \
                                             self.content[self.cursorY][self.cursorX:len(self.content[self.cursorY])]
                self.cursorX += 1
            else:
                self.paste([str(chr(key))])
            self.selectionY, self.selectionX = self.cursorY, self.cursorX

        if not (key == 547 or key == 548 or key == curses.KEY_SRIGHT or key == curses.KEY_SLEFT or key == 3 or
                key == curses.KEY_SHOME or key == curses.KEY_SEND):
            self.selectionY, self.selectionX = self.cursorY, self.cursorX
