import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from classes import *


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
        self.edit_window.title(f"Редактирование абитуриента: {self.selected_applicant.get_full_name()}")
        self.edit_window.geometry("800x600")
        self.edit_window.resizable(False, False)  # Запрет изменения размера окна
        self.edit_window.grab_set()  # Делаем окно модальным

        # Создаем Canvas с полосой прокрутки
        canvas = tk.Canvas(self.edit_window)
        scrollbar = ttk.Scrollbar(self.edit_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Создаем фреймы для организации интерфейса в scrollable_frame вместо edit_window
        main_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Создаем элементы формы
        self._create_personal_info_section(main_frame)
        self._create_education_section(main_frame)
        self._create_application_section(main_frame)
        self._create_additional_info_section(main_frame)
        self._create_parent_info_section(main_frame)
        self._create_buttons_section(main_frame)

        # Привязываем обработчик к событию закрытия окна
        self.edit_window.protocol("WM_DELETE_WINDOW", self._on_edit_closing)

    def _create_personal_info_section(self, parent_frame):
        """Создание раздела личной информации"""
        personal_frame = tk.LabelFrame(parent_frame, text="Личная информация", padx=10, pady=10)
        personal_frame.pack(fill="x", pady=5)

        # Поля для ввода основной информации
        tk.Label(personal_frame, text="ФИО:").grid(row=0, column=0, sticky="w", pady=5)
        self.full_name_var = tk.StringVar(value=self.selected_applicant.get_full_name())
        tk.Entry(personal_frame, textvariable=self.full_name_var, width=40).grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(personal_frame, text="Телефон:").grid(row=1, column=0, sticky="w", pady=5)
        self.phone_var = tk.StringVar(value=self.selected_applicant.get_phone())
        self.phone_entry = tk.Entry(personal_frame, textvariable=self.phone_var, width=40)
        self.phone_entry.grid(row=1, column=1, sticky="w", pady=5)
        # Привязываем форматирование телефона
        self.phone_entry.bind("<KeyRelease>", lambda event: format_phone(event, self.phone_entry))

        tk.Label(personal_frame, text="Город:").grid(row=2, column=0, sticky="w", pady=5)
        self.city_var = tk.StringVar(value=self.selected_applicant.get_city())
        tk.Entry(personal_frame, textvariable=self.city_var, width=40).grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(personal_frame, text="Профиль ВК:").grid(row=3, column=0, sticky="w", pady=5)
        self.vk_var = tk.StringVar(value=self.selected_applicant.contact_info.vk or "")
        tk.Entry(personal_frame, textvariable=self.vk_var, width=40).grid(row=3, column=1, sticky="w", pady=5)

    def _create_education_section(self, parent_frame):
        """Создание раздела информации об образовании"""
        education_frame = tk.LabelFrame(parent_frame, text="Образование", padx=10, pady=10)
        education_frame.pack(fill="x", pady=5)

        tk.Label(education_frame, text="Учебное заведение:").grid(row=0, column=0, sticky="w", pady=5)
        self.institution_var = tk.StringVar(value=self.selected_applicant.education.institution)
        tk.Entry(education_frame, textvariable=self.institution_var, width=40).grid(row=0, column=1, sticky="w", pady=5)

    def _create_application_section(self, parent_frame):
        """Создание раздела информации о заявке"""
        application_frame = tk.LabelFrame(parent_frame, text="Информация о заявке", padx=10, pady=10)
        application_frame.pack(fill="x", pady=5)

        tk.Label(application_frame, text="Код:").grid(row=0, column=0, sticky="w", pady=5)
        self.code_var = tk.StringVar(value=self.selected_applicant.get_code())
        tk.Entry(application_frame, textvariable=self.code_var, width=20).grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(application_frame, text="Рейтинг:").grid(row=1, column=0, sticky="w", pady=5)
        self.rating_var = tk.StringVar(value=str(self.selected_applicant.get_rating()))
        tk.Entry(application_frame, textvariable=self.rating_var, width=20).grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(application_frame, text="Льгота:").grid(row=2, column=0, sticky="w", pady=5)
        self.benefits_var = tk.StringVar(value=self.selected_applicant.get_benefits() or "")
        tk.Entry(application_frame, textvariable=self.benefits_var, width=20).grid(row=2, column=1, sticky="w", pady=5)

        self.has_original_var = tk.BooleanVar(value=self.selected_applicant.has_original_documents())
        tk.Checkbutton(application_frame, text="Оригинал документов", variable=self.has_original_var).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=5)

    def _create_additional_info_section(self, parent_frame):
        """Создание раздела дополнительной информации"""
        additional_frame = tk.LabelFrame(parent_frame, text="Дополнительная информация", padx=10, pady=10)
        additional_frame.pack(fill="x", pady=5)

        self.dormitory_var = tk.BooleanVar(value=self.selected_applicant.additional_info.dormitory_needed)
        tk.Checkbutton(additional_frame, text="Нужно общежитие", variable=self.dormitory_var).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=5)

        tk.Label(additional_frame, text="Дата посещения:").grid(row=1, column=0, sticky="w", pady=5)
        self.visit_date_var = tk.StringVar()
        if self.selected_applicant.additional_info.department_visit:
            visit_date_str = self.selected_applicant.additional_info.department_visit.strftime("%d.%m.%Y")
            self.visit_date_var.set(visit_date_str)
        self.visit_date_entry = tk.Entry(additional_frame, textvariable=self.visit_date_var, width=20)
        self.visit_date_entry.grid(row=1, column=1, sticky="w", pady=5)
        # Привязываем форматирование даты
        self.visit_date_entry.bind("<KeyRelease>", lambda event: format_date(event, self.visit_date_entry))

        tk.Label(additional_frame, text="Источник информации:").grid(row=2, column=0, sticky="w", pady=5)
        self.info_source_var = tk.StringVar(value=self.selected_applicant.additional_info.information_source or "")
        tk.Entry(additional_frame, textvariable=self.info_source_var, width=40).grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(additional_frame, text="Примечания:").grid(row=3, column=0, sticky="w", pady=5)
        self.notes_text = tk.Text(additional_frame, width=40, height=4)
        self.notes_text.grid(row=3, column=1, sticky="w", pady=5)
        if self.selected_applicant.additional_info.notes:
            self.notes_text.insert("1.0", self.selected_applicant.additional_info.notes)

    def _create_parent_info_section(self, parent_frame):
        """Создание раздела информации о родителе"""
        parent_frame = tk.LabelFrame(parent_frame, text="Информация о родителе", padx=10, pady=10)
        parent_frame.pack(fill="x", pady=5)

        tk.Label(parent_frame, text="ФИО родителя:").grid(row=0, column=0, sticky="w", pady=5)
        self.parent_name_var = tk.StringVar()
        if self.selected_applicant.parent:
            self.parent_name_var.set(self.selected_applicant.parent.full_name)
        tk.Entry(parent_frame, textvariable=self.parent_name_var, width=40).grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(parent_frame, text="Телефон родителя:").grid(row=1, column=0, sticky="w", pady=5)
        self.parent_phone_var = tk.StringVar()
        if self.selected_applicant.parent:
            self.parent_phone_var.set(self.selected_applicant.parent.phone)
        self.parent_phone_entry = tk.Entry(parent_frame, textvariable=self.parent_phone_var, width=40)
        self.parent_phone_entry.grid(row=1, column=1, sticky="w", pady=5)
        # Привязываем форматирование телефона родителя
        self.parent_phone_entry.bind("<KeyRelease>", lambda event: format_phone(event, self.parent_phone_entry))

    def _create_buttons_section(self, parent_frame):
        """Создание раздела с кнопками управления"""
        button_frame = tk.Frame(parent_frame)
        button_frame.pack(fill="x", pady=10)

        save_button = tk.Button(button_frame, text="Сохранить", width=10, command=self._save_changes)
        save_button.pack(side="left", padx=5)

        cancel_button = tk.Button(button_frame, text="Отмена", width=10, command=self._on_edit_closing)
        cancel_button.pack(side="left", padx=5)

    def _on_edit_closing(self):
        """Обработка закрытия окна редактирования"""
        ask_save = messagebox.askyesnocancel("Сохранение изменений",
                                           "Хотите сохранить внесенные изменения?")
        if ask_save is None:  # Пользователь нажал Отмена
            return
        elif ask_save:  # Пользователь нажал Да
            self._save_changes()
        else:  # Пользователь нажал Нет
            self.edit_window.destroy()

    def _save_changes(self):
        """Сохранение изменений данных абитуриента"""
        try:
            # Обновление данных абитуриента
            self.selected_applicant.full_name = self.full_name_var.get()
            self.selected_applicant.phone = self.phone_var.get()
            self.selected_applicant.city = self.city_var.get()
            self.selected_applicant.contact_info.vk = self.vk_var.get()

            self.selected_applicant.education.institution = self.institution_var.get()

            self.selected_applicant.application_details.code = self.code_var.get()
            self.selected_applicant.application_details.rating = float(self.rating_var.get())
            self.selected_applicant.application_details.benefits = self.benefits_var.get()
            self.selected_applicant.application_details.has_original = self.has_original_var.get()

            self.selected_applicant.additional_info.dormitory_needed = self.dormitory_var.get()
            self.selected_applicant.additional_info.information_source = self.info_source_var.get()
            self.selected_applicant.additional_info.notes = self.notes_text.get("1.0", "end-1c")

            # Обработка даты посещения
            visit_date = self.visit_date_var.get()
            if visit_date:
                try:
                    visit_date = datetime.strptime(visit_date, "%d.%m.%Y")
                    # Проверка на будущую дату
                    if visit_date > datetime.now():
                        messagebox.showwarning("Ошибка даты", "Дата посещения не может быть в будущем")
                        return
                    self.selected_applicant.additional_info.department_visit = visit_date
                except ValueError:
                    messagebox.showwarning("Ошибка даты", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
                    return

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

            # Вызов колбэка для обновления данных в основном окне
            self.on_save_callback()

            # Закрытие окна редактирования
            self.edit_window.destroy()
            messagebox.showinfo("Редактирование", "Данные абитуриента успешно обновлены")

        except Exception as e:
            error_msg = f"Ошибка при сохранении данных: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка", error_msg)