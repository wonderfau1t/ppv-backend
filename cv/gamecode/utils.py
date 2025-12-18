"""
Вспомогательные функции
"""
import cv2
import numpy as np
import json
import os
from datetime import datetime


def calculate_homography(src_points, dst_points):
    """Вычисление матрицы гомографии"""
    return cv2.findHomography(src_points, dst_points)


def project_point(point, H):
    p = np.array([[point]], dtype=np.float32)
    projected = cv2.perspectiveTransform(p, H)[0][0]

    return int(projected[0]), int(projected[1])



def calculate_distance(point1, point2):
    """Расстояние между двумя точками"""
    return np.linalg.norm(np.array(point1) - np.array(point2))


def calculate_speed(pos1, pos2, time1, time2):
    """Расчет скорости между двумя позициями"""
    if time2 <= time1:
        return 0
    distance = calculate_distance(pos1, pos2)
    return distance / (time2 - time1)


def load_calibration(filename='calibration.json'):
    """Загрузка калибровки из файла"""
    if not os.path.exists(filename):
        return None

    with open(filename, 'r') as f:
        data = json.load(f)

    return data


def save_calibration(data, filename='calibration.json'):
    """Сохранение калибровки в файл"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Калибровка сохранена в {filename}")
    return True


def get_timestamp():
    """Получение временной метки"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_table_view(width, height):
    """Создание пустого вида стола сверху"""
    return np.zeros((height, width, 3), dtype=np.uint8)


def draw_table_grid(table_view, width, height, colors):
    """Рисование разметки стола"""
    # Контур стола
    cv2.rectangle(table_view, (0, 0), (width, height), colors['table'], 2)

    # Сетка
    cv2.line(table_view, (width // 2, 0), (width // 2, height), colors['net'], 2)

    # Зоны подачи
    service_line = width // 4
    cv2.line(table_view, (service_line, 0), (service_line, height), (70, 130, 70), 1)
    cv2.line(table_view, (width - service_line, 0), (width - service_line, height), (70, 130, 70), 1)

    return table_view