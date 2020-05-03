import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, 
    QHBoxLayout, QVBoxLayout, QApplication, QGridLayout, QFrame, QSizePolicy)
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QObject
board_size = 840 // 2

v_width = 840 // 2
v_height = 66 // 2

h_width = 66 // 2
h_height = (840 + 66 + 66) // 2

class Communicate(QObject):
    cellPressed = pyqtSignal(int, int) 

class Figure(QFrame):
    def __init__(self, type):
        super().__init__()
        self.type = type
        if self.type == 10:
            self.setStyleSheet("border-image: url(images/merida/wP.png) 0 0 0 0 stretch stretch;")

class Cell(QFrame):
    def __init__(self, x, y, type, c):
        super().__init__()
        self.c = c
        self.x = x
        self.y = y
        self.figure = Figure(type)
        self.setProperty("pressed", "0")
        vbox = QVBoxLayout()
        vbox.addWidget(self.figure)
        self.setLayout(vbox) 
        vbox.setContentsMargins(4,4,4,4)
 

    def mousePressEvent(self, event):
        self.c.cellPressed.emit(self.x, self.y)

    def press(self):
        self.setProperty("pressed", "1")
        self.setStyle(self.style())

    

    def release(self):
        self.setProperty("pressed", "0")
        self.setStyle(self.style())
        


class Board(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(board_size, board_size)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.c = Communicate()
        self.c.cellPressed.connect(self.cell_pressed)

        cells = QGridLayout()
        cells.setSpacing(0)
        cells.setContentsMargins(0,0,0,0)

        self.making_a_move = False
        self.start = (0, 0)

        self.cells_arr = [list() for i  in range(8) ]
        for i in range(8):
            for j in range(8):
                self.cells_arr[i].append(Cell(i, j, 10, self.c))
                cells.addWidget(self.cells_arr[i][j], i, j)
        self.setLayout(cells)

    def cell_pressed(self, x, y):
        if not self.making_a_move:
            self.start = (x, y)
            self.cells_arr[x][y].press()
            self.making_a_move = True
        else:
            self.cells_arr[self.start[0]][self.start[1]].release()
            self.making_a_move = False


        


class Border(QFrame):
    def __init__(self, name, width, height):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setObjectName(name)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

class Main_Window(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
        
    def initUI(self):
        self.setMinimumSize(v_width + 2 * h_width, h_height)

        board = Board()

        border_left = Border("border-left", h_width, h_height)
        border_right = Border("border-right", h_width, h_height)
        border_up = Border("border-up", v_width, v_height)
        border_down = Border("border-down", v_width, v_height)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(border_up)
        vbox.addWidget(board)
        vbox.addWidget(border_down)
        vbox.addStretch(1)
        vbox.setSpacing(0);
        vbox.setContentsMargins(0,0,0,0)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(border_left)
        hbox.addLayout(vbox)
        hbox.addWidget(border_right)
        hbox.addStretch(1)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0,0,0,0)

        self.setLayout(hbox)    
        
        
        self.setWindowTitle('Chess')    
        self.show()
