"""app_table.py"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from pandas.plotting import table

from classes import *
from logger import Logger
from app_add_applicant import add_applicant_window, parse_full_name
from app_edit_applicant import ApplicantEditForm


class ApplicantTableWindow:
    def __init__(self, parent, applicants, logger, db_manager=None, offer_import=True):
        """
        Инициализация окна с таблицей абитуриентов

        :param parent: Родительский виджет
        :param applicants: Список абитуриентов
        :param logger: Экземпляр логгера
        :param db_manager: Менеджер базы данных
        :param offer_import: Флаг, предлагать ли импорт данных (только при первом запуске)
        """
        self.parent = parent
        self.applicants = applicants
        self.logger = logger
        self.db_manager = db_manager
        self.selected_applicant = None

        # Логирование запуска окна с таблицей
        self.logger.info("Инициализация окна с таблицей абитуриентов")

        # Настройка адаптивного интерфейса
        self.setup_ui()

        # Предложение импортировать данные из Excel только при запуске программы И если БД пуста
        if offer_import and len(self.applicants) == 0:
            self.offer_import()

        # Заполнение таблицы данными
        self.load_data()

        # Привязка обработчика закрытия окна
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.logger.info("Окно с таблицей абитуриентов успешно инициализировано")

    def offer_import(self):
        """Предлагает пользователю импортировать данные из Excel файла"""
        import_response = messagebox.askyesno("Импорт данных",
                                              "База данных пуста. Хотите импортировать данные из Excel файла?")
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

            # Очистка текущего списка абитуриентов (только в памяти)
            imported_count = 0

            # Преобразование данных из DataFrame в объекты Applicant
            for _, row in df.iterrows():
                try:
                    # Обработка даты посещения
                    visit_date = None
                    if 'Дата посещения' in row and pd.notna(row['Дата посещения']):
                        try:
                            visit_date = pd.to_datetime(row['Дата посещения'], dayfirst=True).to_pydatetime()
                        except:
                            visit_date = None

                    # Обработка даты подачи
                    submission_date = None
                    if 'Дата подачи' in row and pd.notna(row['Дата подачи']):
                        try:
                            submission_date = pd.to_datetime(row['Дата подачи'], dayfirst=True).date()
                        except:
                            submission_date = None

                    # Если в файле есть отдельные колонки — используем их
                    last_name = str(row.get('Фамилия', '')).strip()
                    first_name = str(row.get('Имя', '')).strip()
                    patronymic = str(row.get('Отчество', '')).strip()

                    # Если отдельные колонки пустые — разбираем ФИО
                    if not last_name or not first_name:
                        full_name = str(row.get('ФИО', '')).strip()
                        ln, fn, pt = parse_full_name(full_name)
                        last_name = last_name or ln
                        first_name = first_name or fn
                        patronymic = patronymic or pt

                    # Создание объектов информации
                    app_details = ApplicationDetails(
                        number=str(row.get('Номер', '')),
                        code=str(row.get('Код', '')),
                        rating=float(row.get('Рейтинг', 0)),
                        has_original=row.get('Оригинал', '') == 'Да',
                        benefits=str(row.get('Льгота', '')) if pd.notna(row.get('Льгота', '')) else None,
                        submission_date=submission_date
                    )

                    education = EducationalBackground(
                        institution=str(row.get('Учебное заведение', ''))
                    )

                    contact_info = ContactInfo(
                        phone=str(row.get('Телефон', '')),
                        vk=str(row.get('Профиль ВК', '')) if pd.notna(row.get('Профиль ВК', '')) else None
                    )

                    additional_info = AdditionalInfo(
                        department_visit=visit_date,
                        notes=str(row.get('Примечание', '')) if pd.notna(row.get('Примечание', '')) else None,
                        information_source=str(row.get('Откуда узнал/а', '')) if pd.notna(row.get('Откуда узнал/а', '')) else None,
                        dormitory_needed=row.get('Общежитие', '') == 'Да'
                    )

                    # Создание объекта родителя при наличии данных
                    parent = None
                    parent_raw = row.get('Родитель')

                    if pd.notna(parent_raw) and str(parent_raw).strip():
                        parent = Parent(
                            parent_name=str(parent_raw).strip(),
                            phone=str(row.get('Телефон родителя', ''))
                        )

                    # Создание объекта абитуриента
                    applicant = Applicant(
                        last_name=last_name,
                        first_name=first_name,
                        patronymic=patronymic,
                        phone=str(row.get('Телефон', '')),
                        city=str(row.get('Город', '')),
                        application_details=app_details,
                        education=education,
                        contact_info=contact_info,
                        additional_info=additional_info,
                        parent=parent
                    )

                    # Сохранение в БД
                    if self.db_manager and self.db_manager.connection:
                        try:
                            id_applicant = self.db_manager.add_applicant(applicant)
                            applicant.application_details.number = str(id_applicant)
                            self.applicants.append(applicant)
                            imported_count += 1
                        except Exception as db_error:
                            self.logger.error(f"Ошибка сохранения в БД при импорте: {str(db_error)}")
                    else:
                        self.applicants.append(applicant)
                        imported_count += 1

                except Exception as e:
                    self.logger.error(f"Ошибка при импорте строки: {str(e)}")

            self.logger.info(f"Успешно импортировано {imported_count} записей из файла: {file_path}")
            messagebox.showinfo("Импорт", f"Успешно импортировано {imported_count} записей.")

            # Обновляем таблицу
            self.load_data()

        except Exception as e:
            error_msg = f"Ошибка при импорте данных: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка", f"Произошла ошибка при импорте:\n{str(e)}")

    #Импорт данных с БД
    def import_from_database(self):
        """Импорт данных напрямую из БД"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showwarning("Предупреждение",
                                   "Отсутствует подключение к базе данных.\n"
                                   "Проверьте настройки подключения.")
            self.logger.warning("Попытка импорта из БД без подключения")
            return

        # Проверяем, есть ли данные в памяти
        if self.applicants:
            choice = messagebox.askyesnocancel(
                "Режим импорта из БД",
                f"В памяти уже есть {len(self.applicants)} записей.\n\n"
                "Да - Заменить все данные данными из БД\n"
                "Нет - Добавить данные из БД к существующим\n"
                "Отмена - Отменить импорт"
            )

            if choice is None:  # Отмена
                self.logger.info("Импорт из БД отменен пользователем")
                return
        else:
            choice = True  # Если данных нет, просто загружаем

        try:
            self.logger.info("Начало импорта из БД")
            loaded_applicants = self.db_manager.load_all_applicants()

            if not loaded_applicants:
                messagebox.showinfo("Импорт из БД", "База данных пуста")
                self.logger.info("БД не содержит записей")
                return

            if choice:  # Заменить
                self.applicants.clear()
                self.applicants.extend(loaded_applicants)
                message = f"Загружено {len(loaded_applicants)} записей из БД"
                self.logger.info(message)
            else:  # Добавить
                # Проверяем дубликаты по номеру (ID)
                existing_numbers = {a.get_number() for a in self.applicants}
                new_count = 0
                duplicate_count = 0

                for applicant in loaded_applicants:
                    if applicant.get_number() not in existing_numbers:
                        self.applicants.append(applicant)
                        existing_numbers.add(applicant.get_number())
                        new_count += 1
                    else:
                        duplicate_count += 1

                if duplicate_count > 0:
                    message = (f"Добавлено {new_count} новых записей из БД.\n"
                               f"Пропущено дубликатов: {duplicate_count}")
                else:
                    message = f"Добавлено {new_count} новых записей из БД"

                self.logger.info(message)

            # Обновляем таблицу
            self.load_data()
            messagebox.showinfo("Импорт из БД", message)

        except Exception as e:
            error_msg = f"Ошибка импорта из БД: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка импорта",
                                 f"Произошла ошибка при импорте из базы данных:\n\n{str(e)}")

    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.applicants:
            export_response = messagebox.askyesno("Экспорт данных",
                                                  "Хотите экспортировать данные в Excel перед закрытием?")
            if export_response:
                self.export_to_excel()

        # Закрытие соединения с БД
        if self.db_manager:
            self.db_manager.disconnect()
            self.logger.info("Соединение с БД закрыто")

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
        button_frame.grid_columnconfigure(8, weight=1)

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

        # В методе setup_ui() после кнопки "Импорт"
        self.import_db_button = tk.Button(button_frame, bg="#3f51b5", fg="white",
                                          text="Импорт из БД", width=12,
                                          command=self.import_from_database)
        self.import_db_button.grid(row=0, column=7, padx=5)

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
            "number", "last_name", "first_name", "patronymic", "code", "rating", "benefits", "original",
            "city", "dormitory", "institution", "submission_date",
            "visit_date", "info_source", "phone", "vk", "parent", "parent_phone", "notes"
        )

        # Показываем заголовки
        self.table["show"] = "headings"

        # Настройка заголовков и ширины столбцов
        columns_config = {
            "number": {"text": "Номер", "width": 50, "anchor": "center"},
            "last_name": {"text": "Фамилия", "width": 120, "anchor": "w"},
            "first_name": {"text": "Имя", "width": 100, "anchor": "w"},
            "patronymic": {"text": "Отчество", "width": 120, "anchor": "w"},
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
            "number": lambda a: int(a.get_number()) if a.get_number().isdigit() else 0,
            "last_name": lambda a: a.get_last_name().lower(),
            "first_name": lambda a: a.get_first_name().lower(),
            "patronymic": lambda a: (a.get_patronymic() or "").lower(),
            "code": lambda a: a.get_code().lower(),
            "rating": lambda a: float(a.get_rating()),
            "benefits": lambda a: (a.get_benefits() or "").lower(),
            "original": lambda a: a.has_original_documents(),
            "city": lambda a: a.get_city().lower(),
            "dormitory": lambda a: a.additional_info.dormitory_needed,
            "institution": lambda a: a.education.institution.lower(),
            "submission_date": lambda a: (a.application_details.submission_date or datetime.min.date()),
            "visit_date": lambda a: (a.additional_info.department_visit or datetime.min),
            "info_source": lambda a: (a.additional_info.information_source or "").lower(),
            "phone": lambda a: a.get_phone(),
            "vk": lambda a: (a.contact_info.vk or "").lower(),
            "parent": lambda a: (a.parent.get_full_name().lower() if a.parent else ""),
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
                if isinstance(applicant.additional_info.department_visit, date):
                    visit_date = applicant.additional_info.department_visit.strftime("%d.%m.%Y")
                elif isinstance(applicant.additional_info.department_visit, datetime):
                    visit_date = applicant.additional_info.department_visit.strftime("%d.%m.%Y")

            submission_date = ""
            if applicant.application_details.submission_date:
                submission_date = applicant.application_details.get_submission_date_formatted()

            parent_name = ""
            parent_phone = ""
            if applicant.parent:
                parent_name = applicant.parent.parent_name
                parent_phone = applicant.parent.phone

            # Вставка данных в таблицу
            values = (
                applicant.get_number(),
                applicant.get_last_name(),
                applicant.get_first_name(),
                applicant.get_patronymic() or "",
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
            self.search_var.set("")

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
        add_applicant_window(self.parent, self.applicants, self.load_data, self.logger, self.db_manager)

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

        def save_to_db_callback():
            if self.db_manager and self.db_manager.connection:
                try:
                    self.db_manager.update_applicant(self.selected_applicant)
                    self.logger.info(f"Изменения сохранены в БД для: {self.selected_applicant.get_full_name()}")
                except Exception as e:
                    self.logger.error(f"Ошибка сохранения изменений в БД: {e}")
                    messagebox.showerror("Ошибка БД", f"Не удалось сохранить изменения в БД:\n{str(e)}")
            self.refresh_data()

        # Создаем и показываем форму редактирования
        edit_form = ApplicantEditForm(
            parent=self.parent,
            selected_applicant=self.selected_applicant,
            on_save_callback=save_to_db_callback,
            logger=self.logger
        )
        edit_form.show()

    def renumber_applicants(self):
        """Перенумерация абитуриентов и всех связанных таблиц после удаления"""
        if not self.db_manager or not self.db_manager.connection:
            self.logger.warning("Нет подключения к БД для перенумерации")
            return

        self.logger.info("Запуск полной перенумерации всех таблиц")

        try:
            cursor = self.db_manager.connection.cursor()

            # ===== 1. СОХРАНЯЕМ ДАННЫЕ АБИТУРИЕНТОВ =====
            cursor.execute("""
                           SELECT a.id_applicant,
                                  a.last_name,
                                  a.first_name,
                                  a.patronymic,
                                  a.city,
                                  a.phone,
                                  e.name_education,
                                  p.name     as parent_name,
                                  p.phone    as parent_phone,
                                  p.relation as parent_relation,
                                  ad.rating,
                                  ad.has_original,
                                  ad.submission_date,
                                  s.name_specialty,
                                  s.form_of_education,
                                  ai.department_visit,
                                  ai.notes,
                                  ai.dormitory_needed,
                                  isrc.name_source
                           FROM Applicant a
                                    LEFT JOIN Education e ON a.id_education = e.id_education
                                    LEFT JOIN Parent p ON a.id_parent = p.id_parent
                                    LEFT JOIN Application_details ad ON a.id_applicant = ad.id_applicant
                                    LEFT JOIN Specialty s ON ad.id_specialty = s.id_specialty
                                    LEFT JOIN Additional_info ai ON a.id_applicant = ai.id_applicant
                                    LEFT JOIN Information_source isrc ON ai.id_source = isrc.id_source
                           ORDER BY a.id_applicant
                           """)
            applicants_data = cursor.fetchall()

            if not applicants_data:
                self.logger.info("Нет абитуриентов для перенумерации")
                return

            # ===== 2. СОХРАНЯЕМ ЛЬГОТЫ =====
            benefits_map = {}
            cursor.execute("""
                           SELECT ab.id_applicant, b.name_benefit, b.bonus_points
                           FROM Applicant_benefit ab
                                    JOIN Benefit b ON ab.id_benefit = b.id_benefit
                           """)
            for row in cursor.fetchall():
                if row.id_applicant not in benefits_map:
                    benefits_map[row.id_applicant] = []
                benefits_map[row.id_applicant].append({
                    'name': row.name_benefit,
                    'points': row.bonus_points
                })

            # ===== 3. УДАЛЯЕМ ВСЕ ДАННЫЕ =====
            cursor.execute("DELETE FROM Applicant_benefit")
            cursor.execute("DELETE FROM Application_details")
            cursor.execute("DELETE FROM Additional_info")
            cursor.execute("DELETE FROM Applicant")
            cursor.execute("DELETE FROM Education")
            cursor.execute("DELETE FROM Parent")
            cursor.execute("DELETE FROM Specialty")
            cursor.execute("DELETE FROM Information_source")
            cursor.execute("DELETE FROM Benefit")

            # ===== 4. СБРАСЫВАЕМ IDENTITY =====
            cursor.execute("DBCC CHECKIDENT ('Applicant', RESEED, 0)")
            cursor.execute("DBCC CHECKIDENT ('Education', RESEED, 0)")
            cursor.execute("DBCC CHECKIDENT ('Parent', RESEED, 0)")
            cursor.execute("DBCC CHECKIDENT ('Application_details', RESEED, 0)")
            cursor.execute("DBCC CHECKIDENT ('Additional_info', RESEED, 0)")
            cursor.execute("DBCC CHECKIDENT ('Specialty', RESEED, 0)")
            cursor.execute("DBCC CHECKIDENT ('Information_source', RESEED, 0)")
            cursor.execute("DBCC CHECKIDENT ('Benefit', RESEED, 0)")

            # ===== 5. СОЗДАЕМ СПРАВОЧНИКИ С УНИКАЛЬНЫМИ ЗНАЧЕНИЯМИ =====

            # Education
            education_map = {}  # {old_name: new_id}
            education_id = 1
            for row in applicants_data:
                if row.name_education and row.name_education not in education_map:
                    cursor.execute("""
                        SET IDENTITY_INSERT Education ON;
                        INSERT INTO Education (id_education, name_education) VALUES (?, ?);
                        SET IDENTITY_INSERT Education OFF;
                    """, (education_id, row.name_education))
                    education_map[row.name_education] = education_id
                    education_id += 1

            # Parent
            parent_map = {}  # {(name, phone): new_id}
            parent_id = 1
            for row in applicants_data:
                if row.parent_name:
                    parent_key = (row.parent_name, row.parent_phone)
                    if parent_key not in parent_map:
                        cursor.execute("""
                            SET IDENTITY_INSERT Parent ON;
                            INSERT INTO Parent (id_parent, name, phone, relation) VALUES (?, ?, ?, ?);
                            SET IDENTITY_INSERT Parent OFF;
                        """, (parent_id, row.parent_name, row.parent_phone, row.parent_relation or "Родитель"))
                        parent_map[parent_key] = parent_id
                        parent_id += 1

            # Specialty
            specialty_map = {}  # {(name, form): new_id}
            specialty_id = 1
            for row in applicants_data:
                if row.name_specialty:
                    specialty_key = (row.name_specialty, row.form_of_education)
                    if specialty_key not in specialty_map:
                        cursor.execute("""
                            SET IDENTITY_INSERT Specialty ON;
                            INSERT INTO Specialty (id_specialty, name_specialty, form_of_education) VALUES (?, ?, ?);
                            SET IDENTITY_INSERT Specialty OFF;
                        """, (specialty_id, row.name_specialty, row.form_of_education))
                        specialty_map[specialty_key] = specialty_id
                        specialty_id += 1

            # Information_source
            info_source_map = {}  # {name: new_id}
            info_source_id = 1
            for row in applicants_data:
                if row.name_source and row.name_source not in info_source_map:
                    cursor.execute("""
                        SET IDENTITY_INSERT Information_source ON;
                        INSERT INTO Information_source (id_source, name_source) VALUES (?, ?);
                        SET IDENTITY_INSERT Information_source OFF;
                    """, (info_source_id, row.name_source))
                    info_source_map[row.name_source] = info_source_id
                    info_source_id += 1

            # Benefit (собираем все уникальные льготы)
            benefit_map = {}  # {name: new_id}
            benefit_id = 1
            all_benefits = set()
            for old_id, benefits_list in benefits_map.items():
                for benefit in benefits_list:
                    all_benefits.add((benefit['name'], benefit['points']))

            for benefit_name, bonus_points in all_benefits:
                cursor.execute("""
                    SET IDENTITY_INSERT Benefit ON;
                    INSERT INTO Benefit (id_benefit, name_benefit, bonus_points) VALUES (?, ?, ?);
                    SET IDENTITY_INSERT Benefit OFF;
                """, (benefit_id, benefit_name, bonus_points))
                benefit_map[benefit_name] = benefit_id
                benefit_id += 1

            # ===== 6. ВСТАВЛЯЕМ АБИТУРИЕНТОВ ЗАНОВО =====
            for new_id, row in enumerate(applicants_data, start=1):
                old_id = row.id_applicant

                # Получаем новые ID для справочников
                new_education_id = education_map.get(row.name_education) if row.name_education else None
                new_parent_id = parent_map.get((row.parent_name, row.parent_phone)) if row.parent_name else None
                new_specialty_id = specialty_map.get(
                    (row.name_specialty, row.form_of_education)) if row.name_specialty else None
                new_info_source_id = info_source_map.get(row.name_source) if row.name_source else None

                # Вставляем абитуриента
                cursor.execute("""
                    SET IDENTITY_INSERT Applicant ON;
                    INSERT INTO Applicant (id_applicant, last_name, first_name, patronymic, city, phone, id_education, id_parent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    SET IDENTITY_INSERT Applicant OFF;
                """, (new_id, row.last_name, row.first_name, row.patronymic, row.city, row.phone,
                      new_education_id, new_parent_id))

                # Вставляем детали заявки
                cursor.execute("""
                               INSERT INTO Application_details (id_applicant, id_specialty, rating, has_original, submission_date)
                               VALUES (?, ?, ?, ?, ?)
                               """, (new_id, new_specialty_id, row.rating, row.has_original, row.submission_date))

                # Получаем новый id_details
                cursor.execute("SELECT id_details FROM Application_details WHERE id_applicant = ?", (new_id,))
                new_id_details = cursor.fetchone()[0]

                # Вставляем дополнительную информацию
                cursor.execute("""
                               INSERT INTO Additional_info (id_applicant, department_visit, notes, id_source, dormitory_needed)
                               VALUES (?, ?, ?, ?, ?)
                               """, (new_id, row.department_visit, row.notes, new_info_source_id, row.dormitory_needed))

                # Получаем новый id_info
                cursor.execute("SELECT id_info FROM Additional_info WHERE id_applicant = ?", (new_id,))
                new_id_info = cursor.fetchone()[0]

                # Обновляем ссылки в Applicant
                cursor.execute("""
                               UPDATE Applicant
                               SET id_details = ?,
                                   id_info    = ?
                               WHERE id_applicant = ?
                               """, (new_id_details, new_id_info, new_id))

                # Восстанавливаем льготы
                if old_id in benefits_map:
                    for benefit in benefits_map[old_id]:
                        benefit_id = benefit_map[benefit['name']]
                        cursor.execute("""
                                       INSERT INTO Applicant_benefit (id_applicant, id_benefit)
                                       VALUES (?, ?)
                                       """, (new_id, benefit_id))

            # ===== 7. УСТАНАВЛИВАЕМ ПРАВИЛЬНЫЕ ЗНАЧЕНИЯ IDENTITY =====
            cursor.execute(f"DBCC CHECKIDENT ('Applicant', RESEED, {len(applicants_data)})")
            cursor.execute(f"DBCC CHECKIDENT ('Education', RESEED, {len(education_map)})")
            cursor.execute(f"DBCC CHECKIDENT ('Parent', RESEED, {len(parent_map)})")
            cursor.execute(f"DBCC CHECKIDENT ('Specialty', RESEED, {len(specialty_map)})")
            cursor.execute(f"DBCC CHECKIDENT ('Information_source', RESEED, {len(info_source_map)})")
            cursor.execute(f"DBCC CHECKIDENT ('Benefit', RESEED, {len(benefit_map)})")

            self.db_manager.connection.commit()

            # ===== 8. ОБНОВЛЯЕМ ДАННЫЕ В ПАМЯТИ =====
            self.applicants.clear()
            loaded_applicants = self.db_manager.load_all_applicants()
            self.applicants.extend(loaded_applicants)

            self.logger.info(f"Полная перенумерация завершена:")
            self.logger.info(f"  - Абитуриенты: {len(applicants_data)}")
            self.logger.info(f"  - Учебные заведения: {len(education_map)}")
            self.logger.info(f"  - Родители: {len(parent_map)}")
            self.logger.info(f"  - Специальности: {len(specialty_map)}")
            self.logger.info(f"  - Источники информации: {len(info_source_map)}")
            self.logger.info(f"  - Льготы: {len(benefit_map)}")

            self.load_data()

        except Exception as e:
            self.logger.error(f"Ошибка при перенумерации: {e}")
            self.db_manager.connection.rollback()
            messagebox.showerror("Ошибка", f"Не удалось выполнить перенумерацию:\n{str(e)}")

    def delete_applicant(self):
        """Удаление выбранного абитуриента + очистка неиспользуемых записей"""
        if not self.selected_applicant:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите абитуриента для удаления")
            self.logger.warning("Попытка удаления без выбора абитуриента")
            return

        # Подтверждение
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить абитуриента:\n{self.selected_applicant.get_full_name()}?"
        )
        if not confirm:
            self.logger.info("Удаление отменено пользователем")
            return

        try:
            if self.db_manager and self.db_manager.connection:
                cursor = self.db_manager.connection.cursor()

                applicant_id = self.selected_applicant.get_number()
                self.logger.info(f"Попытка удаления абитуриента ID={applicant_id}")

                # Удаляем дочерние записи
                delete_order = [
                    "Applicant_benefit",
                    "Application_details",
                    "Additional_info",
                    "Applicant"
                ]

                for table in delete_order:
                    try:
                        cursor.execute(
                            f"DELETE FROM {table} WHERE id_applicant = ?",
                            (applicant_id,)
                        )
                        self.logger.info(f"Удалено из таблицы {table}")
                    except Exception as e:
                        self.logger.warning(f"Ошибка при удалении из {table}: {e}")

                # Очистка неиспользуемых справочных записей
                cursor.execute("""
                               DELETE
                               FROM Education
                               WHERE id_education NOT IN
                                     (SELECT DISTINCT id_education FROM Applicant WHERE id_education IS NOT NULL)
                               """)

                cursor.execute("""
                               DELETE
                               FROM Parent
                               WHERE id_parent NOT IN
                                     (SELECT DISTINCT id_parent FROM Applicant WHERE id_parent IS NOT NULL)
                               """)

                cursor.execute("""
                               DELETE
                               FROM Information_source
                               WHERE id_source NOT IN
                                     (SELECT DISTINCT id_source FROM Additional_info WHERE id_source IS NOT NULL)
                               """)

                cursor.execute("""
                               DELETE
                               FROM Specialty
                               WHERE id_specialty NOT IN (SELECT DISTINCT id_specialty
                                                          FROM Application_details
                                                          WHERE id_specialty IS NOT NULL)
                               """)

                cursor.execute("""
                               DELETE
                               FROM Benefit
                               WHERE id_benefit NOT IN (SELECT DISTINCT id_benefit FROM Applicant_benefit)
                               """)

                self.db_manager.connection.commit()
                self.logger.info(f"Абитуриент успешно удалён (ID={applicant_id})")

            # Удаление из памяти
            if self.selected_applicant in self.applicants:
                self.applicants.remove(self.selected_applicant)

            self.selected_applicant = None

            # ВАЖНО: сначала перенумеровать, потом обновить таблицу
            self.renumber_applicants()

            messagebox.showinfo("Успех", "Абитуриент успешно удалён и записи перенумерованы")

        except Exception as e:
            self.logger.error(f"Ошибка удаления: {e}")
            messagebox.showerror("Ошибка", f"Не удалось удалить абитуриента:\n{e}")

    def refresh_data(self):
        """Обновление данных в таблице"""
        self.logger.info("Обновление данных в таблице")

        # ДОБАВЛЕНО: Перезагрузка из БД
        if self.db_manager and self.db_manager.connection:
            try:
                self.applicants.clear()
                loaded_applicants = self.db_manager.load_all_applicants()
                self.applicants.extend(loaded_applicants)
                self.logger.info(f"Данные обновлены из БД: {len(self.applicants)} записей")
            except Exception as e:
                self.logger.error(f"Ошибка обновления из БД: {e}")

            self.renumber_applicants()

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
        bool_frame.grid_remove()

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

        field_var.trace("w", update_filter_interface)

        # Применение фильтра
        def apply_filter():
            selected_field = field_var.get()

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
                "Номер", "Фамилия", "Имя", "Отчество", "Код", "Рейтинг", "Льгота", "Оригинал",
                "Город", "Общежитие", "Учебное заведение", "Дата подачи",
                "Дата посещения", "Откуда узнал/а", "Телефон", "Профиль ВК",
                "Родитель", "Телефон родителя", "Примечание"
            ]

            for i, applicant in enumerate(self.applicants):
                visit_date = ""
                if applicant.additional_info.department_visit:
                    if isinstance(applicant.additional_info.department_visit, date):
                        visit_date = applicant.additional_info.department_visit.strftime("%d.%m.%Y")
                    elif isinstance(applicant.additional_info.department_visit, datetime):
                        visit_date = applicant.additional_info.department_visit.strftime("%d.%m.%Y")

                submission_date = ""
                if applicant.application_details.submission_date:
                    submission_date = applicant.application_details.get_submission_date_formatted()

                parent_name = ""
                parent_phone = ""
                if applicant.parent:
                    parent_name = applicant.parent.parent_name
                    parent_phone = applicant.parent.phone

                row = [
                    applicant.get_number(),
                    applicant.last_name,
                    applicant.first_name,
                    applicant.patronymic,
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
