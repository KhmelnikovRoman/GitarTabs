import sys
import threading
from OpenGL import GL as gl
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QPainter, QFont
from stopwatch import Stopwatch
from find_note import FindNote

#класс отображении графики
class OpenGLWidget(QOpenGLWidget):
    def initializeGL(self):
        gl.glClearColor(1, 1, 1, 1)
        gl.glColor3f(0,0,0)
        gl.glBegin(gl.GL_LINES)
        for i in range(6):
            gl.glVertex2f(-1.0, -0.5 + i * 0.2)
            gl.glVertex2f(1.0, -0.5 + i * 0.2)
        gl.glEnd()
        self.note = -1
        self.string = -1
        self.step_note = 0

    def draw_note(self):
        painter = QPainter(self)
        painter.setPen(Qt.black)
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)
        if (self.note != -1 and self.string != -1):
            painter.drawText(20 + self.step_note, 30 + self.string * 20 + 2 * painter.fontMetrics().descent(), str(self.note))
        painter.end()

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.initializeGL()
        self.draw_note()


class Ui_MainWindow(QtWidgets.QWidget):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 500)
        MainWindow.setMinimumSize(QtCore.QSize(900, 500))
        MainWindow.setMaximumSize(QtCore.QSize(900, 500))
        MainWindow.setStyleSheet("background-color: rgb(51, 51, 51);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.save = QtWidgets.QPushButton(self.centralwidget)
        self.save.setGeometry(QtCore.QRect(20, 30, 111, 31))
        self.save.setStyleSheet(
            "color: rgb(177, 182, 180);\n"
            "border-color: rgb(47, 47, 47);\n"
            "")
        self.save.setObjectName("save")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 370, 461, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lcdNumber = QtWidgets.QLCDNumber(self.horizontalLayoutWidget)
        self.lcdNumber.setObjectName("lcdNumber")

        self.horizontalLayout.addWidget(self.lcdNumber)
        self.bpm = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.bpm.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.bpm.setStyleSheet(
            "font: 16pt \"MS Shell Dlg 2\";\n"
            "color: rgb(177, 182, 180);\n"
            "border: solid 5px;\n"
            "border-color: rgb(47, 47, 47);\n"
            ""
        )
        self.bpm.setAlignment(QtCore.Qt.AlignCenter)
        self.bpm.setObjectName("bpm")
        self.horizontalLayout.addWidget(self.bpm)
        self.bpm_count = QtWidgets.QSpinBox(self.horizontalLayoutWidget)
        self.bpm_count.setStyleSheet(
            "font: 16pt \"MS Shell Dlg 2\";\n"
            "color: rgb(177, 182, 180);")
        self.bpm_count.setMaximum(300)
        self.bpm_count.setProperty("value", 120)
        self.bpm_count.setObjectName("bpm_count")
        self.horizontalLayout.addWidget(self.bpm_count)
        self.metronom = QtWidgets.QPushButton(self.centralwidget)
        self.metronom.setGeometry(QtCore.QRect(140, 30, 101, 31))
        self.metronom.setStyleSheet(
            "color: rgb(177, 182, 180);\n"
            "border-color: rgb(47, 47, 47);")
        self.metronom.setObjectName("metronom")
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(20, 330, 75, 23))
        self.start.setStyleSheet(
            "color: rgb(177, 182, 180);\n"
            "border-color: rgb(47, 47, 47);\n"
            "")
        self.start.setObjectName("start")
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setGeometry(QtCore.QRect(110, 330, 75, 23))
        self.stop.setStyleSheet(
            "color: rgb(177, 182, 180);\n"
            "border-color: rgb(47, 47, 47);\n"
            "")
        self.stop.setObjectName("stop")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.slider = QtWidgets.QSlider(self.centralwidget)
        self.slider.setGeometry(QtCore.QRect(20, 290, 741, 22))
        self.slider.setObjectName("slider")
        self.slider.setOrientation(QtCore.Qt.Horizontal)

        #запуск секундомера и поиска ноты
        self.stopwatch = Stopwatch()
        self.fn = FindNote()
        self.start.clicked.connect(self.clickStart)
        self.stop.clicked.connect(self.clickStop)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.displayLCD)
        self.lcdNumber.setDigitCount(9)
        self.retranslateUi(MainWindow)

        self.openGL = OpenGLWidget(self.centralwidget)
        self.openGL.setGeometry(QtCore.QRect(20, 80, 741, 200))
        self.openGL.setStyleSheet("border-radius: 50px;")
        self.openGL.setObjectName("openGLWidget")
        self.openGL.show()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "EasyTabs"))
        self.save.setText(_translate("MainWindow", "Сохранить"))
        self.bpm.setText(_translate("MainWindow", "Bpm"))
        self.metronom.setText(_translate("MainWindow", "Метроном"))
        self.start.setText(_translate("MainWindow", "Старт"))
        self.stop.setText(_translate("MainWindow", "Стоп"))

    def clickStart(self):
        self.timer.start()
        self.stopwatch.start()
        self.fn.is_listening = True
        self.listening_thread = threading.Thread(target=self.fn.start_listening)
        self.listening_thread.start()


    def clickStop(self):
        self.timer.stop()
        self.stopwatch.stop()
        self.stopwatch.reset()
        self.lcdNumber.display("00:00:000")
        self.fn.is_listening = False
        if self.listening_thread.is_alive():
            self.listening_thread.join()
        print("Found notes:", self.fn.found_notes)
        self.fn.found_notes = []
        self.fn.num_note = 0

    def displayLCD(self):
        self.lcdNumber.display(self.stopwatch.get_time())
        if self.fn.note_for_render != '':
            buffer = self.fn.note_for_render.split(' ')
            sNote = buffer[0]
            sOctave = int(buffer[1])
            #print(sNote, sOctave , self.fn.step_note)
            self.openGL.note, self.openGL.string = self.fn.calculate_fret(sNote, sOctave)
            self.openGL.step_note = self.fn.step_note
            print('note: ', self.openGL.note, ' string: ', self.openGL.string, ' step: ', self.openGL.step_note)
            self.openGL.draw_note()




def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

