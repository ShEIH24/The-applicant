"""app_reports.py - Модуль для аналитики и отчетов с визуализацией"""
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class ReportsWindow:
    def __init__(self, parent, db_manager, logger):
        """
        Инициализация окна отчетов

        :param parent: Родительское окно
        :param db_manager: Менеджер базы данных
        :param logger: Экземпляр логгера
        """
        self.parent = parent
        self.db_manager = db_manager
        self.logger = logger

        self.window = tk.Toplevel(parent)
        self.window.title("Аналитика и отчёты")
        self.window.geometry("1200x900")
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()

        self.logger.info("Открыто окно аналитики и отчётов")

        # Настройка matplotlib для корректного отображения кириллицы
        plt.rcParams['font.family'] = 'DejaVu Sans'
        try:
            plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        except:
            pass

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса окна отчетов"""
        # Заголовок
        header_frame = tk.Frame(self.window, bg="#3f51b5", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="АНАЛИТИКА И ОТЧЁТЫ",
                font=("Arial", 14, "bold"),
                bg="#3f51b5", fg="white").pack(pady=15)

        # Notebook для вкладок
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка 1: Анализ проходного балла
        self.passing_score_tab = tk.Frame(self.notebook)
        self.notebook.add(self.passing_score_tab, text="Анализ проходного балла")
        self.create_passing_score_section(self.passing_score_tab)

        # Вкладка 2: Диаграммы
        self.charts_tab = tk.Frame(self.notebook)
        self.notebook.add(self.charts_tab, text="Диаграммы")
        self.create_charts_section(self.charts_tab)

        # Вкладка 3: Статистика
        self.stats_tab = tk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Статистика")
        self.create_analytics_section(self.stats_tab)

        # Вкладка 4: Прогнозирование
        self.forecast_tab = tk.Frame(self.notebook)
        self.notebook.add(self.forecast_tab, text="Прогнозирование")
        self.create_forecast_section(self.forecast_tab)

        # Кнопка закрытия
        tk.Button(self.window, text="Закрыть", bg="#9e9e9e", fg="white",
                 width=15, command=self.window.destroy).pack(pady=10)

    def create_passing_score_section(self, parent):
        """Создание секции анализа проходного балла"""
        main_frame = tk.Frame(parent, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        section_frame = tk.LabelFrame(main_frame, text="Анализ проходного балла",
                                     font=("Arial", 11, "bold"), padx=15, pady=15)
        section_frame.pack(fill="both", expand=True)

        # Поля ввода
        input_frame = tk.Frame(section_frame)
        input_frame.pack(fill="x", pady=10)

        tk.Label(input_frame, text="Проходной балл:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.passing_score_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.passing_score_var, width=15).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="Количество бюджетных мест:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.budget_places_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.budget_places_var, width=15).grid(row=1, column=1, padx=10, pady=5)

        # Кнопка анализа
        tk.Button(input_frame, text="Выполнить анализ", bg="#3f51b5", fg="white",
                 width=20, command=self.analyze_passing_score).grid(row=2, column=0, columnspan=2, pady=15)

        # Таблица результатов
        table_frame = tk.Frame(section_frame)
        table_frame.pack(fill="both", expand=True)

        y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        self.passing_table = ttk.Treeview(table_frame,
                                         yscrollcommand=y_scrollbar.set,
                                         xscrollcommand=x_scrollbar.set,
                                         selectmode="browse",
                                         height=15)
        self.passing_table.pack(fill="both", expand=True)

        y_scrollbar.config(command=self.passing_table.yview)
        x_scrollbar.config(command=self.passing_table.xview)

        # Настройка колонок
        self.passing_table["columns"] = ("status", "number", "fio", "code", "rating", "benefit", "original")
        self.passing_table["show"] = "headings"

        columns_config = {
            "status": {"text": "Статус", "width": 100},
            "number": {"text": "№", "width": 50},
            "fio": {"text": "ФИО", "width": 200},
            "code": {"text": "Код", "width": 100},
            "rating": {"text": "Рейтинг", "width": 80},
            "benefit": {"text": "Льгота", "width": 150},
            "original": {"text": "Оригинал", "width": 80}
        }

        for col_id, config in columns_config.items():
            self.passing_table.column(col_id, width=config["width"],
                                     anchor="center" if col_id in ["status", "number", "rating", "original"] else "w")
            self.passing_table.heading(col_id, text=config["text"])

        # Настройка цветов
        self.passing_table.tag_configure("green", background="#c8e6c9", foreground="#1b5e20")
        self.passing_table.tag_configure("yellow", background="#fff9c4", foreground="#f57f17")
        self.passing_table.tag_configure("red", background="#ffcdd2", foreground="#b71c1c")
        self.passing_table.tag_configure("gray", background="#e0e0e0", foreground="#616161")
        self.passing_table.tag_configure("gray_green", background="#d4e8d4", foreground="#5a735a")
        self.passing_table.tag_configure("gray_yellow", background="#f0edd4", foreground="#7a7550")
        self.passing_table.tag_configure("gray_red", background="#ead4d4", foreground="#7a5a5a")

    def create_charts_section(self, parent):
        """Создание секции диаграмм"""
        main_frame = tk.Frame(parent, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Панель кнопок
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        buttons = [
            ("Источники информации", self.show_source_chart),
            ("Города", self.show_city_chart),
            ("Регионы", self.show_region_chart),
            ("Льготы", self.show_benefit_chart),
            ("Распределение баллов", self.show_rating_distribution),
        ]

        for i, (text, command) in enumerate(buttons):
            tk.Button(button_frame, text=text, bg="#3f51b5", fg="white",
                     width=20, command=command).grid(row=i//3, column=i%3, padx=5, pady=5)

        # Область для диаграммы
        self.chart_frame = tk.Frame(main_frame, bg="white")
        self.chart_frame.pack(fill="both", expand=True, pady=10)

    def create_analytics_section(self, parent):
        """Создание секции аналитики"""
        main_frame = tk.Frame(parent, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        section_frame = tk.LabelFrame(main_frame, text="Аналитика по городам и источникам информации",
                                     font=("Arial", 11, "bold"), padx=15, pady=15)
        section_frame.pack(fill="both", expand=True)

        # Кнопки аналитики
        button_frame = tk.Frame(section_frame)
        button_frame.pack(fill="x", pady=10)

        tk.Button(button_frame, text="Статистика по городам", bg="#3f51b5", fg="white",
                 width=25, command=self.show_city_analytics).pack(side="left", padx=5)

        tk.Button(button_frame, text="Статистика по источникам", bg="#3f51b5", fg="white",
                 width=25, command=self.show_source_analytics).pack(side="left", padx=5)

        tk.Button(button_frame, text="Общая статистика", bg="#3f51b5", fg="white",
                 width=25, command=self.show_general_analytics).pack(side="left", padx=5)

        # Таблица для аналитики
        analytics_table_frame = tk.Frame(section_frame)
        analytics_table_frame.pack(fill="both", expand=True, pady=10)

        y_scrollbar = ttk.Scrollbar(analytics_table_frame, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")

        x_scrollbar = ttk.Scrollbar(analytics_table_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        self.analytics_table = ttk.Treeview(analytics_table_frame,
                                           yscrollcommand=y_scrollbar.set,
                                           xscrollcommand=x_scrollbar.set,
                                           selectmode="browse",
                                           height=15)
        self.analytics_table.pack(fill="both", expand=True)

        y_scrollbar.config(command=self.analytics_table.yview)
        x_scrollbar.config(command=self.analytics_table.xview)

    def create_forecast_section(self, parent):
        """Создание секции прогнозирования"""
        main_frame = tk.Frame(parent, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Панель кнопок прогнозирования
        button_frame = tk.LabelFrame(main_frame, text="Выберите тип прогноза",
                                     font=("Arial", 11, "bold"), padx=15, pady=15)
        button_frame.pack(fill="x", pady=10)

        tk.Button(button_frame, text="Прогноз проходного балла", bg="#2196f3", fg="white",
                 width=30, command=self.forecast_passing_score).pack(pady=5)

        tk.Button(button_frame, text="Прогноз потребности в общежитии", bg="#2196f3", fg="white",
                 width=30, command=self.forecast_dormitory_demand).pack(pady=5)

        tk.Button(button_frame, text="Анализ эффективности источников", bg="#2196f3", fg="white",
                 width=30, command=self.analyze_source_effectiveness).pack(pady=5)

        tk.Button(button_frame, text="Географический анализ", bg="#2196f3", fg="white",
                 width=30, command=self.geographic_analysis).pack(pady=5)

        # Область для результатов
        self.forecast_frame = tk.Frame(main_frame)
        self.forecast_frame.pack(fill="both", expand=True, pady=10)

    def clear_chart_frame(self):
        """Очистка области диаграмм"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def show_source_chart(self):
        """Диаграмма по источникам информации"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT 
                ISNULL(isrc.name_source, 'Не указано') as source,
                COUNT(a.id_applicant) as total
            FROM Applicant a
            LEFT JOIN Additional_info ai ON a.id_applicant = ai.id_applicant
            LEFT JOIN Information_source isrc ON ai.id_source = isrc.id_source
            GROUP BY isrc.name_source
            ORDER BY total DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Информация", "Нет данных для отображения")
                return

            sources = [row.source for row in results]
            counts = [row.total for row in results]

            self.clear_chart_frame()

            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)

            colors = plt.cm.Set3(range(len(sources)))
            bars = ax.bar(range(len(sources)), counts, color=colors)

            ax.set_xlabel('Источники информации', fontsize=12)
            ax.set_ylabel('Количество абитуриентов', fontsize=12)
            ax.set_title('Распределение абитуриентов по источникам информации', fontsize=14, fontweight='bold')
            ax.set_xticks(range(len(sources)))
            ax.set_xticklabels(sources, rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)

            # Добавляем значения на столбцы
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom')

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.logger.info("Отображена диаграмма по источникам информации")

        except Exception as e:
            self.logger.error(f"Ошибка построения диаграммы источников: {e}")
            messagebox.showerror("Ошибка", f"Ошибка построения диаграммы:\n{str(e)}")

    def show_city_chart(self):
        """Диаграмма по городам"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT TOP 10
                ISNULL(c.name_city, 'Не указан') as city,
                COUNT(a.id_applicant) as total
            FROM Applicant a
            LEFT JOIN City c ON a.id_city = c.id_city
            GROUP BY c.name_city
            ORDER BY total DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Информация", "Нет данных для отображения")
                return

            cities = [row.city for row in results]
            counts = [row.total for row in results]

            self.clear_chart_frame()

            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)

            colors = plt.cm.Paired(range(len(cities)))
            ax.barh(range(len(cities)), counts, color=colors)

            ax.set_yticks(range(len(cities)))
            ax.set_yticklabels(cities)
            ax.set_xlabel('Количество абитуриентов', fontsize=12)
            ax.set_title('ТОП-10 городов по количеству абитуриентов', fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)

            # Добавляем значения
            for i, count in enumerate(counts):
                ax.text(count, i, f' {int(count)}', va='center')

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.logger.info("Отображена диаграмма по городам")

        except Exception as e:
            self.logger.error(f"Ошибка построения диаграммы городов: {e}")
            messagebox.showerror("Ошибка", f"Ошибка построения диаграммы:\n{str(e)}")

    def show_region_chart(self):
        """Диаграмма по регионам"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT 
                ISNULL(r.name_region, 'Не указан') as region,
                COUNT(a.id_applicant) as total
            FROM Applicant a
            LEFT JOIN City c ON a.id_city = c.id_city
            LEFT JOIN Region r ON c.id_region = r.id_region
            GROUP BY r.name_region
            ORDER BY total DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Информация", "Нет данных для отображения")
                return

            regions = [row.region for row in results]
            counts = [row.total for row in results]

            self.clear_chart_frame()

            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)

            colors = plt.cm.Set2(range(len(regions)))
            wedges, texts, autotexts = ax.pie(counts, labels=regions, autopct='%1.1f%%',
                                               colors=colors, startangle=90)

            # Улучшаем читаемость
            for text in texts:
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)

            ax.set_title('Распределение абитуриентов по регионам', fontsize=14, fontweight='bold')

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.logger.info("Отображена диаграмма по регионам")

        except Exception as e:
            self.logger.error(f"Ошибка построения диаграммы регионов: {e}")
            messagebox.showerror("Ошибка", f"Ошибка построения диаграммы:\n{str(e)}")

    def show_benefit_chart(self):
        """Диаграмма по льготам"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT 
                b.name_benefit,
                COUNT(ab.id_applicant) as total,
                AVG(CAST(b.bonus_points AS FLOAT)) as avg_bonus
            FROM Applicant_benefit ab
            JOIN Benefit b ON ab.id_benefit = b.id_benefit
            GROUP BY b.name_benefit
            ORDER BY total DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Информация", "Нет данных о льготах")
                return

            benefits = [row.name_benefit for row in results]
            counts = [row.total for row in results]
            bonuses = [row.avg_bonus for row in results]

            self.clear_chart_frame()

            fig = Figure(figsize=(12, 6), dpi=100)

            # Две подобласти
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)

            # График 1: Количество абитуриентов
            colors = plt.cm.viridis(np.linspace(0, 1, len(benefits)))
            bars1 = ax1.barh(range(len(benefits)), counts, color=colors)
            ax1.set_yticks(range(len(benefits)))
            ax1.set_yticklabels(benefits, fontsize=9)
            ax1.set_xlabel('Количество абитуриентов', fontsize=10)
            ax1.set_title('Распределение льгот', fontsize=12, fontweight='bold')
            ax1.grid(axis='x', alpha=0.3)

            for i, count in enumerate(counts):
                ax1.text(count, i, f' {int(count)}', va='center', fontsize=9)

            # График 2: Средние баллы
            bars2 = ax2.barh(range(len(benefits)), bonuses, color=colors)
            ax2.set_yticks(range(len(benefits)))
            ax2.set_yticklabels(benefits, fontsize=9)
            ax2.set_xlabel('Бонусные баллы', fontsize=10)
            ax2.set_title('Бонусные баллы льгот', fontsize=12, fontweight='bold')
            ax2.grid(axis='x', alpha=0.3)

            for i, bonus in enumerate(bonuses):
                ax2.text(bonus, i, f' {bonus:.1f}', va='center', fontsize=9)

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.logger.info("Отображена диаграмма по льготам")

        except Exception as e:
            self.logger.error(f"Ошибка построения диаграммы льгот: {e}")
            messagebox.showerror("Ошибка", f"Ошибка построения диаграммы:\n{str(e)}")

    def show_rating_distribution(self):
        """Диаграмма распределения баллов"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT 
                ad.rating,
                ad.has_original
            FROM Application_details ad
            ORDER BY ad.rating DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Информация", "Нет данных для отображения")
                return

            ratings_with_original = [row.rating for row in results if row.has_original]
            ratings_without_original = [row.rating for row in results if not row.has_original]

            self.clear_chart_frame()

            fig = Figure(figsize=(12, 6), dpi=100)
            ax = fig.add_subplot(111)

            # Гистограмма
            bins = np.arange(0, max(r.rating for r in results) + 10, 10)
            ax.hist([ratings_with_original, ratings_without_original],
                   bins=bins,
                   label=['С оригиналом', 'Без оригинала'],
                   color=['#4caf50', '#ff9800'],
                   alpha=0.7,
                   edgecolor='black')

            ax.set_xlabel('Рейтинговый балл', fontsize=12)
            ax.set_ylabel('Количество абитуриентов', fontsize=12)
            ax.set_title('Распределение абитуриентов по баллам', fontsize=14, fontweight='bold')
            ax.legend(fontsize=11)
            ax.grid(axis='y', alpha=0.3)

            # Добавляем среднее значение
            if ratings_with_original:
                avg_with = np.mean(ratings_with_original)
                ax.axvline(avg_with, color='green', linestyle='--', linewidth=2,
                          label=f'Среднее (с ориг.): {avg_with:.1f}')

            if ratings_without_original:
                avg_without = np.mean(ratings_without_original)
                ax.axvline(avg_without, color='orange', linestyle='--', linewidth=2,
                          label=f'Среднее (без ориг.): {avg_without:.1f}')

            ax.legend(fontsize=10)

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.logger.info("Отображена диаграмма распределения баллов")

        except Exception as e:
            self.logger.error(f"Ошибка построения диаграммы распределения: {e}")
            messagebox.showerror("Ошибка", f"Ошибка построения диаграммы:\n{str(e)}")

    def forecast_passing_score(self):
        """Прогноз проходного балла на основе статистики"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            # Получаем статистику по баллам с оригиналами
            query = """
            SELECT 
                ad.rating
            FROM Application_details ad
            WHERE ad.has_original = 1
            ORDER BY ad.rating DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Информация", "Недостаточно данных для прогноза")
                return

            ratings = [row.rating for row in results]

            # Статистический анализ
            avg_rating = np.mean(ratings)
            median_rating = np.median(ratings)
            std_rating = np.std(ratings)
            min_rating = np.min(ratings)
            max_rating = np.max(ratings)

            # Квартили
            q1 = np.percentile(ratings, 25)
            q3 = np.percentile(ratings, 75)

            # Прогноз проходного балла (75-й перцентиль)
            predicted_passing = np.percentile(ratings, 75)

            # Очистка и создание текстового отчета
            for widget in self.forecast_frame.winfo_children():
                widget.destroy()

            report_text = tk.Text(self.forecast_frame, wrap="word", font=("Arial", 11), height=20)
            report_text.pack(fill="both", expand=True, padx=10, pady=10)

            report = f"""
ПРОГНОЗ ПРОХОДНОГО БАЛЛА (СТАТИСТИЧЕСКИЙ)


СТАТИСТИКА ПО РЕЙТИНГОВЫМ БАЛЛАМ (абитуриенты с оригиналами):

• Количество абитуриентов с оригиналами: {len(ratings)}
• Средний балл: {avg_rating:.2f}
• Медиана: {median_rating:.2f}
• Стандартное отклонение: {std_rating:.2f}
• Минимальный балл: {min_rating:.2f}
• Максимальный балл: {max_rating:.2f}

КВАРТИЛЬНЫЙ АНАЛИЗ:

• 1-й квартиль (25%): {q1:.2f}
• 2-й квартиль (50%, медиана): {median_rating:.2f}
• 3-й квартиль (75%): {q3:.2f}

ПРОГНОЗИРУЕМЫЙ ПРОХОДНОЙ БАЛЛ:

• Консервативный прогноз (75-й перцентиль): {predicted_passing:.2f}
• Оптимистичный прогноз (медиана): {median_rating:.2f}
• Безопасный прогноз (среднее + σ): {avg_rating + std_rating:.2f}

РЕКОМЕНДАЦИИ:

1. Рекомендуется установить проходной балл на уровне {predicted_passing:.1f}
   (обеспечит поступление 75% лучших абитуриентов с оригиналами)

2. При высоком конкурсе можно повысить до {avg_rating + std_rating:.1f}
   (более строгий отбор)

3. При низком конкурсе можно снизить до {median_rating:.1f}
   (заполнение всех бюджетных мест)

4. Критический минимум: {q1:.1f}
   (ниже этого уровня качество набора может снизиться)

"""
            report_text.insert("1.0", report)
            report_text.config(state="disabled")

            self.logger.info("Выполнен прогноз проходного балла")

        except Exception as e:
            self.logger.error(f"Ошибка прогнозирования проходного балла: {e}")
            messagebox.showerror("Ошибка", f"Ошибка прогнозирования:\n{str(e)}")

    def forecast_dormitory_demand(self):
        """Прогноз потребности в общежитии"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            # Общая статистика по общежитию
            query = """
            SELECT 
                COUNT(*) as total_applicants,
                SUM(CASE WHEN ai.dormitory_needed = 1 THEN 1 ELSE 0 END) as need_dorm,
                SUM(CASE WHEN ai.dormitory_needed = 1 AND ad.has_original = 1 THEN 1 ELSE 0 END) as need_dorm_with_original
            FROM Applicant a
            JOIN Application_details ad ON a.id_applicant = ad.id_applicant
            LEFT JOIN Additional_info ai ON a.id_applicant = ai.id_applicant
            """

            cursor.execute(query)
            result = cursor.fetchone()

            # Статистика по городам
            query_cities = """
            SELECT 
                ISNULL(c.name_city, 'Не указан') as city,
                COUNT(*) as total,
                SUM(CASE WHEN ai.dormitory_needed = 1 THEN 1 ELSE 0 END) as need_dorm
            FROM Applicant a
            JOIN Application_details ad ON a.id_applicant = ad.id_applicant
            LEFT JOIN Additional_info ai ON a.id_applicant = ai.id_applicant
            LEFT JOIN City c ON a.id_city = c.id_city
            GROUP BY c.name_city
            HAVING SUM(CASE WHEN ai.dormitory_needed = 1 THEN 1 ELSE 0 END) > 0
            ORDER BY need_dorm DESC
            """

            cursor.execute(query_cities)
            city_results = cursor.fetchall()

            # Очистка и создание отчета
            for widget in self.forecast_frame.winfo_children():
                widget.destroy()

            report_text = tk.Text(self.forecast_frame, wrap="word", font=("Arial", 11), height=25)
            report_text.pack(fill="both", expand=True, padx=10, pady=10)

            total = result.total_applicants
            need_dorm = result.need_dorm
            need_dorm_orig = result.need_dorm_with_original
            percent = (need_dorm / total * 100) if total > 0 else 0
            percent_orig = (need_dorm_orig / total * 100) if total > 0 else 0

            report = f"""
ПРОГНОЗ ПОТРЕБНОСТИ В ОБЩЕЖИТИИ


ОБЩАЯ СТАТИСТИКА:

• Всего абитуриентов: {total}
• Нуждаются в общежитии: {need_dorm} ({percent:.1f}%)
• Из них с оригиналами документов: {need_dorm_orig} ({percent_orig:.1f}%)

РАСПРЕДЕЛЕНИЕ ПО ГОРОДАМ (требуют общежитие):

"""
            for city_row in city_results:
                city_percent = (city_row.need_dorm / city_row.total * 100) if city_row.total > 0 else 0
                report += f"• {city_row.city}: {city_row.need_dorm} из {city_row.total} ({city_percent:.1f}%)\n"

            # Прогноз
            projected_enrollment = need_dorm_orig  # Реалистичный прогноз - с оригиналами
            safety_margin = int(projected_enrollment * 1.2)  # +20% запас

            report += f"""

ПРОГНОЗ И РЕКОМЕНДАЦИИ:

1. МИНИМАЛЬНАЯ ПОТРЕБНОСТЬ:
   • {need_dorm_orig} мест (абитуриенты с оригиналами)

2. РЕКОМЕНДУЕМАЯ ЁМКОСТЬ:
   • {safety_margin} мест (с запасом 20%)

3. МАКСИМАЛЬНАЯ ПОТРЕБНОСТЬ:
   • {need_dorm} мест (если все подадут оригиналы)

СТРАТЕГИЧЕСКИЕ РЕКОМЕНДАЦИИ:

• Приоритет 1: Обеспечить {need_dorm_orig} мест для абитуриентов 
  с оригиналами документов

• Приоритет 2: Создать резерв на {safety_margin - need_dorm_orig} мест
  для форс-мажорных ситуаций

• Особое внимание к иногородним абитуриентам из:
"""
            # ТОП-3 города
            for i, city_row in enumerate(city_results[:3], 1):
                report += f"  {i}. {city_row.city} ({city_row.need_dorm} чел.)\n"

            report += """
• Рекомендуется начать бронирование мест заблаговременно

"""
            report_text.insert("1.0", report)
            report_text.config(state="disabled")

            self.logger.info("Выполнен прогноз потребности в общежитии")

        except Exception as e:
            self.logger.error(f"Ошибка прогноза потребности в общежитии: {e}")
            messagebox.showerror("Ошибка", f"Ошибка прогнозирования:\n{str(e)}")

    def analyze_source_effectiveness(self):
        """Анализ эффективности источников информации"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT 
                ISNULL(isrc.name_source, 'Не указано') as source,
                COUNT(a.id_applicant) as total_applicants,
                SUM(CASE WHEN ad.has_original = 1 THEN 1 ELSE 0 END) as with_originals,
                AVG(ad.rating) as avg_rating,
                MAX(ad.rating) as max_rating
            FROM Applicant a
            JOIN Application_details ad ON a.id_applicant = ad.id_applicant
            LEFT JOIN Additional_info ai ON a.id_applicant = ai.id_applicant
            LEFT JOIN Information_source isrc ON ai.id_source = isrc.id_source
            GROUP BY isrc.name_source
            ORDER BY total_applicants DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Информация", "Нет данных для анализа")
                return

            # Очистка и создание отчета
            for widget in self.forecast_frame.winfo_children():
                widget.destroy()

            report_text = tk.Text(self.forecast_frame, wrap="word", font=("Arial", 11), height=25)
            report_text.pack(fill="both", expand=True, padx=10, pady=10)

            report = """
АНАЛИЗ ЭФФЕКТИВНОСТИ ИСТОЧНИКОВ ИНФОРМАЦИИ

ДЕТАЛЬНЫЙ АНАЛИЗ ПО ИСТОЧНИКАМ:

"""
            total_all = sum(row.total_applicants for row in results)

            for row in results:
                conversion_rate = (row.with_originals / row.total_applicants * 100) if row.total_applicants > 0 else 0
                market_share = (row.total_applicants / total_all * 100) if total_all > 0 else 0

                # Оценка эффективности
                if conversion_rate >= 70:
                    effectiveness = "🟢 ВЫСОКАЯ"
                elif conversion_rate >= 50:
                    effectiveness = "🟡 СРЕДНЯЯ"
                else:
                    effectiveness = "🔴 НИЗКАЯ"

                report += f"""
{row.source}

  • Всего абитуриентов: {row.total_applicants} ({market_share:.1f}% от общего числа)
  • Подали оригиналы: {row.with_originals}
  • Конверсия в оригиналы: {conversion_rate:.1f}%
  • Средний балл: {row.avg_rating:.2f}
  • Максимальный балл: {row.max_rating:.2f}
  • Эффективность: {effectiveness}

"""

            # Рекомендации
            best_sources = sorted(results,
                                key=lambda x: (x.with_originals / x.total_applicants if x.total_applicants > 0 else 0),
                                reverse=True)[:3]

            worst_sources = sorted(results,
                                 key=lambda x: (x.with_originals / x.total_applicants if x.total_applicants > 0 else 0))[:3]

            report += """
РЕКОМЕНДАЦИИ ПО МАРКЕТИНГОВОЙ СТРАТЕГИИ:

ТОП-3 САМЫХ ЭФФЕКТИВНЫХ ИСТОЧНИКА:
"""
            for i, source in enumerate(best_sources, 1):
                conv = (source.with_originals / source.total_applicants * 100) if source.total_applicants > 0 else 0
                report += f"  {i}. {source.source} (конверсия {conv:.1f}%)\n"

            report += """
     → Увеличить инвестиции в эти каналы
     → Масштабировать успешные практики

ТРЕБУЮТ УЛУЧШЕНИЯ:
"""
            for i, source in enumerate(worst_sources, 1):
                conv = (source.with_originals / source.total_applicants * 100) if source.total_applicants > 0 else 0
                report += f"  {i}. {source.source} (конверсия {conv:.1f}%)\n"

            report += """
     → Пересмотреть качество контента
     → Улучшить таргетинг аудитории
     → Рассмотреть возможность оптимизации или отказа

"""
            report_text.insert("1.0", report)
            report_text.config(state="disabled")

            self.logger.info("Выполнен анализ эффективности источников")

        except Exception as e:
            self.logger.error(f"Ошибка анализа эффективности источников: {e}")
            messagebox.showerror("Ошибка", f"Ошибка анализа:\n{str(e)}")

    def geographic_analysis(self):
        """Географический анализ набора"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            # Анализ по регионам
            query_regions = """
            SELECT 
                ISNULL(r.name_region, 'Не указан') as region,
                COUNT(a.id_applicant) as total,
                SUM(CASE WHEN ad.has_original = 1 THEN 1 ELSE 0 END) as with_originals,
                AVG(ad.rating) as avg_rating,
                SUM(CASE WHEN ai.dormitory_needed = 1 THEN 1 ELSE 0 END) as need_dorm
            FROM Applicant a
            JOIN Application_details ad ON a.id_applicant = ad.id_applicant
            LEFT JOIN Additional_info ai ON a.id_applicant = ai.id_applicant
            LEFT JOIN City c ON a.id_city = c.id_city
            LEFT JOIN Region r ON c.id_region = r.id_region
            GROUP BY r.name_region
            ORDER BY total DESC
            """

            cursor.execute(query_regions)
            region_results = cursor.fetchall()

            # Анализ по городам
            query_cities = """
            SELECT TOP 10
                ISNULL(c.name_city, 'Не указан') as city,
                ISNULL(r.name_region, 'Не указан') as region,
                COUNT(a.id_applicant) as total,
                SUM(CASE WHEN ad.has_original = 1 THEN 1 ELSE 0 END) as with_originals,
                AVG(ad.rating) as avg_rating
            FROM Applicant a
            JOIN Application_details ad ON a.id_applicant = ad.id_applicant
            LEFT JOIN City c ON a.id_city = c.id_city
            LEFT JOIN Region r ON c.id_region = r.id_region
            GROUP BY c.name_city, r.name_region
            ORDER BY total DESC
            """

            cursor.execute(query_cities)
            city_results = cursor.fetchall()

            # Очистка и создание отчета
            for widget in self.forecast_frame.winfo_children():
                widget.destroy()

            report_text = tk.Text(self.forecast_frame, wrap="word", font=("Arial", 11), height=25)
            report_text.pack(fill="both", expand=True, padx=10, pady=10)

            total_all = sum(row.total for row in region_results)

            report = f"""

ГЕОГРАФИЧЕСКИЙ АНАЛИЗ НАБОРА                   


РАСПРЕДЕЛЕНИЕ ПО РЕГИОНАМ:

"""
            for row in region_results:
                share = (row.total / total_all * 100) if total_all > 0 else 0
                conv = (row.with_originals / row.total * 100) if row.total > 0 else 0
                dorm_rate = (row.need_dorm / row.total * 100) if row.total > 0 else 0

                report += f"""
{row.region}

  • Абитуриентов: {row.total} ({share:.1f}% от общего числа)
  • С оригиналами: {row.with_originals} ({conv:.1f}%)
  • Средний балл: {row.avg_rating:.2f}
  • Нужно общежитие: {row.need_dorm} ({dorm_rate:.1f}%)

"""

            report += f"""

ТОП-10 ГОРОДОВ ПО КОЛИЧЕСТВУ АБИТУРИЕНТОВ:

"""
            for i, row in enumerate(city_results, 1):
                conv = (row.with_originals / row.total * 100) if row.total > 0 else 0
                report += f"""  {i}. {row.city} ({row.region})
     • Абитуриентов: {row.total}
     • С оригиналами: {row.with_originals} ({conv:.1f}%)
     • Средний балл: {row.avg_rating:.2f}

"""

            # Прогноз и рекомендации
            top_region = region_results[0] if region_results else None
            if top_region:
                report += f"""
СТРАТЕГИЧЕСКИЕ ВЫВОДЫ И РЕКОМЕНДАЦИИ:

1. ГЕОГРАФИЧЕСКАЯ КОНЦЕНТРАЦИЯ:
   • Основной регион: {top_region.region}
   • Доля: {(top_region.total / total_all * 100):.1f}% от общего набора
   
2. РЕКОМЕНДАЦИИ ПО РАЗВИТИЮ:
   
   Приоритет 1 - Укрепление позиций:
      → Усилить работу в {top_region.region}
      → Увеличить количество профориентационных мероприятий
      
   Приоритет 2 - Диверсификация:
"""
                # Регионы с низким представительством
                low_regions = [r for r in region_results if r.total < total_all * 0.1]
                if low_regions:
                    report += "      → Расширить охват в регионах:\n"
                    for lr in low_regions[:3]:
                        report += f"         • {lr.region}\n"

                report += f"""
   Приоритет 3 - Инфраструктура:
      → Требуется {top_region.need_dorm} мест в общежитии
      → Организовать транспортную логистику для иногородних

3. ПРОГНОЗ НА СЛЕДУЮЩИЙ ГОД:
   • Ожидаемый рост: +10-15% от текущих {total_all} абитуриентов
   • Прогноз: {int(total_all * 1.12)} абитуриентов
   • Основной прирост ожидается из: {top_region.region}

"""

            report += """
"""
            report_text.insert("1.0", report)
            report_text.config(state="disabled")

            self.logger.info("Выполнен географический анализ")

        except Exception as e:
            self.logger.error(f"Ошибка географического анализа: {e}")
            messagebox.showerror("Ошибка", f"Ошибка анализа:\n{str(e)}")

    def analyze_passing_score(self):
        """Анализ проходного балла"""
        try:
            passing_score = float(self.passing_score_var.get())
            budget_places = int(self.budget_places_var.get())

            if passing_score < 0 or budget_places < 1:
                messagebox.showerror("Ошибка", "Проверьте корректность введённых данных")
                return

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
            return

        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT 
                a.id_applicant,
                CONCAT(a.last_name, ' ', a.first_name, ' ', ISNULL(a.patronymic, '')) as fio,
                ad.code,
                ad.rating,
                ISNULL(b.name_benefit, 'Без льгот') as benefit,
                ISNULL(b.bonus_points, 0) as bonus_points,
                ad.has_original
            FROM Applicant a
            JOIN Application_details ad ON a.id_applicant = ad.id_applicant
            LEFT JOIN Applicant_benefit ab ON a.id_applicant = ab.id_applicant
            LEFT JOIN Benefit b ON ab.id_benefit = b.id_benefit
            ORDER BY ad.has_original DESC, ad.rating DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            for item in self.passing_table.get_children():
                self.passing_table.delete(item)

            if not results:
                messagebox.showinfo("Информация", "Нет абитуриентов в базе данных")
                return

            reserve_threshold = passing_score * 0.95

            passed_with_originals = 0
            reserve_with_originals = 0
            failed_with_originals = 0
            total_without_originals = 0
            original_idx = 0

            for row in results:
                total_rating = row.rating
                has_original = row.has_original

                if has_original:
                    original_idx += 1

                    if original_idx <= budget_places:
                        if total_rating >= passing_score:
                            status = "🟢 Проходит"
                            tag = "green"
                            passed_with_originals += 1
                        else:
                            status = "🟡 В резерве"
                            tag = "yellow"
                            reserve_with_originals += 1
                    else:
                        if total_rating >= reserve_threshold:
                            status = "🟡 В резерве"
                            tag = "yellow"
                            reserve_with_originals += 1
                        else:
                            status = "🔴 Не проходит"
                            tag = "red"
                            failed_with_originals += 1

                    display_number = original_idx
                    original_status = "Да"
                else:
                    total_without_originals += 1
                    potential_position = original_idx + total_without_originals

                    if potential_position <= budget_places:
                        if total_rating >= passing_score:
                            status = "⚪ Проходит*"
                            tag = "gray_green"
                        else:
                            status = "⚪ В резерве*"
                            tag = "gray_yellow"
                    else:
                        if total_rating >= reserve_threshold:
                            status = "⚪ В резерве*"
                            tag = "gray_yellow"
                        else:
                            status = "⚪ Не проходит*"
                            tag = "gray_red"

                    display_number = "-"
                    original_status = "Нет"

                self.passing_table.insert("", "end",
                                        values=(status, display_number, row.fio, row.code,
                                               f"{total_rating:.2f}", row.benefit, original_status),
                                        tags=(tag,))

            self.logger.info(f"Выполнен анализ проходного балла: порог={passing_score}, мест={budget_places}")

            messagebox.showinfo("Результат анализа",
                              f"АБИТУРИЕНТЫ С ОРИГИНАЛАМИ:\n"
                              f"  • Проходят на бюджет: {passed_with_originals}\n"
                              f"  • В резерве: {reserve_with_originals}\n"
                              f"  • Не проходят: {failed_with_originals}\n"
                              f"  • Всего с оригиналами: {original_idx}\n\n"
                              f"АБИТУРИЕНТЫ БЕЗ ОРИГИНАЛОВ:\n"
                              f"  • Всего без оригиналов: {total_without_originals}\n\n"
                              f"* - потенциальный статус (нужен оригинал документов)")

        except pyodbc.Error as e:
            self.logger.error(f"Ошибка при анализе проходного балла: {e}")
            messagebox.showerror("Ошибка БД", f"Ошибка при выполнении запроса:\n{str(e)}")

    def show_city_analytics(self):
        """Показать аналитику по городам"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT 
                r.name_region as region,
                c.name_city as city,
                COUNT(a.id_applicant) as total_applicants,
                SUM(CASE WHEN ad.has_original = 1 THEN 1 ELSE 0 END) as with_originals,
                AVG(ad.rating) as avg_rating,
                MAX(ad.rating) as max_rating,
                MIN(ad.rating) as min_rating
            FROM Applicant a
            LEFT JOIN City c ON a.id_city = c.id_city
            LEFT JOIN Region r ON c.id_region = r.id_region
            JOIN Application_details ad ON a.id_applicant = ad.id_applicant
            GROUP BY r.name_region, c.name_city
            ORDER BY total_applicants DESC, r.name_region, c.name_city
            """

            cursor.execute(query)
            results = cursor.fetchall()

            self.analytics_table["columns"] = ("region", "city", "total", "originals", "avg_rating", "max_rating", "min_rating")
            self.analytics_table["show"] = "headings"

            columns_config = {
                "region": {"text": "Регион", "width": 200},
                "city": {"text": "Город", "width": 150},
                "total": {"text": "Всего", "width": 80},
                "originals": {"text": "С оригиналами", "width": 120},
                "avg_rating": {"text": "Средний балл", "width": 120},
                "max_rating": {"text": "Макс. балл", "width": 100},
                "min_rating": {"text": "Мин. балл", "width": 100}
            }

            for col_id, config in columns_config.items():
                self.analytics_table.column(col_id, width=config["width"],
                                          anchor="center" if col_id in ["total", "originals", "avg_rating", "max_rating", "min_rating"] else "w")
                self.analytics_table.heading(col_id, text=config["text"])

            for item in self.analytics_table.get_children():
                self.analytics_table.delete(item)

            for row in results:
                self.analytics_table.insert("", "end",
                                          values=(
                                              row.region or "Не указан",
                                              row.city or "Не указан",
                                              row.total_applicants,
                                              row.with_originals,
                                              f"{row.avg_rating:.2f}" if row.avg_rating else "0.00",
                                              f"{row.max_rating:.2f}" if row.max_rating else "0.00",
                                              f"{row.min_rating:.2f}" if row.min_rating else "0.00"
                                          ))

            self.logger.info("Отображена статистика по городам")

        except pyodbc.Error as e:
            self.logger.error(f"Ошибка при получении статистики по городам: {e}")
            messagebox.showerror("Ошибка БД", f"Ошибка при выполнении запроса:\n{str(e)}")

    def show_source_analytics(self):
        """Показать аналитику по источникам информации"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            query = """
            SELECT 
                ISNULL(isrc.name_source, 'Не указано') as source,
                COUNT(a.id_applicant) as total_applicants,
                SUM(CASE WHEN ad.has_original = 1 THEN 1 ELSE 0 END) as with_originals,
                AVG(ad.rating) as avg_rating,
                CAST(COUNT(a.id_applicant) * 100.0 / (SELECT COUNT(*) FROM Applicant) AS DECIMAL(5,2)) as percentage
            FROM Applicant a
            JOIN Application_details ad ON a.id_applicant = ad.id_applicant
            LEFT JOIN Additional_info ai ON a.id_applicant = ai.id_applicant
            LEFT JOIN Information_source isrc ON ai.id_source = isrc.id_source
            GROUP BY isrc.name_source
            ORDER BY total_applicants DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            self.analytics_table["columns"] = ("source", "total", "originals", "avg_rating", "percentage")
            self.analytics_table["show"] = "headings"

            columns_config = {
                "source": {"text": "Источник информации", "width": 300},
                "total": {"text": "Всего", "width": 100},
                "originals": {"text": "С оригиналами", "width": 150},
                "avg_rating": {"text": "Средний балл", "width": 120},
                "percentage": {"text": "Процент (%)", "width": 120}
            }

            for col_id, config in columns_config.items():
                self.analytics_table.column(col_id, width=config["width"],
                                          anchor="center" if col_id in ["total", "originals", "avg_rating", "percentage"] else "w")
                self.analytics_table.heading(col_id, text=config["text"])

            for item in self.analytics_table.get_children():
                self.analytics_table.delete(item)

            for row in results:
                self.analytics_table.insert("", "end",
                                          values=(
                                              row.source,
                                              row.total_applicants,
                                              row.with_originals,
                                              f"{row.avg_rating:.2f}" if row.avg_rating else "0.00",
                                              f"{row.percentage:.2f}%"
                                          ))

            self.logger.info("Отображена статистика по источникам информации")

        except pyodbc.Error as e:
            self.logger.error(f"Ошибка при получении статистики по источникам: {e}")
            messagebox.showerror("Ошибка БД", f"Ошибка при выполнении запроса:\n{str(e)}")

    def show_general_analytics(self):
        """Показать общую аналитику"""
        if not self.db_manager or not self.db_manager.connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = self.db_manager.connection.cursor()

            stats = []

            cursor.execute("SELECT COUNT(*) FROM Applicant")
            total_applicants = cursor.fetchone()[0]
            stats.append(("Всего абитуриентов", total_applicants))

            cursor.execute("SELECT COUNT(*) FROM Application_details WHERE has_original = 1")
            with_originals = cursor.fetchone()[0]
            stats.append(("С оригиналами документов", with_originals))

            cursor.execute("SELECT AVG(rating) FROM Application_details")
            avg_rating = cursor.fetchone()[0]
            stats.append(("Средний рейтинговый балл", f"{avg_rating:.2f}" if avg_rating else "0.00"))

            cursor.execute("SELECT MAX(rating) FROM Application_details")
            max_rating = cursor.fetchone()[0]
            stats.append(("Максимальный балл", f"{max_rating:.2f}" if max_rating else "0.00"))

            cursor.execute("SELECT COUNT(*) FROM Additional_info WHERE dormitory_needed = 1")
            need_dorm = cursor.fetchone()[0]
            stats.append(("Нуждаются в общежитии", need_dorm))

            cursor.execute("""
                SELECT b.name_benefit, COUNT(ab.id_applicant) as cnt
                FROM Applicant_benefit ab
                JOIN Benefit b ON ab.id_benefit = b.id_benefit
                GROUP BY b.name_benefit
                ORDER BY cnt DESC
            """)
            benefits_data = cursor.fetchall()

            self.analytics_table["columns"] = ("parameter", "value")
            self.analytics_table["show"] = "headings"

            self.analytics_table.column("parameter", width=400, anchor="w")
            self.analytics_table.heading("parameter", text="Параметр")

            self.analytics_table.column("value", width=200, anchor="center")
            self.analytics_table.heading("value", text="Значение")

            for item in self.analytics_table.get_children():
                self.analytics_table.delete(item)

            for param, value in stats:
                self.analytics_table.insert("", "end", values=(param, value))

            self.analytics_table.insert("", "end", values=("", ""))
            self.analytics_table.insert("", "end", values=("СТАТИСТИКА ПО ЛЬГОТАМ", ""))

            for row in benefits_data:
                self.analytics_table.insert("", "end",
                                          values=(f"  {row.name_benefit}", row.cnt))

            self.logger.info("Отображена общая статистика")

        except pyodbc.Error as e:
            self.logger.error(f"Ошибка при получении общей статистики: {e}")
            messagebox.showerror("Ошибка БД", f"Ошибка при выполнении запроса:\n{str(e)}")


def open_reports_window(parent, db_manager, logger):
    """Функция для открытия окна отчетов"""
    if not db_manager or not db_manager.connection:
        messagebox.showerror("Ошибка", "Нет подключения к базе данных.\nОтчёты недоступны.")
        logger.warning("Попытка открыть окно отчётов без подключения к БД")
        return

    ReportsWindow(parent, db_manager, logger)