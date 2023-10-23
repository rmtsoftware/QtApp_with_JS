import math

class Estimator:

    def __init__(self):
        self.__R = 6371.0 # Радиус Земли в километрах


    def __deg2rad(self, point: dict) -> (float, float):
        """
            Преобразование грудусов в радианы\n
            Возвращает: широта[rad]: float , долгота[rad]: float
        """
        return math.radians(point['Latitude']), math.radians(point['Longitude'])


    def haversine(self, start_point: dict, end_point: dict) -> float:
        """
            Вычисление расстояния между двумя точками в градусах
        """

        # Переводим градусы в радианы
        lat1 , lon1 = self.__deg2rad(start_point)
        lat2, lon2 = self.__deg2rad(end_point)
        
        # Разница между широтами и долготами
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Вычисление расстояния с использованием формулы Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = self.__R * c  # Расстояние в километрах
        
        return distance
    

    def initial_bearing(self, start_point: dict, end_point: dict) -> float:
        """
            # Функция для вычисления начального азимута между двумя точками
        """

         # Переводим градусы в радианы
        lat1 , lon1 = self.__deg2rad(start_point)
        lat2, lon2 = self.__deg2rad(end_point)

        # Разница долгот
        dlon = lon2 - lon1
        
        # Формула для вычисления начального азимута
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        initial_bearing = math.atan2(y, x)
        
        # Переводим радианы в градусы
        initial_bearing = math.degrees(initial_bearing)
        
        # Нормализуем азимут в диапазон от 0 до 360 градусов
        initial_bearing = (initial_bearing + 360) % 360
        
        return initial_bearing
    

if __name__ == "__main__":

    lat1 = 59.818124      # Широта первой точки
    lon1 = 30.327906      # Долгота первой точки
    lat2 = 59.818124      # Широта второй точки
    lon2 = 30.327905      # Долгота второй точки
    
    p1 = {'Latitude': lat1, 'Longitude': lon1}
    p2 = {'Latitude': lat2, 'Longitude': lon2}

    myEst = Estimator()
    print('Расстояние между точками: ', end='')
    print(myEst.haversine(start_point=p1, 
                          end_point=p2))
    
    print('Начальный азимут: ', end='')
    print(myEst.initial_bearing(start_point=p1, 
                                end_point=p2))

