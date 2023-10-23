from PySide6 import QtWidgets
from PySide6.QtGui import QMouseEvent
from base_ui import Ui_MainWindow
from PySide6.QtCore import Qt, Signal, QObject, QRunnable, QTimer
import sys
import time

from PySide6.QtWebEngineCore import QWebEnginePage
from estimator import Estimator


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
        #print(f'Длина исходного листа {len(self._data)}')
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

        # Начальная позиция (координаты Nobius)
        self.__currentPos = {'Point': 'Current Position', 'Latitude': 59.818080, 'Longitude': 30.328469}

        # Конфигурирование вебвью виджета
        self.view = self.ui.webEngineView
        self.page = WebEnginePage()

        self.view.setPage(self.page)
        self.view.setHtml(open("index.html").read())

        # Получение координат точек каждые 1000мс
        self.timer = QTimer()
        self.timer.timeout.connect(self.getPoints)
        self.timer.start(1000)

        # Отображения карты
        self.view.show()

        # Действия по нажатию кнопок
        self.ui.btn_delete_points.clicked.connect(self.deletePoints)
        self.ui.btn_get_points.clicked.connect(self.getPoints)

        # Работа с таблицей
        self.ui.table_points.setColumnCount(4)
        self.ui.table_points.resizeColumnsToContents()
        self.ui.table_points.setColumnWidth(0, 200)
        self.ui.table_points.setColumnWidth(1, 200)
        self.ui.table_points.setColumnWidth(2, 100)
        self.ui.table_points.setColumnWidth(3, 100)

        column_name = ['Lat', 'Long', 'Dist', 'AZ']
        self.ui.table_points.setHorizontalHeaderLabels(column_name)

        # Создание объекта расчeтчика расстояния и азимута
        self.estimator = Estimator()


    def getPoints(self):

        try:

            if len(self.page) == 0:
                self.ui.table_points.setRowCount(0)
                pass

            else:
                self.ui.table_points.setRowCount(len(self.page))

                for idx, point in enumerate(self.page):

                    if idx == 0:
                        distance = self.estimator.haversine(start_point=self.__currentPos,
                                                            end_point=point)
                        azimut = self.estimator.initial_bearing(start_point=self.__currentPos,
                                                                end_point=point)
                    else:
                        distance = self.estimator.haversine(start_point=self.page[idx-1],
                                                            end_point=point)
                        azimut = self.estimator.initial_bearing(start_point=self.page[idx-1],
                                                                end_point=point)
                        
                    self.__pasteValueInTable(idx, point['Latitude'], point['Longitude'], distance, azimut)

        except ValueError as e:
            print(e)


    def deletePoints(self):
        self.view.reload()
        self.page.removePoints()


    def __pasteValueInTable(self, *args):
        for idx, arg in enumerate(args):
            if 0 < idx <= 2:
                self.ui.table_points.setItem(args[0], idx-1, QtWidgets.QTableWidgetItem(f'{arg:.4f}'))
            elif idx > 2:
                self.ui.table_points.setItem(args[0], idx-1, QtWidgets.QTableWidgetItem(f'{arg:.2f}'))
             

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = Base()
    window.mouseMoveEvent = window.mouseMoveEvent
    window.show()
    sys.exit(app.exec())
