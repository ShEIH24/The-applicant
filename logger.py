"""logger.py"""
import logging
import os


class Logger:
    def __init__(self, log_file="app.log"):
        """
        Инициализация логгера с указанным файлом для записи логов

        :param log_file: Путь к файлу логов
        """
        # Создание директории для логов, если она не существует
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Настройка логгера
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Проверка, есть ли уже обработчики, чтобы избежать дублирования
        if not self.logger.handlers:
            # Обработчик для записи в файл
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            # Обработчик для вывода в консоль
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Формат сообщений логов
            log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(log_format)
            console_handler.setFormatter(log_format)

            # Добавление обработчиков к логгеру
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        self.info(f"Логгер инициализирован, файл логов: {log_file}")

    def debug(self, message):
        """Запись отладочной информации"""
        self.logger.debug(message)

    def info(self, message):
        """Запись информационного сообщения"""
        self.logger.info(message)

    def warning(self, message):
        """Запись предупреждения"""
        self.logger.warning(message)

    def error(self, message):
        """Запись сообщения об ошибке"""
        self.logger.error(message)

    def critical(self, message):
        """Запись критической ошибки"""
        self.logger.critical(message)

    def log_api_request(self, endpoint, method, data=None, response=None, status_code=None):
        """
        Запись информации о запросе к внешнему API

        :param endpoint: URL эндпоинта
        :param method: HTTP метод (GET, POST, PUT, DELETE)
        :param data: Отправленные данные (опционально)
        :param response: Полученный ответ (опционально)
        :param status_code: Код статуса ответа (опционально)
        """
        message = f"API запрос: {method} {endpoint}"
        if data:
            message += f", Данные: {data}"
        if status_code:
            message += f", Статус: {status_code}"
        if response:
            message += f", Ответ: {response}"

        self.info(message)