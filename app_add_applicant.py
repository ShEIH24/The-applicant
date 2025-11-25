"""app_add_applicant.py"""
import tkinter as tk
from tkinter import messagebox, ttk
from classes import *

BENEFITS_LIST = [
            "Без льгот",
            "Сирота",
            "Инвалид I группы",
            "Инвалид II группы",
            "Инвалид III группы",
            "Участник СВО",
            "Ребенок участника СВО",
            "Ребенок погибшего участника СВО",
            "Многодетная семья",
            "Целевое обучение",
            "Отличник (аттестат с отличием)",
            "Золотая медаль",
            "Серебряная медаль",
            "Победитель олимпиады (всероссийская)",
            "Призер олимпиады (всероссийская)",
            "Победитель олимпиады (региональная)",
            "Призер олимпиады (региональная)",
            "ГТО (золотой знак)",
            "ГТО (серебряный знак)",
            "ГТО (бронзовый знак)",
            "Волонтер (более 100 часов)",
            "Спортивные достижения (КМС и выше)",
            "Творческие достижения (лауреат)"
        ]

def setup_keyboard_shortcuts(window):
    """Настройка горячих клавиш для работы с русской раскладкой"""

    def handle_keypress(event):
        # Проверяем, что нажат Ctrl
        if not (event.state & 0x4):  # 0x4 - флаг Control
            return

        widget = window.focus_get()
        if not widget:
            return

        # Проверяем тип виджета
        if not isinstance(widget, (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox)):
            return

        # Определяем действие по keycode (работает для любой раскладки)
        if event.keycode == 67:  # C/С - копирование
            widget.event_generate("<<Copy>>")
            return "break"
        elif event.keycode == 86:  # V/М - вставка
            widget.event_generate("<<Paste>>")
            return "break"
        elif event.keycode == 88:  # X/Ч - вырезание
            widget.event_generate("<<Cut>>")
            return "break"
        elif event.keycode == 65:  # A/Ф - выделить всё
            if isinstance(widget, tk.Text):
                widget.tag_add("sel", "1.0", "end")
            else:
                widget.select_range(0, tk.END)
            return "break"

    window.bind("<Control-KeyPress>", handle_keypress)


def create_context_menu(widget, parent_window):
    """Создаёт контекстное меню для копирования, вставки и вырезания"""
    popup_menu = tk.Menu(widget, tearoff=0)

    # Функции для работы с буфером обмена
    def copy_to_clipboard():
        try:
            # Проверяем, является ли виджет текстовым полем
            if isinstance(widget, tk.Text):
                selected_text = widget.get("sel.first", "sel.last")
                parent_window.clipboard_clear()
                parent_window.clipboard_append(selected_text)
            else:  # Entry widget
                parent_window.clipboard_clear()
                parent_window.clipboard_append(widget.selection_get())
        except tk.TclError:
            pass  # Нет выделенного текста

    def cut_to_clipboard():
        try:
            if isinstance(widget, tk.Text):
                selected_text = widget.get("sel.first", "sel.last")
                parent_window.clipboard_clear()
                parent_window.clipboard_append(selected_text)
                widget.delete("sel.first", "sel.last")
            else:  # Entry widget
                parent_window.clipboard_clear()
                parent_window.clipboard_append(widget.selection_get())
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass  # Нет выделенного текста

    def paste_from_clipboard():
        try:
            clipboard_text = parent_window.clipboard_get()
            if isinstance(widget, tk.Text):
                try:
                    widget.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass  # Нет выделенного текста
                widget.insert(tk.INSERT, clipboard_text)
            else:  # Entry widget
                try:
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except tk.TclError:
                    pass  # Нет выделенного текста
                widget.insert(tk.INSERT, clipboard_text)
        except:
            pass  # Буфер обмена пуст

    def select_all():
        try:
            if isinstance(widget, tk.Text):
                widget.tag_add(tk.SEL, "1.0", tk.END)
                widget.mark_set(tk.INSERT, "1.0")
                widget.see(tk.INSERT)
                return 'break'
            else:  # Entry widget
                widget.select_range(0, tk.END)
                widget.icursor(tk.END)
                return 'break'
        except:
            pass

    # Добавляем пункты меню
    popup_menu.add_command(label="Копировать", command=copy_to_clipboard)
    popup_menu.add_command(label="Вырезать", command=cut_to_clipboard)
    popup_menu.add_command(label="Вставить", command=paste_from_clipboard)
    popup_menu.add_command(label="Выделить всё", command=select_all)

    # Функция для показа контекстного меню
    def show_popup_menu(event):
        try:
            popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup_menu.grab_release()

    # Привязываем правый клик мыши к показу меню
    widget.bind("<Button-3>", show_popup_menu)  # Правая кнопка мыши

    # Привязываем горячие клавиши
    widget.bind("<Control-c>", lambda e: copy_to_clipboard())
    widget.bind("<Control-x>", lambda e: cut_to_clipboard())
    widget.bind("<Control-v>", lambda e: paste_from_clipboard())
    widget.bind("<Control-a>", lambda e: select_all())

    # Для Ctrl+Z и Ctrl+Y используем встроенные возможности Tkinter
    if isinstance(widget, tk.Text):
        # Для текстовых виджетов
        widget.bind("<Control-z>", lambda e: widget.edit_undo())
        widget.bind("<Control-y>", lambda e: widget.edit_redo())
    else:
        # Для Entry виджетов нет встроенной поддержки undo/redo
        # Можно реализовать историю изменений, но здесь используем стандартные
        # бинды для поддержки совместимости с системными правилами
        pass


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


def add_applicant_window(parent, applicants, load_data_callback, logger):
    """Открывает окно для добавления нового абитуриента"""
    logger.info("Открытие формы добавления абитуриента")

    # Создаем всплывающее окно
    add_window = tk.Toplevel(parent)
    add_window.title("Добавление абитуриента")
    add_window.geometry("1400x750")
    add_window.resizable(True, True)
    add_window.minsize(1400, 650)
    add_window.grab_set()  # Делаем окно модальным

    setup_keyboard_shortcuts(add_window)
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

    # Основные данные и Контактная информация в одной строке
    info_container = tk.Frame(form_container)
    info_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)
    info_container.columnconfigure(0, weight=1)
    info_container.columnconfigure(1, weight=1)
    info_container.rowconfigure(0, weight=1)

    # Основные данные (левая половина)
    basic_frame = tk.LabelFrame(info_container, text="ОСНОВНАЯ ИНФОРМАЦИЯ:", font=("Arial", 12, "bold"), padx=10,
                                pady=10)
    basic_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    # Настройка масштабирования для basic_frame
    for i in range(3):
        basic_frame.rowconfigure(i, weight=1)
    basic_frame.columnconfigure(0, weight=1)
    basic_frame.columnconfigure(1, weight=2)

    # Создаем метку для обязательных полей
    required_label = tk.Label(basic_frame, text="* - обязательное поле", font=("Arial", 8), fg="red")
    required_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

    # ФИО с пометкой обязательного поля
    tk.Label(basic_frame, text="ФИО *", font=("Arial", 9), fg="red").grid(row=0, column=0, sticky="w", pady=5)
    fio_entry = tk.Entry(basic_frame)
    fio_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(fio_entry, add_window)

    # Учебное заведение с пометкой обязательного поля
    tk.Label(basic_frame, text="Учебное заведение *", font=("Arial", 9), fg="red").grid(row=1, column=0, sticky="w",
                                                                                        pady=5)
    institution_entry = tk.Entry(basic_frame)
    institution_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(institution_entry, add_window)

    # Город
    tk.Label(basic_frame, text="Город *", font=("Arial", 9), fg="red").grid(row=2, column=0, sticky="w", pady=5)
    city_entry = tk.Entry(basic_frame)
    city_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(city_entry, add_window)

    # Контактная информация (правая половина)
    contact_frame = tk.LabelFrame(info_container, text="КОНТАКТНАЯ ИНФОРМАЦИЯ:", font=("Arial", 12, "bold"), padx=10,
                                  pady=10)
    contact_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    # Настройка масштабирования для contact_frame
    for i in range(3):
        contact_frame.rowconfigure(i, weight=1)
    contact_frame.columnconfigure(0, weight=1)
    contact_frame.columnconfigure(1, weight=2)

    # Телефон
    tk.Label(contact_frame, text="Телефон *", font=("Arial", 9), fg="red").grid(row=0, column=0, sticky="w", pady=5)
    phone_entry = tk.Entry(contact_frame)
    phone_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    phone_entry.insert(0, "+7-___-___-__-__")
    phone_entry.bind("<FocusIn>",
                     lambda e: phone_entry.delete(0, tk.END) if "+7-___-___-__-__" in phone_entry.get() else None)
    phone_entry.bind("<KeyRelease>", lambda event: format_phone(event, phone_entry))
    create_context_menu(phone_entry, add_window)

    # Email
    tk.Label(contact_frame, text="Email", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
    email_entry = tk.Entry(contact_frame)
    email_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(email_entry, add_window)

    # Профиль ВК
    tk.Label(contact_frame, text="Профиль ВК", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
    vk_entry = tk.Entry(contact_frame)
    vk_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(vk_entry, add_window)

    # Ник
    tk.Label(contact_frame, text="Ник", font=("Arial", 9)).grid(row=3, column=0, sticky="w", pady=5)
    nickname_entry = tk.Entry(contact_frame)
    nickname_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(nickname_entry, add_window)

    # Дополнительная информация
    additional_frame = tk.LabelFrame(form_container, text="ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:", font=("Arial", 12, "bold"),
                                     padx=10,
                                     pady=10)
    additional_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    # Настройка масштабирования для additional_frame
    for i in range(7):  # для строк (увеличено)
        additional_frame.rowconfigure(i, weight=1)
    for i in range(4):  # для столбцов
        additional_frame.columnconfigure(i, weight=1)
    additional_frame.columnconfigure(1, weight=2)
    additional_frame.columnconfigure(3, weight=2)

    # Номер - генерируется автоматически
    tk.Label(additional_frame, text="Номер", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
    number_entry = tk.Entry(additional_frame)
    number_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    # Устанавливаем следующий номер и делаем поле неактивным
    next_number = str(len(applicants) + 1)
    number_entry.insert(0, next_number)
    number_entry.config(state="readonly")

    # Код специальности
    tk.Label(additional_frame, text="Код", font=("Arial", 9)).grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
    code_entry = tk.Entry(additional_frame)
    code_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
    create_context_menu(code_entry, add_window)

    # Рейтинг со значением по умолчанию 0
    tk.Label(additional_frame, text="Рейтинг", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
    rating_var = tk.StringVar(value="0")
    rating_entry = tk.Entry(additional_frame, textvariable=rating_var)
    rating_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(rating_entry, add_window)

    # Льгота (заменить Entry на Combobox)
    tk.Label(additional_frame, text="Льгота", font=("Arial", 9)).grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
    benefits_var = tk.StringVar()
    benefits_combo = ttk.Combobox(additional_frame, textvariable=benefits_var, values=BENEFITS_LIST, state="readonly")
    benefits_combo.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
    benefits_combo.current(0)  # Устанавливаем пустое значение по умолчанию

    # Дата подачи и Оригинал документов в одной строке
    tk.Label(additional_frame, text="Дата подачи", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
    submission_date_entry = tk.Entry(additional_frame)
    submission_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(submission_date_entry, add_window)

    # Подсказка для даты
    submission_date_entry.insert(0, "ДД.ММ.ГГГГ")
    submission_date_entry.bind("<FocusIn>", lambda e: submission_date_entry.delete(0,
                                                                                   tk.END) if submission_date_entry.get() == "ДД.ММ.ГГГГ" else None)

    # Привязка функции форматирования к полям даты
    submission_date_entry.bind("<KeyRelease>", lambda event: format_date(event, submission_date_entry))

    tk.Label(additional_frame, text="Оригинал", font=("Arial", 9)).grid(row=2, column=2, sticky="w", pady=5,
                                                                        padx=(20, 0))
    original_var = tk.BooleanVar()
    original_check = tk.Checkbutton(additional_frame, text="Да", variable=original_var)
    original_check.grid(row=2, column=3, sticky="w", padx=5, pady=5)

    # Дата посещения
    tk.Label(additional_frame, text="Дата посещения", font=("Arial", 9)).grid(row=3, column=0, sticky="w", pady=5)
    visit_date_entry = tk.Entry(additional_frame)
    visit_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(visit_date_entry, add_window)

    # Подсказка для даты посещения
    visit_date_entry.insert(0, "ДД.ММ.ГГГГ")
    visit_date_entry.bind("<FocusIn>", lambda e: visit_date_entry.delete(0,
                                                                         tk.END) if visit_date_entry.get() == "ДД.ММ.ГГГГ" else None)
    visit_date_entry.bind("<KeyRelease>", lambda event: format_date(event, visit_date_entry))

    # Общежитие
    tk.Label(additional_frame, text="Общежитие", font=("Arial", 9)).grid(row=3, column=2, sticky="w", pady=5,
                                                                         padx=(20, 0))
    dormitory_var = tk.BooleanVar()
    dormitory_check = tk.Checkbutton(additional_frame, text="Да", variable=dormitory_var)
    dormitory_check.grid(row=3, column=3, sticky="w", padx=5, pady=5)

    # Откуда узнал/а
    tk.Label(additional_frame, text="Откуда узнал/а", font=("Arial", 9)).grid(row=4, column=0, sticky="w", pady=5)
    info_source_entry = tk.Entry(additional_frame)
    info_source_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5, columnspan=3)
    create_context_menu(info_source_entry, add_window)

    # Примечание
    tk.Label(additional_frame, text="Примечание", font=("Arial", 9)).grid(row=5, column=0, sticky="nw", pady=5)
    notes_text = tk.Text(additional_frame, height=3)
    notes_text.grid(row=5, column=1, rowspan=2, sticky="nsew", padx=5, pady=5, columnspan=3)
    create_context_menu(notes_text, add_window)

    # Контейнер для контактной информации родителей и экзаменов
    bottom_container = tk.Frame(form_container)
    bottom_container.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
    bottom_container.columnconfigure(0, weight=1)
    bottom_container.rowconfigure(0, weight=1)
    bottom_container.rowconfigure(1, weight=1)

    # Контактная информация родителей (верхняя половина)
    parent_contact_frame = tk.LabelFrame(bottom_container, text="КОНТАКТНАЯ ИНФОРМАЦИЯ РОДИТЕЛЕЙ:",
                                         font=("Arial", 12, "bold"), padx=10, pady=10)
    parent_contact_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

    # Настройка масштабирования для parent_contact_frame
    for i in range(2):
        parent_contact_frame.rowconfigure(i, weight=1)
    parent_contact_frame.columnconfigure(0, weight=1)
    parent_contact_frame.columnconfigure(1, weight=2)

    # Родитель
    tk.Label(parent_contact_frame, text="Родитель", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
    parent_entry = tk.Entry(parent_contact_frame)
    parent_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    create_context_menu(parent_entry, add_window)

    # Телефон родителя
    tk.Label(parent_contact_frame, text="Телефон родителя", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
    parent_phone_entry = tk.Entry(parent_contact_frame)
    parent_phone_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    parent_phone_entry.insert(0, "+7-___-___-__-__")
    parent_phone_entry.bind("<FocusIn>", lambda e: parent_phone_entry.delete(0,
                                                                             tk.END) if "+7-___-___-__-__" in parent_phone_entry.get() else None)
    parent_phone_entry.bind("<KeyRelease>", lambda event: format_phone(event, parent_phone_entry))
    create_context_menu(parent_phone_entry, add_window)

    # Экзамены (нижняя половина)
    exam_frame = tk.LabelFrame(bottom_container, text="ЭКЗАМЕНЫ:",
                               font=("Arial", 12, "bold"), padx=10, pady=10)
    exam_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

    # Настройка масштабирования для exam_frame
    for i in range(3):
        exam_frame.rowconfigure(i, weight=1)
    exam_frame.columnconfigure(0, weight=1)
    exam_frame.columnconfigure(1, weight=2)

    # Функция валидации для ввода только чисел от 0 до 100
    def validate_exam_score(P):
        if P == "":
            return True
        try:
            value = int(P)
            return 0 <= value <= 100
        except ValueError:
            return False

    vcmd = (add_window.register(validate_exam_score), '%P')

    # Русский язык
    tk.Label(exam_frame, text="Русский язык (0-100)", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
    russian_entry = tk.Entry(exam_frame, validate='key', validatecommand=vcmd)
    russian_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    russian_entry.insert(0, "0")
    create_context_menu(russian_entry, add_window)

    # Математика
    tk.Label(exam_frame, text="Математика (0-100)", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
    math_entry = tk.Entry(exam_frame, validate='key', validatecommand=vcmd)
    math_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    math_entry.insert(0, "0")
    create_context_menu(math_entry, add_window)

    # Информатика
    tk.Label(exam_frame, text="Информатика (0-100)", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
    informatics_entry = tk.Entry(exam_frame, validate='key', validatecommand=vcmd)
    informatics_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
    informatics_entry.insert(0, "0")
    create_context_menu(informatics_entry, add_window)

    # Фрейм для кнопок
    button_frame = tk.Frame(add_window)
    button_frame.pack(fill="x", padx=20, pady=20)

    def update_rating(*args):
        try:
            russian = int(russian_entry.get()) if russian_entry.get() and russian_entry.get() != "0" else 0
            math = int(math_entry.get()) if math_entry.get() and math_entry.get() != "0" else 0
            informatics = int(
                informatics_entry.get()) if informatics_entry.get() and informatics_entry.get() != "0" else 0
            total = russian + math + informatics
            rating_var.set(str(total))
        except ValueError:
            pass

    russian_entry.bind("<KeyRelease>", update_rating)
    math_entry.bind("<KeyRelease>", update_rating)
    informatics_entry.bind("<KeyRelease>", update_rating)

    # Функция сохранения данных
    def save_applicant():
        try:

            # Валидация обязательных полей
            if not fio_entry.get().strip():
                messagebox.showerror("Ошибка", "Поле ФИО не может быть пустым")
                return

            email = email_entry.get().strip()
            if email and '@' not in email:
                messagebox.showerror("Ошибка", "Неверный формат email")
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
                rating = float(rating_entry.get().strip()) if rating_entry.get().strip() else 0.0
            except ValueError:
                messagebox.showerror("Ошибка", "Рейтинг должен быть числом")
                return

            try:
                russian_score = int(russian_entry.get().strip()) if russian_entry.get().strip() else 0
                math_score = int(math_entry.get().strip()) if math_entry.get().strip() else 0
                informatics_score = int(informatics_entry.get().strip()) if informatics_entry.get().strip() else 0

                if not (0 <= russian_score <= 100):
                    messagebox.showerror("Ошибка", "Балл по русскому языку должен быть от 0 до 100")
                    return
                if not (0 <= math_score <= 100):
                    messagebox.showerror("Ошибка", "Балл по математике должен быть от 0 до 100")
                    return
                if not (0 <= informatics_score <= 100):
                    messagebox.showerror("Ошибка", "Балл по информатике должен быть от 0 до 100")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Баллы экзаменов должны быть целыми числами")
                return

            current_date = datetime.now().date()

            # Дата подачи теперь необязательное поле
            submission_date = None
            if submission_date_entry.get() and submission_date_entry.get() != "ДД.ММ.ГГГГ":
                try:
                    submission_date_str = submission_date_entry.get()
                    submission_date = datetime.strptime(submission_date_str, "%d.%m.%Y").date()
                    # Проверка, что дата не в будущем
                    if submission_date > current_date:
                        logger.warning(f"Введена будущая дата подачи: {submission_date_entry.get()}")
                        messagebox.showwarning("Предупреждение", "Дата подачи не может быть в будущем времени")
                        return
                except ValueError:
                    messagebox.showerror("Ошибка", "Неправильный формат даты подачи (ДД.ММ.ГГГГ)")
                    return

            visit_date = None
            if visit_date_entry.get() and visit_date_entry.get() != "ДД.ММ.ГГГГ":
                try:
                    # Преобразуем строку в объект date
                    visit_date = datetime.strptime(visit_date_entry.get(), "%d.%m.%Y").date()
                    if visit_date > current_date:
                        logger.warning(f"Введена будущая дата посещения: {visit_date_entry.get()}")
                        messagebox.showwarning("Предупреждение", "Дата посещения не может быть в будущем времени")
                        return
                except ValueError:
                    messagebox.showerror("Ошибка", "Неправильный формат даты посещения (ДД.ММ.ГГГГ)")
                    return

            # Создание объектов для нового абитуриента
            application_details = ApplicationDetails(
                number=number_entry.get(),
                code=code_entry.get(),
                rating=rating,
                has_original=original_var.get(),
                benefits=benefits_var.get() if benefits_var.get() else None,  # Из ComboBox
                submission_date=submission_date
            )

            education = EducationalBackground(
                institution=institution_entry.get()
            )

            contact_info = ContactInfo(
                phone=phone_entry.get(),
                email=email if email else None,
                vk=vk_entry.get() if vk_entry.get() else None,
                nickname=nickname_entry.get() if nickname_entry.get() else None
            )

            additional_info = AdditionalInfo(
                department_visit=visit_date,
                notes=notes_text.get("1.0", tk.END).strip() if notes_text.get("1.0", tk.END).strip() else None,
                information_source=info_source_entry.get() if info_source_entry.get() else None,
                dormitory_needed=dormitory_var.get()
            )

            exam_scores = ExamScores(
                russian=russian_score,
                math=math_score,
                informatics=informatics_score
            )

            parent = None
            if parent_entry.get() and parent_phone_entry.get():
                parent = Parent(
                    full_name=parent_entry.get(),
                    phone=parent_phone_entry.get()
                )

            new_applicant = Applicant(
                full_name=fio_entry.get(),
                phone=phone_entry.get(),
                city=city_entry.get(),
                application_details=application_details,
                education=education,
                contact_info=contact_info,
                additional_info=additional_info,
                parent=parent,
                exam_scores=exam_scores  # Добавляем баллы экзаменов
            )

            # Добавление абитуриента в реестр
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
        add_applicant_window(parent, applicants, load_data_callback, logger)

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