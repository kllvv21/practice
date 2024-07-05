from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QHBoxLayout, QVBoxLayout, QMainWindow, QPushButton, \
    QComboBox, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
import cv2
import numpy as np


class MainWindow(QMainWindow):
    """Основное окно фоторедактора"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Фоторедактор")
        self.setGeometry(50, 50, 500, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setFixedSize(750, 430)
        self.image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()

        self.button1 = QPushButton("Выбор изображения на компьютере")
        button_layout.addWidget(self.button1)
        self.button1.setFixedHeight(35)
        self.button1.clicked.connect(self.open_image)

        self.button2 = QPushButton("Включение веб-камеры")
        button_layout.addWidget(self.button2)
        self.button2.setFixedHeight(35)
        self.button2.clicked.connect(self.start_camera)
        self.button2.clicked.connect(self.show_button)

        self.capture_button = QPushButton("Сделать фото")
        self.capture_button.hide()
        button_layout.addWidget(self.capture_button)
        self.capture_button.setFixedHeight(35)
        self.capture_button.clicked.connect(self.capture_image)

        main_layout.addLayout(button_layout)

        self.combobox = QComboBox()
        self.combobox.setFixedHeight(30)
        self.combobox.addItems(["Все каналы", "Красный канал", "Зеленый канал", "Синий канал"])
        self.combobox.currentIndexChanged.connect(self.update_image_channel)
        main_layout.addWidget(self.combobox)

        input_layout = QHBoxLayout()

        self.label = QLabel("Изменение размера изображения")
        input_layout.addWidget(self.label)

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Высота")
        input_layout.addWidget(self.height_input)

        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Ширина")
        input_layout.addWidget(self.width_input)

        main_layout.addLayout(input_layout)

        input_layout2 = QHBoxLayout()

        self.bright_label = QLabel("Понизить яркость")
        input_layout2.addWidget(self.bright_label)
        self.brightness_input = QLineEdit()
        self.brightness_input.setPlaceholderText("Понижение яркости")
        input_layout2.addWidget(self.brightness_input)
        main_layout.addLayout(input_layout2)

        circle_layout = QHBoxLayout()

        self.circle_label = QLabel("Нарисовать круг")
        circle_layout.addWidget(self.circle_label)
        self.center_x_input = QLineEdit()
        self.center_x_input.setPlaceholderText("Координата X центра круга")
        circle_layout.addWidget(self.center_x_input)

        self.center_y_input = QLineEdit()
        self.center_y_input.setPlaceholderText("Координата Y центра круга")
        circle_layout.addWidget(self.center_y_input)

        self.radius_input = QLineEdit()
        self.radius_input.setPlaceholderText("Радиус круга")
        circle_layout.addWidget(self.radius_input)

        main_layout.addLayout(circle_layout)

        action_button_layout = QHBoxLayout()

        self.apply_button = QPushButton("Применить изменения")
        self.apply_button.setStyleSheet('QPushButton {background-color: #99ff99}')
        action_button_layout.addWidget(self.apply_button)
        self.apply_button.setFixedHeight(30)
        self.apply_button.clicked.connect(self.apply_changes)

        self.reset_button = QPushButton("Отмена изменений")
        action_button_layout.addWidget(self.reset_button)
        self.reset_button.setFixedHeight(30)
        self.reset_button.clicked.connect(self.reset_image)

        main_layout.addLayout(action_button_layout)

        central_widget.setLayout(main_layout)

        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_video_stream)

        self.current_image = None
        self.original_image = None

    def show_button(self):
        """Появление кнопки 'Сделать фото'"""
        self.capture_button.show()

    def center(self):
        """Центрирует окно на экране"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_image(self):
        """Открытие диалогового окна для выбора изображения,
        загрузка выбранного изображения и отображение на экране"""
        file_dialog = QFileDialog(self)
        filename, _ = file_dialog.getOpenFileName(self, "Выбрать изображение", "", "Изображения (*.png *.jpg)")
        if filename:
            self.current_image = cv2.imread(filename)
            self.original_image = self.current_image.copy()
            self.display_image(self.current_image)

    def start_camera(self):
        """Инициализация камеры и запуск видеопотока"""
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)

    def display_video_stream(self):
        """Считывание кадра из видеопотока"""
        ret, frame = self.cap.read()
        if ret:
            self.current_image = frame
            self.display_image(frame)

    def capture_image(self):
        """Cнимок текущего кадра с камеры"""
        self.capture_button.hide()
        ret, frame = self.cap.read()
        if ret:
            self.current_image = frame
            self.original_image = self.current_image.copy()
            self.display_image(frame)
            self.timer.stop()
            self.cap.release()
            self.capture_button.setEnabled(False)

    def display_image(self, image):
        """Отображение изображения"""
        if image is not None:
            channel = self.combobox.currentText()
            if channel == "Красный канал":
                image = self.extract_channel(image, 2)
            elif channel == "Зеленый канал":
                image = self.extract_channel(image, 1)
            elif channel == "Синий канал":
                image = self.extract_channel(image, 0)

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # OpenCV использует порядок цветов BGR, а Qt RGB
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

    def update_image_channel(self):
        """Обновление отображения текущего изображения"""
        if self.current_image is not None:
            self.display_image(self.current_image)

    @staticmethod
    def extract_channel(image, channel_idx):
        """Извлечение одного из цветовых каналов изображения"""
        channel_image = np.zeros_like(image)
        channel_image[:, :, channel_idx] = image[:, :, channel_idx]
        return channel_image

    def apply_changes(self):
        """Применение изменений к текущему изображению"""
        global resized_image
        if self.current_image is None:
            QMessageBox.warning(self, "Ошибка", "Необходимо загрузить изображение")
            return
        try:
            new_width = int(self.width_input.text()) if self.width_input.text() else None
            new_height = int(self.height_input.text()) if self.height_input.text() else None
            brightness_value = int(self.brightness_input.text()) if self.brightness_input.text() else 0
            center_x = int(self.center_x_input.text()) if self.center_x_input.text() else None
            center_y = int(self.center_y_input.text()) if self.center_y_input.text() else None
            radius = int(self.radius_input.text()) if self.radius_input.text() else None

            if new_width and new_width <= 0:
                raise ValueError("Неверное значение ширины")
            if new_height and new_height <= 0:
                raise ValueError("Неверное значение высоты")
            if radius and radius <= 0:
                raise ValueError("Радиус должен быть положительным числом")

            if new_width or new_height:
                if new_width and new_height:
                    resized_image = cv2.resize(self.current_image, (new_width, new_height))
                elif new_width:
                    h, w, _ = self.current_image.shape
                    ratio = new_width / w
                    resized_image = cv2.resize(self.current_image, (new_width, int(h * ratio)))
                elif new_height:
                    h, w, _ = self.current_image.shape
                    ratio = new_height / h
                    resized_image = cv2.resize(self.current_image, (int(w * ratio), new_height))
            else:
                resized_image = self.current_image

            if 0 <= brightness_value <= 255:
                adjusted_image = self.adjust_brightness(resized_image, brightness_value)
            else:
                raise ValueError("Значение яркости должно быть в диапазоне от 0 до 255 включительно")
                adjusted_image = self.adjust_brightness(resized_image, 0)
            if center_x is not None and center_y is not None and radius is not None:
                circled_image = self.draw_circle(adjusted_image, center_x, center_y, radius)
            else:
                circled_image = adjusted_image
            self.current_image = circled_image
            self.display_image(self.current_image)
            self.clear_inputs()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Некорректные значения: {e}")

    def reset_image(self):
        """Cброс изображения к исходному состоянию"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)

    def clear_inputs(self):
        """Очищения полей для ввода после нажатия кнопки 'Применить изменения'"""
        self.width_input.clear()
        self.height_input.clear()
        self.brightness_input.clear()
        self.center_x_input.clear()
        self.center_y_input.clear()
        self.radius_input.clear()

    @staticmethod
    def adjust_brightness(image, value):
        """Функция, понижающая яркость изображения"""
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv_image[:, :, 2] = hsv_image[:, :, 2] - value
        hsv_image[:, :, 2] = np.clip(hsv_image[:, :, 2], 0, 255)
        image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        return image

    @staticmethod
    def draw_circle(image, center_x, center_y, radius):
        """Функция, рисующая красный круг на изображении"""
        height, width, _ = image.shape
        if center_x < 0 or center_x >= width or center_y < 0 or center_y >= height:
            raise ValueError("Координаты центра круга выходят за границы изображения")
        if (radius <= 0 or center_x - radius < 0 or center_x + radius >= width or center_y - radius < 0
                or center_y + radius >= height):
            raise ValueError("Радиус круга должен быть положительным числом и в пределах границ изображения")
        return cv2.circle(image, (center_x, center_y), radius, (0, 0, 255), 2)
