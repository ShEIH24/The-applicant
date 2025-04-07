"""app_table.py"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from classes import *
from logger import Logger
from app_add_applicant import add_applicant_window
from app_edit_applicant import ApplicantEditForm


class ApplicantTableWindow:
    def __init__(self, parent, applicants, logger, offer_import=True):
        """
        Инициализация окна с таблицей абитуриентов

        :param parent: Родительский виджет
        :param applicants: Список абитуриентов
        :param logger: Экземпляр логгера
        :param offer_import: Флаг, предлагать ли импорт данных (только при первом запуске)
        """
        self.parent = parent
        self.applicants = applicants
        self.logger = logger
        self.selected_applicant = None

        # Логирование запуска окна с таблицей
        self.logger.info("Инициализация окна с таблицей абитуриентов")

        # Предложение импортировать данные из Excel только при запуске программы
        if offer_import:
            self.offer_import()

        # Настройка адаптивного интерфейса
        self.setup_ui()

        # Заполнение таблицы данными
        self.load_data()

        # Привязка обработчика закрытия окна
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.logger.info("Окно с таблицей абитуриентов успешно инициализировано")

    def offer_import(self):
        """Предлагает пользователю импортировать данные из Excel файла"""
        import_response = messagebox.askyesno("Импорт данных",
                                              "Хотите импортировать данные из Excel файла?")
        if import_response:
            self.import_from_excel()

    def import_from_excel(self):
        """Импорт данных из Excel файла"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")],
            title="Выберите файл Excel для импорта"
        )

        if not file_path:
            self.logger.info("Импорт отменен пользователем")
            return

        try:
            # Чтение данных из Excel
            df = pd.read_excel(file_path)

            # Очистка текущего списка абитуриентов
            self.applicants.clear()

            # Преобразование данных из DataFrame в объекты Applicant
            for _, row in df.iterrows():
                try:
                    # Обработка даты посещения
                    visit_date = None
                    if 'Дата посещения' in row and pd.notna(row['Дата посещения']):
                        try:
                            # Явно указываем формат даты при конвертации
                            visit_date = pd.to_datetime(row['Дата посещения'], dayfirst=True).to_pydatetime()
                        except:
                            visit_date = None

                    # Создание объектов информации
                    app_details = ApplicationDetails(
                        number=row.get('Номер', ''),
                        code=row.get('Код', ''),
                        rating=float(row.get('Рейтинг', 0)),
                        has_original=row.get('Оригинал', '') == 'Да',
                        benefits=row.get('Льгота', ''),
                        submission_date=row.get('Дата подачи', '')
                    )

                    education = EducationalBackground(
                        institution=row.get('Учебное заведение', '')
                    )

                    contact_info = ContactInfo(
                        phone=row.get('Телефон', ''),
                        vk=row.get('Профиль ВК', '')
                    )

                    additional_info = AdditionalInfo(
                        department_visit=visit_date,
                        notes=row.get('Примечание', ''),
                        information_source=row.get('Откуда узнал/а', ''),
                        dormitory_needed=row.get('Общежитие', '') == 'Да'
                    )

                    # Создание объекта родителя при наличии данных
                    parent = None
                    if pd.notna(row.get('Родитель', '')) and row.get('Родитель', '') != '':
                        parent = Parent(
                            full_name=row.get('Родитель', ''),
                            phone=row.get('Телефон родителя', '')
                        )

                    # Создание объекта абитуриента
                    applicant = Applicant(
                        full_name=row.get('ФИО', ''),
                        phone=row.get('Телефон', ''),
                        city=row.get('Город', ''),
                        application_details=app_details,
                        education=education,
                        contact_info=contact_info,
                        additional_info=additional_info,
                        parent=parent
                    )

                    self.applicants.append(applicant)

                except Exception as e:
                    self.logger.error(f"Ошибка при импорте строки: {str(e)}")

            self.logger.info(f"Успешно импортировано {len(self.applicants)} записей из файла: {file_path}")
            messagebox.showinfo("Импорт", f"Успешно импортировано {len(self.applicants)} записей.")

        except Exception as e:
            error_msg = f"Ошибка при импорте данных: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка", f"Произошла ошибка при импорте:\n{str(e)}")

    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.applicants:
            export_response = messagebox.askyesno("Экспорт данных",
                                                  "Хотите экспортировать данные в Excel перед закрытием?")
            if export_response:
                self.export_to_excel()

        self.parent.destroy()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(3, weight=1)

        # Заголовок
        header_frame = tk.Frame(self.parent, bg="#3f51b5", height=70)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        header_label = tk.Label(header_frame, text="АБИТУРИЕНТ",
                                font=("Arial", 16, "bold"),
                                bg="#3f51b5", fg="white")
        header_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Панель кнопок
        button_frame = tk.Frame(self.parent)
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure(7, weight=1)  # Увеличено число столбцов

        # Кнопки управления
        self.add_button = tk.Button(button_frame, bg="#3f51b5", fg="white", text="Добавить", width=10,
                                    command=self.add_applicant)
        self.add_button.grid(row=0, column=0, padx=5)

        self.edit_button = tk.Button(button_frame, bg="#3f51b5", fg="white", text="Изменить", width=10,
                                     command=self.edit_applicant)
        self.edit_button.grid(row=0, column=1, padx=5)

        self.delete_button = tk.Button(button_frame, bg="#3f51b5", fg="white", text="Удалить", width=10,
                                       command=self.delete_applicant)
        self.delete_button.grid(row=0, column=2, padx=5)

        self.refresh_button = tk.Button(button_frame, bg="#3f51b5", fg="white", text="Обновить", width=10,
                                        command=self.refresh_data)
        self.refresh_button.grid(row=0, column=3, padx=5)

        self.filter_button = tk.Button(button_frame, bg="#3f51b5", fg="white", text="Фильтр", width=10,
                                       command=self.filter_data)
        self.filter_button.grid(row=0, column=4, padx=5)

        self.export_button = tk.Button(button_frame, bg="#3f51b5", fg="white", text="Экспорт", width=10,
                                       command=self.export_to_excel)
        self.export_button.grid(row=0, column=5, padx=5)

        self.import_button = tk.Button(button_frame, bg="#3f51b5", fg="white", text="Импорт", width=10,
                                       command=self.import_from_excel)
        self.import_button.grid(row=0, column=6, padx=5)

        # Поле поиска
        search_frame = tk.Frame(self.parent)
        search_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.insert(0, "Поиск абитуриента")

        # Очистка поля поиска при фокусе
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        # Восстановление placeholder при потере фокуса если поле пустое
        self.search_entry.bind("<FocusOut>", self.restore_search_placeholder)
        # Поиск при нажатии Enter
        self.search_entry.bind("<Return>", self.search_applicant)

        # Создание таблицы
        table_frame = tk.Frame(self.parent)
        table_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Создание и настройка скроллбаров
        y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        y_scrollbar.grid(row=0, column=1, sticky="ns")

        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Создание таблицы Treeview
        self.table = ttk.Treeview(table_frame,
                                  yscrollcommand=y_scrollbar.set,
                                  xscrollcommand=x_scrollbar.set,
                                  selectmode="browse")

        self.table.grid(row=0, column=0, sticky="nsew")

        # Настройка скроллбаров
        y_scrollbar.config(command=self.table.yview)
        x_scrollbar.config(command=self.table.xview)

        # Создание и применение стиля для заголовков таблицы
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), foreground='#3f51b5')

        # Настройка заголовков таблицы
        self.setup_table_columns()

        # Обработчик события выбора строки в таблице
        self.table.bind("<<TreeviewSelect>>", self.on_select)

    def setup_table_columns(self):
        """Настройка столбцов таблицы"""
        # Определение столбцов
        self.table["columns"] = (
            "number", "fio", "code", "rating", "benefits", "original",
            "city", "dormitory", "institution", "submission_date",
            "visit_date", "info_source", "phone", "vk", "parent", "parent_phone", "notes"
        )

        # Показываем заголовки
        self.table["show"] = "headings"

        # Настройка заголовков и ширины столбцов
        columns_config = {
            "number": {"text": "Номер", "width": 50, "anchor": "center"},
            "fio": {"text": "ФИО", "width": 200, "anchor": "w"},
            "code": {"text": "Код", "width": 80, "anchor": "center"},
            "rating": {"text": "Рейтинг", "width": 80, "anchor": "center"},
            "benefits": {"text": "Льгота", "width": 100, "anchor": "center"},
            "original": {"text": "Оригинал", "width": 80, "anchor": "center"},
            "city": {"text": "Город", "width": 120, "anchor": "center"},
            "dormitory": {"text": "Общежитие", "width": 100, "anchor": "center"},
            "institution": {"text": "Учебное заведение", "width": 200, "anchor": "w"},
            "submission_date": {"text": "Дата подачи", "width": 100, "anchor": "center"},
            "visit_date": {"text": "Дата посещения", "width": 120, "anchor": "center"},
            "info_source": {"text": "Откуда узнал/а", "width": 150, "anchor": "w"},
            "phone": {"text": "Телефон", "width": 120, "anchor": "w"},
            "vk": {"text": "Профиль ВК", "width": 120, "anchor": "w"},
            "parent": {"text": "Родитель", "width": 200, "anchor": "w"},
            "parent_phone": {"text": "Телефон родителя", "width": 150, "anchor": "w"},
            "notes": {"text": "Примечание", "width": 200, "anchor": "w"}
        }

        # Настройка столбцов
        for col_id, config in columns_config.items():
            if col_id in self.table["columns"]:
                # Установка минимальной ширины для столбца на основе длины заголовка
                min_width = max(config["width"], len(config["text"]) * 10)
                self.table.column(col_id, width=min_width, minwidth=min_width, anchor=config["anchor"])
                self.table.heading(col_id, text=config["text"], anchor=config["anchor"],
                                   command=lambda _col=col_id: self.sort_table(_col))

        # Добавляем переменную для отслеживания сортировки
        self.sort_by = None
        self.sort_reverse = False

    def sort_table(self, column):
        """Сортировка таблицы по выбранному столбцу"""
        self.logger.info(f"Сортировка таблицы по столбцу: {column}")

        # Определяем направление сортировки
        if self.sort_by == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_by = column

        # Маппинг столбцов таблицы на атрибуты класса Applicant
        column_mapping = {
            "number": lambda a: a.get_number(),
            "fio": lambda a: a.get_full_name().lower(),
            "code": lambda a: a.get_code().lower(),
            "rating": lambda a: float(a.get_rating()),
            "benefits": lambda a: (a.get_benefits() or "").lower(),
            "original": lambda a: a.has_original_documents(),
            "city": lambda a: a.get_city().lower(),
            "dormitory": lambda a: a.additional_info.dormitory_needed,
            "institution": lambda a: a.education.institution.lower(),
            "visit_date": lambda a: (a.additional_info.department_visit or datetime.min),
            "info_source": lambda a: (a.additional_info.information_source or "").lower(),
            "phone": lambda a: a.get_phone(),
            "vk": lambda a: (a.contact_info.vk or "").lower(),
            "parent": lambda a: (a.parent.full_name.lower() if a.parent else ""),
            "parent_phone": lambda a: (a.parent.phone if a.parent else ""),
            "notes": lambda a: (a.additional_info.notes or "").lower()
        }

        # Если выбран столбец для сортировки
        if column in column_mapping:
            # Сортируем список абитуриентов
            self.applicants.sort(key=column_mapping[column], reverse=self.sort_reverse)
            # Обновляем таблицу
            self.load_data()

    def load_data(self):
        """Загрузка данных в таблицу"""
        # Очистка таблицы перед загрузкой
        for item in self.table.get_children():
            self.table.delete(item)

        # Применение стиля с границами для таблицы
        style = ttk.Style()
        style.configure("Treeview",
                        rowheight=25,
                        borderwidth=1,
                        relief="solid")

        style.configure("Treeview.Cell",
                        borderwidth=1,
                        relief="solid")

        style.map("Treeview",
                  background=[("selected", "#3f51b5")],
                  foreground=[("selected", "white")])

        # Добавление данных в таблицу
        for i, applicant in enumerate(self.applicants):
            # Форматирование данных для таблицы
            visit_date = ""
            if applicant.additional_info.department_visit:
                visit_date = applicant.additional_info.department_visit.strftime("%d.%m.%Y")

            submission_date = ""
            if applicant.application_details.submission_date:
                submission_date = applicant.application_details.get_submission_date_formatted()
            parent_name = ""
            parent_phone = ""
            if applicant.parent:
                parent_name = applicant.parent.full_name
                parent_phone = applicant.parent.phone

            # Вставка данных в таблицу
            values = (
                applicant.get_number(),
                applicant.get_full_name(),
                applicant.get_code(),
                str(applicant.get_rating()),
                applicant.get_benefits() or "",
                "Да" if applicant.has_original_documents() else "Нет",
                applicant.get_city(),
                "Да" if applicant.additional_info.dormitory_needed else "Нет",
                applicant.education.institution,
                submission_date,
                visit_date,
                applicant.additional_info.information_source or "",
                applicant.get_phone(),
                applicant.contact_info.vk or "",
                parent_name,
                parent_phone,
                applicant.additional_info.notes or ""
            )

            self.table.insert("", "end", iid=str(i), values=values)

        self.logger.info(f"Загружено {len(self.applicants)} записей в таблицу")

    def on_select(self, event):
        """Обработчик выбора строки в таблице"""
        selected_items = self.table.selection()
        if selected_items:
            item_id = selected_items[0]
            applicant_index = int(item_id)
            self.selected_applicant = self.applicants[applicant_index]
            self.logger.info(f"Выбран абитуриент: {self.selected_applicant.get_full_name()}")

    def clear_search_placeholder(self, event):
        """Очистка placeholder в поле поиска при фокусе"""
        if self.search_var.get() == "Поиск абитуриента":
            self.search_entry.delete(0, tk.END)
            self.search_var.set("")  # Добавлено для очистки переменной

    def restore_search_placeholder(self, event):
        """Восстановление placeholder в поле поиска при потере фокуса"""
        if not self.search_var.get():
            self.search_entry.insert(0, "Поиск абитуриента")

    def search_applicant(self, event=None):
        """Поиск абитуриента по введенному тексту"""
        search_text = self.search_var.get().lower()
        if not search_text or search_text == "поиск абитуриента":
            return

        self.logger.info(f"Поиск абитуриента по тексту: {search_text}")

        # Сбрасываем текущее выделение
        for item in self.table.selection():
            self.table.selection_remove(item)

        # Перебираем все строки таблицы
        found = False
        for item_id in self.table.get_children():
            # Получаем все значения в строке
            item_values = self.table.item(item_id, "values")

            # Поиск в значениях
            for value in item_values:
                if value and search_text in str(value).lower():
                    self.table.selection_set(item_id)
                    self.table.see(item_id)
                    found = True
                    break

            if found:
                break

        if not found:
            messagebox.showinfo("Поиск", f"Абитуриент с текстом '{search_text}' не найден")
            self.logger.info(f"Абитуриент с текстом '{search_text}' не найден")

    def add_applicant(self):
        """Открывает окно для добавления нового абитуриента"""
        self.logger.info("Открытие формы добавления абитуриента")

        # Вызываем функцию из отдельного модуля
        add_applicant_window(self.parent, self.applicants, self.load_data, self.logger)

    def edit_applicant(self):
        """Открытие формы редактирования выбранного абитуриента"""
        if not self.applicants:
            messagebox.showwarning("Предупреждение", "Нет записей для редактирования")
            self.logger.warning("Попытка редактирования при отсутствии записей")
            return

        if not self.selected_applicant:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите абитуриента для редактирования")
            self.logger.warning("Попытка редактирования без выбора абитуриента")
            return

        # Создаем и показываем форму редактирования
        edit_form = ApplicantEditForm(
            parent=self.parent,
            selected_applicant=self.selected_applicant,
            on_save_callback=self.refresh_data,
            logger=self.logger
        )
        edit_form.show()
        
    def delete_applicant(self):
        """Удаление выбранного абитуриента"""
        if not self.selected_applicant:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите абитуриента для удаления")
            self.logger.warning("Попытка удаления без выбора абитуриента")
            return

        # Запрос подтверждения
        confirm = messagebox.askyesno("Подтверждение",
                                     f"Вы уверены, что хотите удалить абитуриента {self.selected_applicant.get_full_name()}?")

        if confirm:
            # Удаляем из списка
            self.applicants.remove(self.selected_applicant)

            # Перенумеровываем всех абитуриентов
            for i, applicant in enumerate(self.applicants, 1):
                applicant.application_details.number = str(i)

            self.logger.info(f"Удален абитуриент: {self.selected_applicant.get_full_name()}")

            # Обновляем таблицу
            self.refresh_data()

            messagebox.showinfo("Информация", "Абитуриент успешно удален")

    def refresh_data(self):
        """Обновление данных в таблице"""
        self.logger.info("Обновление данных в таблице")
        self.load_data()

    def filter_data(self):
        """Фильтрация данных в таблице"""
        self.logger.info("Открытие окна фильтрации")

        # Создаем всплывающее окно для фильтрации
        filter_window = tk.Toplevel(self.parent)
        filter_window.title("Фильтр абитуриентов")
        filter_window.geometry("400x300")
        filter_window.resizable(False, False)
        filter_window.transient(self.parent)
        filter_window.grab_set()

        # Создаем фрейм для элементов формы
        filter_frame = tk.Frame(filter_window, padx=10, pady=10)
        filter_frame.pack(fill="both", expand=True)

        # Выбор поля для фильтрации
        tk.Label(filter_frame, text="Поле для фильтрации:").grid(row=0, column=0, sticky="w", pady=5)

        fields = [
            "Город", "Общежитие", "Оригинал документов", "Льгота", "Учебное заведение"
        ]

        field_var = tk.StringVar()
        field_combo = ttk.Combobox(filter_frame, textvariable=field_var, values=fields, state="readonly")
        field_combo.grid(row=0, column=1, sticky="ew", pady=5)
        field_combo.current(0)

        # Значение для фильтрации
        tk.Label(filter_frame, text="Значение:").grid(row=1, column=0, sticky="w", pady=5)
        value_var = tk.StringVar()
        value_entry = tk.Entry(filter_frame, textvariable=value_var)
        value_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # Для полей с да/нет создаем специальный виджет
        bool_frame = tk.Frame(filter_frame)
        bool_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        bool_frame.grid_remove()  # Изначально скрыт

        bool_var = tk.BooleanVar()
        tk.Radiobutton(bool_frame, text="Да", variable=bool_var, value=True).pack(side="left", padx=5)
        tk.Radiobutton(bool_frame, text="Нет", variable=bool_var, value=False).pack(side="left", padx=5)

        # Функция для обновления интерфейса в зависимости от выбранного поля
        def update_filter_interface(*args):
            selected_field = field_var.get()
            if selected_field in ["Общежитие", "Оригинал документов"]:
                value_entry.grid_remove()
                bool_frame.grid()
            else:
                bool_frame.grid_remove()
                value_entry.grid()

        # Привязываем функцию к изменению выбранного поля
        field_var.trace("w", update_filter_interface)

        # Применение фильтра
        def apply_filter():
            selected_field = field_var.get()

            # Получаем значение фильтра
            filter_value = None
            if selected_field in ["Общежитие", "Оригинал документов"]:
                filter_value = bool_var.get()
            else:
                filter_value = value_var.get()

            self.logger.info(f"Применение фильтра: {selected_field} = {filter_value}")

            # Фильтрация данных
            filtered_applicants = []

            for applicant in self.applicants:
                match = False

                if selected_field == "Город":
                    match = applicant.get_city().lower() == filter_value.lower()
                elif selected_field == "Общежитие":
                    match = applicant.additional_info.dormitory_needed == filter_value
                elif selected_field == "Оригинал документов":
                    match = applicant.has_original_documents() == filter_value
                elif selected_field == "Льгота":
                    benefit = applicant.get_benefits() or ""
                    match = filter_value.lower() in benefit.lower()
                elif selected_field == "Учебное заведение":
                    match = filter_value.lower() in applicant.education.institution.lower()

                if match:
                    filtered_applicants.append(applicant)

            # Временно заменяем список абитуриентов и обновляем таблицу
            original_applicants = self.applicants
            self.applicants = filtered_applicants
            self.load_data()

            # Восстанавливаем оригинальный список для последующих операций
            self.applicants = original_applicants

            filter_window.destroy()

            if not filtered_applicants:
                messagebox.showinfo("Информация", "Нет записей, соответствующих фильтру")

        # Сброс фильтра
        def reset_filter():
            self.load_data()
            filter_window.destroy()

        # Кнопки
        button_frame = tk.Frame(filter_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Применить", command=apply_filter).pack(side="left", padx=5)
        tk.Button(button_frame, text="Сбросить", command=reset_filter).pack(side="left", padx=5)
        tk.Button(button_frame, text="Отмена", command=filter_window.destroy).pack(side="left", padx=5)

    def export_to_excel(self):
        """Экспорт данных в Excel файл"""
        self.logger.info("Экспорт данных в Excel")

        # Запрос места сохранения файла
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")],
            title="Сохранить как"
        )

        if not file_path:
            self.logger.info("Экспорт отменен пользователем")
            return

        try:
            # Создаем DataFrame для экспорта
            data = []
            columns = [
                "Номер", "ФИО", "Код", "Рейтинг", "Льгота", "Оригинал",
                "Город", "Общежитие", "Учебное заведение", "Дата подачи",
                "Дата посещения", "Откуда узнал/а", "Телефон", "Профиль ВК",
                "Родитель", "Телефон родителя", "Примечание"
            ]

            for i, applicant in enumerate(self.applicants):
                visit_date = ""
                if applicant.additional_info.department_visit:
                    visit_date = applicant.additional_info.department_visit.strftime("%d.%m.%Y")

                submission_date = ""
                if applicant.application_details.submission_date:
                    submission_date = applicant.application_details.get_submission_date_formatted()

                parent_name = ""
                parent_phone = ""
                if applicant.parent:
                    parent_name = applicant.parent.full_name
                    parent_phone = applicant.parent.phone


                row = [
                    applicant.get_number(),
                    applicant.get_full_name(),
                    applicant.get_code(),
                    applicant.get_rating(),
                    applicant.get_benefits() or "",
                    "Да" if applicant.has_original_documents() else "Нет",
                    applicant.get_city(),
                    "Да" if applicant.additional_info.dormitory_needed else "Нет",
                    applicant.education.institution,
                    submission_date,
                    visit_date,
                    applicant.additional_info.information_source or "",
                    applicant.get_phone(),
                    applicant.contact_info.vk or "",
                    parent_name,
                    parent_phone,
                    applicant.additional_info.notes or ""
                ]

                data.append(row)

            # Создаем DataFrame и экспортируем в Excel
            df = pd.DataFrame(data, columns=columns)
            df.to_excel(file_path, index=False, sheet_name="Абитуриенты")

            self.logger.info(f"Данные успешно экспортированы в файл: {file_path}")
            messagebox.showinfo("Экспорт", f"Данные успешно экспортированы в файл:\n{file_path}")

        except Exception as e:
            error_msg = f"Ошибка при экспорте данных: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка", f"Произошла ошибка при экспорте:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Реестр абитуриентов")
    root.geometry("800x600")
    icon = tk.PhotoImage(file="icon.png")
    root.iconphoto(True, icon)

    # Создаем тестовые данные
    logger = Logger("test.log")
    applicant_registry = ApplicantRegistry()

    # Создаем окно с таблицей
    app = ApplicantTableWindow(root, applicant_registry.applicants, logger)

    root.mainloop()