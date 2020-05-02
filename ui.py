import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, 
    QHBoxLayout, QVBoxLayout, QApplication)
from PyQt5 import QtGui

QPushButton# { background-color: red }

class Main_Window(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        self.setGeometry(0, 0, 740, 740)
        new_game = QPushButton("Start Game")
        new_game.setStyleSheet("evilButton");
        # QPushButton#evilButton { background-color: red }
        quit = QPushButton("Quit")
        # Pixmap
        image = QtGui.QPixmap()
        image.load('images/board.jpg')
        image = image.scaled(self.width(), self.height())

        # Palette
        palette = QtGui.QPalette()
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(image))
        self.setPalette(palette)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(new_game)
        vbox.addWidget(quit)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)    
        
        
        self.setWindowTitle('Chess')    
        self.show()
