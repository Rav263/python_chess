import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
    QHBoxLayout, QVBoxLayout, QStackedLayout, QApplication, QGridLayout, QFrame, QSizePolicy, QDialog, 
    QLabel, QProgressBar)
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QObject, QMimeData, Qt, QPoint
from PyQt5.QtGui import QDrag, QPixmap
import time
import threading

board_size = 416

lock = threading.Lock()

def swap(a, b):
    a, b = b, a

class Gui():
    def __init__(self, api):
        qss_file = open('styles.qss').read()
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(qss_file)
        self.main_window = Main_Window(api)
    
    def start(self):
        """Starts UI
        """
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
    Situation = pyqtSignal(float)


class Figure(QFrame):
    fig_translation = {1:"P", 2:"N", 3:"B", 4:"R", 5:"K", 6:"Q"}
    
    def __init__(self, figure_type, comm):
        super().__init__()
        self.comm = comm
        self.set_type(figure_type)

    def set_type(self, figure_type):
        """Updates figure's type

        :param figure_type: new type
        :type figure_type: int
        """
        self.figure_type = figure_type
        self.setProperty("type", str(figure_type))
        self.setStyle(self.style())

    def get_color(self):
        """Converts figure color to text

        :return: "w" or "b" depending on figure color
        :rtype: str
        """
        return "w" if self.figure_type // 10 == 1 else "b"

    def get_type(self):
        """Returns numeric type

        :return: Returns numeric type
        :rtype: int
        """
        return self.figure_type

    def get_named_type(self):
        """Converts numeric type to text

        :return: "P", "N", "B", "R", "K" or "Q"  depending on figure type
        :rtype: str
        """
        if self.figure_type % 10 in self.fig_translation:
            return self.fig_translation[self.figure_type % 10]
        else:
            return 0

    def get_figure_name(self):
        """Converts full numeric type to text

        :return: "w" or "b" + "P", "N", "B", "R", "K" or "Q"  depending on figure type
        :rtype: str
        """
        return self.get_color() + self.get_named_type()

class TakenFigure(Figure):
    def __init__(self, figure_type, comm):
        super().__init__(figure_type, comm)
        self.comm = comm
        self.set_type(figure_type)
        self.setMinimumSize(board_size // 17, board_size // 17)
    
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
        self.setProperty("type", "")
        self.check_move = check_move
        self.pressed = 0
        self.color = color
        self.set_color(color)
        vbox = QVBoxLayout()
        vbox.addWidget(self.figure)
        self.setLayout(vbox)
        vbox.setContentsMargins(4, 4, 4, 4)

    def set_color(self, color):
        self.color = color
        if self.x == 7 or self.y == 0:
            text_color = "{}{}{}".format(color, self.x, self.y)
        else:
            text_color = "white" if color == 1 else "black"
        self.setProperty("color", text_color)
        self.setStyle(self.style())

    def set_type(self, cell_type):
        """Updates cell's type

        :param cell_type: new type
        :type cell_type: int
        """
        self.setProperty("type", str(cell_type))
        self.setStyle(self.style())

    def mousePressEvent(self, event):
        """Process cell press event

        :param event: press event
        :type event: QEvent
        """
        self.comm.cellPressed.emit(self.x, self.y)

    def mouseReleaseEvent(self, event):
        """Process cell release event

        :param event: release event
        :type event: QEvent
        """
        self.comm.cellReleased.emit(self.x, self.y)

    def press(self):
        """Set cell style when cell is pressed
        """
        self.setProperty("pressed", "yes")
        self.setStyle(self.style())

    def beat(self):
        """Set cell style when figure in cell may be beaten
        """
        self.setProperty("pressed", "beat")
        self.setStyle(self.style())

    def release(self):
        """Set cell style to normal state
        """
        self.setProperty("pressed", "no")
        self.setStyle(self.style())

class GuiBoard(QFrame):
    updBoard = pyqtSignal()
    def __init__(self, api, comm, start_color, taken):
        super().__init__()
        self.game_human = False
        self.change_human = False
        self.taken = taken
        self.history = 0
        self.reached_hist_bottom = False
        self.color = start_color
        self.api = api
        self.white = self.api.board.white
        self.black = self.api.board.black
        self.setMinimumSize(board_size, board_size)
        self.resize(board_size, board_size)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setSizePolicy(sizePol)
        self.game_over = False

        self.comm = comm
        self.comm.cellPressed.connect(self.cell_pressed)
        self.comm.cellReleased.connect(self.cell_released)
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
        
        self.after_st = (0, 0)
        self.after_fn = (0, 0)

        self.cells_arr = [list() for i  in range(8)]
        cell_color = self.color
        for x in range(8):
            for y in range(8):
                self.cells_arr[x].append(Cell(x, y, self.api.get_field((x, y)), self.comm, cell_color, self.check_move))
                cells.addWidget(self.cells_arr[x][y], x, y)
                cell_color = 3 - cell_color
            cell_color = 3 - cell_color
        self.setLayout(cells)


    def flip_board(self):
        self.clear_afterturn()
        self.after_st = (7 - self.after_st[0], 7 - self.after_st[1])
        self.after_fn = (7 - self.after_fn[0], 7 - self.after_fn[1])
        self.cells_arr[self.after_st[0]][self.after_st[1]].set_type("moved")
        self.cells_arr[self.after_fn[0]][self.after_fn[1]].set_type("moved")
        self.api.flip_board()
        self.upd_whole_board()

    def cell_released(self, x, y):
        """Alows II to make a move

        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        """
        if self.ai_do_turn:
            self.pass_turn()
            self.ai_do_turn = False

        if self.change_human:
            self.pass_turn()
            self.change_human = False

    def cell_pressed(self, x, y):
        """Processes event when user presses a field

        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        """
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
                self.process_move(x, y)
    
    def process_move(self, x, y):
        """Processes a piece move, and displays it on the board

        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        """
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
                self.make_turn(self.start, (x, y), True)
            else:    
                self.make_turn(self.start, (x, y), self.api.do_turn(self.start, (x, y)))
            self.change_color()
            if self.game_human:
                self.change_human = True
            else:
                self.ai_do_turn = True

    def make_turn(self, start, stop, upd_all = False):
        """Display move on the board

        :param start: start position
        :type start: (int, int)
        :param stop: stop position
        :type stop: (int, int)
        """
        if (start[0] == -1 and not self.history):
            self.mate(False)
            return

        if upd_all:
            self.upd_whole_board()
        else:
            self.cells_arr[start[0]][start[1]].figure.set_type(0)
            self.cells_arr[stop[0]][stop[1]].figure.set_type(self.api.get_field(stop))
        
        self.clear_afterturn()
        self.cells_arr[start[0]][start[1]].set_type("moved")
        self.cells_arr[stop[0]][stop[1]].set_type("moved")
        self.after_st = start
        self.after_fn = stop

        white, black, score_w, score_b = self.api.get_taken_figures()
        if self.taken[0].color == self.white:
            self.taken[1].update_taken_fig(white, score_w)
            self.taken[0].update_taken_fig(black, score_b)
        else:
            self.taken[0].update_taken_fig(white, score_w)
            self.taken[1].update_taken_fig(black, score_b)
        
        self.comm.Situation.emit(self.api.get_board_eval())

    def clear_afterturn(self):
        self.cells_arr[self.after_st[0]][self.after_st[1]].set_type("")
        self.cells_arr[self.after_fn[0]][self.after_fn[1]].set_type("")

    def check_move(self, x, y):
        """Checks if a move is correct

        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :return: returns true if user can make such a move
        :rtype: bool
        """
        return True if not self.history and (x, y) in self.possible_moves[self.start] else False

    def promotion(self, color):
        """Promotes a pawn

        :param color: pawn color
        :type color: int(1,2)
        :return: [description]
        :rtype: int
        """
        figures = []
        figures.append(PromotionButton(color + "N", self.get_size()))
        figures.append(PromotionButton(color + "B", self.get_size()))
        figures.append(PromotionButton(color + "R", self.get_size()))
        figures.append(PromotionButton(color + "Q", self.get_size()))

        prom_dialog = QDialog()
        prom_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        curr_board = self.size().height() // 2 - figures[0].size().height()
        prom_dialog.move(self.mapToGlobal(QPoint(0, 0)) + QPoint(curr_board, curr_board)) #fix constants

        for num, figure in enumerate(figures):
            figure.clicked.connect(self.make_answer_button(num + 2, prom_dialog))
        prom_dialog.setWindowTitle("Choose figure:")
        
        layout = QGridLayout(prom_dialog)
        for i, figure in enumerate(figures):
            layout.addWidget(figure, i % 2, i // 2)


        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        prom_dialog.setLayout(layout)

        choice = prom_dialog.exec_()
        return choice if choice in (2, 3, 4) else 6

    def make_answer_button(self, figure, dialog):
        """Makes a funnction processing a promotion reply

        :param figure: chosen figure
        :type figure: int
        :param dialog: promotion dialog
        :type dialog: QDialog
        """
        def answer():
            dialog.done(figure)
        return answer

    def pass_turn(self):
        """Updates board after AI turn
        """
        if self.game_human:
            self.flip_board()
        else:
            turn, upd_whole = self.api.ai_turn(self.color)
            self.make_turn(turn.start_pos, turn.end_pos, upd_whole)
            self.change_color()
        self.upd_possible_moves(self.color)
    
    def upd_whole_board(self):
        for x in range(8):
            self.cells_arr[x][0].set_color(self.color)
        for y in range(8):
            self.cells_arr[7][y].set_color(self.color)

        for x in range(8):
            for y in range(8):
                self.cells_arr[x][y].figure.set_type(self.api.get_field((x, y)))
    
    def upd_possible_moves(self, color):
        """Gets all possible turns of a specific color from API

        :param color: color of a side making a turn
        :type color: int(1,2)
        """
        self.possible_moves = self.api.get_possible_turns(color)
        if not self.possible_moves:
            self.mate(True)
        
    def mate(self, user_lost):
        
        pate = self.api.check_check(self.color)
        finish = QDialog()
        finish.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        finish.resize(3 * 52, 3 * 52)
        
        ok_button = MenuButton("OK")
        ok_button.clicked.connect(finish.accept)
        
        result_str = "Game over! \n"
        if pate:
            result_str += "It is a draw."
        elif user_lost:
            result_str += "You lost."
        else:
            result_str += "You won!"
        result = QLabel(result_str)
        result.setAlignment(Qt.AlignCenter)

        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addStretch()
        v_layout.addWidget(result)
        v_layout.addStretch()
        v_layout.addWidget(ok_button)
        v_layout.addStretch()

        h_layout = QHBoxLayout(finish)
        h_layout.addStretch()
        h_layout.addLayout(v_layout)
        h_layout.addStretch()
        finish.setLayout(h_layout)
        pos_x = self.size().height() // 2 - finish.size().width() // 2 - 0
        pos_y = self.size().height() // 2 - finish.size().height() // 2 
        finish.move(self.mapToGlobal(QPoint(pos_x, pos_y)))
        res = finish.exec_()
        self.game_over = True

            
    def change_color(self):
        """Changes sides
        """
        self.color = 3 - self.color

    def next_move(self):
        """Applies redo option in history
        """
        turn = self.api.next_turn()
        if turn:
            self.history += 1
            self.make_turn(turn.start_pos, turn.end_pos, True)
        else:
            self.reached_hist_bottom = False

    def prev_move(self):
        """Applies undo option in history
        """
        turn = self.api.previous_turn()
        if turn:
            self.history -= 1
            self.make_turn(turn[0].end_pos, turn[0].start_pos, True)
        else:
            self.reached_hist_bottom = True

    def skip_history(self):
        """Applies redo in history until current situation
        """
        while(self.history < 0):
            self.next_move()
        self.reached_hist_bottom = False
    
    def to_start(self):
        """Applies undo in history till the beginning of a game
        """
        while(not self.reached_hist_bottom):
            self.prev_move()
      
    def resizeEvent(self, event):
        """Process resize event

        :param event: new size of a vindow
        :type event: QEvent
        """
        new_size = min(event.size().height(), event.size().width())
        self.resize(new_size, new_size)
    
    def get_size(self):
        return self.size().width()

class BottomMenu(QFrame):
    def __init__(self, comm):
        super().__init__()
        self.comm = comm
        buttons = []
        buttons.append(ControllButton("Back"))
        buttons.append(ControllButton("Undo"))
        buttons.append(ControllButton("Redo"))
        buttons.append(ControllButton("Skip"))
        
        back_button = MenuButton(_("Back"))

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
        """Tells board to make undo in history
        """
        self.comm.prevMove.emit()
    
    def to_game_start(self):
        """Tells board to make move history to the beggining of the game
        """
        self.comm.toStart.emit()

    def next(self):
        """Tells board to make redo in history
        """
        self.comm.nextMove.emit()
    
    def skip_hist(self):
        """Tells board to make move history to the current position in the game
        """
        self.comm.skipHist.emit()
    
    def back(self):
        """Tells main window to open start menu tab
        """
        self.comm.backMenu.emit()
    
class TakenFigures(QFrame):
    possible_figures = [6, 4, 4, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    translate = {"Q":6, "R":4, "B":3, "N":2, "P":1}
    def __init__(self, comm, color, board_size):
        super().__init__()
        self.setMinimumHeight(board_size // 17)
        self.comm = comm
        self.color = color
        self.figures = []
        for fig in self.possible_figures:
            self.figures.append(TakenFigure(color * 10 + fig, comm))
        self.score = QLabel("")
        h_layout = QHBoxLayout()
        for fig in self.figures:
            h_layout.addWidget(fig)
            fig.hide()
        h_layout.addWidget(self.score)
        h_layout.addStretch(1)
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(h_layout)
    
    def update_taken_fig(self, figures, score):
        for fig in self.figures:
            fig_n = fig.get_type() % 10
            if (fig_n in figures and figures[fig_n]):
                fig.show()
                figures[fig_n] -= 1
            else:
                fig.hide()
        if score:
            self.score.setText("+{}".format(score))
        else:
            self.score.setText("")
    
    def set_color(self, color):
        if color != self.color:
            self.color = color
            for fig in self.figures:
                fig.set_type(color * 10 + fig.get_type() % 10)
        
    def hide_all(self):
        for fig in self.figures:
            fig.hide()
        self.score.setText("")

class MainMenu(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(board_size, board_size)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setSizePolicy(sizePol)

        self.start_game = MenuButton(_("New game"))
        self.resume = MenuButton(_("Resume"))
        self.computer = MenuButton(_("Computer"))
        self.human = MenuButton(_("Human"))

        self.computer.hide()
        self.human.hide()
        
        self.resume.hide()
        self.difficulties = [MenuButton(str(i)) for i in range(1, 5)]
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.start_game)
        vbox.addWidget(self.resume)
        vbox.addWidget(self.computer)
        vbox.addWidget(self.human)
        for difficulty in self.difficulties:
            vbox.addWidget(difficulty)
            difficulty.hide()

        h_col_lay = QHBoxLayout()
        self.white = MenuButton(_("white"))
        self.white.setProperty("pushed", "yes")
        self.black = MenuButton(_("black"))
        self.black.setProperty("pushed", "no")
        self.white.hide()
        self.black.hide()
        h_col_lay.addWidget(self.white)
        h_col_lay.addWidget(self.black)
        vbox.addLayout(h_col_lay)
        vbox.addStretch(1)


        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)
        self.setLayout(hbox)

        
        self.start_game.clicked.connect(self.choose_mode)

    def choose_mode(self):
        self.start_game.hide()
        self.resume.hide()
        self.computer.show()
        self.human.show()
        
class MainGame(QFrame):
    def __init__(self, api, comm, start_color):
        super().__init__()
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)

        self.comm = comm
        self.comm.Situation.connect(self.upd_progress)
        hbox = QHBoxLayout()

        self.pbar = QProgressBar(self)
        self.up_taken = TakenFigures(comm, start_color, board_size)
        self.down_taken = TakenFigures(comm, 3 - start_color, board_size)
        self.board = GuiBoard(api, comm, start_color, (self.up_taken, self.down_taken))
        self.pbar.setGeometry(0, 0, 40, 52*8)
        self.pbar.setOrientation(Qt.Vertical)
        self.pbar.setValue(50)
        self.pbar.setTextVisible(False)

        hbox.addWidget(self.pbar)
        hbox.addWidget(self.board)

        v_layout.addWidget(self.up_taken)
        v_layout.addLayout(hbox)
        v_layout.addWidget(self.down_taken)
        self.bottom_menu = BottomMenu(comm)
        v_layout.addWidget(self.bottom_menu)

        h_layout = QHBoxLayout()
        h_layout.addLayout(v_layout)
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(h_layout)

    def upd_progress(self, val):
        self.pbar.setValue(val)

class MenuButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)

class PromotionButton(QPushButton):
    def __init__(self, *args):
        super().__init__()
        self.setObjectName(args[0])
        button_size = args[1] // 8
        self.setText("")
        self.setMinimumSize(button_size, button_size)
        self.resize(button_size, button_size)

    def resizeEvent(self, event):
        new_size = min(event.size().height(), event.size().width())
        self.resize(new_size, new_size)

class ControllButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)
        self.setObjectName(args[0])
        self.setText("")


class Main_Window(QWidget):
    def __init__(self, api):
        super().__init__()
        self.resiz = True
        self.setMinimumSize(board_size + 40, board_size + 105)
        sizePol = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePol.setHeightForWidth(True)
        self.setSizePolicy(sizePol)
        self.api = api
        self.start_color = self.api.board.white
        self.comm = Communicate()

        self.comm.backMenu.connect(self.return_to_menu)
        
        self.game = MainGame(api, self.comm, self.start_color)
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

        self.menu.resume.clicked.connect(self.resume_game)
        self.menu.white.clicked.connect(self.white_start)
        self.menu.black.clicked.connect(self.black_start)
        self.menu.human.clicked.connect(self.game_with_human)
        self.menu.computer.clicked.connect(self.choose_difficulty)

        self.setWindowTitle('Chess')
        self.show()

    def choose_difficulty(self):
        """Shows difficulty buttons
        """
        self.menu.computer.hide()
        self.menu.human.hide()
        self.menu.start_game.hide()
        self.menu.resume.hide()
        for difficulty in self.menu.difficulties:
            difficulty.show()
        self.menu.white.show()
        self.menu.black.show()
        if self.start_color == self.api.board.white:
            self.white_start()
        else:
            self.black_start()

    def game_with_human(self):
        self.api.start_new_game()
        self.game.board.game_human = True
        self.start_color = self.api.board.white
        self.start_new_game()

    def resume_game(self):
        self.tabs.setCurrentIndex(self.tab_names["game_board"])
    
    def white_start(self):
        self.start_color = self.api.board.white
        self.menu.white.setProperty("pushed", "yes")
        self.menu.black.setProperty("pushed", "no")
        self.menu.black.setStyle(self.style())
        self.menu.white.setStyle(self.style())

    def black_start(self):
        self.start_color = self.api.board.black
        self.menu.black.setProperty("pushed", "yes")
        self.menu.white.setProperty("pushed", "no")
        self.menu.black.setStyle(self.style())
        self.menu.white.setStyle(self.style())

    def resizeEvent(self, event):
        """Process resize event

        :param event: new size of a vindow
        :type event: QEvent
        """
        if self.resiz:
            self.resiz = False
            new_size = min(event.size().height(), event.size().width())
            self.resize(new_size + 40, new_size + 105)
        
        self.resiz = True

    def return_to_menu(self):
        """Return user to main menu
        """
        for difficulty in self.menu.difficulties:
            difficulty.hide()
        self.menu.black.hide()
        self.menu.white.hide()
        self.menu.computer.hide()
        self.menu.human.hide()
        self.menu.start_game.show()
        if not self.game.board.game_over:
            self.menu.resume.show()
        self.tabs.setCurrentIndex(self.tab_names["start"])

    def start_game_with_difficulty(self, difficulty):
        """Makes functions that start a new game with a specific difficulty

        :param difficulty: difficulty of a game
        :type difficulty: int
        """
        def start_game():
            self.game.board.game_human = False
            self.api.start_new_game(difficulty + 1)
            if self.start_color == self.api.board.black:
                self.game.board.flip_board()
            self.start_new_game()
        return start_game
    
    def start_new_game(self):
        self.game.up_taken.set_color(self.start_color)
        self.game.down_taken.set_color(3 - self.start_color)
        self.game.up_taken.hide_all()
        self.game.down_taken.hide_all()

        self.game.board.color = self.api.board.white
        if self.start_color == self.api.board.black:
            self.game.board.pass_turn()
        else:
            self.game.board.clear_afterturn()

        self.game.board.history = 0
        self.game.board.upd_whole_board()
        self.game.board.upd_possible_moves(self.start_color)
        self.tabs.setCurrentIndex(self.tab_names["game_board"])
