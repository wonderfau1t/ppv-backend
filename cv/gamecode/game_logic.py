# """
# Логика игры, ведение счета, определение событий
# """
# from collections import deque
# import time
# from datetime import datetime
#
# from gamecode.config import *
# import numpy as np
#
#
# class PingPongGame:
#     def __init__(self):
#         self.score = [0, 0]
#         self.current_server = 0
#         self.serves_in_row = 0
#         self.game_state = "WAITING"
#         self.last_hitter = None
#         self.last_bounce_side = None
#         self.bounces_in_row = 0
#         self.rally_count = 0
#         self.total_rallies = 0
#         self.max_rally = 0
#
#         # Аналитика
#         self.match_start_time = datetime.now()
#         self.point_start_time = None
#         self.game_history = []
#         self.current_point_data = self._create_empty_point_data()
#
#         # Траектория
#         self.ball_trajectory = deque(maxlen=MAX_BALL_HISTORY)
#         self.ball_speed_history = deque(maxlen=MAX_SPEED_HISTORY)
#
#         # Настройка зон стола
#         self._setup_table_zones()
#
#     def _create_empty_point_data(self):
#         """Создание пустой записи для очка"""
#         return {
#             "point_number": len(self.game_history) + 1,
#             "start_time": None,
#             "end_time": None,
#             "duration": 0,
#             "winner": None,
#             "rally_count": 0,
#             "server": self.current_server,
#             "serve_type": None,
#             "max_speed": 0,
#             "avg_speed": 0,
#             "events": []
#         }
#
#     def _setup_table_zones(self):
#         """Настройка виртуальных зон стола"""
#         self.table_zones = {
#             'player1_half': {'x1': 0, 'y1': 0, 'x2': TABLE_WIDTH // 2, 'y2': TABLE_HEIGHT},
#             'player2_half': {'x1': TABLE_WIDTH // 2, 'y1': 0, 'x2': TABLE_WIDTH, 'y2': TABLE_HEIGHT},
#             'net_zone': {'x1': TABLE_WIDTH // 2 - NET_CROSSING_MARGIN,
#                          'y1': 0,
#                          'x2': TABLE_WIDTH // 2 + NET_CROSSING_MARGIN,
#                          'y2': TABLE_HEIGHT}
#         }
#
#     def update_game_state(self, ball_data, racket_positions):
#         """Обновление состояния игры на основе новых данных"""
#         if not ball_data:
#             return self.game_state
#
#         # Добавляем данные мяча
#         self.ball_trajectory.append({
#             'pos': ball_data['pos_table'],
#             'speed': ball_data.get('speed', 0),
#             'time': ball_data['timestamp'],
#             'side': self._get_ball_side(ball_data['pos_table'])
#         })
#
#         self.ball_speed_history.append(ball_data.get('speed', 0))
#
#         # Определяем ударившего
#         current_hitter = self._determine_hitter(racket_positions, ball_data['pos_table'])
#
#         # Обработка в зависимости от состояния
#         if self.game_state == "WAITING":
#             self._handle_waiting_state()
#
#         elif self.game_state == "SERVING":
#             self._handle_serving_state(current_hitter)
#
#         elif self.game_state == "RALLY":
#             self._handle_rally_state(current_hitter)
#
#         elif self.game_state == "POINT_END":
#             self._handle_point_end_state()
#
#         return self.game_state
#
#     def _handle_waiting_state(self):
#         """Обработка состояния ожидания"""
#         avg_speed = np.mean(self.ball_speed_history) if self.ball_speed_history else 0
#         if avg_speed > GAME_START_SPEED_THRESHOLD:
#             self.game_state = "SERVING"
#             self.point_start_time = time.time()
#             self.current_point_data = self._create_empty_point_data()
#             print(f"🎮 Начало подачи. Подающий: Игрок {self.current_server + 1}")
#
#     def _handle_serving_state(self, current_hitter):
#         """Обработка состояния подачи"""
#         if self._check_valid_serve(self.current_server):
#             self.game_state = "RALLY"
#             self.last_hitter = self.current_server
#             self.rally_count = 1
#             print(f"✅ Подача принята. Начало розыгрыша")
#
#     def _handle_rally_state(self, current_hitter):
#         """Обработка состояния розыгрыша"""
#         # Проверка пересечения сетки
#         if self._check_net_crossing():
#             self.bounces_in_row = 0
#
#         # Проверка отскока
#         bounce, bounce_side = self._check_bounce()
#         if bounce:
#             self.bounces_in_row += 1
#             self.last_bounce_side = bounce_side
#
#             # Обновляем last_hitter при первом отскоке после удара
#             if current_hitter is not None and self.bounces_in_row == 1:
#                 self.last_hitter = current_hitter
#                 self.rally_count += 1
#
#         # Проверка условий завершения очка
#         self._check_point_end_conditions()
#
#     def _handle_point_end_state(self):
#         """Обработка состояния завершения очка"""
#         # Автоматический переход обратно в WAITING через 2 секунды
#         if time.time() - self.point_start_time > 2:
#             self.game_state = "WAITING"
#             self.ball_trajectory.clear()
#             self.ball_speed_history.clear()
#
#     def _check_point_end_conditions(self):
#         """Проверка условий завершения очка"""
#         if not self.ball_trajectory:
#             return
#
#         last_ball = self.ball_trajectory[-1]
#         ball_pos = last_ball['pos']
#
#         # Условия завершения
#         conditions = [
#             (self._check_double_bounce(), "Двойной отскок"),
#             (self._check_out_of_table(ball_pos), "Мяч вне стола"),
#             (self._check_net_touch(), "Касание сетки")
#         ]
#
#         for condition, reason in conditions:
#             if condition:
#                 winner = self._determine_point_winner(reason)
#                 if winner is not None:
#                     self.end_point(winner, last_ball['time'])
#                     print(f"❌ {reason}")
#                     break
#
#     def _get_ball_side(self, ball_pos):
#         """Определение стороны мяча"""
#         x, _ = ball_pos
#         return 0 if x < TABLE_WIDTH // 2 else 1
#
#     def _determine_hitter(self, racket_positions, ball_pos):
#         """Определение, кто ударил по мячу"""
#         from gamecode.utils import calculate_distance
#
#         if not racket_positions:
#             return None
#
#         min_distance = float('inf')
#         hitter = None
#
#         for player_id, racket_pos in enumerate(racket_positions):
#             if racket_pos is not None:
#                 x1, y1, x2, y2 = racket_pos['bbox']  # берём bbox из словаря
#                 racket_center = ((x1 + x2) / 2, (y1 + y2) / 2)  # центр ракетки
#                 distance = calculate_distance(racket_center, ball_pos)
#                 if distance < min_distance and distance < 100:
#                     min_distance = distance
#                     hitter = player_id
#
#         return hitter
#
#     def _check_valid_serve(self, serve_side):
#         """Проверка валидности подачи"""
#         # Упрощенная проверка (можно расширить)
#         if len(self.ball_trajectory) < 3:
#             return False
#
#         # Проверяем, что мяч пересек сетку
#         for i in range(len(self.ball_trajectory) - 1):
#             pos1 = self.ball_trajectory[i]['pos']
#             pos2 = self.ball_trajectory[i + 1]['pos']
#             if self._get_ball_side(pos1) != self._get_ball_side(pos2):
#                 return True
#
#         return False
#
#     def _check_net_crossing(self):
#         """Проверка пересечения сетки"""
#         if len(self.ball_trajectory) < 2:
#             return False
#
#         pos1 = self.ball_trajectory[-2]['pos']
#         pos2 = self.ball_trajectory[-1]['pos']
#
#         return self._get_ball_side(pos1) != self._get_ball_side(pos2)
#
#     def _check_bounce(self):
#         """Проверка отскока мяча"""
#         if len(self.ball_trajectory) < 3:
#             return False, None
#
#         # Упрощенная проверка по изменению направления
#         pos1 = self.ball_trajectory[-3]['pos']
#         pos2 = self.ball_trajectory[-2]['pos']
#         pos3 = self.ball_trajectory[-1]['pos']
#
#         # Если мяч резко изменил направление (особенно по Y)
#         dy1 = pos2[1] - pos1[1]
#         dy2 = pos3[1] - pos2[1]
#
#         if dy1 * dy2 < 0 and abs(dy1) > 5 and abs(dy2) > 5:
#             return True, self._get_ball_side(pos2)
#
#         return False, None
#
#     def _check_double_bounce(self):
#         """Проверка двойного отскока"""
#         return self.bounces_in_row >= 2
#
#     def _check_out_of_table(self, ball_pos):
#         """Проверка выхода мяча за пределы стола"""
#         x, y = ball_pos
#         return x < 0 or x > TABLE_WIDTH or y < 0 or y > TABLE_HEIGHT
#
#     def _check_net_touch(self):
#         """Проверка касания сетки"""
#         if not self._check_net_crossing():
#             return False
#
#         # Упрощенная проверка - если мяч слишком низко пересек сетку
#         if len(self.ball_trajectory) < 2:
#             return False
#
#         last_pos = self.ball_trajectory[-1]['pos']
#         net_zone = self.table_zones['net_zone']
#
#         # Проверяем, находится ли мяч в зоне сетки
#         return (net_zone['x1'] <= last_pos[0] <= net_zone['x2'] and
#                 net_zone['y1'] <= last_pos[1] <= net_zone['y2'])
#
#     def _determine_point_winner(self, reason):
#         """Определение победителя очка"""
#         if "отскок" in reason.lower():
#             return 1 - self.last_bounce_side if self.last_bounce_side is not None else 0
#         elif "сетка" in reason.lower():
#             return 1 - self.last_hitter if self.last_hitter is not None else 0
#         else:
#             return 1 - self.last_hitter if self.last_hitter is not None else 0
#
#     def end_point(self, winner, timestamp):
#         """Завершение очка"""
#         self.game_state = "POINT_END"
#         self.score[winner] += 1
#
#         # Обновляем данные очка
#         self.current_point_data['end_time'] = timestamp
#         self.current_point_data['duration'] = timestamp - self.current_point_data['start_time']
#         self.current_point_data['winner'] = winner
#         self.current_point_data['rally_count'] = self.rally_count
#
#         # Статистика скорости
#         if self.ball_speed_history:
#             self.current_point_data['max_speed'] = max(self.ball_speed_history)
#             self.current_point_data['avg_speed'] = np.mean(self.ball_speed_history)
#
#         # Сохраняем историю
#         self.game_history.append(self.current_point_data.copy())
#
#         # Обновляем общую статистику
#         self.total_rallies += self.rally_count
#         self.max_rally = max(self.max_rally, self.rally_count)
#
#         # Смена подачи
#         self.serves_in_row += 1
#         if self.serves_in_row >= GAME_RULES['serves_per_turn']:
#             self.current_server = 1 - self.current_server
#             self.serves_in_row = 0
#
#         # Вывод информации
#         self._print_point_summary(winner)
#
#         # Проверка конца матча
#         if self._is_match_complete():
#             self.game_state = "MATCH_END"
#             print("\n🎊 МАТЧ ЗАВЕРШЕН!")
#             print(f"   ФИНАЛЬНЫЙ СЧЁТ: {self.score[0]} - {self.score[1]}")
#
#     def _print_point_summary(self, winner):
#         """Вывод информации о завершенном очке"""
#         print("\n" + "=" * 50)
#         print(f"🎉 ОЧКО ЗАВЕРШЕНО!")
#         print(f"   Победитель: Игрок {winner + 1}")
#         print(f"   Счёт: {self.score[0]} - {self.score[1]}")
#         print(f"   Количество ударов: {self.rally_count}")
#         print(f"   Длительность: {self.current_point_data['duration']:.1f} сек")
#         print("=" * 50)
#
#     def _is_match_complete(self):
#         """Проверка завершения матча"""
#         max_score = max(self.score)
#         min_score = min(self.score)
#
#         return (max_score >= GAME_RULES['winning_score'] and
#                 (max_score - min_score) >= GAME_RULES['min_lead'])
#
#     def get_game_info(self):
#         """Получение информации об игре"""
#         avg_speed = np.mean(self.ball_speed_history) if self.ball_speed_history else 0
#         max_speed = max(self.ball_speed_history) if self.ball_speed_history else 0
#
#         return {
#             'score': self.score,
#             'server': self.current_server,
#             'game_state': self.game_state,
#             'rally_count': self.rally_count,
#             'max_speed': max_speed,
#             'avg_speed': avg_speed,
#             'total_points': len(self.game_history)
#         }
#
#     def reset_game(self):
#         """Сброс игры"""
#         self.__init__()
#         print("🔄 Игра сброшена")


# from collections import deque
# import time
# from datetime import datetime
# import numpy as np
#
# from gamecode.config import *
# from gamecode.utils import calculate_distance
#
#
# class PingPongGame:
#     """
#     Модуль анализа игры и логики счета
#     Реализация строго по требованиям ТЗ 4.2.4.3
#     """
#
#     # ---------- ИНИЦИАЛИЗАЦИЯ ----------
#
#     def __init__(self):
#         # ===== МАТЧ =====
#         self.set_score = [0, 0]  # выигранные партии
#         self.current_set = self._new_set()
#         self.match_winner = None
#         self.max_sets = 5
#         self.sets_to_win = 3
#
#         # ===== ПАРТИЯ =====
#         self.score = [0, 0]  # очки в текущей партии
#         self.current_server = 0
#         self.game_state = "WAITING"  # WAITING / SERVING / RALLY / POINT_END / SET_END / MATCH_END
#         self.match_state = "IDLE"   # IDLE → RUNNING → MATCH_END
#
#
#         # ===== РОЗЫГРЫШ =====
#         self.rally_count = 0
#         self.point_start_time = None
#
#         # ===== ИГРОВЫЕ СОБЫТИЯ =====
#         self.last_hitter = None
#         self.last_bounce_side = None
#         self.bounces_in_row = 0
#
#         # ===== ТРАЕКТОРИЯ =====
#         self.ball_trajectory = deque(maxlen=MAX_BALL_HISTORY)
#         self.ball_speed_history = deque(maxlen=MAX_SPEED_HISTORY)
#
#     # ---------- СТАРТ / СТОП МАТЧА ----------
#
#     def start_match(self):
#         """Запуск анализа матча (по сигналу / кнопке)"""
#         self.match_state = "RUNNING"
#         self.current_set = self._new_set()
#         print("▶ Матч начат")
#
#     def _end_match(self, winner):
#         self.match_state = "MATCH_END"
#         print(f"\n🏆 МАТЧ ЗАВЕРШЕН. Победитель: Игрок {winner + 1}")
#         print(f"Финальный счет по партиям: {self.set_score[0]}:{self.set_score[1]}")
#
#     # ---------- ОБНОВЛЕНИЕ СОСТОЯНИЯ ----------
#
#     def update(self, ball_data, racket_positions):
#         """
#         Главный метод обновления (вызывается каждый кадр)
#         """
#         if self.match_state != "RUNNING" or not ball_data:
#             return
#
#         # 1️⃣ Сохраняем траекторию мяча
#         self._update_ball_trajectory(ball_data)
#
#         # 2️⃣ Детектируем события
#         hit = self._detect_hit(racket_positions)
#         bounce, bounce_side = self._detect_bounce()
#         error = self._detect_error()
#
#         # 3️⃣ Обрабатываем события
#         if hit:
#             self.current_set['hits'] += 1
#             self.last_hitter = hit
#
#         if bounce:
#             self.bounce_count += 1
#             self.last_bounce_side = bounce_side
#
#         if error:
#             self._end_rally(error)
#
#     # ---------- СОБЫТИЯ ----------
#
#     def _detect_hit(self, racket_positions):
#         """Фиксация удара (пересечение траекторий мяча и ракетки)"""
#         HIT_DISTANCE_THRESHOLD = 0.08
#         if not racket_positions or len(self.ball_trajectory) < 2:
#             return None
#
#         ball_pos = self.ball_trajectory[-1]['pos']
#
#         for racket in racket_positions:
#             x1, y1, x2, y2 = racket['bbox']
#             racket_center = ((x1 + x2) / 2, (y1 + y2) / 2)
#
#             if calculate_distance(racket_center, ball_pos) < HIT_DISTANCE_THRESHOLD:
#                 return racket['player_id']
#
#         return None
#
#     def _detect_bounce(self):
#         """Фиксация отскока мяча от стола с учетом зон"""
#         if len(self.ball_trajectory) < 3:
#             return False, None
#
#         p1 = self.ball_trajectory[-3]['pos']
#         p2 = self.ball_trajectory[-2]['pos']
#         p3 = self.ball_trajectory[-1]['pos']
#
#         dy1 = p2[1] - p1[1]
#         dy2 = p3[1] - p2[1]
#
#         if dy1 * dy2 < 0:
#             side = 0 if p2[0] < TABLE_WIDTH / 2 else 1
#             return True, side
#
#         return False, None
#
#     def _detect_error(self):
#         """Детекция ошибок"""
#         last = self.ball_trajectory[-1]['pos']
#         x, y = last
#
#         if x < 0 or x > TABLE_WIDTH or y < 0 or y > TABLE_HEIGHT:
#             return "OUT"
#
#         if self.bounce_count >= 2:
#             return "DOUBLE_BOUNCE"
#
#         return None
#
#     # ---------- РОЗЫГРЫШ ----------
#
#     def _end_rally(self, error_type):
#         """Завершение розыгрыша"""
#         winner = 1 - self.last_hitter if self.last_hitter is not None else 0
#
#         duration = time.time() - self.current_set['rally_start_time']
#         hits = self.current_set['hits']
#
#         self._add_point(winner)
#
#         print(f"❌ Ошибка: {error_type}")
#         print(f"Очко игроку {winner + 1} | Удары: {hits} | Длительность: {duration:.2f} сек")
#
#         self._reset_rally()
#
#     def _reset_rally(self):
#         self.ball_trajectory.clear()
#         self.bounce_count = 0
#         self.last_hitter = None
#         self.current_set['rally_start_time'] = time.time()
#         self.current_set['hits'] = 0
#
#     # ---------- ПАРТИЯ ----------
#
#     def _add_point(self, player):
#         self.current_set['score'][player] += 1
#         self._check_set_end()
#
#     def _check_set_end(self):
#         s = self.current_set['score']
#         if max(s) >= 11 and abs(s[0] - s[1]) >= 2:
#             winner = int(s[0] < s[1])
#             self.set_score[winner] += 1
#             print(f"\n🏁 Партия завершена. Победитель: Игрок {winner + 1}")
#             self._check_match_end()
#
#             if self.match_state == "RUNNING":
#                 self.current_set = self._new_set()
#
#     # ---------- МАТЧ ----------
#
#     def _check_match_end(self):
#         if max(self.set_score) >= 3:
#             winner = int(self.set_score[0] < self.set_score[1])
#             self._end_match(winner)
#
#     # ---------- ВСПОМОГАТЕЛЬНЫЕ ----------
#
#     def _update_ball_trajectory(self, ball_data):
#         self.ball_trajectory.append({
#             'pos': ball_data['pos_table'],
#             'time': ball_data['timestamp']
#         })
#
#     def _new_set(self):
#         return {
#             'score': [0, 0],
#             'hits': 0,
#             'rally_start_time': time.time()
#         }
#
#     def get_game_info(self):
#         """Получение информации об игре (строго по ТЗ 4.2.4.3)"""
#
#         avg_speed = float(np.mean(self.ball_speed_history)) if self.ball_speed_history else 0.0
#         max_speed = float(max(self.ball_speed_history)) if self.ball_speed_history else 0.0
#
#         rally_duration = 0.0
#         if self.point_start_time and self.game_state in ("SERVING", "RALLY"):
#             rally_duration = time.time() - self.point_start_time
#         return {
#             'total_points': self.score,  # [очки в партии]
#             'score_sets': self.set_score,  # [партии]
#             'server': self.current_server,
#             'game_state': self.game_state,
#             'match_state': self.match_state,
#             'rally_count': self.rally_count,
#             'max_speed': round(max_speed, 2),
#             'avg_speed': round(avg_speed, 2),
#             'rally_duration': round(rally_duration, 2)
#         }
#         return {
#             # Очки в текущей партии
#             'score_points': {
#                 'player1': self.score[0],
#                 'player2': self.score[1]
#             },
#
#             # Счёт партий
#             'score_sets': {
#                 'player1': self.set_score[0],
#                 'player2': self.set_score[1]
#             },
#
#             # Подача
#             'current_server': self.current_server,
#
#             # Состояние игры
#             'game_state': self.game_state,
#
#             # Розыгрыш
#             'rally': {
#                 'hits': self.rally_count,
#                 'duration_sec': round(rally_duration, 2),
#                 'is_long_rally': self.rally_count > 6
#             },
#
#             # Скорости мяча
#             'ball_speed': {
#                 'max': round(max_speed, 2),
#                 'avg': round(avg_speed, 2)
#             },
#
#             # Матч
#             'match_finished': self.game_state == "MATCH_END",
#             'match_winner': self.match_winner
#         }

from dataclasses import dataclass
from enum import Enum
import numpy as np
from gamecode.config import GAME_START_SPEED_THRESHOLD


@dataclass
class RacketHit:
    player: str
    time: float


@dataclass
class TableGeometry:
    left: float
    right: float
    top: float
    bottom: float
    net: float

class RallyState(Enum):
    WAIT_SERVE = 0
    RALLY = 1
    POINT_OVER = 2

class MatchScore:
    def __init__(self, games_to_win=5):
        self.points = {"A": 0, "B": 0}
        self.games = {"A": 0, "B": 0}
        self.games_to_win = games_to_win
        self.winner = None

    def add_point(self, player):
        self.points[player] += 1

        if self._game_won(player):
            self.games[player] += 1
            self.points = {"A": 0, "B": 0}

            if self.games[player] >= self.games_to_win:
                self.winner = player

    def _game_won(self, player):
        other = "B" if player == "A" else "A"
        return self.points[player] >= 11 and \
               self.points[player] - self.points[other] >= 2

class TableTennisLogic:
    def __init__(self, table: TableGeometry):
        self.table = table
        self.state = RallyState.WAIT_SERVE
        self.score = MatchScore()

        self.ball_history = []
        self.last_side = None
        self.bounce_count = {"A": 0, "B": 0}

        self.rally_started = False
        self.last_hit_by = None
        self.last_hit_time = 0
        self.last_speed_vec = None

    def update_ball(self, x, y, t, speed, speed_vec, rackets):
        """
        rackets: [
            {"player_id": 0/1, "pos_table": (x, y)}
        ]
        """
        self.ball_history.append((x, y, t))
        if len(self.ball_history) < 3:
            return

        # --- Старт розыгрыша ---
        if not self.rally_started and speed > GAME_START_SPEED_THRESHOLD:
            self.rally_started = True
            self.state = RallyState.RALLY
            self.last_side = self._ball_side(y)

        # --- Удар ракеткой ---
        self._detect_racket_hit(x, y, t, rackets, speed_vec)

        if self.state == RallyState.RALLY:
            self._process_events()

    def _detect_racket_hit(self, x, y, t, rackets, speed_vec, hit_dist=40):
        for r in rackets:
            rx, ry = r["pos_table"]
            if np.hypot(x - rx, y - ry) < hit_dist:
                if t - self.last_hit_time < 0.2:
                    return  # антидребезг

                player = "A" if r["player_id"] == 0 else "B"
                self.last_hit_by = player
                self.last_hit_time = t
                self.last_speed_vec = speed_vec

                self.bounce_count = {"A": 0, "B": 0}
                return

    def _process_events(self):
        (x1, y1, t1), (x2, y2, t2), (x3, y3, t3) = self.ball_history[-3:]

        # --- Отскок ---
        if y2 < y1 and y2 < y3 and self._near_table(y2):
            side = self._ball_side(y2)
            self.bounce_count[side] += 1

            if self.bounce_count[side] >= 2:
                self._end_point(winner=self._other(side))
                return

        # --- Перелёт сетки ---
        current_side = self._ball_side(y2)
        if self.last_side and current_side != self.last_side:
            self.last_side = current_side

        # --- Вылет ---
        if not self._inside_table(x2, y2):
            if self.last_hit_by:
                self._end_point(winner=self._other(self.last_hit_by))
            return

    def _end_point(self, winner):
        if self.state == RallyState.POINT_OVER:
            return

        self.score.add_point(winner)
        self.state = RallyState.POINT_OVER
        self._reset_rally()

    def _reset_rally(self):
        self.ball_history.clear()
        self.bounce_count = {"A": 0, "B": 0}
        self.last_side = None
        self.last_hit_by = None
        self.last_speed_vec = None
        self.rally_started = False
        self.state = RallyState.WAIT_SERVE

    def _ball_side(self, y):
        return "A" if y < self.table.net else "B"

    def _other(self, p):
        return "B" if p == "A" else "A"

    def _inside_table(self, x, y):
        return (
                self.table.left <= x <= self.table.right and
                self.table.top <= y <= self.table.bottom
        )

    def _near_table(self, y, eps=8):
        return abs(y - self.table.top) < eps or abs(y - self.table.bottom) < eps

    def get_game_info(self):
        return {
            "state": self.state.name,
            "points": self.score.points.copy(),
            "games": self.score.games.copy(),
            "match_winner": self.score.winner
        }
