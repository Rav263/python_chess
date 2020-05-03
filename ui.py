import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, 
    QHBoxLayout, QVBoxLayout, QApplication, QGridLayout, QFrame, QSizePolicy)
from PyQt5 import QtGui

board_size = 820 // 2

v_width = 820 // 2
v_height = 66 // 2

h_width = 66 // 2
h_height = (820 + 66 + 66) // 2


class Board(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(board_size, board_size)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

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

        # vbox.SetMinimumSize(h_height)
        
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
