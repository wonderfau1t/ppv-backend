"""
Визуализация и отображение
"""
import cv2
import numpy as np
from gamecode.config import *
from gamecode.utils import create_table_view, draw_table_grid


class Visualizer:
    def __init__(self, homography_matrix, src_points):
        self.homography_matrix = homography_matrix
        self.src_points = src_points

    def draw_main_frame(self, frame, tracked_objects, game_info):
        """Рисование основного кадра с детекциями"""
        frame_display = frame.copy()

        # Контур стола
        cv2.polylines(frame_display, [self.src_points.astype(np.int32)],
                      isClosed=True, color=COLORS['table'], thickness=2)

        # Сетка
        mid_top = ((self.src_points[0] + self.src_points[1]) / 2).astype(int)
        mid_bottom = ((self.src_points[3] + self.src_points[2]) / 2).astype(int)
        cv2.line(frame_display, tuple(mid_top), tuple(mid_bottom),
                 COLORS['net'], 2)

        # Мячи
        for ball in tracked_objects.get('balls', []):
            self._draw_ball(frame_display, ball)

        # Игроки
        for player in tracked_objects.get('players', []):
            self._draw_player(frame_display, player)

        for racket in tracked_objects.get('racket_positions', []):
            if racket is not None:
                self._draw_racket(frame_display, racket)

        # Игровая информация
        self._draw_game_info(frame_display, game_info)

        return frame_display

    def draw_table_view(self, tracked_objects, game_info, ball_history):
        """Рисование вида стола сверху"""
        table_view = create_table_view(TABLE_WIDTH, TABLE_HEIGHT)
        table_view = draw_table_grid(table_view, TABLE_WIDTH, TABLE_HEIGHT, COLORS)

        # Мячи
        for ball in tracked_objects.get('balls', []):
            self._draw_ball_on_table(table_view, ball)

        # Траектория
        if ball_history:
            self._draw_trajectory(table_view, ball_history)

        # Игровая информация на столе
        self._draw_table_info(table_view, game_info)

        return table_view

    def _draw_ball(self, frame, ball):
        """Рисование мяча на основном кадре"""
        x1, y1, x2, y2 = ball['bbox']
        cx, cy = ball['center']

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLORS['ball'], 2)

        # Центр
        cv2.circle(frame, (cx, cy), 5, COLORS['ball'], -1)

        # Информация
        speed = ball.get('speed', 0)
        label = f"Ball: {speed:.1f} px/sec"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['ball'], 2)

    def _draw_player(self, frame, player):
        """Рисование игрока"""
        x1, y1, x2, y2 = player['bbox']
        player_id = player['player_id']
        conf = player['conf']

        color = COLORS['player1'] if player_id == 0 else COLORS['player2']

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        label = f"Player {player_id + 1}: {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def _draw_racket(self, frame, racket):
        """Рисование игрока"""
        x1, y1, x2, y2 = racket['bbox']
        player_id = racket['player_id']
        conf = racket['conf']

        color = COLORS['racket1'] if player_id == 0 else COLORS['racket2']

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        label = f"Racket {player_id + 1}: {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def _draw_ball_on_table(self, table_view, ball):
        """Рисование мяча на виде сверху"""
        pos_x, pos_y = ball['pos_table']

        cv2.circle(table_view, (pos_x, pos_y), 5, COLORS['ball'], -1)
        cv2.circle(table_view, (pos_x, pos_y), 7, (255, 255, 255), 1)

    def _draw_trajectory(self, table_view, ball_history):
        """Рисование траектории мяча"""
        if len(ball_history) < 2:
            return

        # Группируем по ID
        trajectories = {}
        for item in ball_history:
            ball_id = item['id']
            if ball_id not in trajectories:
                trajectories[ball_id] = []
            trajectories[ball_id].append(item['pos_table'])

        # Рисуем каждую траекторию
        for ball_id, trajectory in trajectories.items():
            if len(trajectory) > 1:
                for i in range(1, len(trajectory)):
                    alpha = i / len(trajectory)
                    color = (0, int(255 * alpha), int(255 * (1 - alpha)))
                    cv2.line(table_view, trajectory[i - 1], trajectory[i], color, 2)

    def _draw_game_info(self, frame, game_info):
        """Рисование игровой информации на основном кадре"""
        h, w = frame.shape[:2]

        # Счет (правый верхний угол)
        score_text = f"Score: {game_info['score'][0]} - {game_info['score'][1]}"
        cv2.putText(frame, score_text, (w - 300, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['score'], 3)

        # Состояние игры
        state_text = f"State: {game_info['game_state']}"
        cv2.putText(frame, state_text, (w - 300, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['text'], 2)

        # Подающий
        server_text = f"Server: Player {game_info['server'] + 1}"
        cv2.putText(frame, server_text, (w - 300, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['text'], 2)

        # Количество ударов в розыгрыше
        if game_info['game_state'] == "RALLY":
            rally_text = f"Rally: {game_info['rally_count']}"
            cv2.putText(frame, rally_text, (w - 300, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['text'], 2)

        # Скорость (левый верхний угол)
        speed_text = f"Speed: {game_info['avg_speed']:.1f} px/sec"
        cv2.putText(frame, speed_text, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['text'], 2)

        # Общее количество очков
        points_text = f"Points: {game_info['total_points']}"
        cv2.putText(frame, points_text, (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['text'], 2)

    def _draw_table_info(self, table_view, game_info):
        """Рисование информации на виде сверху"""
        # Счет игроков
        cv2.putText(table_view, f"P1: {game_info['score'][0]}",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['player1'], 2)
        cv2.putText(table_view, f"P2: {game_info['score'][1]}",
                    (TABLE_WIDTH - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['player2'], 2)

        # Розыгрыш
        if game_info['game_state'] == "RALLY":
            cv2.putText(table_view, f"Rally: {game_info['rally_count']}",
                        (TABLE_WIDTH // 2 - 60, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['score'], 2)