"""
Логика игры, ведение счета, определение событий
"""
from collections import deque
import time
from datetime import datetime

from gamecode.config import *
import numpy as np


class PingPongGame:
    def __init__(self):
        self.score = [0, 0]
        self.current_server = 0
        self.serves_in_row = 0
        self.game_state = "WAITING"
        self.last_hitter = None
        self.last_bounce_side = None
        self.bounces_in_row = 0
        self.rally_count = 0
        self.total_rallies = 0
        self.max_rally = 0

        # Аналитика
        self.match_start_time = datetime.now()
        self.point_start_time = None
        self.game_history = []
        self.current_point_data = self._create_empty_point_data()

        # Траектория
        self.ball_trajectory = deque(maxlen=MAX_BALL_HISTORY)
        self.ball_speed_history = deque(maxlen=MAX_SPEED_HISTORY)

        # Настройка зон стола
        self._setup_table_zones()

    def _create_empty_point_data(self):
        """Создание пустой записи для очка"""
        return {
            "point_number": len(self.game_history) + 1,
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "winner": None,
            "rally_count": 0,
            "server": self.current_server,
            "serve_type": None,
            "max_speed": 0,
            "avg_speed": 0,
            "events": []
        }

    def _setup_table_zones(self):
        """Настройка виртуальных зон стола"""
        self.table_zones = {
            'player1_half': {'x1': 0, 'y1': 0, 'x2': TABLE_WIDTH // 2, 'y2': TABLE_HEIGHT},
            'player2_half': {'x1': TABLE_WIDTH // 2, 'y1': 0, 'x2': TABLE_WIDTH, 'y2': TABLE_HEIGHT},
            'net_zone': {'x1': TABLE_WIDTH // 2 - NET_CROSSING_MARGIN,
                         'y1': 0,
                         'x2': TABLE_WIDTH // 2 + NET_CROSSING_MARGIN,
                         'y2': TABLE_HEIGHT}
        }

    def update_game_state(self, ball_data, racket_positions):
        """Обновление состояния игры на основе новых данных"""
        if not ball_data:
            return self.game_state

        # Добавляем данные мяча
        self.ball_trajectory.append({
            'pos': ball_data['pos_table'],
            'speed': ball_data.get('speed', 0),
            'time': ball_data['timestamp'],
            'side': self._get_ball_side(ball_data['pos_table'])
        })

        self.ball_speed_history.append(ball_data.get('speed', 0))

        # Определяем ударившего
        current_hitter = self._determine_hitter(racket_positions, ball_data['pos_table'])

        # Обработка в зависимости от состояния
        if self.game_state == "WAITING":
            self._handle_waiting_state()

        elif self.game_state == "SERVING":
            self._handle_serving_state(current_hitter)

        elif self.game_state == "RALLY":
            self._handle_rally_state(current_hitter)

        elif self.game_state == "POINT_END":
            self._handle_point_end_state()

        return self.game_state

    def _handle_waiting_state(self):
        """Обработка состояния ожидания"""
        avg_speed = np.mean(self.ball_speed_history) if self.ball_speed_history else 0
        if avg_speed > GAME_START_SPEED_THRESHOLD:
            self.game_state = "SERVING"
            self.point_start_time = time.time()
            self.current_point_data = self._create_empty_point_data()
            print(f"🎮 Начало подачи. Подающий: Игрок {self.current_server + 1}")

    def _handle_serving_state(self, current_hitter):
        """Обработка состояния подачи"""
        if self._check_valid_serve(self.current_server):
            self.game_state = "RALLY"
            self.last_hitter = self.current_server
            self.rally_count = 1
            print(f"✅ Подача принята. Начало розыгрыша")

    def _handle_rally_state(self, current_hitter):
        """Обработка состояния розыгрыша"""
        # Проверка пересечения сетки
        if self._check_net_crossing():
            self.bounces_in_row = 0

        # Проверка отскока
        bounce, bounce_side = self._check_bounce()
        if bounce:
            self.bounces_in_row += 1
            self.last_bounce_side = bounce_side

            # Обновляем last_hitter при первом отскоке после удара
            if current_hitter is not None and self.bounces_in_row == 1:
                self.last_hitter = current_hitter
                self.rally_count += 1

        # Проверка условий завершения очка
        self._check_point_end_conditions()

    def _handle_point_end_state(self):
        """Обработка состояния завершения очка"""
        # Автоматический переход обратно в WAITING через 2 секунды
        if time.time() - self.point_start_time > 2:
            self.game_state = "WAITING"
            self.ball_trajectory.clear()
            self.ball_speed_history.clear()

    def _check_point_end_conditions(self):
        """Проверка условий завершения очка"""
        if not self.ball_trajectory:
            return

        last_ball = self.ball_trajectory[-1]
        ball_pos = last_ball['pos']

        # Условия завершения
        conditions = [
            (self._check_double_bounce(), "Двойной отскок"),
            (self._check_out_of_table(ball_pos), "Мяч вне стола"),
            (self._check_net_touch(), "Касание сетки")
        ]

        for condition, reason in conditions:
            if condition:
                winner = self._determine_point_winner(reason)
                if winner is not None:
                    self.end_point(winner, last_ball['time'])
                    print(f"❌ {reason}")
                    break

    def _get_ball_side(self, ball_pos):
        """Определение стороны мяча"""
        x, _ = ball_pos
        return 0 if x < TABLE_WIDTH // 2 else 1

    def _determine_hitter(self, racket_positions, ball_pos):
        """Определение, кто ударил по мячу"""
        from gamecode.utils import calculate_distance

        if not racket_positions:
            return None

        min_distance = float('inf')
        hitter = None

        for player_id, racket_pos in enumerate(racket_positions):
            if racket_pos is not None:
                x1, y1, x2, y2 = racket_pos['bbox']  # берём bbox из словаря
                racket_center = ((x1 + x2) / 2, (y1 + y2) / 2)  # центр ракетки
                distance = calculate_distance(racket_center, ball_pos)
                if distance < min_distance and distance < 100:
                    min_distance = distance
                    hitter = player_id

        return hitter

    def _check_valid_serve(self, serve_side):
        """Проверка валидности подачи"""
        # Упрощенная проверка (можно расширить)
        if len(self.ball_trajectory) < 3:
            return False

        # Проверяем, что мяч пересек сетку
        for i in range(len(self.ball_trajectory) - 1):
            pos1 = self.ball_trajectory[i]['pos']
            pos2 = self.ball_trajectory[i + 1]['pos']
            if self._get_ball_side(pos1) != self._get_ball_side(pos2):
                return True

        return False

    def _check_net_crossing(self):
        """Проверка пересечения сетки"""
        if len(self.ball_trajectory) < 2:
            return False

        pos1 = self.ball_trajectory[-2]['pos']
        pos2 = self.ball_trajectory[-1]['pos']

        return self._get_ball_side(pos1) != self._get_ball_side(pos2)

    def _check_bounce(self):
        """Проверка отскока мяча"""
        if len(self.ball_trajectory) < 3:
            return False, None

        # Упрощенная проверка по изменению направления
        pos1 = self.ball_trajectory[-3]['pos']
        pos2 = self.ball_trajectory[-2]['pos']
        pos3 = self.ball_trajectory[-1]['pos']

        # Если мяч резко изменил направление (особенно по Y)
        dy1 = pos2[1] - pos1[1]
        dy2 = pos3[1] - pos2[1]

        if dy1 * dy2 < 0 and abs(dy1) > 5 and abs(dy2) > 5:
            return True, self._get_ball_side(pos2)

        return False, None

    def _check_double_bounce(self):
        """Проверка двойного отскока"""
        return self.bounces_in_row >= 2

    def _check_out_of_table(self, ball_pos):
        """Проверка выхода мяча за пределы стола"""
        x, y = ball_pos
        return x < 0 or x > TABLE_WIDTH or y < 0 or y > TABLE_HEIGHT

    def _check_net_touch(self):
        """Проверка касания сетки"""
        if not self._check_net_crossing():
            return False

        # Упрощенная проверка - если мяч слишком низко пересек сетку
        if len(self.ball_trajectory) < 2:
            return False

        last_pos = self.ball_trajectory[-1]['pos']
        net_zone = self.table_zones['net_zone']

        # Проверяем, находится ли мяч в зоне сетки
        return (net_zone['x1'] <= last_pos[0] <= net_zone['x2'] and
                net_zone['y1'] <= last_pos[1] <= net_zone['y2'])

    def _determine_point_winner(self, reason):
        """Определение победителя очка"""
        if "отскок" in reason.lower():
            return 1 - self.last_bounce_side if self.last_bounce_side is not None else 0
        elif "сетка" in reason.lower():
            return 1 - self.last_hitter if self.last_hitter is not None else 0
        else:
            return 1 - self.last_hitter if self.last_hitter is not None else 0

    def end_point(self, winner, timestamp):
        """Завершение очка"""
        self.game_state = "POINT_END"
        self.score[winner] += 1

        # Обновляем данные очка
        self.current_point_data['end_time'] = timestamp
        self.current_point_data['duration'] = timestamp - self.current_point_data['start_time']
        self.current_point_data['winner'] = winner
        self.current_point_data['rally_count'] = self.rally_count

        # Статистика скорости
        if self.ball_speed_history:
            self.current_point_data['max_speed'] = max(self.ball_speed_history)
            self.current_point_data['avg_speed'] = np.mean(self.ball_speed_history)

        # Сохраняем историю
        self.game_history.append(self.current_point_data.copy())

        # Обновляем общую статистику
        self.total_rallies += self.rally_count
        self.max_rally = max(self.max_rally, self.rally_count)

        # Смена подачи
        self.serves_in_row += 1
        if self.serves_in_row >= GAME_RULES['serves_per_turn']:
            self.current_server = 1 - self.current_server
            self.serves_in_row = 0

        # Вывод информации
        self._print_point_summary(winner)

        # Проверка конца матча
        if self._is_match_complete():
            self.game_state = "MATCH_END"
            print("\n🎊 МАТЧ ЗАВЕРШЕН!")
            print(f"   ФИНАЛЬНЫЙ СЧЁТ: {self.score[0]} - {self.score[1]}")

    def _print_point_summary(self, winner):
        """Вывод информации о завершенном очке"""
        print("\n" + "=" * 50)
        print(f"🎉 ОЧКО ЗАВЕРШЕНО!")
        print(f"   Победитель: Игрок {winner + 1}")
        print(f"   Счёт: {self.score[0]} - {self.score[1]}")
        print(f"   Количество ударов: {self.rally_count}")
        print(f"   Длительность: {self.current_point_data['duration']:.1f} сек")
        print("=" * 50)

    def _is_match_complete(self):
        """Проверка завершения матча"""
        max_score = max(self.score)
        min_score = min(self.score)

        return (max_score >= GAME_RULES['winning_score'] and
                (max_score - min_score) >= GAME_RULES['min_lead'])

    def get_game_info(self):
        """Получение информации об игре"""
        avg_speed = np.mean(self.ball_speed_history) if self.ball_speed_history else 0
        max_speed = max(self.ball_speed_history) if self.ball_speed_history else 0

        return {
            'score': self.score,
            'server': self.current_server,
            'game_state': self.game_state,
            'rally_count': self.rally_count,
            'max_speed': max_speed,
            'avg_speed': avg_speed,
            'total_points': len(self.game_history)
        }

    def reset_game(self):
        """Сброс игры"""
        self.__init__()
        print("🔄 Игра сброшена")