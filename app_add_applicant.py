"""app_add_applicant.py"""
import tkinter as tk
from tkinter import messagebox, ttk
from classes import *
from datetime import datetime


def create_context_menu(widget, parent):
    """Создание контекстного меню для виджета"""
    context_menu = tk.Menu(widget, tearoff=0)
    context_menu.add_command(label="Вырезать", command=lambda: widget.event_generate("<<Cut>>"))
    context_menu.add_command(label="Копировать", command=lambda: widget.event_generate("<<Copy>>"))
    context_menu.add_command(label="Вставить", command=lambda: widget.event_generate("<<Paste>>"))

    def show_context_menu(event):
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    widget.bind("<Button-3>", show_context_menu)


def format_date(event=None, entry=None):
    """Функция для автоматического форматирования даты"""
    if not entry:
        return
    text = entry.get().replace(".", "")
    text = ''.join(filter(str.isdigit, text))
    formatted = ""

    # Форматирование даты как ДД.ММ.ГГГГ
    if len(text) > 0:
        formatted += text[:2] if len(text) >= 2 else text
    if len(text) > 2:
        formatted += "." + text[2:4] if len(text) >= 4 else "." + text[2:]
    if len(text) > 4:
        formatted += "." + text[4:8]

    entry.delete(0, tk.END)
    entry.insert(0, formatted)


def format_phone(event=None, entry=None):
    """Функция для форматирования телефона"""
    if not entry:
        return
    text = entry.get().replace("+", "").replace("-", "")
    text = ''.join(filter(str.isdigit, text))
    formatted = ""

    # Форматирование телефона как +#-###-###-##-##
    if len(text) > 0:
        formatted += "+"
        formatted += text[0] if len(text) >= 1 else ""
    if len(text) > 1:
        formatted += "-" + text[1:4] if len(text) >= 4 else "-" + text[1:]
    if len(text) > 4:
        formatted += "-" + text[4:7] if len(text) >= 7 else "-" + text[4:]
    if len(text) > 7:
        formatted += "-" + text[7:9] if len(text) >= 9 else "-" + text[7:]
    if len(text) > 9:
        formatted += "-" + text[9:11]

    entry.delete(0, tk.END)
    entry.insert(0, formatted)


def parse_full_name(full_name: str) -> tuple:
    """
    Разбирает полное имя на фамилию, имя и отчество
    Возвращает кортеж (фамилия, имя, отчество)
    """
    parts = full_name.strip().split()

    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        return parts[0], parts[1], None
    elif len(parts) == 1:
        return parts[0], "", None
    else:
        return "", "", None


def add_applicant_window(parent, applicants, load_data_callback, logger, db_manager=None):
    """Открывает окно для добавления нового абитуриента"""
    logger.info("Открытие формы добавления абитуриента")

    # ДОБАВЛЕНО: Загрузка справочных данных из БД
    benefits_data = {}
    info_source_options = []

    if db_manager and db_manager.connection:
        try:
            benefits_data = db_manager.get_all_benefits()
            info_source_options = db_manager.get_all_information_sources()

            # Если справочники пустые, инициализируем их
            if not benefits_data:
                db_manager.initialize_reference_data()
                benefits_data = db_manager.get_all_benefits()
                info_source_options = db_manager.get_all_information_sources()
        except Exception as e:
            logger.error(f"Ошибка загрузки справочных данных: {e}")

    # Если не удалось загрузить из БД, используем значения по умолчанию
    if not benefits_data:
        benefits_data = {
            "Без льгот": 0,
            "Сирота": 10,
            "Инвалид I группы": 10,
            "Инвалид II группы": 8,
            "Инвалид III группы": 5,
            "Участник СВО": 10,
            "Ребенок участника СВО": 8,
            "Ребенок погибшего участника СВО": 10,
            "Многодетная семья": 3,
            "Целевое обучение": 5,
            "Отличник (аттестат с отличием)": 5,
            "Золотая медаль": 10,
            "Серебряная медаль": 7,
            "Победитель олимпиады (всероссийская)": 10,
            "Призер олимпиады (всероссийская)": 8,
            "Победитель олимпиады (региональная)": 5,
            "Призер олимпиады (региональная)": 3,
            "ГТО (золотой знак)": 5,
            "ГТО (серебряный знак)": 3,
            "ГТО (бронзовый знак)": 2,
            "Волонтер (более 100 часов)": 3,
            "Спортивные достижения (КМС и выше)": 5,
            "Творческие достижения (лауреат)": 3
        }

    if not info_source_options:
        info_source_options = [
            "Сайт учебного заведения",
            "Социальные сети",
            "Рекомендация друзей/знакомых",
            "Рекламные материалы",
            "День открытых дверей",
            "Ярмарка образования",
            "Поисковые системы (Google, Яндекс)",
            "Рекомендация учителей/родителей",
            "СМИ (газеты, телевидение)",
            "Другое"
        ]

    # Создаем всплывающее окно
    logger.info("Открытие формы добавления абитуриента")

    # Создаем всплывающее окно
    add_window = tk.Toplevel(parent)
    add_window.title("Добавление абитуриента")
    add_window.geometry("1400x750")
    add_window.resizable(True, True)
    add_window.minsize(1400, 750)
    add_window.grab_set()

    # Применяем стиль заголовка
    header_frame = tk.Frame(add_window, bg="#3f51b5", height=70)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)

    header_label = tk.Label(header_frame, text="АБИТУРИЕНТ",
                            font=("Arial", 16, "bold"),
                            bg="#3f51b5", fg="white")
    header_label.pack(side="left", padx=20, pady=20)

    # Создаем контейнер для формы
    form_container = tk.Frame(add_window, padx=20, pady=20)
    form_container.pack(fill="both", expand=True)

    # Конфигурация строк и столбцов для правильного масштабирования
    form_container.columnconfigure(0, weight=1)
    form_container.columnconfigure(1, weight=1)
    form_container.rowconfigure(0, weight=3)
    form_container.rowconfigure(1, weight=1)

    # Основные данные
    basic_frame = tk.LabelFrame(form_container, text="ОСНОВНЫЕ ДАННЫЕ:", font=("Arial", 12, "bold"), padx=10,
                                pady=10)
    basic_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Настройка масштабирования для basic_frame
    for i in range(9):
        basic_frame.rowconfigure(i, weight=1)

    for i in range(4):
        basic_frame.columnconfigure(i, weight=1)
    basic_frame.columnconfigure(1, weight=2)
    basic_frame.columnconfigure(3, weight=2)

    # Создаем метку для обязательных полей
    required_label = tk.Label(basic_frame, text="* - обязательное поле", font=("Arial", 8), fg="red")
    required_label.grid(row=8, column=0, columnspan=4, sticky="w", pady=(10, 0))

    # Фамилия с пометкой обязательного поля
    tk.Label(basic_frame, text="Фамилия *", font=("Arial", 9), fg="red").grid(row=0, column=0, sticky="w", pady=5)
    last_name_entry = tk.Entry(basic_frame)
    last_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(last_name_entry, add_window)

    # Имя с пометкой обязательного поля
    tk.Label(basic_frame, text="Имя *", font=("Arial", 9), fg="red").grid(row=0, column=2, sticky="w", pady=5)
    first_name_entry = tk.Entry(basic_frame)
    first_name_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
    create_context_menu(first_name_entry, add_window)

    # Отчество
    tk.Label(basic_frame, text="Отчество", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
    patronymic_entry = tk.Entry(basic_frame)
    patronymic_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5, columnspan=3)
    create_context_menu(patronymic_entry, add_window)

    # Номер - будет назначен автоматически из БД или из памяти
    tk.Label(basic_frame, text="Номер", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
    number_entry = tk.Entry(basic_frame)
    number_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    # ИСПРАВЛЕНО: показываем следующий номер, который будет присвоен
    if db_manager and db_manager.connection:
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_applicant), 0) + 1 FROM Applicant")
            next_number = str(cursor.fetchone()[0])
        except:
            next_number = str(len(applicants) + 1)
    else:
        next_number = str(len(applicants) + 1)

    number_entry.insert(0, next_number)
    number_entry.config(state="readonly")

    # Код специальности с пометкой обязательного поля
    tk.Label(basic_frame, text="Код *", font=("Arial", 9), fg="red").grid(row=2, column=2, sticky="w", pady=5)
    code_entry = tk.Entry(basic_frame)
    code_entry.grid(row=2, column=3, sticky="ew", padx=5, pady=5)
    create_context_menu(code_entry, add_window)

    # ДОБАВЛЕНО: Форма обучения
    tk.Label(basic_frame, text="Форма обучения *", font=("Arial", 9), fg="red").grid(row=3, column=0, sticky="w",
                                                                                     pady=5)

    form_of_education_options = [
        "Очная",
        "Заочная",
        "Очно-заочная",
    ]

    form_of_education_combobox = ttk.Combobox(basic_frame, values=form_of_education_options, state="readonly")
    form_of_education_combobox.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
    form_of_education_combobox.set("Очная")  # Значение по умолчанию
    create_context_menu(form_of_education_combobox, add_window)

    # Рейтинг с пометкой обязательного поля
    tk.Label(basic_frame, text="Рейтинг *", font=("Arial", 9), fg="red").grid(row=3, column=2, sticky="w", pady=5)
    rating_entry = tk.Entry(basic_frame)
    rating_entry.grid(row=3, column=3, sticky="ew", padx=5, pady=5)
    create_context_menu(rating_entry, add_window)

    # Льгота с пометкой обязательного поля и баллами
    tk.Label(basic_frame, text="Льгота *", font=("Arial", 9), fg="red").grid(row=4, column=0, sticky="w", pady=5)

    # ИСПОЛЬЗУЕМ данные из БД (benefits_data уже загружен выше)
    benefits_options = list(benefits_data.keys())

    # Создаем фрейм для льготы и баллов
    benefit_frame = tk.Frame(basic_frame)
    benefit_frame.grid(row=4, column=1, sticky="ew", padx=5, pady=5, columnspan=3)
    benefit_frame.columnconfigure(0, weight=3)
    benefit_frame.columnconfigure(1, weight=1)

    benefits_combobox = ttk.Combobox(benefit_frame, values=benefits_options)
    benefits_combobox.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    benefits_combobox.set("")

    # Поле для отображения баллов
    bonus_points_label = tk.Label(benefit_frame, text="Баллы: 0", font=("Arial", 9), fg="#3f51b5", anchor="w")
    bonus_points_label.grid(row=0, column=1, sticky="ew")

    # Функция обновления баллов при выборе льготы
    def update_bonus_points(event=None):
        selected_benefit = benefits_combobox.get()
        points = benefits_data.get(selected_benefit, 0)
        bonus_points_label.config(text=f"Баллы: {points}")

    benefits_combobox.bind("<<ComboboxSelected>>", update_bonus_points)
    create_context_menu(benefits_combobox, add_window)

    # ИСПРАВЛЕНО: Оригинал документов и Дата подачи - изменен номер строки на 5
    frame_row5 = tk.Frame(basic_frame)
    frame_row5.grid(row=5, column=0, columnspan=4, sticky="ew")
    frame_row5.columnconfigure(0, weight=1)
    frame_row5.columnconfigure(1, weight=1)
    frame_row5.columnconfigure(2, weight=1)
    frame_row5.columnconfigure(3, weight=1)

    tk.Label(frame_row5, text="Оригинал", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
    original_var = tk.BooleanVar()
    original_check = tk.Checkbutton(frame_row5, text="Да", variable=original_var)
    original_check.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # Дата подачи с пометкой обязательного поля
    tk.Label(frame_row5, text="Дата подачи *", font=("Arial", 9), fg="red").grid(row=0, column=2, sticky="w",
                                                                                 pady=5, padx=(20, 0))
    submission_date_entry = tk.Entry(frame_row5)
    submission_date_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
    create_context_menu(submission_date_entry, add_window)

    # Подсказка для даты
    submission_date_entry.insert(0, "ДД.ММ.ГГГГ")
    submission_date_entry.bind("<FocusIn>", lambda e: submission_date_entry.delete(0,
                                                                                   tk.END) if submission_date_entry.get() == "ДД.ММ.ГГГГ" else None)
    submission_date_entry.bind("<KeyRelease>", lambda event: format_date(event, submission_date_entry))

    # ИСПРАВЛЕНО: Учебное заведение - изменен номер строки на 6
    tk.Label(basic_frame, text="Учебное заведение *", font=("Arial", 9), fg="red").grid(row=6, column=0,
                                                                                        sticky="w", pady=5)
    institution_entry = tk.Entry(basic_frame)
    institution_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=5, columnspan=3)
    create_context_menu(institution_entry, add_window)

    # ИСПРАВЛЕНО: Город - изменен номер строки на 7
    tk.Label(basic_frame, text="Город *", font=("Arial", 9), fg="red").grid(row=7, column=0, sticky="w", pady=5)
    city_entry = tk.Entry(basic_frame)
    city_entry.grid(row=7, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(city_entry, add_window)

    # Общежитие
    tk.Label(basic_frame, text="Общежитие", font=("Arial", 9)).grid(row=7, column=2, sticky="w", pady=5)
    dormitory_var = tk.BooleanVar()
    dormitory_check = tk.Checkbutton(basic_frame, text="", variable=dormitory_var)
    dormitory_check.grid(row=7, column=3, sticky="w", padx=5, pady=5)

    # Дополнительная информация
    additional_frame = tk.LabelFrame(form_container, text="ДОПОЛНИТЕЛЬНО:", font=("Arial", 12, "bold"), padx=10,
                                     pady=10)
    additional_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    # Настройка масштабирования для additional_frame
    for i in range(6):
        additional_frame.rowconfigure(i, weight=1)
    additional_frame.columnconfigure(0, weight=2)
    additional_frame.columnconfigure(1, weight=2)

    # Дата посещения
    tk.Label(additional_frame, text="Дата посещения", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 5))
    visit_date_entry = tk.Entry(additional_frame)
    visit_date_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(visit_date_entry, add_window)

    # Подсказка для даты посещения
    visit_date_entry.insert(0, "ДД.ММ.ГГГГ")
    visit_date_entry.bind("<FocusIn>", lambda e: visit_date_entry.delete(0,
                                                                         tk.END) if visit_date_entry.get() == "ДД.ММ.ГГГГ" else None)
    visit_date_entry.bind("<KeyRelease>", lambda event: format_date(event, visit_date_entry))

    # Откуда узнал/а - ИСПРАВЛЕНО: заменено на ComboBox
    tk.Label(additional_frame, text="Откуда узнал/а", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5,
                                                                              padx=(0, 5))

    # Список предопределенных источников информации
    info_source_options = [
        "Сайт учебного заведения",
        "Социальные сети",
        "Рекомендация друзей/знакомых",
        "Рекламные материалы",
        "День открытых дверей",
        "Ярмарка образования",
        "Поисковые системы (Google, Яндекс)",
        "Рекомендация учителей/родителей",
        "СМИ (газеты, телевидение)",
        "Другое"
    ]

    info_source_combobox = ttk.Combobox(additional_frame, values=info_source_options)
    info_source_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    info_source_combobox.set("")  # Пустое значение по умолчанию
    create_context_menu(info_source_combobox, add_window)

    # Примечание
    tk.Label(additional_frame, text="Примечание", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5, padx=(0, 5))
    notes_text = tk.Text(additional_frame, height=8)
    notes_text.grid(row=2, column=1, rowspan=4, sticky="nsew", padx=5, pady=5)
    create_context_menu(notes_text, add_window)

    # Контактная информация
    contact_frame = tk.LabelFrame(form_container, text="КОНТАКТНАЯ ИНФОРМАЦИЯ:", font=("Arial", 12, "bold"),
                                  padx=10, pady=10)
    contact_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)

    # Настройка масштабирования для contact_frame
    for i in range(5):
        contact_frame.rowconfigure(i, weight=1)
    contact_frame.columnconfigure(0, weight=1)
    contact_frame.columnconfigure(1, weight=5)

    # Телефон с пометкой обязательного поля
    tk.Label(contact_frame, text="Телефон *", font=("Arial", 9), fg="red").grid(row=0, column=0, sticky="w",
                                                                                 pady=5)
    phone_entry = tk.Entry(contact_frame)
    phone_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    phone_entry.insert(0, "+7-___-___-__-__")
    phone_entry.bind("<FocusIn>",
                     lambda e: phone_entry.delete(0, tk.END) if "+7-___-___-__-__" in phone_entry.get() else None)
    phone_entry.bind("<KeyRelease>", lambda event: format_phone(event, phone_entry))
    create_context_menu(phone_entry, add_window)

    # Профиль ВК
    tk.Label(contact_frame, text="Профиль ВК", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
    vk_entry = tk.Entry(contact_frame)
    vk_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(vk_entry, add_window)

    # Родитель (Фамилия Имя Отчество)
    tk.Label(contact_frame, text="Родитель (ФИО)", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
    parent_entry = tk.Entry(contact_frame)
    parent_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(parent_entry, add_window)

    # ДОБАВЛЕНО: Кем приходится (родственная связь)
    tk.Label(contact_frame, text="Кем приходится", font=("Arial", 9)).grid(row=3, column=0, sticky="w", pady=5)

    relation_options = [
        "Родитель",
        "Мать",
        "Отец",
        "Опекун",
        "Бабушка",
        "Дедушка",
        "Брат",
        "Сестра",
        "Другой родственник"
    ]

    relation_combobox = ttk.Combobox(contact_frame, values=relation_options)
    relation_combobox.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
    relation_combobox.set("Родитель")  # Значение по умолчанию
    create_context_menu(relation_combobox, add_window)

    # Телефон родителя
    tk.Label(contact_frame, text="Телефон родителя", font=("Arial", 9)).grid(row=4, column=0, sticky="w", pady=5)
    parent_phone_entry = tk.Entry(contact_frame)
    parent_phone_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
    parent_phone_entry.insert(0, "+7-___-___-__-__")
    parent_phone_entry.bind("<FocusIn>", lambda e: parent_phone_entry.delete(0,
                                                                             tk.END) if "+7-___-___-__-__" in parent_phone_entry.get() else None)
    parent_phone_entry.bind("<KeyRelease>", lambda event: format_phone(event, parent_phone_entry))
    create_context_menu(parent_phone_entry, add_window)

    # Фрейм для кнопок
    button_frame = tk.Frame(add_window)
    button_frame.pack(fill="x", padx=20, pady=20)

    # Функция сохранения данных
    def save_applicant():
        try:
            # Валидация обязательных полей
            if not last_name_entry.get().strip():
                messagebox.showerror("Ошибка", "Поле Фамилия не может быть пустым")
                return

            if not first_name_entry.get().strip():
                messagebox.showerror("Ошибка", "Поле Имя не может быть пустым")
                return

            if not code_entry.get().strip():
                messagebox.showerror("Ошибка", "Поле Код не может быть пустым")
                return

            if not form_of_education_combobox.get().strip():
                messagebox.showerror("Ошибка", "Поле Форма обучения не может быть пустым")
                return

            if not rating_entry.get().strip():
                messagebox.showerror("Ошибка", "Поле Рейтинг не может быть пустым")
                return

            if not benefits_combobox.get().strip():
                messagebox.showerror("Ошибка", "Поле Льгота не может быть пустым")
                return

            if not submission_date_entry.get().strip() or submission_date_entry.get() == "ДД.ММ.ГГГГ":
                messagebox.showerror("Ошибка", "Поле Дата подачи не может быть пустым")
                return

            if not institution_entry.get().strip():
                messagebox.showerror("Ошибка", "Поле Учебное заведение не может быть пустым")
                return

            if not city_entry.get().strip():
                messagebox.showerror("Ошибка", "Поле Город не может быть пустым")
                return

            if not phone_entry.get().strip() or "+7-___-___-__-__" in phone_entry.get():
                messagebox.showerror("Ошибка", "Поле Телефон не может быть пустым")
                return

            try:
                rating = float(rating_entry.get().strip())
            except ValueError:
                messagebox.showerror("Ошибка", "Рейтинг должен быть числом")
                return

            current_date = datetime.now().date()

            # Обработка даты подачи
            if submission_date_entry.get() and submission_date_entry.get() != "ДД.ММ.ГГГГ":
                try:
                    submission_date_str = submission_date_entry.get()
                    submission_date = datetime.strptime(submission_date_str, "%d.%m.%Y").date()
                    if submission_date > current_date:
                        logger.warning(f"Введена будущая дата подачи: {submission_date_entry.get()}")
                        messagebox.showwarning("Предупреждение", "Дата подачи не может быть в будущем времени")
                        return
                except ValueError:
                    messagebox.showerror("Ошибка", "Неправильный формат даты подачи (ДД.ММ.ГГГГ)")
                    return
            else:
                messagebox.showerror("Ошибка", "Поле Дата подачи не может быть пустым")
                return

            # Обработка даты посещения
            visit_date = None
            if visit_date_entry.get() and visit_date_entry.get() != "ДД.ММ.ГГГГ":
                try:
                    visit_date = datetime.strptime(visit_date_entry.get(), "%d.%m.%Y").date()
                    if visit_date > current_date:
                        logger.warning(f"Введена будущая дата посещения: {visit_date_entry.get()}")
                        messagebox.showwarning("Предупреждение", "Дата посещения не может быть в будущем времени")
                        return
                except ValueError:
                    messagebox.showerror("Ошибка", "Неправильный формат даты посещения (ДД.ММ.ГГГГ)")
                    return

            # Получение данных из полей
            last_name = last_name_entry.get().strip()
            first_name = first_name_entry.get().strip()
            patronymic = patronymic_entry.get().strip() if patronymic_entry.get().strip() else None

            # Получаем бонусные баллы за выбранную льготу
            selected_benefit = benefits_combobox.get()
            bonus_points = benefits_data.get(selected_benefit, 0)

            # Создание объектов для нового абитуриента
            application_details = ApplicationDetails(
                number=number_entry.get(),
                code=code_entry.get(),
                rating=rating,
                has_original=original_var.get(),
                benefits=benefits_combobox.get(),
                submission_date=submission_date,
                form_of_education=form_of_education_combobox.get(),
                bonus_points = bonus_points
            )

            education = EducationalBackground(
                institution=institution_entry.get()
            )

            contact_info = ContactInfo(
                phone=phone_entry.get(),
                vk=vk_entry.get() if vk_entry.get() else None
            )

            additional_info = AdditionalInfo(
                department_visit=visit_date,
                notes=notes_text.get("1.0", tk.END).strip() if notes_text.get("1.0", tk.END).strip() else None,
                information_source=info_source_combobox.get() if info_source_combobox.get() else None,
                dormitory_needed=dormitory_var.get()
            )

            # Обработка данных родителя
            parent = None
            if parent_entry.get() and parent_phone_entry.get() and "+7-___-___-__-__" not in parent_phone_entry.get():
                # ИСПРАВЛЕНО: используем parent_name вместо разбиения на компоненты
                parent = Parent(
                    parent_name=parent_entry.get().strip(),
                    phone=parent_phone_entry.get(),
                    relation = relation_combobox.get()
                )

            # Создание нового абитуриента
            new_applicant = Applicant(
                last_name=last_name,
                first_name=first_name,
                patronymic=patronymic,
                phone=phone_entry.get(),
                city=city_entry.get(),
                application_details=application_details,
                education=education,
                contact_info=contact_info,
                additional_info=additional_info,
                parent=parent
            )

            # Сохранение в БД
            if db_manager and db_manager.connection:
                try:
                    applicant_id = db_manager.add_applicant(new_applicant)
                    # Обновляем номер абитуриента ID из БД
                    new_applicant.application_details.number = str(applicant_id)
                    logger.info(f"Абитуриент сохранен в БД с ID: {applicant_id}")
                except Exception as db_error:
                    logger.error(f"Ошибка сохранения в БД: {str(db_error)}")
                    messagebox.showerror("Ошибка БД",
                                       f"Не удалось сохранить в базу данных:\n{str(db_error)}\n\nДанные будут сохранены только в памяти.")
                    # Устанавливаем номер для памяти если БД не сработала
                    new_applicant.application_details.number = str(len(applicants) + 1)
            else:
                # Если нет БД, используем порядковый номер
                new_applicant.application_details.number = str(len(applicants) + 1)

            # Добавление абитуриента в реестр (в памяти)
            applicants.append(new_applicant)

            # Обновление таблицы
            load_data_callback()

            logger.info(f"Добавлен новый абитуриент: {new_applicant.get_full_name()}")

            # Закрытие окна
            add_window.destroy()

        except Exception as e:
            logger.error(f"Ошибка при добавлении абитуриента: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка при добавлении: {str(e)}")

    def save_and_create_new():
        """Сохраняет текущего абитуриента и открывает форму для создания нового"""
        save_applicant()
        # Если сохранение прошло успешно, окно будет закрыто, поэтому открываем новое
        if not add_window.winfo_exists():
            add_applicant_window(parent, applicants, load_data_callback, logger, db_manager)

    # Кнопки
    save_button = tk.Button(
        button_frame,
        text="Сохранить",
        bg="#3f51b5",
        fg="white",
        font=("Arial", 10),
        width=15,
        command=save_applicant
    )
    save_button.pack(side="right", padx=5)

    save_new_button = tk.Button(
        button_frame,
        text="Сохранить и создать новый",
        bg="#3f51b5",
        fg="white",
        font=("Arial", 10),
        width=25,
        command=save_and_create_new
    )
    save_new_button.pack(side="right", padx=5)

    cancel_button = tk.Button(
        button_frame,
        text="Отмена",
        bg="#757575",
        fg="white",
        font=("Arial", 10),
        width=15,
        command=add_window.destroy
    )
    cancel_button.pack(side="right", padx=5)