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
    backMenu = pyqtSignal()
    toStart = pyqtSignal()
    skipHist = pyqtSignal()

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

    def get_color(self):
        return "w" if self.figure_type // 10 == 1 else "b"

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
    def __init__(self, api, comm):
        super().__init__()
        self.history = 0
        self.reached_hist_bottom = False
        self.color = api.board.white
        self.api = api
        self.setMinimumSize(board_size, board_size)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setSizePolicy(sizePol)

        self.comm = comm
        self.comm.cellPressed.connect(self.cell_pressed)
        self.comm.cellReleased.connect(self.cell_released)
        self.comm.figureMoved.connect(self.figure_moved)
        self.comm.nextMove.connect(self.next_move)
        self.comm.prevMove.connect(self.prev_move)
        self.comm.toStart.connect(self.to_start)
        self.comm.skipHist.connect(self.skip_history)
        
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
        self.setLayout(cells)

    def cell_released(self, x, y):
        if self.ai_do_turn:
            self.upd_board()
            self.ai_do_turn = False
        
    def figure_moved(self, x, y):
        self.process_move(x, y, "drag")

    def cell_pressed(self, x, y):
        if not self.ai_do_turn and not self.history:
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
            fig_color = self.cells_arr[self.start[0]][self.start[1]].figure.get_color()
            if moved_fig_type == "P" and x in (0, 7):
                self.api.do_turn(self.start, (x, y), self.promotion(fig_color))
            elif moved_fig_type == "K" and y in (2, 6):
                self.api.do_turn(self.start, (x, y), castling=True)
                self.make_castling(x, y)
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
        return True if not self.history and (x, y) in self.possible_moves[self.start] else False

    def promotion(self, color):
        figures = []
        figures.append(PromotionButton(color + "N"))
        figures.append(PromotionButton(color + "B"))
        figures.append(PromotionButton(color + "R"))
        figures.append(PromotionButton(color + "Q"))

        prom_dialog = QDialog()
        prom_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog);
        prom_dialog.move(self.mapToGlobal(self.pos()) - QPoint(-53 * 3, -52 * 3)) #fix constants

        for num, figure in enumerate(figures):
            figure.clicked.connect(self.make_answer_button(num + 2, prom_dialog))
        prom_dialog.setWindowTitle("Choose figure:")
        
        layout = QGridLayout(prom_dialog)
        for i, figure in enumerate(figures):
            layout.addWidget(figure, i % 2, i // 2)


        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        prom_dialog.setLayout(layout)

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
            self.history += 1
            self.make_turn(turn.start_pos, turn.end_pos)
            if turn.castling:
                self.make_castling(*turn.end_pos)
        else:
            self.reached_hist_bottom = False

    def prev_move(self):
        turn = self.api.previous_turn()
        if turn:
            self.history -= 1
            if turn[0].castling:
                self.make_castling(*turn[0].end_pos, True)
            self.make_turn(turn[0].end_pos, turn[0].start_pos)
        else:
            self.reached_hist_bottom = True

    def skip_history(self):
        while(self.history < 0):
            self.next_move()
        self.reached_hist_bottom = False
    
    def to_start(self):
        while(not self.reached_hist_bottom):
            self.prev_move()
      
    def make_castling(self, x, y, reverse=False):
        short_rook_st = 7
        short_rook_fn = 5
        long_rook_st = 0
        long_rook_fn = 3
        if reverse:
            swap(short_rook_fn, short_rook_st)
            swap(long_rook_fn, long_rook_st)
        if y == 2:
            #long castling
            rook_color = self.cells_arr[x][long_rook_st].figure.figure_type
            self.cells_arr[x][long_rook_st].figure.set_type(0)
            self.cells_arr[x][long_rook_fn].figure.set_type(rook_color)
        else:
            #short castling
            rook_color = self.cells_arr[x][short_rook_st].figure.figure_type
            print(rook_color)
            self.cells_arr[x][short_rook_st].figure.set_type(0)
            self.cells_arr[x][short_rook_fn].figure.set_type(rook_color)
    
    def resizeEvent(self, event):
        new_size = max(event.size().height(), event.size().width())
        self.resize(new_size, new_size)

class BottomMenu(QFrame):
    def __init__(self, comm):
        super().__init__()
        self.comm = comm
        buttons = []
        buttons.append(ControllButton("Back"))
        buttons.append(ControllButton("Undo"))
        buttons.append(ControllButton("Redo"))
        buttons.append(ControllButton("Skip"))
        
        back_button = MenuButton("Back")

        buttons[0].clicked.connect(self.to_game_start)
        buttons[1].clicked.connect(self.previous)
        buttons[2].clicked.connect(self.next)
        buttons[3].clicked.connect(self.skip_hist)
        back_button.clicked.connect(self.back)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(back_button)
        for but in buttons:
            h_layout.addWidget(but)
        h_layout.addStretch(1)
        h_layout.setSpacing(20)
        h_layout.setContentsMargins(10, 0, 10, 0)
        self.setLayout(h_layout)
        
    def previous(self):
        self.comm.prevMove.emit()
    
    def to_game_start(self):
        self.comm.toStart.emit()

    def next(self):
        self.comm.nextMove.emit()
    
    def skip_hist(self):
        self.comm.skipHist.emit()
    
    def back(self):
        self.comm.backMenu.emit()
    

class MainMenu(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(board_size, board_size)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setSizePolicy(sizePol)

        self.start_game = MenuButton("Start Game")
        self.difficulties = [MenuButton(str(i)) for i in range(1, 5)]
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

class MainGame(QFrame):
    def __init__(self, api, comm):
        super().__init__()
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)

        self.board = GuiBoard(api, comm)
        self.board.upd_possible_moves(self.board.color)
        v_layout.addWidget(self.board)
        self.bottom_menu = BottomMenu(comm)
        v_layout.addWidget(self.bottom_menu)

        h_layout = QHBoxLayout()
        h_layout.addLayout(v_layout)
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(h_layout)

class Border(QFrame):
    def __init__(self, name, width, height):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setObjectName(name)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

class MenuButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)

class PromotionButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)
        self.setObjectName(args[0])
        self.setText("")

class ControllButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)
        self.setObjectName(args[0])
        self.setText("")


class Main_Window(QWidget):
    
    def __init__(self, api):
        super().__init__()
        self.setMinimumSize(board_size, board_size + 50)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setSizePolicy(sizePol)
        self.api = api
        self.comm = Communicate()

        self.comm.backMenu.connect(self.return_to_menu)

        
        self.game = MainGame(api, self.comm)
        self.menu = MainMenu()

        self.tabs = QStackedLayout()
        self.tabs.addWidget(self.menu)
        self.tabs.addWidget(self.game)

        self.tab_names = {"start":0, "game_board":1}
        self.tabs.setCurrentIndex(self.tab_names["start"])

        self.tabs.setSpacing(self.tab_names["start"])
        self.tabs.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.tabs)

        for diff, difficulty in enumerate(self.menu.difficulties):
            difficulty.clicked.connect(self.start_game_with_difficulty(diff + 1))

        self.setWindowTitle('Chess')
        self.show()
    
    def resizeEvent(self, event):
        new_size = min(event.size().height(), event.size().width())
        self.resize(new_size, new_size + 50)

    def return_to_menu(self):
        self.tabs.setCurrentIndex(self.tab_names["start"])

    def start_game_with_difficulty(self, difficulty):
        def start_game():
            self.api.difficulty = difficulty + 1
            self.tabs.setCurrentIndex(self.tab_names["game_board"])
        return start_game
  
    


