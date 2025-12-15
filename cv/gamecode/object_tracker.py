from collections import deque
import time
from ultralytics import YOLO
from gamecode.utils import project_point, calculate_distance
from gamecode.config import *

class ObjectTracker:
    def __init__(self, model_path, homography_matrix, max_ball_history=MAX_BALL_HISTORY):
        """
        Инициализация трекера

        Args:
            model_path (str): путь к весам YOLO
            homography_matrix (np.array): матрица гомографии для проекции
            max_ball_history (int): длина истории позиции мяча
        """
        self.model = YOLO(model_path)
        self.homography_matrix = homography_matrix

        self.ball_history = deque(maxlen=max_ball_history)
        self.last_ball_data = None
        self.frame_count = 0
        self.last_detection_time = time.time()

    def detect_objects(self, frame):
        """
        Детекция объектов на кадре.
        Мяч трекается по ближайшей детекции к последнему известному положению.

        Args:
            frame (np.array): кадр видео

        Returns:
            dict: {'balls': [...], 'racket_positions': [...], 'players': [...], 'timestamp': float}
        """
        self.frame_count += 1
        current_time = time.time()

        # YOLO детекция
        results = self.model(
            frame,
            classes=[BALL_CLASS_ID, RACKET_CLASS_ID, PLAYER_CLASS_ID],
            conf=YOLO_CONFIG['conf_threshold'],
            iou=YOLO_CONFIG['iou_threshold'],
            verbose=False
        )

        tracked_balls = []
        tracked_rackets = []
        players = []
        ball_candidates = []

        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                for box in result.boxes:
                    cls = int(box.cls[0].cpu().numpy())
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0].cpu().numpy())
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)

                    if cls == BALL_CLASS_ID:
                        ball_candidates.append({
                            'center': (cx, cy),
                            'bbox': (x1, y1, x2, y2),
                            'conf': conf,
                            'timestamp': current_time
                        })

                    elif cls == RACKET_CLASS_ID:
                        tracked_rackets.append(self._process_racket(x1, y1, x2, y2, conf, frame.shape[1]))

                    elif cls == PLAYER_CLASS_ID:
                        players.append(self._process_player(cx, cy, x1, y1, x2, y2, conf, frame.shape[1]))

        # Трекинг мяча с фиксированным ID
        ball_data = None
        if ball_candidates:
            if self.last_ball_data:
                def dist(c):
                    lx, ly = self.last_ball_data['center']
                    x, y = c['center']
                    return ((x - lx) ** 2 + (y - ly) ** 2) ** 0.5
                best_candidate = min(ball_candidates, key=dist)
            else:
                best_candidate = ball_candidates[0]

            ball_data = {
                'id': 1,  # фиксированный ID мяча
                'bbox': best_candidate['bbox'],
                'center': best_candidate['center'],
                'pos_table': project_point(best_candidate['center'], self.homography_matrix),
                'conf': best_candidate['conf'],
                'timestamp': best_candidate['timestamp'],
                'speed': self._calculate_speed(best_candidate['center'], current_time)
            }
            self.last_ball_data = ball_data
            self.ball_history.append(ball_data.copy())

        elif self.last_ball_data:
            # Мяч временно пропал, возвращаем последнее состояние
            ball_data = self.last_ball_data

        if ball_data:
            tracked_balls.append(ball_data)

        self.last_detection_time = current_time

        return {
            'balls': tracked_balls,
            'racket_positions': tracked_rackets,
            'players': players,
            'timestamp': current_time
        }

    def _calculate_speed(self, center, timestamp):
        """Расчет скорости мяча по последним координатам"""
        if not self.ball_history:
            return 0.0
        prev = self.ball_history[-1]
        dt = timestamp - prev['timestamp']
        if dt <= 0:
            return 0.0
        return calculate_distance(center, prev['pos_table']) / dt

    def _process_racket(self, x1, y1, x2, y2, conf, frame_width):
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        player_id = 0 if cx < frame_width // 2 else 1
        pos_table = project_point((cx, cy), self.homography_matrix)
        return {
            'bbox': (x1, y1, x2, y2),
            'player_id': player_id,
            'conf': conf,
            'pos_table': pos_table
        }

    def _process_player(self, cx, cy, x1, y1, x2, y2, conf, frame_width):
        player_id = 0 if cx < frame_width // 2 else 1
        return {
            'bbox': (x1, y1, x2, y2),
            'center': (cx, cy),
            'player_id': player_id,
            'conf': conf
        }

    def get_ball_trajectory(self):
        """Возвращает историю траектории мяча"""
        return list(self.ball_history)

    def clear_history(self):
        """Очистка истории трекинга мяча"""
        self.ball_history.clear()
        self.last_ball_data = None
        print("🗑 История трекинга очищена")