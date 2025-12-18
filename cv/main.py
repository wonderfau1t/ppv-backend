"""
Главный файл для запуска системы анализа настольного тенниса
"""
import cv2
from gamecode.config import *
from gamecode.utils import load_calibration
from gamecode.object_tracker import ObjectTracker
from gamecode.game_logic import TableTennisLogic, TableGeometry
from gamecode.visualization import Visualizer
from gamecode.analytics import Analytics
import time

def main():
    # 1. Загрузка калибровки
    calibration_data = load_calibration()
    if calibration_data:
        src_points = np.array(calibration_data['table_points'], dtype=np.float32)
        H = np.array(calibration_data['homography_matrix'])
        print("✅ Калибровка загружена")
    else:
        print("⚠️ Используются значения по умолчанию")
        src_points = HOMOGRAPHY_CONFIG['src_points']
        H = update_homography(src_points)

    # 2. Инициализация компонентов
    print("\nИнициализация компонентов...")
    table = TableGeometry(
        left=0,
        right=TABLE_WIDTH,
        top=0,
        bottom=TABLE_HEIGHT,
        net=TABLE_HEIGHT / 2
    )

    # Трекер объектов
    tracker = ObjectTracker(
        model_path=YOLO_CONFIG['model_path'],
        homography_matrix=H
    )

    # Логика игры
    game = TableTennisLogic(table)

    # Визуализация
    visualizer = Visualizer(H, src_points)

    # Аналитика и TTS
    # analytics = Analytics()

    # 3. Загрузка видео
    video_source = 'train2.mp4'  # или 0 для веб-камеры
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print(f"❌ Не удалось открыть видео: {video_source}")
        return

    print(f"\n🎬 Видео: {video_source}")
    print("   Управление:")
    print("   - ESC: Выход")
    print("   - R: Сброс игры")
    print("   - S: Сохранить аналитику")
    print("   - P: Пауза")
    print("=" * 60)

    # 4. Главный цикл обработки
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("📼 Конец видео")
                break

            # Детекция объектов
            tracked_objects = tracker.detect_objects(frame)

            # Обработка логики игры
            if tracked_objects["balls"]:
                ball = tracked_objects["balls"][0]

                game.update_ball(
                    x=ball["pos_table"][0],
                    y=ball["pos_table"][1],
                    t=ball["timestamp"],
                    speed=ball["speed"],
                    speed_vec=ball["velocity"],
                    rackets=tracked_objects["racket_positions"]
                )

            # Получение информации об игре
            game_info = game.get_game_info()

            # Озвучивание счета
            # analytics.announce_score(game_info['score'])

            # Визуализация
            frame_display = visualizer.draw_main_frame(frame, tracked_objects, game_info)

            table_view = visualizer.draw_table_view(
                tracked_objects,
                game_info,
                tracker.get_ball_trajectory()
            )

            # Отображение
            cv2.imshow("Ping Pong Game", frame_display)
            cv2.imshow("Table View", table_view)

            # Управление
            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC
                break
            elif key == ord('r'):  # Reset
                game.reset_game()
                tracker.clear_history()
            # elif key == ord('s'):  # Save analytics
            #     # analytics.save_game_analytics(game.game_history, game_info)
            elif key == ord('p'):  # Pause
                cv2.waitKey(0)

    except KeyboardInterrupt:
        print("\n⏹️ Прервано пользователем")

    finally:
        # 5. Завершение
        cap.release()
        cv2.destroyAllWindows()

        # Сохранение аналитики при выходе
        # if game.game_history:
        #     print("\n💾 Автосохранение аналитики...")
        #     analytics.save_game_analytics(game.game_history, game.get_game_info())

        print("\n🎮 Система анализа завершила работу")
        print("=" * 60)


if __name__ == "__main__":
    main()