"""
Аналитика, сохранение данных, TTS
"""
import json
import pandas as pd
from datetime import datetime
import os
from sympy.stats.sampling.sample_numpy import numpy as np

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class Analytics:
    def __init__(self):
        self.match_start_time = datetime.now()
        self.last_announced_score = None

        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
        else:
            self.tts_engine = None
            print("⚠️ TTS не доступен, установите pyttsx3")

    def announce_score(self, score):
        """Озвучивание счета"""
        if not TTS_AVAILABLE or self.tts_engine is None:
            return

        if self.last_announced_score != tuple(score):
            score_text = self._format_score_text(score)
            self.tts_engine.say(score_text)
            self.tts_engine.runAndWait()
            self.last_announced_score = tuple(score)

    def _format_score_text(self, score):
        """Форматирование текста для TTS"""
        p1, p2 = score

        if p1 >= 10 and p2 >= 10:
            if p1 == p2:
                return "десять — десять"
            elif p1 > p2:
                return f"десять — {self._number_to_words(p2)}"
            else:
                return f"{self._number_to_words(p1)} — десять"
        else:
            return f"{self._number_to_words(p1)} — {self._number_to_words(p2)}"

    def _number_to_words(self, n):
        """Преобразование числа в слова (русский)"""
        numbers = {
            0: "ноль", 1: "один", 2: "два", 3: "три", 4: "четыре",
            5: "пять", 6: "шесть", 7: "семь", 8: "восемь", 9: "девять",
            10: "десять", 11: "одиннадцать"
        }
        return numbers.get(n, str(n))

    def save_game_analytics(self, game_history, game_info, match_stats=None):
        """Сохранение аналитики игры"""
        if not game_history:
            print("⚠️ Нет данных для сохранения")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Сохраняем CSV
        csv_data = self._prepare_csv_data(game_history, game_info)
        csv_filename = f"analytics/pingpong_analytics_{timestamp}.csv"
        os.makedirs("analytics", exist_ok=True)
        csv_data.to_csv(csv_filename, index=False)

        # Сохраняем JSON
        json_data = self._prepare_json_data(game_history, game_info, match_stats)
        json_filename = f"analytics/pingpong_match_{timestamp}.json"

        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)

        print(f"\n📊 Аналитика сохранена:")
        print(f"   CSV: {csv_filename}")
        print(f"   JSON: {json_filename}")

        return csv_filename, json_filename

    def _prepare_csv_data(self, game_history, game_info):
        """Подготовка данных для CSV"""
        df = pd.DataFrame(game_history)

        # Добавляем общие колонки
        df['match_date'] = self.match_start_time.strftime("%Y-%m-%d")
        df['match_time'] = self.match_start_time.strftime("%H:%M:%S")

        return df

    def _prepare_json_data(self, game_history, game_info, match_stats=None):
        """Подготовка данных для JSON"""
        if match_stats is None:
            match_stats = self._calculate_match_stats(game_history, game_info)

        json_data = {
            'match_info': {
                'date': self.match_start_time.strftime("%Y-%m-%d"),
                'time': self.match_start_time.strftime("%H:%M:%S"),
                'duration_seconds': (datetime.now() - self.match_start_time).total_seconds(),
                'final_score': f"{game_info['score'][0]}-{game_info['score'][1]}",
                'winner': "Player 1" if game_info['score'][0] > game_info['score'][1] else "Player 2"
            },
            'statistics': match_stats,
            'point_by_point': game_history
        }

        return json_data

    def _calculate_match_stats(self, game_history, game_info):
        """Расчет статистики матча"""
        total_points = len(game_history)
        total_rallies = sum(point['rally_count'] for point in game_history)

        player1_wins = sum(1 for point in game_history if point['winner'] == 0)
        player2_wins = sum(1 for point in game_history if point['winner'] == 1)

        avg_point_duration = np.mean([point['duration'] for point in game_history]) if game_history else 0
        avg_rally_per_point = total_rallies / total_points if total_points > 0 else 0

        max_speeds = [point['max_speed'] for point in game_history if point['max_speed'] > 0]
        avg_max_speed = np.mean(max_speeds) if max_speeds else 0

        return {
            'total_points': total_points,
            'player1_score': game_info['score'][0],
            'player2_score': game_info['score'][1],
            'player1_wins': player1_wins,
            'player2_wins': player2_wins,
            'total_rallies': total_rallies,
            'avg_rally_per_point': avg_rally_per_point,
            'avg_point_duration': avg_point_duration,
            'avg_max_speed': avg_max_speed,
            'player1_win_percentage': player1_wins / total_points * 100 if total_points > 0 else 0,
            'player2_win_percentage': player2_wins / total_points * 100 if total_points > 0 else 0
        }