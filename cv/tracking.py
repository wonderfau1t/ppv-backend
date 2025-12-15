import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque

# --- Параметры гомографии ---
src_pts = np.array([
    [776, 400],  # верхний левый угол стола
    [1192, 424],  # верхний правый угол стола
    [1292, 960],  # нижний правый угол стола
    [537, 904]  # нижний левый угол стола
], dtype=np.float32)

width, height = 1000, 500
dst_pts = np.array([
    [0, 0],
    [width, 0],
    [width, height],
    [0, height]
], dtype=np.float32)

# Вычисляем матрицу гомографии (H)
H, _ = cv2.findHomography(src_pts, dst_pts)

# --- Загрузка модели ---
model = YOLO('runs/content/runs/detect/train/weights/best.pt')

# --- Видеопоток ---
cap = cv2.VideoCapture('train2.mp4')

# --- Константы ---
BALL_CLASS_ID = 2  # ID класса мяча в вашей модели
RACKET_CLASS_ID = 1  # ID класса ракетки
PLAYER_CLASS_ID = 3  # ID класса игрока
MAX_BALL_HISTORY = 30

# --- История траектории мяча ---
ball_history = deque(maxlen=MAX_BALL_HISTORY)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    frame_display = frame.copy()

    # --- Трекинг мяча ---
    tracked_balls = []

    # Используем track для мяча
    results = model.track(
        frame,
        classes=[BALL_CLASS_ID],
        persist=True,
        verbose=False,
        conf=0.3,
        iou=0.5,
        tracker="bytetrack.yaml"
    )

    if results and len(results) > 0:
        result = results[0]  # Берем первый результат
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes[i]

                # Извлекаем данные корректно
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())

                # Проверяем наличие ID и извлекаем корректно
                if box.id is not None:
                    track_id = int(box.id[0].cpu().numpy())
                else:
                    track_id = frame_count  # Используем номер кадра как временный ID

                # Центр мяча
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                # Проецируем на плоскость стола
                ball_point = np.array([[[cx, cy]]], dtype=np.float32)
                ball_on_table = cv2.perspectiveTransform(ball_point, H)[0][0]

                # Рассчитываем скорость
                speed = 0
                if len(ball_history) > 0:
                    # Ищем предыдущую позицию этого мяча
                    for prev_ball in reversed(list(ball_history)):
                        if prev_ball['id'] == track_id:
                            last_pos = prev_ball['pos_table']
                            speed = np.sqrt((ball_on_table[0] - last_pos[0]) ** 2 +
                                            (ball_on_table[1] - last_pos[1]) ** 2)
                            break

                ball_data = {
                    'id': track_id,
                    'bbox': (x1, y1, x2, y2),
                    'center': (cx, cy),
                    'pos_table': (int(ball_on_table[0]), int(ball_on_table[1])),
                    'conf': conf,
                    'speed': speed
                }
                tracked_balls.append(ball_data)

                # Добавляем в историю
                ball_history.append(ball_data)

    # --- Детекция игроков и ракеток ---
    detected_objects = []

    # Используем predict для статических объектов
    det_results = model.predict(
        frame,
        classes=[RACKET_CLASS_ID, PLAYER_CLASS_ID],
        conf=0.3,
        verbose=False
    )

    if det_results and len(det_results) > 0:
        result = det_results[0]
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes[i]

                # Извлекаем данные
                cls = int(box.cls[0].cpu().numpy())
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())

                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                # Определяем сторону
                player_side = "left" if cx < frame.shape[1] // 2 else "right"

                detected_objects.append({
                    'class': cls,
                    'class_name': "Racket" if cls == RACKET_CLASS_ID else "Player",
                    'bbox': (x1, y1, x2, y2),
                    'center': (cx, cy),
                    'conf': conf,
                    'side': player_side
                })

    # --- Создание вида сверху ---
    table_view = np.zeros((height, width, 3), dtype=np.uint8)

    # Рисуем стол
    cv2.rectangle(table_view, (0, 0), (width, height), (50, 150, 50), 2)
    cv2.line(table_view, (width // 2, 0), (width // 2, height), (255, 255, 255), 2)

    # Зоны подачи
    service_line = width // 4
    cv2.line(table_view, (service_line, 0), (service_line, height), (70, 130, 70), 1)
    cv2.line(table_view, (width - service_line, 0), (width - service_line, height), (70, 130, 70), 1)

    # --- Визуализация на основном кадре ---

    # 1. Контур стола
    cv2.polylines(frame_display, [src_pts.astype(np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

    # 2. Сетка
    mid_top = ((src_pts[0] + src_pts[1]) / 2).astype(int)
    mid_bottom = ((src_pts[3] + src_pts[2]) / 2).astype(int)
    cv2.line(frame_display, tuple(mid_top), tuple(mid_bottom), (0, 255, 255), 2)

    # 3. Отрисовка мячей
    for ball in tracked_balls:
        x1, y1, x2, y2 = ball['bbox']
        cx, cy = ball['center']
        pos_x, pos_y = ball['pos_table']
        ball_id = ball['id']
        conf = ball['conf']
        speed = ball['speed']

        # Bounding box
        cv2.rectangle(frame_display, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.circle(frame_display, (cx, cy), 5, (0, 0, 255), -1)

        # Подпись
        label = f'Ball {ball_id}: {conf:.2f} ({speed:.1f} px/frame)'
        cv2.putText(frame_display, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # На виде сверху
        cv2.circle(table_view, (pos_x, pos_y), 5, (0, 0, 255), -1)
        cv2.putText(table_view, f'B{ball_id}', (pos_x + 5, pos_y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # 4. Рисуем траекторию мяча
    if len(ball_history) > 1:
        # Группируем по ID мяча
        ball_trajectories = {}
        for item in ball_history:
            ball_id = item['id']
            if ball_id not in ball_trajectories:
                ball_trajectories[ball_id] = []
            ball_trajectories[ball_id].append(item['pos_table'])

        # Рисуем траектории для каждого мяча
        for ball_id, trajectory in ball_trajectories.items():
            if len(trajectory) > 1:
                for i in range(1, len(trajectory)):
                    alpha = i / len(trajectory)
                    color = (0, int(255 * alpha), int(255 * (1 - alpha)))
                    cv2.line(table_view, trajectory[i - 1], trajectory[i], color, 2)

    # 5. Отрисовка игроков и ракеток
    color_map = {
        RACKET_CLASS_ID: (255, 100, 0),  # Оранжевый
        PLAYER_CLASS_ID: (255, 255, 0)  # Желтый
    }

    for obj in detected_objects:
        x1, y1, x2, y2 = obj['bbox']
        conf = obj['conf']
        class_name = obj['class_name']
        side = obj['side']

        color = color_map.get(obj['class'], (255, 255, 255))
        cv2.rectangle(frame_display, (x1, y1), (x2, y2), color, 2)

        label = f"{class_name} {conf:.2f} ({side})"
        cv2.putText(frame_display, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 6. Статистика
    stats_text = [
        f"Frame: {frame_count}",
        f"Balls: {len(tracked_balls)}",
        f"Players: {len([o for o in detected_objects if o['class'] == PLAYER_CLASS_ID])}",
        f"Rackets: {len([o for o in detected_objects if o['class'] == RACKET_CLASS_ID])}"
    ]

    for i, text in enumerate(stats_text):
        cv2.putText(frame_display, text, (10, 30 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # --- Показ окон ---
    cv2.imshow("Ping Pong Detection", frame_display)
    cv2.imshow("Table Top View", table_view)

    # --- Управление ---
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == ord('r'):  # Сброс истории
        ball_history.clear()
        print("История траектории сброшена")
    elif key == ord('p'):  # Пауза
        cv2.waitKey(0)

# --- Очистка ---
cap.release()
cv2.destroyAllWindows()
print(f"Обработано кадров: {frame_count}")
