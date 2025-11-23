"""app_table.py - главный файл приложения с интеграцией БД"""
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from database import DatabaseManager
from classes import ApplicantRegistry
from logger import Logger
from app_table import ApplicantTableWindow

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('applicant_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def initialize_database():
    """
    Инициализация подключения к БД
    """
    try:
        # Вариант 1: Windows Authentication
        db_manager = DatabaseManager(
            server='localhost',
            database='ApplicantDB',
            use_windows_auth=True
        )

        # Подключаемся к БД
        if db_manager.connect():
            logging.info("Успешное подключение к БД")

            # Создаем структуру БД если её нет
            db_manager.create_database_structure()
            db_manager.initialize_reference_data()
            logging.info("Структура БД проверена/создана")

            return db_manager
        else:
            logging.error("Не удалось подключиться к БД")
            messagebox.showwarning(
                "Предупреждение",
                "Не удалось подключиться к базе данных.\nПриложение будет работать без сохранения в БД."
            )
            return None

    except Exception as e:
        logging.error(f"Ошибка инициализации БД: {e}")
        messagebox.showwarning(
            "Предупреждение БД",
            f"Ошибка при инициализации базы данных:\n{str(e)}\n\nПриложение будет работать в режиме без БД."
        )
        return None

def main():
    """Главная функция приложения"""
    root = tk.Tk()
    root.title("Реестр абитуриентов")
    root.geometry("1400x800")

    # Установка иконки если есть
    try:
        icon = tk.PhotoImage(file="icon.ico")
        root.iconphoto(True, icon)
    except:
        pass

    # Создаем логгер
    logger = Logger("applicant_system.log")
    logger.info("=== Запуск приложения ===")

    # Инициализация БД
    db_manager = initialize_database()

    # Создаем реестр абитуриентов
    applicant_registry = ApplicantRegistry()
    applicants = applicant_registry.applicants

    # Загрузка данных из БД при старте
    if db_manager and db_manager.connection:
        try:
            loaded_applicants = db_manager.load_all_applicants()
            applicants.extend(loaded_applicants)
            logger.info(f"Загружено {len(applicants)} абитуриентов из БД")

            # Предлагаем импорт только если БД пуста
            offer_import = (len(applicants) == 0)
        except Exception as e:
            logger.error(f"Ошибка загрузки данных из БД: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные из БД:\n{str(e)}")
            offer_import = True
    else:
        # Если нет БД, предлагаем импорт
        offer_import = True

    # Создаем главное окно приложения с таблицей
    app = ApplicantTableWindow(
        parent=root,
        applicants=applicants,
        logger=logger,
        db_manager=db_manager,
        offer_import=offer_import
    )

    logger.info("Приложение успешно запущено")

    # Запуск главного цикла
    root.mainloop()

if __name__ == "__main__":
    main()