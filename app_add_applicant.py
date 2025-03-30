"""app_add_applicant.py"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from classes import *
from logger import Logger
from app_table import ApplicantTableWindow

# Инициализация логгера для всего приложения
logger = Logger("applicant_app.log")
applicant_registry = ApplicantRegistry()


class ApplicantForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Абитуриент")
        self.configure(bg="white")
        self.minsize(800, 600)

        # Логирование запуска формы
        logger.info("Запуск формы добавления абитуриента")

        # Настраиваем сетку для адаптивности
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=0)

        # Создаем переменные для хранения значений полей
        self.full_name_var = tk.StringVar()
        self.case_number_var = tk.StringVar()
        self.code_var = tk.StringVar()
        self.rating_var = tk.StringVar()
        self.benefits_var = tk.StringVar()
        self.original_var = tk.BooleanVar()
        self.submission_date_var = tk.StringVar()
        self.institution_var = tk.StringVar()
        self.city_var = tk.StringVar()
        self.dormitory_var = tk.BooleanVar()
        self.visit_date_var = tk.StringVar()
        self.info_source_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.vk_var = tk.StringVar()
        self.parent_var = tk.StringVar()
        self.parent_phone_var = tk.StringVar()

        # Заголовок
        header_frame = tk.Frame(self, bg="#3f51b5", height=70)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        header_label = tk.Label(header_frame, text="АБИТУРИЕНТ",
                                font=tkfont.Font(family="Arial", size=16, weight="bold"),
                                bg="#3f51b5", fg="white")
        header_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Основной контейнер для элементов формы
        main_frame = tk.Frame(self, bg="white")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Раздел основной информации
        basic_info_label = tk.Label(main_frame, text="ОСНОВНЫЕ ДАННЫЕ:",
                                    font=tkfont.Font(family="Arial", size=12, weight="bold"),
                                    bg="white")
        basic_info_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Раздел дополнительной информации (с отступом слева)
        additional_info_label = tk.Label(main_frame, text="ДОПОЛНИТЕЛЬНО:",
                                         font=tkfont.Font(family="Arial", size=12, weight="bold"),
                                         bg="white")
        additional_info_label.grid(row=0, column=1, sticky="w", pady=(0, 10), padx=(20, 0))

        # Левая колонка - Основная информация
        self.create_form_field(main_frame, 1, 0, "ФИО", self.full_name_var)

        # Номер дела и код в одной строке
        case_frame = tk.Frame(main_frame, bg="white")
        case_frame.grid(row=2, column=0, sticky="ew", pady=5)
        case_frame.grid_columnconfigure(0, weight=0)
        case_frame.grid_columnconfigure(1, weight=1)
        case_frame.grid_columnconfigure(2, weight=0)
        case_frame.grid_columnconfigure(3, weight=1)

        tk.Label(case_frame, text="Номер дела", bg="white").grid(row=0, column=0, sticky="w")
        tk.Entry(case_frame, textvariable=self.case_number_var).grid(row=0, column=1, sticky="ew", padx=(5, 10))
        tk.Label(case_frame, text="Код", bg="white").grid(row=0, column=2, sticky="w")
        tk.Entry(case_frame, textvariable=self.code_var).grid(row=0, column=3, sticky="ew", padx=(5, 0))

        # Рейтинг и льгота в одной строке
        rating_frame = tk.Frame(main_frame, bg="white")
        rating_frame.grid(row=3, column=0, sticky="ew", pady=5)
        rating_frame.grid_columnconfigure(0, weight=0)
        rating_frame.grid_columnconfigure(1, weight=1)
        rating_frame.grid_columnconfigure(2, weight=0)
        rating_frame.grid_columnconfigure(3, weight=1)

        tk.Label(rating_frame, text="Рейтинг", bg="white").grid(row=0, column=0, sticky="w")
        tk.Entry(rating_frame, textvariable=self.rating_var).grid(row=0, column=1, sticky="ew", padx=(5, 10))
        tk.Label(rating_frame, text="Льгота", bg="white").grid(row=0, column=2, sticky="w")
        tk.Entry(rating_frame, textvariable=self.benefits_var).grid(row=0, column=3, sticky="ew", padx=(5, 0))

        # Оригинал документов и дата подачи
        original_frame = tk.Frame(main_frame, bg="white")
        original_frame.grid(row=4, column=0, sticky="ew", pady=5)
        original_frame.grid_columnconfigure(0, weight=0)
        original_frame.grid_columnconfigure(1, weight=0)
        original_frame.grid_columnconfigure(2, weight=0)
        original_frame.grid_columnconfigure(3, weight=0)
        original_frame.grid_columnconfigure(4, weight=1)

        tk.Label(original_frame, text="Оригинал", bg="white").grid(row=0, column=0, sticky="w")
        tk.Label(original_frame, text="Да", bg="white").grid(row=0, column=1, sticky="w", padx=(5, 0))
        tk.Checkbutton(original_frame, bg="white", variable=self.original_var).grid(row=0, column=2, sticky="w",
                                                                                    padx=(0, 10))
        tk.Label(original_frame, text="Дата подачи", bg="white").grid(row=0, column=3, sticky="w")
        tk.Entry(original_frame, textvariable=self.submission_date_var).grid(row=0, column=4, sticky="ew", padx=(5, 0))

        self.create_form_field(main_frame, 5, 0, "Учебное заведение", self.institution_var)

        # Город и общежитие
        city_frame = tk.Frame(main_frame, bg="white")
        city_frame.grid(row=6, column=0, sticky="ew", pady=5)
        city_frame.grid_columnconfigure(0, weight=0)
        city_frame.grid_columnconfigure(1, weight=1)
        city_frame.grid_columnconfigure(2, weight=0)
        city_frame.grid_columnconfigure(3, weight=0)

        tk.Label(city_frame, text="Город", bg="white").grid(row=0, column=0, sticky="w")
        tk.Entry(city_frame, textvariable=self.city_var).grid(row=0, column=1, sticky="ew", padx=(5, 10))
        tk.Label(city_frame, text="Общежитие", bg="white").grid(row=0, column=2, sticky="w")
        tk.Checkbutton(city_frame, bg="white", variable=self.dormitory_var).grid(row=0, column=3, sticky="w",
                                                                                 padx=(5, 0))

        # Правая колонка - Дополнительная информация
        self.create_form_field(main_frame, 1, 1, "Дата посещения", self.visit_date_var, padx=(20, 0))
        self.create_form_field(main_frame, 2, 1, "Откуда узнал/а", self.info_source_var, padx=(20, 0))

        # Поле для примечаний
        note_label = tk.Label(main_frame, text="Примечание", bg="white")
        note_label.grid(row=3, column=1, sticky="w", pady=5, padx=(20, 0))
        self.note_text = tk.Text(main_frame, height=10, width=40)
        self.note_text.grid(row=4, column=1, rowspan=3, sticky="nsew", pady=5, padx=(20, 0))

        # Контактная информация
        contact_frame = tk.Frame(self, bg="white")
        contact_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        contact_frame.grid_columnconfigure(0, weight=1)

        contact_label = tk.Label(contact_frame, text="КОНТАКТНАЯ ИНФОРМАЦИЯ:",
                                 font=tkfont.Font(family="Arial", size=12, weight="bold"),
                                 bg="white")
        contact_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.create_form_field(contact_frame, 1, 0, "Телефон", self.phone_var)
        self.create_form_field(contact_frame, 2, 0, "Профиль ВК", self.vk_var)
        self.create_form_field(contact_frame, 3, 0, "Родитель", self.parent_var)
        self.create_form_field(contact_frame, 4, 0, "Телефон родителя", self.parent_phone_var)

        # Кнопки
        button_frame = tk.Frame(self, bg="white")
        button_frame.grid(row=3, column=0, sticky="e", padx=20, pady=20)

        # Используем обычные кнопки Windows вместо ttk.Button
        save_button = tk.Button(button_frame, text="Сохранить", command=self.save_data)
        save_button.grid(row=0, column=0, padx=5)

        cancel_button = tk.Button(button_frame, text="Отмена", command=self.destroy)
        cancel_button.grid(row=0, column=1, padx=5)

        save_new_button = tk.Button(button_frame, text="Сохранить и создать новый", command=self.save_and_create_new)
        save_new_button.grid(row=0, column=2, padx=5)

        logger.info("Форма абитуриента успешно инициализирована")

    def create_form_field(self, parent, row, column, label_text, variable=None, padx=(0, 0)):
        """Вспомогательный метод для создания поля формы с меткой и полем ввода"""
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=row, column=column, sticky="ew", pady=5, padx=padx)
        frame.grid_columnconfigure(1, weight=1)

        label = tk.Label(frame, text=label_text, bg="white")
        label.grid(row=0, column=0, sticky="w")

        entry = tk.Entry(frame, textvariable=variable)
        entry.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        return entry

    def save_data(self):
        """Сохраняет данные в объект Applicant и добавляет его в реестр"""
        try:
            logger.info("Попытка сохранения данных абитуриента")

            # Получаем данные из полей формы
            full_name = self.full_name_var.get()
            phone = self.phone_var.get()
            city = self.city_var.get()

            # Проверка обязательных полей
            if not full_name or not phone or not city or not self.code_var.get():
                error_msg = "Не заполнены обязательные поля"
                logger.warning(error_msg)
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
                return

            # Создаем объекты для Applicant
            try:
                rating = float(self.rating_var.get()) if self.rating_var.get() else 0.0
            except ValueError:
                error_msg = "Неверный формат рейтинга"
                logger.error(error_msg)
                messagebox.showerror("Ошибка", "Рейтинг должен быть числом")
                return

            application_details = ApplicationDetails(
                code=self.code_var.get(),
                rating=rating,
                has_original=self.original_var.get(),
                benefits=self.benefits_var.get() if self.benefits_var.get() else None
            )

            education = EducationalBackground(
                institution=self.institution_var.get()
            )

            contact_info = ContactInfo(
                phone=phone,
                vk=self.vk_var.get() if self.vk_var.get() else None
            )

            # Преобразование строки даты в datetime, если она указана
            visit_date = None
            if self.visit_date_var.get():
                try:
                    visit_date = datetime.strptime(self.visit_date_var.get(), "%d.%m.%Y")
                    logger.info(f"Успешно преобразована дата посещения: {self.visit_date_var.get()}")
                except ValueError:
                    logger.warning(f"Неверный формат даты: {self.visit_date_var.get()}")
                    messagebox.showwarning("Предупреждение",
                                           "Формат даты должен быть ДД.ММ.ГГГГ. Дата не будет сохранена.")

            additional_info = AdditionalInfo(
                department_visit=visit_date,
                notes=self.note_text.get("1.0", tk.END).strip(),
                information_source=self.info_source_var.get() if self.info_source_var.get() else None,
                dormitory_needed=self.dormitory_var.get()
            )

            # Создаем родителя, если указаны данные
            parent = None
            if self.parent_var.get() and self.parent_phone_var.get():
                parent = Parent(
                    full_name=self.parent_var.get(),
                    phone=self.parent_phone_var.get(),
                    city=city  # Предполагаем, что город совпадает с городом абитуриента
                )
                logger.info(f"Добавлена информация о родителе: {self.parent_var.get()}")

            # Создаем абитуриента
            applicant = Applicant(
                full_name=full_name,
                phone=phone,
                city=city,
                application_details=application_details,
                education=education,
                contact_info=contact_info,
                additional_info=additional_info,
                parent=parent
            )

            # Добавляем в реестр
            applicant_registry.add_applicant(applicant)
            logger.info(f"Абитуриент успешно добавлен в реестр: {full_name}")

            messagebox.showinfo("Успешно", "Данные абитуриента сохранены")

            # Закрываем окно и открываем основную программу с таблицей
            logger.info("Переход к главному окну с таблицей")
            self.destroy()
            self.open_main_application()

        except Exception as e:
            error_msg = f"Ошибка при сохранении данных: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении: {str(e)}")

    def save_and_create_new(self):
        """Сохраняет данные и очищает форму для создания нового абитуриента"""
        try:
            logger.info("Сохранение данных с последующим созданием новой записи")
            self.save_data()
            # Если save_data() выполнился успешно, но не закрыл окно (например, из-за проверок),
            # то очищаем поля формы
            if self.winfo_exists():
                self.clear_form()
                logger.info("Форма очищена для новой записи")
        except Exception as e:
            error_msg = f"Ошибка при сохранении и создании новой записи: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def clear_form(self):
        """Очищает все поля формы"""
        logger.info("Очистка всех полей формы")
        self.full_name_var.set("")
        self.case_number_var.set("")
        self.code_var.set("")
        self.rating_var.set("")
        self.benefits_var.set("")
        self.original_var.set(False)
        self.submission_date_var.set("")
        self.institution_var.set("")
        self.city_var.set("")
        self.dormitory_var.set(False)
        self.visit_date_var.set("")
        self.info_source_var.set("")
        self.phone_var.set("")
        self.vk_var.set("")
        self.parent_var.set("")
        self.parent_phone_var.set("")
        self.note_text.delete("1.0", tk.END)

    def open_main_application(self):
        """Открывает основную программу с таблицей"""
        logger.info("Открытие главного окна приложения с таблицей абитуриентов")
        root = tk.Tk()
        root.title("Реестр абитуриентов")
        root.geometry("800x600")

        # Создаем экземпляр окна с таблицей
        table_window = ApplicantTableWindow(root, applicant_registry.applicants, logger)

        # Кнопка для добавления нового абитуриента
        add_button = tk.Button(root, text="Добавить абитуриента",
                               command=lambda: self.open_applicant_form(root))
        add_button.pack(pady=10)

        root.mainloop()

    @staticmethod
    def open_applicant_form(parent_window=None):
        """Открывает форму для добавления абитуриента"""
        if parent_window:
            logger.info("Закрытие текущего окна и открытие формы абитуриента")
            parent_window.destroy()
        else:
            logger.info("Открытие формы абитуриента")
        app = ApplicantForm()
        app.mainloop()


if __name__ == "__main__":
    logger.info("Запуск приложения")
    app = ApplicantForm()
    app.mainloop()