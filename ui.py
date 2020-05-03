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


class Cell(QFrame):
    def __init__(self, x, y, c):
        super().__init__()
        self.c = c
        self.x = x
        self.y = y


    def mousePressEvent(self, event):
        print("clicked")
        self.c.cellPressed.emit(self.x, self.y)
        self.setStyleSheet("border: 3px solid green")

        


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

        self.cells_arr = [list() for i  in range(8) ]
        for i in range(8):
            for j in range(8):
                self.cells_arr[i].append(Cell(i, j, self.c))
                cells.addWidget(self.cells_arr[i][j], i, j)
        self.setLayout(cells)

    def cell_pressed(self, x, y):
        print("got signal", x, y)
        self.cells_arr[x + 1][y + 1].setStyleSheet("border: 3px solid green")
        self.cells_arr[x - 1][y - 1].setStyleSheet("border: 3px solid green")
        


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
