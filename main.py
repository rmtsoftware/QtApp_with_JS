from PySide6 import QtWidgets
from PySide6.QtGui import QMouseEvent
from base_ui import Ui_MainWindow
from PySide6.QtCore import Qt, Signal, QObject, QRunnable
import sys
import time

from PySide6.QtWebEngineCore import QWebEnginePage


class WebEnginePage(QWebEnginePage):
    """
    Наследование от PySide6.QtWebEngineWidgets.QWebEngineView
    -> Добавление публичного атрибута - data: List
    -> Возможность получить координаты выставленных точек
    """
    
    _data = []

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID) -> None:
        self._data.append(message)
        return super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)
    
    #def __str__(self):
    #    return 'hello from page'
    
    def __getitem__(self, i: int): 
        try:
            item = self.__parse_raw_data(i)
        except IndexError as _:
            item = None
        return item
    
    def __len__(self):
        return len(self._data) - 1
    
    def __iter__(self):
        for i in range(len(self._data)-1):
            item = self.__parse_raw_data(i)
            yield item

    def __parse_raw_data(self, key):
        raw_str = self._data[key+1].split(' ')[1:]
        coord = [float(el) for el in raw_str[0].split(',')]
        item = {'Point': key, 'Latitude': coord[1], 'Longitude': coord[0]}
        return item
    
    def removePoints(self):
        self._data = []


    
class Base(QtWidgets.QMainWindow):

    def __init__(self):
        super(Base, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Конфигурирование вебвью виджета
        self.view = self.ui.webEngineView
        self.page = WebEnginePage()

        self.view.setPage(self.page)
        self.view.setHtml(open("index.html").read())

        self.view.focusProxy().installEventFilter(self)

        self.view.show()


        # Действия по нажатию кнопок
        self.ui.btn_delete_points.clicked.connect(self.deletePoints)
        self.ui.btn_get_points.clicked.connect(self.getPoints)


        # Работа с таблицей
        self.ui.table_points.setColumnCount(4)
        self.ui.table_points.resizeColumnsToContents()

        column_name = ['Lat', 'Long', 'Dist', 'AZ']
        self.ui.table_points.setHorizontalHeaderLabels(column_name)

    def eventFilter(self, obj, event):
        if obj is self.view.focusProxy() and event.type() == event.Type.MouseButtonRelease:
            self.getPoints()
        return super(Base, self).eventFilter(obj, event)


    def getPoints(self):
        if len(self.page) == 0:
            print('Нет выставленных точек')
        else:
            self.ui.table_points.setRowCount(len(self.page))
            for idx, point in enumerate(self.page):
                self.ui.table_points.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(point['Latitude'])))
                self.ui.table_points.setItem(idx, 1, QtWidgets.QTableWidgetItem(str(point['Longitude'])))


    def deletePoints(self):
        self.view.reload()
        self.page.removePoints()
        self.getPoints()
    

    
    #def mousePressEvent(self, event: QMouseEvent) -> None:
#
    #    pos = event.globalPos()
    #    print(pos)
#
    #    """обрабатываем нажатия мыши"""
    #    if event.button() == Qt.LeftButton:
    #        print('i m here')



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = Base()
    window.mouseMoveEvent = window.mouseMoveEvent
    window.show()
    sys.exit(app.exec())
