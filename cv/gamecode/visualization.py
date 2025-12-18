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

        pos_x = int(pos_x)
        pos_y = int(pos_y)

        # защита от выхода за границы
        if 0 <= pos_x < TABLE_WIDTH and 0 <= pos_y < TABLE_HEIGHT:
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
        h, w = frame.shape[:2]

        points = game_info['points']
        games = game_info['games']
        state = game_info['state']

        # --- СЧЁТ ПО ОЧКАМ ---
        score_text = f"Points: {points['A']} - {points['B']}"
        cv2.putText(frame, score_text, (w - 320, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['score'], 3)

        # --- СЧЁТ ПО ПАРТИЯМ ---
        games_text = f"Games: {games['A']} - {games['B']}"
        cv2.putText(frame, games_text, (w - 320, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS['text'], 2)

        # --- СОСТОЯНИЕ ---
        state_text = f"State: {state}"
        cv2.putText(frame, state_text, (w - 320, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['text'], 2)

        # --- ПОБЕДИТЕЛЬ МАТЧА ---
        if game_info['match_winner'] is not None:
            winner = game_info['match_winner']
            win_text = f"🏆 Winner: Player {1 if winner == 'A' else 2}"
            cv2.putText(frame, win_text, (w // 2 - 200, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 255), 4)

    def _draw_table_info(self, table_view, game_info):
        points = game_info['points']
        games = game_info['games']
        state = game_info['state']

        # Игрок A (левая сторона)
        cv2.putText(table_view,
                    f"P1  {points['A']} ({games['A']})",
                    (40, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    COLORS['player1'],
                    2)

        # Игрок B (правая сторона)
        cv2.putText(table_view,
                    f"P2  {points['B']} ({games['B']})",
                    (TABLE_WIDTH - 220, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    COLORS['player2'],
                    2)

        # Статус
        cv2.putText(table_view,
                    f"{state}",
                    (TABLE_WIDTH // 2 - 80, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    COLORS['score'],
                    2)
