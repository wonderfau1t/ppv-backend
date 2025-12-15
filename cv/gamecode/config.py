"""
Конфигурационные параметры и константы
"""
import numpy as np

# ID классов YOLO (настройте под вашу модель)
BALL_CLASS_ID = 2
RACKET_CLASS_ID = 1
PLAYER_CLASS_ID = 3

# Размеры стола (вид сверху)
TABLE_WIDTH = 1000
TABLE_HEIGHT = 500

# Пороговые значения
NET_CROSSING_MARGIN = 20
BOUNCE_PROXIMITY = 30
MIN_BOUNCE_SPEED = 10
GAME_START_SPEED_THRESHOLD = 50
MAX_BALL_HISTORY = 60
MAX_SPEED_HISTORY = 10

# Цвета BGR
COLORS = {
    'ball': (0, 0, 255),
    'racket': (255, 100, 0),
    'player': (255, 255, 0),
    'table': (50, 150, 50),
    'net': (0, 255, 255),
    'trajectory': (0, 200, 255),
    'text': (255, 255, 255),
    'score': (255, 255, 0),
    'player1': (0, 255, 0),
    'player2': (0, 0, 255),
    'racket1': (150, 255, 0),
    'racket2': (0, 150, 255)
}

# Настройки модели YOLO
YOLO_CONFIG = {
    'model_path': 'runs/content/runs/detect/train/weights/best.pt',
    'conf_threshold': 0.25,
    'iou_threshold': 0.5,
    'tracker': "bytetrack.yaml"
}

# Параметры гомографии (заполняются при калибровке)
HOMOGRAPHY_CONFIG = {
    'src_points': np.array([
        [776, 400],  # верхний левый угол стола
        [1192, 424],  # верхний правый угол стола
        [1292, 960],  # нижний правый угол стола
        [537, 904]
    ], dtype=np.float32),
    'dst_points': np.array([
        [0, 0],
        [TABLE_WIDTH, 0],
        [TABLE_WIDTH, TABLE_HEIGHT],
        [0, TABLE_HEIGHT]
    ], dtype=np.float32),
    'matrix': None  # Заполнится после вычисления
}

# Настройки игры
GAME_RULES = {
    'winning_score': 11,
    'min_lead': 2,
    'serves_per_turn': 2
}

def update_homography(src_points):
    """Обновление матрицы гомографии"""
    from gamecode.utils import calculate_homography
    HOMOGRAPHY_CONFIG['src_points'] = np.array(src_points, dtype=np.float32)
    HOMOGRAPHY_CONFIG['matrix'], _ = calculate_homography(
        HOMOGRAPHY_CONFIG['src_points'],
        HOMOGRAPHY_CONFIG['dst_points']
    )
    return HOMOGRAPHY_CONFIG['matrix']