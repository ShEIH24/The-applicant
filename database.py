"""database.py - Модуль для работы с Microsoft SQL Server"""
import pyodbc
from typing import Optional, List
from classes import Applicant, Parent, EducationalBackground, ContactInfo, ApplicationDetails, AdditionalInfo
import logging


class DatabaseManager:
    def __init__(self, server: str, database: str, username: str = None, password: str = None,
                 use_windows_auth: bool = True):
        """
        Инициализация менеджера БД

        Args:
            server: Имя сервера (например, 'localhost' или 'localhost\\SQLEXPRESS')
            database: Имя базы данных
            username: Имя пользователя (если не используется Windows Authentication)
            password: Пароль (если не используется Windows Authentication)
            use_windows_auth: Использовать Windows Authentication
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.use_windows_auth = use_windows_auth
        self.connection = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Установка соединения с БД"""
        try:
            if self.use_windows_auth:
                connection_string = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"Trusted_Connection=yes;"
                )
            else:
                connection_string = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                )

            self.connection = pyodbc.connect(connection_string)
            self.logger.info(f"Успешное подключение к БД {self.database}")

            # ИЗМЕНЕНО: Сначала создаем структуру БД, потом инициализируем данные
            try:
                # Проверяем, нужно ли создавать структуру
                cursor = self.connection.cursor()
                cursor.execute("""
                               SELECT COUNT(*)
                               FROM sysobjects
                               WHERE name = 'Region'
                                 AND xtype = 'U'
                               """)
                if cursor.fetchone()[0] == 0:
                    self.logger.info("Таблицы не найдены, создаём структуру БД")
                    self.create_database_structure()

                # Инициализируем регионы и города только если таблицы существуют
                self.initialize_regions_and_cities()
            except Exception as init_error:
                self.logger.warning(f"Ошибка при инициализации справочников: {init_error}")

            return True
        except pyodbc.Error as e:
            self.logger.error(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()
            self.logger.info("Соединение с БД закрыто")

    def create_database_structure(self):
        """Создание структуры БД с каскадным удалением"""
        try:
            cursor = self.connection.cursor()

            # ИЗМЕНЕНО: Сначала проверяем и создаем таблицы Region и City
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Region' AND xtype='U')
                CREATE TABLE Region (
                    id_region INT IDENTITY(1,1) PRIMARY KEY,
                    name_region NVARCHAR(255) NOT NULL
                )
            """)

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='City' AND xtype='U')
                CREATE TABLE City (
                    id_city INT IDENTITY(1,1) PRIMARY KEY,
                    name_city NVARCHAR(255) NOT NULL,
                    id_region INT,
                    FOREIGN KEY (id_region)
                        REFERENCES Region(id_region)
                        ON DELETE SET NULL ON UPDATE CASCADE
                )
            """)

            # Коммитим создание Region и City перед их использованием
            self.connection.commit()

            # Таблица Education (ИЗМЕНЕНО: добавлен id_city)
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Education' AND xtype='U')
                CREATE TABLE Education (
                    id_education INT IDENTITY(1,1) PRIMARY KEY,
                    name_education NVARCHAR(255) NOT NULL,
                    id_city INT,
                    FOREIGN KEY (id_city)
                        REFERENCES City(id_city)
                        ON DELETE SET NULL ON UPDATE CASCADE
                )
            """)

            # Таблица Parent
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Parent' AND xtype='U')
                CREATE TABLE Parent (
                    id_parent INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(100),
                    phone NVARCHAR(20),
                    relation NVARCHAR(50) DEFAULT 'Родитель'
                )
            """)

            # Таблица Information_source
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Information_source' AND xtype='U')
                CREATE TABLE Information_source (
                    id_source INT IDENTITY(1,1) PRIMARY KEY,
                    name_source NVARCHAR(255)
                )
            """)

            # Таблица Benefit
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Benefit' AND xtype='U')
                CREATE TABLE Benefit (
                    id_benefit INT IDENTITY(1,1) PRIMARY KEY,
                    name_benefit NVARCHAR(255) NOT NULL,
                    bonus_points INT DEFAULT 0
                )
            """)

            # Таблица Applicant (ИЗМЕНЕНО: удален id_education)
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Applicant' AND xtype='U')
                CREATE TABLE Applicant (
                    id_applicant INT IDENTITY(1,1) PRIMARY KEY,
                    last_name NVARCHAR(100) NOT NULL,
                    first_name NVARCHAR(100) NOT NULL,
                    patronymic NVARCHAR(100),
                    id_city INT,
                    phone NVARCHAR(20) NOT NULL,
                    vk NVARCHAR(255),

                    id_parent INT,
                    id_details INT,
                    id_info INT,

                    FOREIGN KEY (id_city)
                        REFERENCES City(id_city)
                        ON DELETE SET NULL ON UPDATE CASCADE,

                    FOREIGN KEY (id_parent)
                        REFERENCES Parent(id_parent)
                        ON DELETE SET NULL ON UPDATE CASCADE
                )
            """)

            # Таблица Application_details
            # ИСПРАВЛЕНО: Убраны каскадные UPDATE для избежания циклических зависимостей
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Application_details' AND xtype='U')
                CREATE TABLE Application_details (
                    id_details INT IDENTITY(1,1) PRIMARY KEY,
                    id_applicant INT,
                    code NVARCHAR(50) NOT NULL,
                    rating FLOAT NOT NULL,
                    has_original BIT DEFAULT 0,
                    submission_date DATE,

                    FOREIGN KEY (id_applicant)
                        REFERENCES Applicant(id_applicant)
                        ON DELETE CASCADE ON UPDATE NO ACTION
                )
            """)

            # Таблица Additional_info
            # ИСПРАВЛЕНО: Убраны каскадные UPDATE для избежания циклических зависимостей
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Additional_info' AND xtype='U')
                CREATE TABLE Additional_info (
                    id_info INT IDENTITY(1,1) PRIMARY KEY,
                    id_applicant INT,
                    department_visit DATE,
                    notes NVARCHAR(MAX),
                    id_source INT,
                    dormitory_needed BIT DEFAULT 0,

                    FOREIGN KEY (id_applicant)
                        REFERENCES Applicant(id_applicant)
                        ON DELETE CASCADE ON UPDATE NO ACTION,

                    FOREIGN KEY (id_source)
                        REFERENCES Information_source(id_source)
                        ON DELETE SET NULL ON UPDATE CASCADE
                )
            """)

            # Таблица связи Applicant_benefit
            # ИСПРАВЛЕНО: Убраны каскадные UPDATE для избежания циклических зависимостей
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Applicant_benefit' AND xtype='U')
                CREATE TABLE Applicant_benefit (
                    id_applicant INT,
                    id_benefit INT,
                    PRIMARY KEY (id_applicant, id_benefit),

                    FOREIGN KEY (id_applicant)
                        REFERENCES Applicant(id_applicant)
                        ON DELETE CASCADE ON UPDATE NO ACTION,

                    FOREIGN KEY (id_benefit)
                        REFERENCES Benefit(id_benefit)
                        ON DELETE CASCADE ON UPDATE NO ACTION
                )
            """)

            self.connection.commit()
            self.logger.info("Структура БД успешно создана с каскадными связями")

        except pyodbc.Error as e:
            self.logger.error(f"Ошибка создания структуры БД: {e}")
            self.connection.rollback()
            raise

    def initialize_reference_data(self):
        """Инициализация справочных данных (льготы, источники информации, формы обучения)"""
        try:
            cursor = self.connection.cursor()

            # Инициализация льгот с баллами
            benefits_data = [
                ("Без льгот", 0),
                ("Сирота", 10),
                ("Инвалид I группы", 10),
                ("Инвалид II группы", 8),
                ("Инвалид III группы", 5),
                ("Участник СВО", 10),
                ("Ребенок участника СВО", 8),
                ("Ребенок погибшего участника СВО", 10),
                ("Многодетная семья", 3),
                ("Целевое обучение", 5),
                ("Отличник (аттестат с отличием)", 5),
                ("Золотая медаль", 10),
                ("Серебряная медаль", 7),
                ("Победитель олимпиады (всероссийская)", 10),
                ("Призер олимпиады (всероссийская)", 8),
                ("Победитель олимпиады (региональная)", 5),
                ("Призер олимпиады (региональная)", 3),
                ("ГТО (золотой знак)", 5),
                ("ГТО (серебряный знак)", 3),
                ("ГТО (бронзовый знак)", 2),
                ("Волонтер (более 100 часов)", 3),
                ("Спортивные достижения (КМС и выше)", 5),
                ("Творческие достижения (лауреат)", 3)
            ]

            for benefit_name, bonus_points in benefits_data:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Benefit WHERE name_benefit = ?)
                    BEGIN
                        INSERT INTO Benefit (name_benefit, bonus_points) VALUES (?, ?)
                    END
                    ELSE
                    BEGIN
                        UPDATE Benefit SET bonus_points = ? WHERE name_benefit = ?
                    END
                """, (benefit_name, benefit_name, bonus_points, bonus_points, benefit_name))

            # Инициализация источников информации
            info_sources = [
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

            for source in info_sources:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Information_source WHERE name_source = ?)
                    BEGIN
                        INSERT INTO Information_source (name_source) VALUES (?)
                    END
                """, (source, source))

            self.connection.commit()
            self.logger.info("Справочные данные успешно инициализированы")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации справочных данных: {e}")
            self.connection.rollback()

    def get_or_create_region(self, region_name: str) -> int:
        """Получить ID региона или создать новый"""
        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT id_region FROM Region WHERE name_region = ?",
            (region_name,)
        )
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute("SELECT ISNULL(MAX(id_region), 0) + 1 FROM Region")
        id_region = cursor.fetchone()[0]

        cursor.execute("""
            SET IDENTITY_INSERT Region ON;
            INSERT INTO Region (id_region, name_region) VALUES (?, ?);
            SET IDENTITY_INSERT Region OFF;
        """, (id_region, region_name))

        self.connection.commit()
        return id_region

    def get_or_create_city(self, city_name: str, region_name: str) -> int:
        """Получить ID города или создать новый"""
        cursor = self.connection.cursor()

        # Получаем или создаем регион
        id_region = self.get_or_create_region(region_name)

        # Проверяем существование города в этом регионе
        cursor.execute("""
                       SELECT id_city
                       FROM City
                       WHERE name_city = ?
                         AND id_region = ?
                       """, (city_name, id_region))
        row = cursor.fetchone()

        if row:
            return row[0]

        # Создаем новый город
        cursor.execute("""
                       INSERT INTO City (name_city, id_region)
                       VALUES (?, ?)
                       """, (city_name, id_region))

        self.connection.commit()

        cursor.execute("SELECT @@IDENTITY")
        return int(cursor.fetchone()[0])

    def initialize_regions_and_cities(self):
        """Инициализация основных регионов и городов"""
        try:
            cursor = self.connection.cursor()

            # ДОБАВЛЕНО: Проверяем существование таблиц перед использованием
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Region' AND xtype='U')
                BEGIN
                    RAISERROR('Таблица Region не существует', 16, 1)
                    RETURN
                END
            """)

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='City' AND xtype='U')
                BEGIN
                    RAISERROR('Таблица City не существует', 16, 1)
                    RETURN
                END
            """)

            # Основные регионы с их городами
            regions_cities = {
                "Донецкая народная республика": [
                    "Донецк", "Макеевка", "Горловка", "Енакиево", "Харцызск",
                    "Дебальцево", "Шахтерск", "Ясиноватая", "Снежное", "Тельманово"
                ],
                "Луганская народная республика": [
                    "Луганск", "Алчевск", "Антрацит", "Брянка", "Красный Луч",
                    "Первомайск", "Ровеньки", "Стаханов", "Свердловск", "Краснодон"
                ],
                "Херсонская область": [
                    "Херсон", "Каховка", "Новая Каховка", "Скадовск", "Голая Пристань",
                    "Берислав", "Геническ", "Таврийск"
                ],
                "Запорожская область": [
                    "Запорожье", "Мелитополь", "Бердянск", "Энергодар", "Токмак",
                    "Васильевка", "Орехов", "Приморск", "Пологи"
                ],
                "Ростовская область": [
                    "Ростов-на-Дону", "Таганрог", "Шахты", "Новочеркасск", "Волгодонск",
                    "Новошахтинск", "Каменск-Шахтинский", "Азов", "Батайск", "Гуково"
                ]
            }

            for region_name, cities in regions_cities.items():
                # Проверяем существование региона
                cursor.execute("""
                               SELECT id_region
                               FROM Region
                               WHERE name_region = ?
                               """, (region_name,))
                row = cursor.fetchone()

                if not row:
                    # Создаем регион
                    cursor.execute("""
                                   INSERT INTO Region (name_region)
                                   VALUES (?)
                                   """, (region_name,))
                    cursor.execute("SELECT @@IDENTITY")
                    id_region = cursor.fetchone()[0]
                    self.logger.info(f"Создан регион: {region_name} (ID: {id_region})")
                else:
                    id_region = row[0]

                # Добавляем города для этого региона
                for city_name in cities:
                    cursor.execute("""
                        IF NOT EXISTS (SELECT 1 FROM City WHERE name_city = ? AND id_region = ?)
                        BEGIN
                            INSERT INTO City (name_city, id_region) VALUES (?, ?)
                        END
                    """, (city_name, id_region, city_name, id_region))

            self.connection.commit()
            self.logger.info("Регионы и города успешно инициализированы")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации регионов и городов: {e}")
            self.connection.rollback()

    def get_all_regions(self):
        """Получить все регионы из БД"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name_region FROM Region ORDER BY name_region")
            return [row.name_region for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Ошибка получения регионов: {e}")
            return []

    def get_cities_by_region(self, region_name: str):
        """Получить города по региону"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                           SELECT c.name_city
                           FROM City c
                                    JOIN Region r ON c.id_region = r.id_region
                           WHERE r.name_region = ?
                           ORDER BY c.name_city
                           """, (region_name,))
            return [row.name_city for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Ошибка получения городов: {e}")
            return []

    def get_or_create_education(self, institution_name: str, city_name: str, region_name: str) -> int:
        """Получить ID учебного заведения или создать новое с привязкой к городу"""
        cursor = self.connection.cursor()

        # Получаем id_city
        id_city = self.get_or_create_city(city_name, region_name)

        # Ищем существующую школу в этом городе
        cursor.execute("""
                       SELECT id_education
                       FROM Education
                       WHERE name_education = ?
                         AND id_city = ?
                       """, (institution_name, id_city))
        row = cursor.fetchone()

        if row:
            return row[0]

        # Создаем новую запись
        cursor.execute("""
                       INSERT INTO Education (name_education, id_city)
                       VALUES (?, ?)
                       """, (institution_name, id_city))

        self.connection.commit()

        cursor.execute("SELECT @@IDENTITY")
        return int(cursor.fetchone()[0])

    def get_all_benefits(self):
        """Получить все льготы с баллами из БД"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name_benefit, bonus_points FROM Benefit ORDER BY name_benefit")
            return {row.name_benefit: row.bonus_points for row in cursor.fetchall()}
        except Exception as e:
            self.logger.error(f"Ошибка получения льгот: {e}")
            return {}

    def get_all_information_sources(self):
        """Получить все источники информации из БД"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name_source FROM Information_source ORDER BY name_source")
            return [row.name_source for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Ошибка получения источников информации: {e}")
            return []

    def get_benefit_points(self, benefit_name: str) -> int:
        """Получить баллы за конкретную льготу"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT bonus_points FROM Benefit WHERE name_benefit = ?", (benefit_name,))
            row = cursor.fetchone()
            return row.bonus_points if row else 0
        except Exception as e:
            self.logger.error(f"Ошибка получения баллов льготы: {e}")
            return 0

    def get_or_create_benefit(self, benefit_name: str, bonus_points: int = 0) -> int:
        """Получить ID льготы или создать новую"""
        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT id_benefit, bonus_points FROM Benefit WHERE name_benefit = ?",
            (benefit_name,)
        )
        row = cursor.fetchone()

        if row:
            # Если баллы изменились, обновляем их
            if row.bonus_points != bonus_points:
                cursor.execute("""
                               UPDATE Benefit
                               SET bonus_points = ?
                               WHERE id_benefit = ?
                               """, (bonus_points, row.id_benefit))
                self.connection.commit()
            return row.id_benefit

        # Создаем новую льготу (без ручного управления IDENTITY)
        cursor.execute("""
                       INSERT INTO Benefit (name_benefit, bonus_points)
                       VALUES (?, ?);
                       """, (benefit_name, bonus_points))

        self.connection.commit()

        # Получаем назначенный ID
        cursor.execute("SELECT @@IDENTITY")
        return int(cursor.fetchone()[0])

    def get_or_create_information_source(self, source_name: str) -> Optional[int]:
        """Получить ID источника информации или создать новый"""
        if not source_name:
            return None

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT id_source FROM Information_source WHERE name_source = ?",
            (source_name,)
        )
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute("SELECT ISNULL(MAX(id_source), 0) + 1 FROM Information_source")
        id_source = cursor.fetchone()[0]

        cursor.execute("""
            SET IDENTITY_INSERT Information_source ON;
            INSERT INTO Information_source (id_source, name_source) VALUES (?, ?);
            SET IDENTITY_INSERT Information_source OFF;
        """, (id_source, source_name))

        self.connection.commit()
        return id_source

    def add_parent(self, parent: Parent) -> int:
        """Добавить родителя в БД"""
        cursor = self.connection.cursor()

        cursor.execute("SELECT ISNULL(MAX(id_parent), 0) + 1 FROM Parent")
        id_parent = cursor.fetchone()[0]

        cursor.execute("""
            SET IDENTITY_INSERT Parent ON;
            INSERT INTO Parent (id_parent, name, phone, relation)
            VALUES (?, ?, ?, ?);
            SET IDENTITY_INSERT Parent OFF;
        """, (id_parent, parent.parent_name, parent.phone,
              parent.relation if hasattr(parent, 'relation') else "Родитель"))

        self.connection.commit()
        return id_parent

    def add_applicant(self, applicant: Applicant) -> int:
        """Добавить абитуриента в БД"""
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT ISNULL(MAX(id_applicant), 0) + 1 FROM Applicant")
            id_applicant = cursor.fetchone()[0]

            # ИЗМЕНЕНО: Получаем id_education с привязкой к городу
            id_education = self.get_or_create_education(
                applicant.education.institution,
                applicant.city,
                applicant.region
            )

            id_parent = None
            if applicant.parent:
                id_parent = self.add_parent(applicant.parent)

            id_city = self.get_or_create_city(applicant.city, applicant.region)

            # ИЗМЕНЕНО: Удален id_education из Applicant
            cursor.execute("""
                SET IDENTITY_INSERT Applicant ON;
                INSERT INTO Applicant (id_applicant, last_name, first_name, patronymic, id_city, phone, vk, id_parent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                SET IDENTITY_INSERT Applicant OFF;
            """, (id_applicant, applicant.last_name, applicant.first_name, applicant.patronymic,
                  id_city, applicant.phone, applicant.contact_info.vk, id_parent))

            self.connection.commit()

            # Вычисляем итоговый рейтинг
            benefit_points = 0
            if applicant.application_details.benefits:
                benefit_points = self.get_benefit_points(applicant.application_details.benefits)

            total_rating = applicant.application_details.rating + benefit_points

            # ИЗМЕНЕНО: Добавлен id_education в Application_details
            cursor.execute("""
                           INSERT INTO Application_details (id_applicant, code, rating, has_original, submission_date)
                           VALUES (?, ?, ?, ?, ?)
                           """, (id_applicant, applicant.application_details.code, total_rating,
                                 applicant.application_details.has_original,
                                 applicant.application_details.submission_date))

            self.connection.commit()

            if applicant.application_details.benefits:
                id_benefit = self.get_or_create_benefit(
                    applicant.application_details.benefits,
                    applicant.application_details.bonus_points
                )
                cursor.execute("""
                               INSERT INTO Applicant_benefit (id_applicant, id_benefit)
                               VALUES (?, ?)
                               """, (id_applicant, id_benefit))

            id_source = self.get_or_create_information_source(
                applicant.additional_info.information_source
            )

            cursor.execute("""
                           INSERT INTO Additional_info (id_applicant, department_visit, notes, id_source, dormitory_needed)
                           VALUES (?, ?, ?, ?, ?)
                           """, (id_applicant, applicant.additional_info.department_visit,
                                 applicant.additional_info.notes, id_source,
                                 applicant.additional_info.dormitory_needed))

            cursor.execute("SELECT @@IDENTITY")
            id_info = cursor.fetchone()[0]

            cursor.execute("SELECT id_details FROM Application_details WHERE id_applicant = ?", (id_applicant,))
            id_details = cursor.fetchone()[0]

            cursor.execute("""
                           UPDATE Applicant
                           SET id_details = ?,
                               id_info    = ?
                           WHERE id_applicant = ?
                           """, (id_details, id_info, id_applicant))

            self.connection.commit()

            self.logger.info(f"Абитуриент {applicant.get_full_name()} успешно добавлен в БД (ID: {id_applicant})")
            return id_applicant

        except pyodbc.Error as e:
            self.logger.error(f"Ошибка добавления абитуриента в БД: {e}")
            self.connection.rollback()
            raise

    def update_applicant(self, applicant: Applicant) -> bool:
        """Обновить данные абитуриента в БД"""
        try:
            cursor = self.connection.cursor()

            id_applicant = int(applicant.application_details.number)

            base_rating = applicant.application_details.rating

            new_bonus_points = 0
            if applicant.application_details.benefits:
                new_bonus_points = self.get_benefit_points(applicant.application_details.benefits)

            total_rating = base_rating + new_bonus_points

            # ИЗМЕНЕНО: Получаем id_education с привязкой к городу
            id_education = self.get_or_create_education(
                applicant.education.institution,
                applicant.city,
                applicant.region
            )

            id_city = self.get_or_create_city(applicant.city, applicant.region)

            # Обработка родителя
            id_parent = None
            if applicant.parent:
                cursor.execute("""
                               SELECT id_parent
                               FROM Applicant
                               WHERE id_applicant = ?
                               """, (id_applicant,))
                row = cursor.fetchone()

                if row and row[0]:
                    id_parent = row[0]
                    cursor.execute("""
                                   UPDATE Parent
                                   SET name     = ?,
                                       phone    = ?,
                                       relation = ?
                                   WHERE id_parent = ?
                                   """, (applicant.parent.parent_name, applicant.parent.phone,
                                         applicant.parent.relation if hasattr(applicant.parent,
                                                                              'relation') else "Родитель",
                                         id_parent))
                else:
                    id_parent = self.add_parent(applicant.parent)

            # ИЗМЕНЕНО: Удален id_education из UPDATE Applicant
            cursor.execute("""
                           UPDATE Applicant
                           SET last_name  = ?,
                               first_name = ?,
                               patronymic = ?,
                               id_city    = ?,
                               phone      = ?,
                               vk         = ?,
                               id_parent  = ?
                           WHERE id_applicant = ?
                           """, (applicant.last_name, applicant.first_name, applicant.patronymic,
                                 id_city, applicant.phone, applicant.contact_info.vk,
                                 id_parent, id_applicant))

            # ИЗМЕНЕНО: Добавлен id_education в UPDATE Application_details
            cursor.execute("""
                           UPDATE Application_details
                           SET code            = ?,
                               rating          = ?,
                               has_original    = ?,
                               submission_date = ?
                           WHERE id_applicant = ?
                           """, (applicant.application_details.code, total_rating,
                                 applicant.application_details.has_original,
                                 applicant.application_details.submission_date, id_applicant))

            # Обновляем связь с льготами
            cursor.execute("DELETE FROM Applicant_benefit WHERE id_applicant = ?", (id_applicant,))

            if applicant.application_details.benefits:
                id_benefit = self.get_or_create_benefit(
                    applicant.application_details.benefits,
                    new_bonus_points
                )
                cursor.execute("""
                               INSERT INTO Applicant_benefit (id_applicant, id_benefit)
                               VALUES (?, ?)
                               """, (id_applicant, id_benefit))

            id_source = self.get_or_create_information_source(
                applicant.additional_info.information_source
            )

            cursor.execute("""
                           UPDATE Additional_info
                           SET department_visit = ?,
                               notes            = ?,
                               id_source        = ?,
                               dormitory_needed = ?
                           WHERE id_applicant = ?
                           """, (applicant.additional_info.department_visit,
                                 applicant.additional_info.notes,
                                 id_source,
                                 applicant.additional_info.dormitory_needed,
                                 id_applicant))

            self.connection.commit()
            self.logger.info(f"Абитуриент {applicant.get_full_name()} успешно обновлен в БД (ID: {id_applicant})")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления абитуриента в БД: {e}")
            self.connection.rollback()
            raise

    def load_all_applicants(self) -> List[Applicant]:
        """Загрузить всех абитуриентов из БД"""
        try:
            cursor = self.connection.cursor()

            # ИСПРАВЛЕНО: Убираем JOIN Education, так как он создаёт дубликаты
            cursor.execute("""
                           SELECT a.id_applicant,
                                  a.last_name,
                                  a.first_name,
                                  a.patronymic,
                                  c.id_city,
                                  c.name_city,
                                  r.name_region,
                                  a.phone,
                                  a.vk,
                                  ad.code,
                                  ad.rating,
                                  ad.has_original,
                                  ad.submission_date,
                                  b.name_benefit,
                                  b.bonus_points,
                                  ai.department_visit,
                                  ai.notes,
                                  ai.dormitory_needed,
                                  isrc.name_source,
                                  p.name     as parent_name,
                                  p.phone    as parent_phone,
                                  p.relation as parent_relation
                           FROM Applicant a
                                    LEFT JOIN City c ON a.id_city = c.id_city
                                    LEFT JOIN Region r ON c.id_region = r.id_region
                                    LEFT JOIN Application_details ad ON a.id_applicant = ad.id_applicant
                                    LEFT JOIN Additional_info ai ON a.id_applicant = ai.id_applicant
                                    LEFT JOIN Information_source isrc ON ai.id_source = isrc.id_source
                                    LEFT JOIN Parent p ON a.id_parent = p.id_parent
                                    LEFT JOIN Applicant_benefit ab ON a.id_applicant = ab.id_applicant
                                    LEFT JOIN Benefit b ON ab.id_benefit = b.id_benefit
                           """)

            rows = cursor.fetchall()
            self.logger.info(f"Получено {len(rows)} строк из БД")

            # ИСПРАВЛЕНО: Группируем данные по id_applicant
            applicants_dict = {}

            for row in rows:
                try:
                    id_applicant = row.id_applicant

                    # Если абитуриент уже обработан, пропускаем
                    if id_applicant in applicants_dict:
                        continue

                    # Получаем название учебного заведения по id_city
                    institution_name = ""
                    if row.id_city:
                        cursor.execute("""
                                       SELECT TOP 1 e.name_education
                                       FROM Education e
                                       WHERE e.id_city = ?
                                       ORDER BY e.id_education
                                       """, (row.id_city,))
                        education_row = cursor.fetchone()
                        institution_name = education_row.name_education if education_row else ""

                    education = EducationalBackground(institution=institution_name)

                    contact_info = ContactInfo(phone=row.phone or "", vk=row.vk)

                    base_rating = (row.rating or 0.0) - (row.bonus_points or 0)

                    application_details = ApplicationDetails(
                        number=str(id_applicant),
                        code=row.code or "",
                        rating=base_rating,
                        has_original=row.has_original or False,
                        benefits=row.name_benefit,
                        submission_date=row.submission_date,
                        form_of_education="Очная",
                        bonus_points=row.bonus_points or 0
                    )

                    additional_info = AdditionalInfo(
                        department_visit=row.department_visit,
                        notes=row.notes,
                        information_source=row.name_source,
                        dormitory_needed=row.dormitory_needed or False
                    )

                    parent = None
                    if row.parent_name:
                        parent = Parent(
                            parent_name=row.parent_name,
                            phone=row.parent_phone or "",
                            relation=row.parent_relation or "Родитель"
                        )

                    applicant = Applicant(
                        last_name=row.last_name,
                        first_name=row.first_name,
                        patronymic=row.patronymic,
                        phone=row.phone or "",
                        city=row.name_city or "",
                        application_details=application_details,
                        education=education,
                        contact_info=contact_info,
                        additional_info=additional_info,
                        parent=parent,
                        region=row.name_region or ""
                    )

                    applicants_dict[id_applicant] = applicant

                except Exception as e:
                    self.logger.error(f"Ошибка обработки строки с id_applicant={row.id_applicant}: {e}")
                    continue

            applicants = list(applicants_dict.values())
            self.logger.info(f"Успешно загружено {len(applicants)} абитуриентов из БД")
            return applicants

        except pyodbc.Error as e:
            self.logger.error(f"Ошибка загрузки абитуриентов из БД: {e}")
            return []