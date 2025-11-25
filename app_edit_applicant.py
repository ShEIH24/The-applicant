import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from classes import *


# Список основных льгот
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

    def copy_to_clipboard():
        try:
            if isinstance(widget, tk.Text):
                selected_text = widget.get("sel.first", "sel.last")
                parent_window.clipboard_clear()
                parent_window.clipboard_append(selected_text)
            else:
                parent_window.clipboard_clear()
                parent_window.clipboard_append(widget.selection_get())
        except tk.TclError:
            pass

    def cut_to_clipboard():
        try:
            if isinstance(widget, tk.Text):
                selected_text = widget.get("sel.first", "sel.last")
                parent_window.clipboard_clear()
                parent_window.clipboard_append(selected_text)
                widget.delete("sel.first", "sel.last")
            else:
                parent_window.clipboard_clear()
                parent_window.clipboard_append(widget.selection_get())
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def paste_from_clipboard():
        try:
            clipboard_text = parent_window.clipboard_get()
            if isinstance(widget, tk.Text):
                try:
                    widget.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass
                widget.insert(tk.INSERT, clipboard_text)
            else:
                try:
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except tk.TclError:
                    pass
                widget.insert(tk.INSERT, clipboard_text)
        except:
            pass

    def select_all():
        try:
            if isinstance(widget, tk.Text):
                widget.tag_add(tk.SEL, "1.0", tk.END)
                widget.mark_set(tk.INSERT, "1.0")
                widget.see(tk.INSERT)
                return 'break'
            else:
                widget.select_range(0, tk.END)
                widget.icursor(tk.END)
                return 'break'
        except:
            pass

    popup_menu.add_command(label="Копировать", command=copy_to_clipboard)
    popup_menu.add_command(label="Вырезать", command=cut_to_clipboard)
    popup_menu.add_command(label="Вставить", command=paste_from_clipboard)
    popup_menu.add_command(label="Выделить всё", command=select_all)

    def show_popup_menu(event):
        try:
            popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup_menu.grab_release()

    widget.bind("<Button-3>", show_popup_menu)
    widget.bind("<Control-c>", lambda e: copy_to_clipboard())
    widget.bind("<Control-x>", lambda e: cut_to_clipboard())
    widget.bind("<Control-v>", lambda e: paste_from_clipboard())
    widget.bind("<Control-a>", lambda e: select_all())

    if isinstance(widget, tk.Text):
        widget.bind("<Control-z>", lambda e: widget.edit_undo())
        widget.bind("<Control-y>", lambda e: widget.edit_redo())


def format_date(event=None, entry=None):
    """Функция для автоматического форматирования даты"""
    if not entry:
        return
    text = entry.get().replace(".", "")
    text = ''.join(filter(str.isdigit, text))
    formatted = ""

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


class ApplicantEditForm:
    def __init__(self, parent, selected_applicant, on_save_callback, logger):
        """Конструктор формы редактирования абитуриента"""
        self.parent = parent
        self.selected_applicant = selected_applicant
        self.on_save_callback = on_save_callback
        self.logger = logger
        self.edit_window = None

    def show(self):
        """Отображение формы редактирования абитуриента"""
        if not self.selected_applicant:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите абитуриента для редактирования")
            self.logger.warning("Попытка редактирования без выбора абитуриента")
            return

        self.logger.info(f"Открытие формы редактирования абитуриента: {self.selected_applicant.get_full_name()}")

        # Создаем окно редактирования
        self.edit_window = tk.Toplevel(self.parent)
        self.edit_window.title(f"Редактирование абитуриента")
        self.edit_window.geometry("1400x650")
        self.edit_window.resizable(True, True)
        self.edit_window.minsize(1400, 650)
        self.edit_window.grab_set()

        setup_keyboard_shortcuts(self.edit_window)

        # Применяем стиль заголовка
        header_frame = tk.Frame(self.edit_window, bg="#3f51b5", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame, text="АБИТУРИЕНТ",
                                font=("Arial", 16, "bold"),
                                bg="#3f51b5", fg="white")
        header_label.pack(side="left", padx=20, pady=20)

        # Создаем контейнер для формы
        form_container = tk.Frame(self.edit_window, padx=20, pady=20)
        form_container.pack(fill="both", expand=True)

        # Конфигурация строк и столбцов
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

        # Основная информация (левая половина)
        basic_frame = tk.LabelFrame(info_container, text="ОСНОВНАЯ ИНФОРМАЦИЯ:", font=("Arial", 12, "bold"), padx=10,
                                    pady=10)
        basic_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        for i in range(3):
            basic_frame.rowconfigure(i, weight=1)
        basic_frame.columnconfigure(0, weight=1)
        basic_frame.columnconfigure(1, weight=2)

        # ФИО
        tk.Label(basic_frame, text="ФИО *", font=("Arial", 9), fg="red").grid(row=0, column=0, sticky="w", pady=5)
        self.fio_var = tk.StringVar(value=self.selected_applicant.get_full_name())
        fio_entry = tk.Entry(basic_frame, textvariable=self.fio_var)
        fio_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(fio_entry, self.edit_window)

        # Учебное заведение
        tk.Label(basic_frame, text="Учебное заведение *", font=("Arial", 9), fg="red").grid(row=1, column=0, sticky="w",
                                                                                            pady=5)
        self.institution_var = tk.StringVar(value=self.selected_applicant.education.institution)
        institution_entry = tk.Entry(basic_frame, textvariable=self.institution_var)
        institution_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(institution_entry, self.edit_window)

        # Город
        tk.Label(basic_frame, text="Город *", font=("Arial", 9), fg="red").grid(row=2, column=0, sticky="w", pady=5)
        self.city_var = tk.StringVar(value=self.selected_applicant.get_city())
        city_entry = tk.Entry(basic_frame, textvariable=self.city_var)
        city_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(city_entry, self.edit_window)

        # Контактная информация (правая половина)
        contact_frame = tk.LabelFrame(info_container, text="КОНТАКТНАЯ ИНФОРМАЦИЯ:", font=("Arial", 12, "bold"),
                                      padx=10, pady=10)
        contact_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        for i in range(4):
            contact_frame.rowconfigure(i, weight=1)
        contact_frame.columnconfigure(0, weight=1)
        contact_frame.columnconfigure(1, weight=2)

        # Телефон
        tk.Label(contact_frame, text="Телефон *", font=("Arial", 9), fg="red").grid(row=0, column=0, sticky="w", pady=5)
        self.phone_var = tk.StringVar(value=self.selected_applicant.get_phone())
        self.phone_entry = tk.Entry(contact_frame, textvariable=self.phone_var)
        self.phone_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.phone_entry.bind("<KeyRelease>", lambda event: format_phone(event, self.phone_entry))
        create_context_menu(self.phone_entry, self.edit_window)

        # Email
        tk.Label(contact_frame, text="Email", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
        self.email_var = tk.StringVar(value=self.selected_applicant.contact_info.email or "")
        email_entry = tk.Entry(contact_frame, textvariable=self.email_var)
        email_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(email_entry, self.edit_window)

        # Профиль ВК
        tk.Label(contact_frame, text="Профиль ВК", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
        self.vk_var = tk.StringVar(value=self.selected_applicant.contact_info.vk or "")
        vk_entry = tk.Entry(contact_frame, textvariable=self.vk_var)
        vk_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(vk_entry, self.edit_window)

        # Ник
        tk.Label(contact_frame, text="Ник", font=("Arial", 9)).grid(row=3, column=0, sticky="w", pady=5)
        self.nickname_var = tk.StringVar(value=self.selected_applicant.contact_info.nickname or "")
        nickname_entry = tk.Entry(contact_frame, textvariable=self.nickname_var)
        nickname_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(nickname_entry, self.edit_window)

        # Дополнительная информация
        additional_frame = tk.LabelFrame(form_container, text="ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:", font=("Arial", 12, "bold"),
                                         padx=10, pady=10)
        additional_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(7):
            additional_frame.rowconfigure(i, weight=1)
        for i in range(4):
            additional_frame.columnconfigure(i, weight=1)
        additional_frame.columnconfigure(1, weight=2)
        additional_frame.columnconfigure(3, weight=2)

        # Номер (readonly)
        tk.Label(additional_frame, text="Номер", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
        self.number_var = tk.StringVar(value=self.selected_applicant.get_number())
        number_entry = tk.Entry(additional_frame, textvariable=self.number_var, state="readonly")
        number_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Код
        tk.Label(additional_frame, text="Код", font=("Arial", 9)).grid(row=0, column=2, sticky="w", pady=5,
                                                                       padx=(20, 0))
        self.code_var = tk.StringVar(value=self.selected_applicant.get_code())
        code_entry = tk.Entry(additional_frame, textvariable=self.code_var)
        code_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        create_context_menu(code_entry, self.edit_window)

        # Рейтинг
        tk.Label(additional_frame, text="Рейтинг", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
        self.rating_var = tk.StringVar(value=str(self.selected_applicant.get_rating()))
        self.rating_entry = tk.Entry(additional_frame, textvariable=self.rating_var)
        self.rating_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(self.rating_entry, self.edit_window)

        # Льгота (ComboBox)
        tk.Label(additional_frame, text="Льгота", font=("Arial", 9)).grid(row=1, column=2, sticky="w", pady=5,
                                                                          padx=(20, 0))
        self.benefits_var = tk.StringVar(value=self.selected_applicant.get_benefits() or "")
        benefits_combo = ttk.Combobox(additional_frame, textvariable=self.benefits_var, values=BENEFITS_LIST,
                                      state="readonly")
        benefits_combo.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        if self.selected_applicant.get_benefits() in BENEFITS_LIST:
            benefits_combo.current(BENEFITS_LIST.index(self.selected_applicant.get_benefits()))
        else:
            benefits_combo.current(0)

        # Дата подачи
        tk.Label(additional_frame, text="Дата подачи", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
        self.submission_date_var = tk.StringVar()
        if self.selected_applicant.application_details.submission_date:
            submission_date_str = self.selected_applicant.application_details.get_submission_date_formatted()
            self.submission_date_var.set(submission_date_str)
        self.submission_date_entry = tk.Entry(additional_frame, textvariable=self.submission_date_var)
        self.submission_date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.submission_date_entry.bind("<KeyRelease>", lambda event: format_date(event, self.submission_date_entry))
        create_context_menu(self.submission_date_entry, self.edit_window)

        # Оригинал
        tk.Label(additional_frame, text="Оригинал", font=("Arial", 9)).grid(row=2, column=2, sticky="w", pady=5,
                                                                            padx=(20, 0))
        self.original_var = tk.BooleanVar(value=self.selected_applicant.has_original_documents())
        original_check = tk.Checkbutton(additional_frame, text="Да", variable=self.original_var)
        original_check.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Дата посещения
        tk.Label(additional_frame, text="Дата посещения", font=("Arial", 9)).grid(row=3, column=0, sticky="w", pady=5)
        self.visit_date_var = tk.StringVar()
        if self.selected_applicant.additional_info.department_visit:
            visit_date_str = self.selected_applicant.additional_info.department_visit.strftime("%d.%m.%Y")
            self.visit_date_var.set(visit_date_str)
        self.visit_date_entry = tk.Entry(additional_frame, textvariable=self.visit_date_var)
        self.visit_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.visit_date_entry.bind("<KeyRelease>", lambda event: format_date(event, self.visit_date_entry))
        create_context_menu(self.visit_date_entry, self.edit_window)

        # Общежитие
        tk.Label(additional_frame, text="Общежитие", font=("Arial", 9)).grid(row=3, column=2, sticky="w", pady=5,
                                                                             padx=(20, 0))
        self.dormitory_var = tk.BooleanVar(value=self.selected_applicant.additional_info.dormitory_needed)
        dormitory_check = tk.Checkbutton(additional_frame, text="Да", variable=self.dormitory_var)
        dormitory_check.grid(row=3, column=3, sticky="w", padx=5, pady=5)

        # Откуда узнал/а
        tk.Label(additional_frame, text="Откуда узнал/а", font=("Arial", 9)).grid(row=4, column=0, sticky="w", pady=5)
        self.info_source_var = tk.StringVar(value=self.selected_applicant.additional_info.information_source or "")
        info_source_entry = tk.Entry(additional_frame, textvariable=self.info_source_var)
        info_source_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5, columnspan=3)
        create_context_menu(info_source_entry, self.edit_window)

        # Примечание
        tk.Label(additional_frame, text="Примечание", font=("Arial", 9)).grid(row=5, column=0, sticky="nw", pady=5)
        self.notes_text = tk.Text(additional_frame, height=3)
        self.notes_text.grid(row=5, column=1, rowspan=2, sticky="nsew", padx=5, pady=5, columnspan=3)
        if self.selected_applicant.additional_info.notes:
            self.notes_text.insert("1.0", self.selected_applicant.additional_info.notes)
        create_context_menu(self.notes_text, self.edit_window)

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

        for i in range(2):
            parent_contact_frame.rowconfigure(i, weight=1)
        parent_contact_frame.columnconfigure(0, weight=1)
        parent_contact_frame.columnconfigure(1, weight=2)

        # Родитель
        tk.Label(parent_contact_frame, text="Родитель", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
        self.parent_name_var = tk.StringVar()
        if self.selected_applicant.parent:
            self.parent_name_var.set(self.selected_applicant.parent.full_name)
        parent_entry = tk.Entry(parent_contact_frame, textvariable=self.parent_name_var)
        parent_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(parent_entry, self.edit_window)

        # Телефон родителя
        tk.Label(parent_contact_frame, text="Телефон родителя", font=("Arial", 9)).grid(row=1, column=0, sticky="w",
                                                                                        pady=5)
        self.parent_phone_var = tk.StringVar()
        if self.selected_applicant.parent:
            self.parent_phone_var.set(self.selected_applicant.parent.phone)
        self.parent_phone_entry = tk.Entry(parent_contact_frame, textvariable=self.parent_phone_var)
        self.parent_phone_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.parent_phone_entry.bind("<KeyRelease>", lambda event: format_phone(event, self.parent_phone_entry))
        create_context_menu(self.parent_phone_entry, self.edit_window)

        # Экзамены (нижняя половина)
        exam_frame = tk.LabelFrame(bottom_container, text="ЭКЗАМЕНЫ:",
                                   font=("Arial", 12, "bold"), padx=10, pady=10)
        exam_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

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

        vcmd = (self.edit_window.register(validate_exam_score), '%P')

        # Функция обновления рейтинга
        def update_rating(*args):
            try:
                russian = int(self.russian_var.get()) if self.russian_var.get() else 0
                math = int(self.math_var.get()) if self.math_var.get() else 0
                informatics = int(self.informatics_var.get()) if self.informatics_var.get() else 0
                total = russian + math + informatics
                self.rating_var.set(str(total))
            except ValueError:
                pass

        # Русский язык
        tk.Label(exam_frame, text="Русский язык (0-100)", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
        self.russian_var = tk.StringVar(value=str(self.selected_applicant.exam_scores.russian))
        self.russian_var.trace("w", update_rating)
        russian_entry = tk.Entry(exam_frame, textvariable=self.russian_var, validate='key', validatecommand=vcmd)
        russian_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(russian_entry, self.edit_window)

        # Математика
        tk.Label(exam_frame, text="Математика (0-100)", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
        self.math_var = tk.StringVar(value=str(self.selected_applicant.exam_scores.math))
        self.math_var.trace("w", update_rating)
        math_entry = tk.Entry(exam_frame, textvariable=self.math_var, validate='key', validatecommand=vcmd)
        math_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(math_entry, self.edit_window)

        # Информатика
        tk.Label(exam_frame, text="Информатика (0-100)", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
        self.informatics_var = tk.StringVar(value=str(self.selected_applicant.exam_scores.informatics))
        self.informatics_var.trace("w", update_rating)
        informatics_entry = tk.Entry(exam_frame, textvariable=self.informatics_var, validate='key',
                                     validatecommand=vcmd)
        informatics_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        create_context_menu(informatics_entry, self.edit_window)

        # Фрейм для кнопок
        button_frame = tk.Frame(self.edit_window)
        button_frame.pack(fill="x", padx=20, pady=20)

        save_button = tk.Button(
            button_frame,
            text="Сохранить",
            bg="#3f51b5",
            fg="white",
            font=("Arial", 10),
            width=15,
            command=self._save_changes
        )
        save_button.pack(side="right", padx=5)

        cancel_button = tk.Button(
            button_frame,
            text="Отмена",
            bg="#757575",
            fg="white",
            font=("Arial", 10),
            width=15,
            command=self._on_edit_closing
        )
        cancel_button.pack(side="right", padx=5)

        # Привязываем обработчик к событию закрытия окна
        self.edit_window.protocol("WM_DELETE_WINDOW", self._on_edit_closing)

    def _create_buttons_section(self):
        """Создание блока с кнопками"""
        button_frame = tk.Frame(self.edit_window)
        button_frame.pack(fill="x", padx=20, pady=20)

        save_button = tk.Button(
            button_frame,
            text="Сохранить",
            bg="#3f51b5",
            fg="white",
            font=("Arial", 10),
            width=15,
            command=self._save_changes
        )
        save_button.pack(side="right", padx=5)

        cancel_button = tk.Button(
            button_frame,
            text="Отмена",
            bg="#757575",
            fg="white",
            font=("Arial", 10),
            width=15,
            command=self._on_edit_closing
        )
        cancel_button.pack(side="right", padx=5)

    def _on_edit_closing(self):
        """Обработка закрытия окна редактирования"""
        ask_save = messagebox.askyesnocancel("Сохранение изменений",
                                             "Хотите сохранить внесенные изменения?")
        if ask_save is None:
            return
        elif ask_save:
            self._save_changes()
        else:
            self.edit_window.destroy()

    def _save_changes(self):
        """Сохранение изменений данных абитуриента"""
        try:
            # Валидация обязательных полей
            if not self.fio_var.get().strip():
                messagebox.showerror("Ошибка", "Поле ФИО не может быть пустым")
                return

            if not self.institution_var.get().strip():
                messagebox.showerror("Ошибка", "Поле Учебное заведение не может быть пустым")
                return

            if not self.city_var.get().strip():
                messagebox.showerror("Ошибка", "Поле Город не может быть пустым")
                return

            if not self.phone_var.get().strip():
                messagebox.showerror("Ошибка", "Поле Телефон не может быть пустым")
                return

            # Валидация email
            email = self.email_var.get().strip()
            if email and '@' not in email:
                messagebox.showerror("Ошибка", "Неверный формат email")
                return

            # Валидация баллов экзаменов
            try:
                russian_score = int(self.russian_var.get().strip()) if self.russian_var.get().strip() else 0
                math_score = int(self.math_var.get().strip()) if self.math_var.get().strip() else 0
                informatics_score = int(self.informatics_var.get().strip()) if self.informatics_var.get().strip() else 0

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

            # Обновление данных абитуриента
            self.selected_applicant.full_name = self.fio_var.get()
            self.selected_applicant.phone = self.phone_var.get()
            self.selected_applicant.city = self.city_var.get()
            self.selected_applicant.contact_info.email = email if email else None
            self.selected_applicant.contact_info.vk = self.vk_var.get()
            self.selected_applicant.contact_info.nickname = self.nickname_var.get() if self.nickname_var.get() else None

            self.selected_applicant.education.institution = self.institution_var.get()

            self.selected_applicant.application_details.code = self.code_var.get()
            self.selected_applicant.application_details.rating = float(self.rating_var.get())
            self.selected_applicant.application_details.benefits = self.benefits_var.get() if self.benefits_var.get() else None
            self.selected_applicant.application_details.has_original = self.original_var.get()

            # Обновление баллов экзаменов
            self.selected_applicant.exam_scores.russian = russian_score
            self.selected_applicant.exam_scores.math = math_score
            self.selected_applicant.exam_scores.informatics = informatics_score

            # Обработка даты подачи
            submission_date_str = self.submission_date_var.get()
            if submission_date_str and submission_date_str != "ДД.ММ.ГГГГ":
                try:
                    submission_date = datetime.strptime(submission_date_str, "%d.%m.%Y").date()
                    if submission_date > datetime.now().date():
                        messagebox.showwarning("Ошибка даты", "Дата подачи не может быть в будущем")
                        return
                    self.selected_applicant.application_details.submission_date = submission_date
                except ValueError:
                    messagebox.showwarning("Ошибка даты", "Неверный формат даты подачи. Используйте ДД.ММ.ГГГГ")
                    return
            else:
                self.selected_applicant.application_details.submission_date = None

            self.selected_applicant.additional_info.dormitory_needed = self.dormitory_var.get()
            self.selected_applicant.additional_info.information_source = self.info_source_var.get()
            self.selected_applicant.additional_info.notes = self.notes_text.get("1.0", "end-1c")

            # Обработка даты посещения
            visit_date = self.visit_date_var.get()
            if visit_date and visit_date != "ДД.ММ.ГГГГ":
                try:
                    visit_date = datetime.strptime(visit_date, "%d.%m.%Y").date()
                    if visit_date > datetime.now().date():
                        messagebox.showwarning("Ошибка даты", "Дата посещения не может быть в будущем")
                        return
                    self.selected_applicant.additional_info.department_visit = visit_date
                except ValueError:
                    messagebox.showwarning("Ошибка даты", "Неверный формат даты посещения. Используйте ДД.ММ.ГГГГ")
                    return
            else:
                self.selected_applicant.additional_info.department_visit = None

            # Обработка информации о родителе
            parent_name = self.parent_name_var.get()
            if parent_name:
                if not self.selected_applicant.parent:
                    self.selected_applicant.parent = Parent(full_name=parent_name, phone=self.parent_phone_var.get())
                else:
                    self.selected_applicant.parent.full_name = parent_name
                    self.selected_applicant.parent.phone = self.parent_phone_var.get()
            else:
                self.selected_applicant.parent = None

            self.logger.info(f"Сохранены изменения для абитуриента: {self.selected_applicant.get_full_name()}")

            # Вызов колбэка для обновления данных
            self.on_save_callback()

            # Закрытие окна
            self.edit_window.destroy()
            messagebox.showinfo("Редактирование", "Данные абитуриента успешно обновлены")

        except Exception as e:
            error_msg = f"Ошибка при сохранении данных: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка", error_msg)