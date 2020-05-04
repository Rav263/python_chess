import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
    QHBoxLayout, QVBoxLayout, QApplication, QGridLayout, QFrame, QSizePolicy)
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QObject

board_size = 840 // 2

v_width = 840 // 2
v_height = 66 // 2

h_width = 66 // 2
h_height = (840 + 66 + 66) // 2

def swap(a, b):
    a, b = b, a

class  Gui():
    def __init__(self, api):
        qss_file = open('styles.qss').read()
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(qss_file)
        self.main_window = Main_Window(api)
    
    def start(self):
        sys.exit(self.app.exec_())

class Communicate(QObject):
    cellPressed = pyqtSignal(int, int) 

class Figure(QFrame):
    def __init__(self, figure_type):
        super().__init__()
        self.set_type(figure_type)
    
    def set_type(self, figure_type):
        self.figure_type = figure_type
        self.setProperty("type", str(figure_type))
        self.setStyle(self.style())

class Cell(QFrame):
    def __init__(self, x, y, figure_type, comm):
        super().__init__()
        self.comm = comm
        self.x = x
        self.y = y
        self.figure = Figure(figure_type)
        self.setProperty("pressed", "0")

        vbox = QVBoxLayout()
        vbox.addWidget(self.figure)
        self.setLayout(vbox)
        vbox.setContentsMargins(4, 4, 4, 4)

    def mousePressEvent(self, event):
        self.comm.cellPressed.emit(self.x, self.y)

    def press(self):
        self.setProperty("pressed", "1")
        self.setStyle(self.style())

    def release(self):
        self.setProperty("pressed", "0")
        self.setStyle(self.style())
        


class GuiBoard(QFrame):
    def __init__(self, api):
        super().__init__()
        self.color = api.board.white
        self.api = api
        self.setMinimumSize(board_size, board_size)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.comm = Communicate()
        self.comm.cellPressed.connect(self.cell_pressed)

        cells = QGridLayout()
        cells.setSpacing(0)
        cells.setContentsMargins(0, 0, 0, 0)
        
        self.making_a_move = False
        self.start = (0, 0)
        

        self.cells_arr = [list() for i  in range(8) ]
        for x in range(8):
            for y in range(8):
                self.cells_arr[x].append(Cell(x, y, self.api.get_field((x, y)), self.comm))
                cells.addWidget(self.cells_arr[x][y], x, y)
        self.setLayout(cells)

    def cell_pressed(self, x, y):
        if not self.making_a_move:
            self.start = (x, y)
            self.cells_arr[x][y].press()
            self.making_a_move = True
            for field in self.possible_moves[(x, y)]:
                self.cells_arr[field[0]][field[1]].press()
        else:
            self.cells_arr[self.start[0]][self.start[1]].release()
            self.making_a_move = False
            for field in self.possible_moves[self.start]:
                self.cells_arr[field[0]][field[1]].release()

            if ((x, y) in self.possible_moves[self.start]):
                fig_type = self.cells_arr[self.start[0]][self.start[1]].figure.figure_type
                self.cells_arr[x][y].figure.set_type(fig_type)
                self.cells_arr[self.start[0]][self.start[1]].figure.set_type(0)

                self.api.do_turn(self.start, (x, y))
                self.change_color()
                self.upd_board()

    def upd_board(self):
        print("ai is going to make a turn")
        self.api.ai_turn(self.color)
        print("ai made a turn")
        for x in range(8):
            for y in range(8):
                self.cells_arr[x][y].figure.set_type(self.api.get_field((x, y)))
        self.change_color()
        self.upd_possible_moves(self.color)
    
    def upd_possible_moves(self, color):
        self.possible_moves = self.api.get_possible_turns(color)

    def change_color(self):
        self.color = 3 - self.color

class Border(QFrame):
    def __init__(self, name, width, height):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setObjectName(name)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

class Main_Window(QWidget):
    
    def __init__(self, api):
        super().__init__()
        self.setMinimumSize(v_width + 2 * h_width, h_height)

        self.board = GuiBoard(api)
        self.board.upd_possible_moves(1)

        border_left = Border("border-left", h_width, h_height)
        border_right = Border("border-right", h_width, h_height)
        border_up = Border("border-up", v_width, v_height)
        border_down = Border("border-down", v_width, v_height)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(border_up)
        vbox.addWidget(self.board)
        vbox.addWidget(border_down)
        vbox.addStretch(1)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(border_left)
        hbox.addLayout(vbox)
        hbox.addWidget(border_right)
        hbox.addStretch(1)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(hbox)
        
        
        self.setWindowTitle('Chess')
        self.show()
