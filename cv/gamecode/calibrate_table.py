import cv2
import numpy as np
import json
import os


class TableCalibrator:
    def __init__(self, video_source):
        self.video_source = video_source
        self.cap = cv2.VideoCapture(video_source)

        if not self.cap.isOpened():
            print(f"❌ Не удалось открыть видео: {video_source}")
            # Попробуем веб-камеру как запасной вариант
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                exit(1)

        # Читаем первый кадр
        ret, self.original_frame = self.cap.read()
        if not ret:
            print("❌ Не удалось прочитать кадр из видео")
            exit(1)

        # Параметры масштабирования
        self.scale_factor = 1.0
        self.display_size = (800, 600)  # Размер окна по умолчанию
        self.pan_offset = [0, 0]  # Смещение для панорамирования
        self.dragging = False
        self.drag_start = (0, 0)

        # Точки калибровки
        self.points = []  # 4 точки стола
        self.net_points = []  # 2 точки сетки
        self.mode = 'table'  # 'table' или 'net'
        self.window_name = 'Table Calibration'

        print("✅ Видео загружено успешно")
        print(f"   Оригинальный размер: {self.original_frame.shape[1]}x{self.original_frame.shape[0]}")

        # Рассчитываем начальный масштаб для отображения
        self.calculate_initial_scale()

    def calculate_initial_scale(self):
        """Рассчитать начальный масштаб для отображения"""
        h, w = self.original_frame.shape[:2]

        # Максимальный размер для отображения
        max_display_width = 1200
        max_display_height = 800

        # Рассчитываем масштаб
        scale_w = max_display_width / w
        scale_h = max_display_height / h

        self.scale_factor = min(scale_w, scale_h, 1.0)  # Не увеличиваем, если кадр маленький

        # Размер окна
        display_w = int(w * self.scale_factor)
        display_h = int(h * self.scale_factor)
        self.display_size = (display_w, display_h)

        print(f"   Масштаб: {self.scale_factor:.2f}x")
        print(f"   Размер отображения: {display_w}x{display_h}")

    def get_display_frame(self):
        """Получить кадр для отображения с масштабированием"""
        if self.scale_factor == 1.0 and self.pan_offset == [0, 0]:
            return self.original_frame.copy()

        # Применяем масштабирование
        if self.scale_factor != 1.0:
            scaled_w = int(self.original_frame.shape[1] * self.scale_factor)
            scaled_h = int(self.original_frame.shape[0] * self.scale_factor)
            scaled_frame = cv2.resize(self.original_frame, (scaled_w, scaled_h))
        else:
            scaled_frame = self.original_frame.copy()

        # Применяем панорамирование если нужно
        if self.pan_offset != [0, 0]:
            h, w = scaled_frame.shape[:2]
            M = np.float32([[1, 0, self.pan_offset[0]], [0, 1, self.pan_offset[1]]])
            scaled_frame = cv2.warpAffine(scaled_frame, M, (w, h))

        return scaled_frame

    def mouse_callback(self, event, x, y, flags, param):
        """Обработчик событий мыши"""
        # Корректируем координаты с учетом масштаба и панорамирования
        if self.scale_factor != 1.0:
            orig_x = int(x / self.scale_factor - self.pan_offset[0] / self.scale_factor)
            orig_y = int(y / self.scale_factor - self.pan_offset[1] / self.scale_factor)
        else:
            orig_x = x - self.pan_offset[0]
            orig_y = y - self.pan_offset[1]

        # Ограничиваем координаты размерами оригинала
        h, w = self.original_frame.shape[:2]
        orig_x = max(0, min(orig_x, w - 1))
        orig_y = max(0, min(orig_y, h - 1))

        # Панорамирование с помощью средней кнопки мыши
        if event == cv2.EVENT_MBUTTONDOWN:
            self.dragging = True
            self.drag_start = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging:
                dx = x - self.drag_start[0]
                dy = y - self.drag_start[1]
                self.pan_offset[0] += dx
                self.pan_offset[1] += dy
                self.drag_start = (x, y)

        elif event == cv2.EVENT_MBUTTONUP:
            self.dragging = False

        # Добавление/удаление точек
        elif event == cv2.EVENT_LBUTTONDOWN:
            if self.mode == 'table' and len(self.points) < 4:
                self.points.append((orig_x, orig_y))
                print(f"📌 Точка стола {len(self.points)}: ({orig_x}, {orig_y})")
            elif self.mode == 'net' and len(self.net_points) < 2:
                self.net_points.append((orig_x, orig_y))
                print(f"📌 Точка сетки {len(self.net_points)}: ({orig_x}, {orig_y})")

        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.mode == 'table' and self.points:
                removed = self.points.pop()
                print(f"🗑️ Удалена точка стола: {removed}. Осталось: {len(self.points)}")
            elif self.mode == 'net' and self.net_points:
                removed = self.net_points.pop()
                print(f"🗑️ Удалена точка сетки: {removed}. Осталось: {len(self.net_points)}")

    def draw_points(self, display_frame):
        """Рисование точек и линий на отображаемом кадре"""
        frame_copy = display_frame.copy()

        # Преобразуем точки для отображения
        display_points = []
        for (orig_x, orig_y) in self.points:
            if self.scale_factor != 1.0:
                disp_x = int(orig_x * self.scale_factor + self.pan_offset[0])
                disp_y = int(orig_y * self.scale_factor + self.pan_offset[1])
            else:
                disp_x = orig_x + self.pan_offset[0]
                disp_y = orig_y + self.pan_offset[1]
            display_points.append((disp_x, disp_y))

        # Рисуем точки стола
        for i, (x, y) in enumerate(display_points):
            color = (0, 255, 0) if i < 2 else (0, 165, 255)  # Зеленые и оранжевые
            # Увеличиваем размер точек при масштабировании
            point_size = max(8, int(10 * self.scale_factor))
            cv2.circle(frame_copy, (x, y), point_size, color, -1)
            cv2.circle(frame_copy, (x, y), point_size + 2, (255, 255, 255), 2)

            # Увеличиваем размер текста
            font_scale = max(0.5, 0.8 * self.scale_factor)
            cv2.putText(frame_copy, str(i + 1), (x + 15, y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

        # Соединяем точки стола линиями
        if len(display_points) == 4:
            # Рисуем контур стола
            pts = np.array(display_points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame_copy, [pts], True, (0, 255, 255), max(2, int(3 * self.scale_factor)))
        elif len(display_points) > 1:
            # Рисуем линии между существующими точками
            for i in range(len(display_points) - 1):
                cv2.line(frame_copy, display_points[i], display_points[i + 1],
                         (0, 200, 200), max(2, int(3 * self.scale_factor)))

        # Преобразуем и рисуем точки сетки
        display_net_points = []
        for (orig_x, orig_y) in self.net_points:
            if self.scale_factor != 1.0:
                disp_x = int(orig_x * self.scale_factor + self.pan_offset[0])
                disp_y = int(orig_y * self.scale_factor + self.pan_offset[1])
            else:
                disp_x = orig_x + self.pan_offset[0]
                disp_y = orig_y + self.pan_offset[1]
            display_net_points.append((disp_x, disp_y))

        # Рисуем точки сетки
        for i, (x, y) in enumerate(display_net_points):
            point_size = max(8, int(10 * self.scale_factor))
            cv2.circle(frame_copy, (x, y), point_size, (255, 255, 0), -1)  # Голубой
            cv2.circle(frame_copy, (x, y), point_size + 2, (255, 255, 255), 2)

            font_scale = max(0.5, 0.8 * self.scale_factor)
            cv2.putText(frame_copy, f"N{i + 1}", (x + 15, y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

        # Рисуем линию сетки
        if len(display_net_points) == 2:
            cv2.line(frame_copy, display_net_points[0], display_net_points[1],
                     (255, 255, 0), max(3, int(4 * self.scale_factor)))

        # Инструкции
        instructions = [
            "=== TABLE TENNIS CALIBRATION ===",
            f"MODE: {self.mode.upper()}",
            f"SCALE: {self.scale_factor:.2f}x",
            "LEFT CLICK: Add point",
            "RIGHT CLICK: Remove last point",
            "MIDDLE MOUSE: Drag to pan",
            "MOUSE WHEEL: Zoom in/out",
            "+/-: Zoom in/out",
            "0: Reset zoom and pan",
            "T: Switch to TABLE mode",
            "N: Switch to NET mode",
            "F: Next frame",
            "C: Clear all points",
            "S: Save calibration",
            "Q: Quit",
            "",
            f"Table points: {len(self.points)}/4",
            f"Net points: {len(self.net_points)}/2"
        ]

        # Фон для текста
        font_scale = 0.6
        line_height = 25

        for i, text in enumerate(instructions):
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)[0]
            cv2.rectangle(frame_copy, (5, 20 + i * line_height),
                          (10 + text_size[0], 15 + (i + 1) * line_height),
                          (0, 0, 0), -1)

        # Текст инструкций
        for i, text in enumerate(instructions):
            color = (255, 255, 255)
            if "MODE:" in text:
                color = (0, 255, 255) if self.mode == 'table' else (255, 255, 0)
            elif "SCALE:" in text:
                color = (255, 200, 0)

            cv2.putText(frame_copy, text, (10, 40 + i * line_height),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1)

        # Добавляем индикатор панорамирования
        if self.pan_offset != [0, 0]:
            cv2.putText(frame_copy, f"PAN: {self.pan_offset}",
                        (frame_copy.shape[1] - 200, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        return frame_copy

    def zoom(self, factor_change):
        """Изменение масштаба"""
        old_scale = self.scale_factor
        self.scale_factor = max(0.1, min(3.0, self.scale_factor + factor_change))

        # Корректируем смещение при изменении масштаба
        if old_scale != 0:
            scale_ratio = self.scale_factor / old_scale
            self.pan_offset[0] *= scale_ratio
            self.pan_offset[1] *= scale_ratio

        print(f"🔍 Масштаб: {self.scale_factor:.2f}x")

    def reset_view(self):
        """Сброс масштаба и панорамирования"""
        self.scale_factor = 1.0
        self.pan_offset = [0, 0]
        print("🔄 Вид сброшен")

    def calculate_homography(self):
        """Вычисление матрицы гомографии"""
        if len(self.points) != 4:
            print("⚠️ Need 4 table points!")
            return None

        # Стандартные размеры стола для настольного тенниса
        TABLE_WIDTH_CM = 152.5  # Ширина (короткая сторона)
        TABLE_LENGTH_CM = 274  # Длина (длинная сторона)

        # Размеры для вида сверху
        dst_width = 1000
        dst_height = int(dst_width * (TABLE_LENGTH_CM / TABLE_WIDTH_CM))

        src_pts = np.array(self.points, dtype=np.float32)

        # Определяем порядок точек
        # Сортируем по Y координате
        sorted_by_y = sorted(self.points, key=lambda x: x[1])
        top_points = sorted_by_y[:2]
        bottom_points = sorted_by_y[2:]

        # Сортируем верхние и нижние точки по X
        top_points = sorted(top_points, key=lambda x: x[0])
        bottom_points = sorted(bottom_points, key=lambda x: x[0])

        # Новый порядок: верх-левый, верх-правый, низ-правый, низ-левый
        ordered_src = np.array([
            top_points[0],  # Top-left
            top_points[1],  # Top-right
            bottom_points[1],  # Bottom-right
            bottom_points[0]  # Bottom-left
        ], dtype=np.float32)

        dst_pts = np.array([
            [0, 0],
            [dst_width, 0],
            [dst_width, dst_height],
            [0, dst_height]
        ], dtype=np.float32)

        H, _ = cv2.findHomography(ordered_src, dst_pts)
        return H, (dst_width, dst_height), ordered_src

    def save_calibration(self, filename='calibration.json'):
        """Сохранение калибровки в файл"""
        if len(self.points) != 4:
            print("❌ Need exactly 4 table points to save!")
            return None

        homography_result = self.calculate_homography()
        if not homography_result:
            return None

        H, table_size, ordered_points = homography_result

        calibration_data = {
            'video_source': self.video_source,
            'table_points': ordered_points.tolist(),
            'net_points': self.net_points,
            'frame_size': {
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            },
            'homography_matrix': H.tolist(),
            'table_view_size': table_size,
            'real_table_dimensions': {
                'width_cm': 152.5,
                'length_cm': 274,
                'net_height_cm': 15.25
            }
        }

        with open(filename, 'w') as f:
            json.dump(calibration_data, f, indent=2)

        print(f"✅ Калибровка сохранена в {filename}")
        print(f"   Размер вида сверху: {table_size[0]}x{table_size[1]}")

        # Показываем предпросмотр
        self.show_preview(calibration_data)

        return calibration_data

    def show_preview(self, calibration_data):
        """Показать предпросмотр калибровки"""
        H = np.array(calibration_data['homography_matrix'])
        dst_width, dst_height = calibration_data['table_view_size']

        # Преобразуем кадр
        warped = cv2.warpPerspective(self.original_frame, H, (dst_width, dst_height))

        # Рисуем разметку на виде сверху
        cv2.line(warped, (dst_width // 2, 0), (dst_width // 2, dst_height),
                 (0, 255, 255), 3)

        # Зоны подачи
        service_line = dst_width // 6
        cv2.line(warped, (service_line, 0), (service_line, dst_height),
                 (100, 100, 255), 2)
        cv2.line(warped, (dst_width - service_line, 0), (dst_width - service_line, dst_height),
                 (100, 100, 255), 2)

        cv2.imshow('Top View Preview', warped)
        cv2.waitKey(2000)

        # Сохраняем предпросмотр
        cv2.imwrite('../table_preview.jpg', warped)
        print("💾 Предпросмотр сохранен как 'table_preview.jpg'")

    def run(self):
        """Основной цикл калибровки"""
        print("\n" + "=" * 60)
        print("TABLE TENNIS TABLE CALIBRATION - WITH ZOOM & PAN")
        print("=" * 60)
        print("\nCONTROLS:")
        print("- Mouse Wheel: Zoom in/out")
        print("- Middle Mouse Button: Drag to pan")
        print("- +/-: Zoom in/out")
        print("- 0: Reset zoom and pan")
        print("- LEFT CLICK: Add point")
        print("- RIGHT CLICK: Remove last point")
        print("- T/N: Switch between TABLE and NET modes")
        print("=" * 60 + "\n")

        # Создаем окно
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.display_size[0], self.display_size[1])

        # Устанавливаем callback для мыши
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        # Создаем trackbar для масштабирования
        cv2.createTrackbar('Zoom', self.window_name,
                           int((self.scale_factor - 0.1) * 100),
                           290,  # 0.1-3.0 = 290 шагов
                           lambda x: None)

        while True:
            # Получаем кадр для отображения
            display_frame = self.get_display_frame()

            # Рисуем точки
            frame_with_points = self.draw_points(display_frame)

            # Обновляем trackbar
            trackbar_val = int((self.scale_factor - 0.1) * 100)
            cv2.setTrackbarPos('Zoom', self.window_name, trackbar_val)

            # Показываем кадр
            cv2.imshow(self.window_name, frame_with_points)

            # Проверяем изменение trackbar
            new_trackbar_val = cv2.getTrackbarPos('Zoom', self.window_name)
            new_scale = 0.1 + new_trackbar_val / 100.0
            if abs(new_scale - self.scale_factor) > 0.01:
                old_scale = self.scale_factor
                self.scale_factor = new_scale
                # Корректируем смещение
                if old_scale != 0:
                    scale_ratio = self.scale_factor / old_scale
                    self.pan_offset[0] *= scale_ratio
                    self.pan_offset[1] *= scale_ratio

            # Обработка клавиш
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:  # Q или ESC
                print("\n👋 Выход из калибровки")
                break

            elif key == ord('s'):  # Save
                if len(self.points) == 4:
                    self.save_calibration()
                else:
                    print("❌ Нужно отметить 4 точки стола!")

            elif key == ord('f'):  # Next frame
                ret, frame = self.cap.read()
                if ret:
                    self.original_frame = frame.copy()
                    print("📸 Переключено на следующий кадр")
                else:
                    print("⚠️ Достигнут конец видео")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            elif key == ord('c'):  # Clear all
                self.points.clear()
                self.net_points.clear()
                print("🗑️ Все точки очищены")

            elif key == ord('t'):  # Switch to TABLE mode
                self.mode = 'table'
                print("📏 Режим: ТОЧКИ СТОЛА")

            elif key == ord('n'):  # Switch to NET mode
                self.mode = 'net'
                print("🏓 Режим: ТОЧКИ СЕТКИ")

            elif key == ord('0'):  # Reset view
                self.reset_view()

            elif key == ord('+') or key == ord('='):  # Zoom in
                self.zoom(0.1)

            elif key == ord('-') or key == ord('_'):  # Zoom out
                self.zoom(-0.1)

            elif key == ord('p'):  # Test projection
                if len(self.points) == 4:
                    self.test_projection()

            elif key == ord('r'):  # Reset to first frame
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, self.original_frame = self.cap.read()
                self.reset_view()
                print("🔁 Возврат к первому кадру")

        # Очистка
        cv2.destroyAllWindows()
        self.cap.release()
        print("\n✅ Калибровка завершена")

    def test_projection(self):
        """Тест проекции нескольких точек"""
        homography_result = self.calculate_homography()
        if not homography_result:
            return

        H, table_size, ordered_points = homography_result

        print("\n" + "=" * 50)
        print("TEST PROJECTION")
        print("=" * 50)

        # Тестовые точки
        test_points = [
            ("Center of frame", (self.original_frame.shape[1] // 2, self.original_frame.shape[0] // 2)),
            ("Top-left corner", (0, 0)),
            ("Bottom-right corner", (self.original_frame.shape[1] - 1, self.original_frame.shape[0] - 1))
        ]

        for name, point in test_points:
            point_array = np.array([[[point[0], point[1]]]], dtype=np.float32)
            projected = cv2.perspectiveTransform(point_array, H)[0][0]

            print(f"{name}:")
            print(f"  Original: ({point[0]}, {point[1]})")
            print(f"  On table: ({projected[0]:.1f}, {projected[1]:.1f})")

            # Проверка, находится ли точка на столе
            if 0 <= projected[0] <= table_size[0] and 0 <= projected[1] <= table_size[1]:
                print(f"  Status: ✅ ON TABLE")
            else:
                print(f"  Status: ❌ OFF TABLE")

        print("=" * 50)


# Упрощенная версия с фиксированным масштабированием
def simple_calibrate(video_path='train2.mp4', window_size=(1200, 800)):
    """Простая калибровка с фиксированным размером окна"""
    print("🚀 Запуск простой калибровки...")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Не удалось открыть видео: {video_path}")
        return None

    # Читаем кадр
    ret, frame = cap.read()
    if not ret:
        print("❌ Не удалось прочитать кадр")
        cap.release()
        return None

    # Рассчитываем масштаб для вписывания в окно
    h, w = frame.shape[:2]
    scale_w = window_size[0] / w
    scale_h = window_size[1] / h
    scale = min(scale_w, scale_h, 1.0)  # Не увеличиваем

    points = []
    original_points = []

    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            # Конвертируем координаты обратно в оригинальные
            orig_x = int(x / scale)
            orig_y = int(y / scale)

            points.append((x, y))
            original_points.append((orig_x, orig_y))

            print(f"Point {len(points)}:")
            print(f"  Display: ({x}, {y})")
            print(f"  Original: ({orig_x}, {orig_y})")

            # Рисуем точку
            cv2.circle(display_frame, (x, y), 8, (0, 255, 0), -1)
            cv2.circle(display_frame, (x, y), 10, (255, 255, 255), 2)
            cv2.putText(display_frame, str(len(points)), (x + 15, y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Рисуем линии между точками
            if len(points) > 1:
                cv2.line(display_frame, points[-2], points[-1], (0, 200, 200), 2)

            cv2.imshow("Simple Calibration", display_frame)

    # Масштабируем кадр для отображения
    display_frame = cv2.resize(frame, None, fx=scale, fy=scale) if scale != 1.0 else frame.copy()

    # Создаем окно
    cv2.namedWindow('Simple Calibration', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Simple Calibration', display_frame.shape[1], display_frame.shape[0])

    # Устанавливаем callback
    cv2.setMouseCallback('Simple Calibration', click_event)

    # Показываем инструкции
    cv2.putText(display_frame, "Click 4 corners of the table", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
    cv2.putText(display_frame, "Click 4 corners of the table", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(display_frame, f"Scale: {scale:.2f}x", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
    cv2.putText(display_frame, f"Scale: {scale:.2f}x", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(display_frame, "Press 'S' to save, 'Q' to quit", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
    cv2.putText(display_frame, "Press 'S' to save, 'Q' to quit", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Simple Calibration", display_frame)

    while True:
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord('s') and len(original_points) == 4:
            # Сохраняем оригинальные точки
            np.save('../table_points.npy', np.array(original_points, dtype=np.float32))
            print(f"✅ Точки сохранены в 'table_points.npy'")

            # Вычисляем гомографию
            width, height = 1000, 500
            src_pts = np.array(original_points, dtype=np.float32)
            dst_pts = np.array([[0, 0], [width, 0], [width, height], [0, height]],
                               dtype=np.float32)

            H, _ = cv2.findHomography(src_pts, dst_pts)
            np.save('../homography_matrix.npy', H)
            print(f"✅ Матрица гомографии сохранена в 'homography_matrix.npy'")

            # Создаем JSON файл
            calibration_data = {
                'table_points': original_points,
                'homography_matrix': H.tolist(),
                'table_view_size': (width, height),
                'scale_factor': scale,
                'window_size': window_size
            }

            with open('../simple_calibration.json', 'w') as f:
                json.dump(calibration_data, f, indent=2)

            print(f"✅ Полная калибровка сохранена в 'simple_calibration.json'")
            break

        elif key == ord('c') and points:
            points.pop()
            original_points.pop()
            print(f"🗑️ Удалена последняя точка. Осталось: {len(points)}")

            # Перерисовываем кадр
            display_frame = cv2.resize(frame, None, fx=scale, fy=scale) if scale != 1.0 else frame.copy()

            # Перерисовываем оставшиеся точки
            for i, (x, y) in enumerate(points):
                cv2.circle(display_frame, (x, y), 8, (0, 255, 0), -1)
                cv2.circle(display_frame, (x, y), 10, (255, 255, 255), 2)
                cv2.putText(display_frame, str(i + 1), (x + 15, y + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                if i > 0:
                    cv2.line(display_frame, points[i - 1], points[i], (0, 200, 200), 2)

            # Показываем инструкции
            cv2.putText(display_frame, "Click 4 corners of the table", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
            cv2.putText(display_frame, "Click 4 corners of the table", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Scale: {scale:.2f}x", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
            cv2.putText(display_frame, f"Scale: {scale:.2f}x", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_frame, "Press 'S' to save, 'Q' to quit", (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
            cv2.putText(display_frame, "Press 'S' to save, 'Q' to quit", (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Simple Calibration", display_frame)

    cv2.destroyAllWindows()
    cap.release()

    if len(original_points) == 4:
        return np.array(original_points, dtype=np.float32)
    return None


# Главная функция
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        video_source = sys.argv[1]
    else:
        video_source = 'train2.mp4'  # или 0 для веб-камеры

    print(f"🎬 Источник видео: {video_source}")

    print("\nВыберите режим калибровки:")
    print("1. Полная калибровка с масштабированием и панорамированием")
    print("2. Простая калибровка (рекомендуется)")
    print("3. Выход")

    choice = input("\nВведите номер (1-3): ").strip()

    if choice == '1':
        # Полная калибровка
        calibrator = TableCalibrator(video_source)
        calibrator.run()
    elif choice == '2':
        # Простая калибровка
        points = simple_calibrate(video_source)

        if points is not None:
            print(f"\n✅ Калибровка завершена успешно!")
            print(f"📏 Точки стола (оригинальные координаты):")
            for i, (x, y) in enumerate(points):
                print(f"   {i + 1}: ({x:.0f}, {y:.0f})")

            print("\n🚀 Теперь можно использовать эти точки в основном коде!")
    else:
        print("👋 Выход")