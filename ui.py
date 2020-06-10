import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
    QHBoxLayout, QVBoxLayout, QStackedLayout, QApplication, QGridLayout, QFrame, QSizePolicy, QDialog)
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QObject, QMimeData, Qt, QPoint
from PyQt5.QtGui import QDrag, QPixmap
import time
import threading

board_size = 420

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
    figureMoved = pyqtSignal(int, int)
    nextMove = pyqtSignal()
    prevMove = pyqtSignal()

class Figure(QFrame):
    def __init__(self, figure_type, comm):
        super().__init__()
        self.comm = comm
        self.set_type(figure_type)
        self.fig_translation = {1:"P", 2:"N", 3:"B", 4:"R", 5:"K", 6:"Q"}
    
    def set_type(self, figure_type):
        self.figure_type = figure_type
        self.setProperty("type", str(figure_type))
        self.setStyle(self.style())

    def get_type(self):
        return self.figure_type

    def get_named_type(self):
        return self.fig_translation[self.figure_type % 10]
        
    def get_figure_name(self):
        name = ""
        name += "w" if self.figure_type // 10 == 1 else "b"
        name += self.get_named_type()
        return name

    def mouseMoveEvent(self, e):
        mime_data = QMimeData()
        mime_data.setText(str(self.figure_type))
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(QPixmap("images/merida/{}.png".format(self.get_figure_name())))
        drag.setHotSpot(self.rect().bottomRight())
        dropAction = drag.exec_(Qt.MoveAction)
    

class Cell(QFrame):
    def __init__(self, x, y, figure_type, comm, color, check_move):
        super().__init__()
        self.setMinimumSize(52, 52)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setAcceptDrops(True)
        self.comm = comm
        self.x = x
        self.y = y
        self.figure = Figure(figure_type, comm)
        self.setProperty("pressed", "0")
        self.check_move = check_move
        self.pressed = 0
        if color == 1:
            self.setProperty("color", "white")
        else:
            self.setProperty("color", "black")
        vbox = QVBoxLayout()
        vbox.addWidget(self.figure)
        self.setLayout(vbox)
        vbox.setContentsMargins(4, 4, 4, 4)
    
    def dragEnterEvent(self, e):
        e.accept()


    def dropEvent(self, e):
        position = e.pos()
        if self.check_move(self.x, self.y):
            self.comm.figureMoved.emit(self.x, self.y)
        e.accept()


    def mousePressEvent(self, event):
        self.comm.cellPressed.emit(self.x, self.y)

    def mouseReleaseEvent(self, event):
        self.comm.cellReleased.emit(self.x, self.y)

    def press(self):
        self.setProperty("pressed", "yes")
        self.setStyle(self.style())

    def beat(self):
        self.setProperty("pressed", "beat")
        self.setStyle(self.style())

    def release(self):
        self.setProperty("pressed", "no")
        self.setStyle(self.style())
        


class GuiBoard(QFrame):
    updBoard = pyqtSignal()
    def __init__(self, api):
        super().__init__()
        self.color = api.board.white
        self.api = api
        self.setMinimumSize(board_size, board_size)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setSizePolicy(sizePol)

        self.comm = Communicate()
        self.comm.cellPressed.connect(self.cell_pressed)
        self.comm.cellReleased.connect(self.cell_released)
        self.comm.figureMoved.connect(self.figure_moved)
        self.comm.nextMove.connect(self.next_move)
        self.comm.prevMove.connect(self.prev_move)

        v_layout = QGridLayout()
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)
        
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
                self.cells_arr[x].append(Cell(x, y, self.api.get_field((x, y)), self.comm, cell_color, self.check_move))
                cells.addWidget(self.cells_arr[x][y], x, y)
                cell_color = 3 - cell_color
            cell_color = 3 - cell_color
                
        v_layout.addLayout(cells, 0, 0)

        self.bottom_menu = BottomMenu(self.comm)
        v_layout.addWidget(self.bottom_menu, 1, 0)
        self.setLayout(v_layout)

    def cell_released(self, x, y):
        if self.ai_do_turn:
            self.upd_board()
            self.ai_do_turn = False
        

    def figure_moved(self, x, y):
        self.process_move(x, y, "drag")


    def cell_pressed(self, x, y):
        if not self.ai_do_turn:
            if not self.making_a_move:
                self.start = (x, y)
                self.cells_arr[x][y].press()
                self.making_a_move = True
                for field in self.possible_moves[(x, y)]:
                    if not self.cells_arr[field[0]][field[1]].figure.get_type():
                        self.cells_arr[field[0]][field[1]].figure.set_type("possible")
                    else:
                        self.cells_arr[field[0]][field[1]].beat()

            else:
                self.process_move(x, y, "press")
    
    def process_move(self, x, y, method):
        self.cells_arr[self.start[0]][self.start[1]].release()
        self.making_a_move = False
        for field in self.possible_moves[self.start]:
            if self.cells_arr[field[0]][field[1]].figure.get_type() == "possible":
                self.cells_arr[field[0]][field[1]].figure.set_type(0)
            else:
                self.cells_arr[field[0]][field[1]].release()

        if self.check_move(x, y):
            moved_fig_type = self.cells_arr[self.start[0]][self.start[1]].figure.get_named_type()
            if moved_fig_type == "P" and x in (0, 7):
                self.api.do_turn(self.start, (x, y), self.promotion())
            elif moved_fig_type == "K" and y in (2, 6):
                self.api.do_turn(self.start, (x, y), castling=True)
                if y == 2:
                    #long castling
                    rook_color = self.cells_arr[x][0].figure.figure_type
                    self.cells_arr[x][0].figure.set_type(0)
                    self.cells_arr[x][3].figure.set_type(rook_color)
                else:
                    #short castling
                    rook_color = self.cells_arr[x][7].figure.figure_type
                    print(rook_color)
                    self.cells_arr[x][7].figure.set_type(0)
                    self.cells_arr[x][5].figure.set_type(rook_color)
            else:    
                self.api.do_turn(self.start, (x, y))
            self.make_turn(self.start, (x, y))
            self.change_color()
            if method == "press":
                self.ai_do_turn = True
            elif method == "drag":
                self.upd_board()

    def make_turn(self, start, stop, promotion = -1):
        self.cells_arr[start[0]][start[1]].figure.set_type(0)
        self.cells_arr[stop[0]][stop[1]].figure.set_type(self.api.get_field(stop))

    def check_move(self, x, y):
        return True if ((x, y) in self.possible_moves[self.start]) else False

    def promotion(self):
        figures = []
        figures.append(QPushButton("Knight"))
        figures.append(QPushButton("Bishop"))
        figures.append(QPushButton("Rook"))
        figures.append(QPushButton("Queen"))

        prom_dialog = QDialog()
        prom_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog);
        prom_dialog.move(self.mapToGlobal(self.pos()) - QPoint(-2, -200))

        for num, figure in enumerate(figures):
            figure.clicked.connect(self.make_answer_button(num + 2, prom_dialog))
        prom_dialog.setWindowTitle("Choose figure:")
        
        hbox = QHBoxLayout(prom_dialog)
        hbox.addStretch(1)
        for figure in figures:
            hbox.addWidget(figure)
        hbox.addStretch(1)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        prom_dialog.setLayout(hbox)

        choice = prom_dialog.exec_()
        return choice if choice in (2, 3, 4) else 6

    def make_answer_button(self, figure, dialog):
        def answer():
            dialog.done(figure)
        return answer

    def upd_board(self):
        print("ai is going to make a turn")
        turn = self.api.ai_turn(self.color)
        print("ai made a turn")
        self.make_turn(turn.start_pos, turn.end_pos)
        self.change_color()
        self.upd_possible_moves(self.color)
    
    def upd_possible_moves(self, color):
        self.possible_moves = self.api.get_possible_turns(color)   

    def change_color(self):
        self.color = 3 - self.color

    def next_move(self):
        turn = self.api.next_turn()
        if turn:
            self.make_turn(turn.start_pos, turn.end_pos)

    def prev_move(self):
        turn = self.api.previous_turn()
        if turn:
            self.make_turn(turn[0].end_pos, turn[0].start_pos)
    
class BottomMenu(QFrame):
    def __init__(self, comm):
        super().__init__()
        self.comm = comm
        buttons = []
        buttons.append(QPushButton("undo"))
        buttons.append(QPushButton("redo"))
        buttons[0].clicked.connect(self.previous)
        buttons[1].clicked.connect(self.next)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        for but in buttons:
            h_layout.addWidget(but)
        h_layout.addStretch(1)
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(h_layout)
        
    def previous(self):
        self.comm.prevMove.emit()

    def next(self):
        self.comm.nextMove.emit()

class MainMenu(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(board_size, board_size)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setSizePolicy(sizePol)

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


class Main_Window(QWidget):
    
    def __init__(self, api):
        super().__init__()
        self.setMinimumSize(board_size, board_size)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setSizePolicy(sizePol)
        self.api = api

        self.board = GuiBoard(api)
        self.board.upd_possible_moves(self.board.color)
        self.menu = MainMenu()

        self.tabs = QStackedLayout()
        self.tabs.addWidget(self.menu)
        self.tabs.addWidget(self.board)

        self.tab_names = {"start":0, "game_board":1}
        self.tabs.setCurrentIndex(self.tab_names["start"])

        self.tabs.setSpacing(self.tab_names["start"])
        self.tabs.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.tabs)

        for diff, difficulty in enumerate(self.menu.difficulties):
            difficulty.clicked.connect(self.start_game_with_difficulty(diff + 1))

        self.setWindowTitle('Chess')
        self.show()

    def start_game_with_difficulty(self, difficulty):
        def start_game():
            self.api.difficulty = difficulty + 1
            self.tabs.setCurrentIndex(self.tab_names["game_board"])
        return start_game
  
    


