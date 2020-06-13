import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
    QHBoxLayout, QVBoxLayout, QApplication, QGridLayout, QFrame, QSizePolicy)
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QObject
import time
import threading

board_size = 840 // 2

v_width = 840 // 2
v_height = 66 // 2

h_width = 66 // 2
h_height = (840 + 66 + 66) // 2

lock = threading.Lock()

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
    cellReleased = pyqtSignal(int, int)

class Figure(QFrame):
    def __init__(self, figure_type):
        super().__init__()
        self.set_type(figure_type)
    
    def set_type(self, figure_type):
        self.figure_type = figure_type
        self.setProperty("type", str(figure_type))
        self.setStyle(self.style())

class Cell(QFrame):
    def __init__(self, x, y, figure_type, comm, color):
        super().__init__()
        self.comm = comm
        self.x = x
        self.y = y
        self.figure = Figure(figure_type)
        self.setProperty("pressed", "0")
        if color == 1:
            self.setProperty("color", "white")
        else:
            self.setProperty("color", "black")
        vbox = QVBoxLayout()
        vbox.addWidget(self.figure)
        self.setLayout(vbox)
        vbox.setContentsMargins(4, 4, 4, 4)

    def mousePressEvent(self, event):
        self.comm.cellPressed.emit(self.x, self.y)

    def mouseReleaseEvent(self, event):
        self.comm.cellReleased.emit(self.x, self.y)

    def press(self):
        self.setProperty("pressed", "1")
        self.setStyle(self.style())

    def release(self):
        self.setProperty("pressed", "0")
        self.setStyle(self.style())
        


class GuiBoard(QFrame):
    updBoard = pyqtSignal()
    def __init__(self, api):
        super().__init__()
        self.color = api.board.white
        self.api = api
        self.setMinimumSize(board_size, board_size)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.comm = Communicate()
        self.comm.cellPressed.connect(self.cell_pressed)
        self.comm.cellReleased.connect(self.cell_released)

        cells = QGridLayout()
        cells.setSpacing(0)
        cells.setContentsMargins(0, 0, 0, 0)
        
        self.making_a_move = False
        self.ai_do_turn = False
        self.start = (0, 0)
        
        self.cells_arr = [list() for i  in range(8)]
        cell_color = api.board.white
        for x in range(8):
            for y in range(8):
                self.cells_arr[x].append(Cell(x, y, self.api.get_field((x, y)), self.comm, cell_color))
                cells.addWidget(self.cells_arr[x][y], x, y)
                cell_color = 3 - cell_color
            cell_color = 3 - cell_color
                
        self.setLayout(cells)

    def cell_released(self, x, y):
        if self.ai_do_turn:
            self.upd_board()
            self.ai_do_turn = False

    def cell_pressed(self, x, y):
        if not self.ai_do_turn:
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
                    self.api.do_turn(self.start, (x, y))
                    self.make_turn(self.start, (x, y))
                    self.change_color()
                    self.ai_do_turn = True

    def make_turn(self, start, stop):
        self.cells_arr[start[0]][start[1]].figure.set_type(0)
        self.cells_arr[stop[0]][stop[1]].figure.set_type(self.api.get_field(stop))


    def upd_board(self):
        print("ai is going to make a turn")
        turn = self.api.ai_turn(self.color)[0]
        print("ai made a turn")
        self.make_turn(turn.start_pos, turn.end_pos)
        self.change_color()
        self.upd_possible_moves(self.color)
    
    def upd_possible_moves(self, color):
        self.possible_moves = self.api.get_possible_turns(color)

    def change_color(self):
        self.color = 3 - self.color

class MainMenu(QFrame):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumSize(v_width, v_width)
        self.setMinimumSize(v_width, v_width)
        self.start_game = QPushButton("Start Game")
        self.difficulties = [QPushButton(str(i)) for i in range(1, 5)]
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.start_game)
        for difficulty in self.difficulties:
            vbox.addWidget(difficulty)
            difficulty.hide()
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)
        self.setLayout(hbox)

        self.start_game.clicked.connect(self.choose_difficulty)

    def choose_difficulty(self):
        self.start_game.hide()
        for difficulty in self.difficulties:
            difficulty.show()


class Border(QFrame):
    def __init__(self, name, width, height):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setObjectName(name)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

class MainContainer(QFrame):
    def __init__(self, inside):
        super().__init__()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(inside)
        vbox.addStretch(1)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

class Main_Window(QWidget):
    
    def __init__(self, api):
        super().__init__()
        self.setMinimumSize(v_width + 2 * h_width, h_height)
        self.api = api
        self.board = GuiBoard(api)
        self.menu = MainMenu()
        self.board.upd_possible_moves(self.board.color)

        self.game_board = MainContainer(self.board)
        self.main_menu = MainContainer(self.menu)
        self.game_board.hide()

        
        hbox = QHBoxLayout()
        hbox.addWidget(self.game_board)
        hbox.addWidget(self.main_menu)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        for diff, difficulty in enumerate(self.menu.difficulties):
            difficulty.clicked.connect(self.start_game_with_difficulty(diff + 1))

        self.setWindowTitle('Chess')
        self.show()

    def start_game_with_difficulty(self, difficulty):
        def start_game():
            self.api.difficulty = difficulty + 1
            self.main_menu.hide()
            self.game_board.show()
        return start_game
  
    


