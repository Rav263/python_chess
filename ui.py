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

        # def sizeHint(self):
        #     return QSize(board_size, board_size)


class Main_Window(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
        
    def initUI(self):
        self.setMinimumSize(h_width, h_height)

        board = Board()
        board.setMinimumSize(board_size, board_size)
        board.setSizePolicy(QSizePolicy.Fixed,
                            QSizePolicy.Fixed)
        # board.setPalette(palette)

        border_left = QFrame()
        border_left.setObjectName("border-left")
        border_left.setMaximumSize(h_width, h_height)
        border_left.setMinimumSize(h_width, h_height)
        border_left.setSizePolicy(QSizePolicy.Fixed,
                                  QSizePolicy.Fixed)

        border_right = QFrame()
        border_right.setObjectName("border-right")
        border_right.setMaximumSize(h_width, h_height)
        border_right.setMinimumSize(h_width, h_height)
        border_right.setSizePolicy(QSizePolicy.Fixed,
                                  QSizePolicy.Fixed)

        border_up = QFrame()
        border_up.setObjectName("border-up")
        border_up.setMaximumSize(v_width, v_height)
        border_up.setMinimumSize(v_width, v_height)
        border_up.setSizePolicy(QSizePolicy.Fixed,
                                  QSizePolicy.Fixed)
        

        border_down = QFrame()
        border_down.setObjectName("border-down")
        border_down.setMaximumSize(v_width, v_height)
        border_down.setMinimumSize(v_width, v_height)
        border_down.setSizePolicy(QSizePolicy.Fixed,
                                  QSizePolicy.Fixed)

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
