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

            # Таблица Education
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Education' AND xtype='U')
                CREATE TABLE Education (
                    id_education INT IDENTITY(1,1) PRIMARY KEY,
                    name_education NVARCHAR(255) NOT NULL
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

            # Таблица Specialty
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Specialty' AND xtype='U')
                CREATE TABLE Specialty (
                    id_specialty INT IDENTITY(1,1) PRIMARY KEY,
                    name_specialty NVARCHAR(255) NOT NULL,
                    form_of_education NVARCHAR(255)
                )
            """)

            # Таблица Applicant
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Applicant' AND xtype='U')
                CREATE TABLE Applicant (
                    id_applicant INT IDENTITY(1,1) PRIMARY KEY,
                    last_name NVARCHAR(100) NOT NULL,
                    first_name NVARCHAR(100) NOT NULL,
                    patronymic NVARCHAR(100),
                    city NVARCHAR(100) NOT NULL,
                    phone NVARCHAR(20) NOT NULL,

                    id_education INT,
                    id_parent INT,
                    id_details INT,
                    id_info INT,

                    FOREIGN KEY (id_education)
                        REFERENCES Education(id_education)
                        ON DELETE SET NULL ON UPDATE CASCADE,

                    FOREIGN KEY (id_parent)
                        REFERENCES Parent(id_parent)
                        ON DELETE SET NULL ON UPDATE CASCADE
                )
            """)

            # Таблица Application_details
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Application_details' AND xtype='U')
                CREATE TABLE Application_details (
                    id_details INT IDENTITY(1,1) PRIMARY KEY,
                    id_applicant INT,
                    id_specialty INT,
                    rating FLOAT NOT NULL,
                    has_original BIT DEFAULT 0,
                    submission_date DATE,

                    FOREIGN KEY (id_applicant)
                        REFERENCES Applicant(id_applicant)
                        ON DELETE CASCADE ON UPDATE CASCADE,

                    FOREIGN KEY (id_specialty)
                        REFERENCES Specialty(id_specialty)
                        ON DELETE SET NULL ON UPDATE CASCADE
                )
            """)

            # Таблица Additional_info
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
                        ON DELETE CASCADE ON UPDATE CASCADE,

                    FOREIGN KEY (id_source)
                        REFERENCES Information_source(id_source)
                        ON DELETE SET NULL ON UPDATE CASCADE
                )
            """)

            # Таблица связи Applicant_benefit
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Applicant_benefit' AND xtype='U')
                CREATE TABLE Applicant_benefit (
                    id_applicant INT,
                    id_benefit INT,
                    PRIMARY KEY (id_applicant, id_benefit),

                    FOREIGN KEY (id_applicant)
                        REFERENCES Applicant(id_applicant)
                        ON DELETE CASCADE ON UPDATE CASCADE,

                    FOREIGN KEY (id_benefit)
                        REFERENCES Benefit(id_benefit)
                        ON DELETE CASCADE ON UPDATE CASCADE
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
                """, (benefit_name, benefit_name, bonus_points))

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

    def get_or_create_education(self, institution_name: str) -> int:
        """Получить ID учебного заведения или создать новое"""
        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT id_education FROM Education WHERE name_education = ?",
            (institution_name,)
        )
        row = cursor.fetchone()

        if row:
            return row[0]

        # ПРОСТО берем следующий ID
        cursor.execute("SELECT ISNULL(MAX(id_education), 0) + 1 FROM Education")
        id_education = cursor.fetchone()[0]

        cursor.execute("""
            SET IDENTITY_INSERT Education ON;
            INSERT INTO Education (id_education, name_education) VALUES (?, ?);
            SET IDENTITY_INSERT Education OFF;
        """, (id_education, institution_name))

        self.connection.commit()
        return id_education

    def get_or_create_specialty(self, code: str) -> int:
        """Получить ID специальности по коду или создать новую"""
        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT id_specialty FROM Specialty WHERE name_specialty = ?",
            (code,)
        )
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute("SELECT ISNULL(MAX(id_specialty), 0) + 1 FROM Specialty")
        id_specialty = cursor.fetchone()[0]

        cursor.execute("""
            SET IDENTITY_INSERT Specialty ON;
            INSERT INTO Specialty (id_specialty, name_specialty) VALUES (?, ?);
            SET IDENTITY_INSERT Specialty OFF;
        """, (id_specialty, code))

        self.connection.commit()
        return id_specialty

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
            "SELECT id_benefit FROM Benefit WHERE name_benefit = ?",
            (benefit_name,)
        )
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute("SELECT ISNULL(MAX(id_benefit), 0) + 1 FROM Benefit")
        id_benefit = cursor.fetchone()[0]

        cursor.execute("""
            SET IDENTITY_INSERT Benefit ON;
            INSERT INTO Benefit (id_benefit, name_benefit, bonus_points) VALUES (?, ?, ?);
            SET IDENTITY_INSERT Benefit OFF;
        """, (id_benefit, benefit_name, bonus_points))

        self.connection.commit()
        return id_benefit

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

            # ПРОСТО берем следующий ID
            cursor.execute("SELECT ISNULL(MAX(id_applicant), 0) + 1 FROM Applicant")
            id_applicant = cursor.fetchone()[0]

            last_name = applicant.last_name
            first_name = applicant.first_name
            patronymic = applicant.patronymic

            id_education = self.get_or_create_education(applicant.education.institution)

            id_parent = None
            if applicant.parent:
                id_parent = self.add_parent(applicant.parent)

            cursor.execute("""
                SET IDENTITY_INSERT Applicant ON;

                INSERT INTO Applicant (id_applicant, last_name, first_name, patronymic, city, phone, id_education, id_parent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);

                SET IDENTITY_INSERT Applicant OFF;
            """, (id_applicant, last_name, first_name, patronymic, applicant.city, applicant.phone,
                  id_education, id_parent))

            self.connection.commit()

            # Остальной код без изменений
            id_specialty = self.get_or_create_specialty(applicant.application_details.code)

            # === ДОБАВЛЕНО: вычисляем итоговый рейтинг ===
            benefit_points = 0
            if applicant.application_details.benefits:
                benefit_points = self.get_benefit_points(applicant.application_details.benefits)

            total_rating = applicant.application_details.rating + benefit_points

            # Вставка Application_details
            cursor.execute("""
                           INSERT INTO Application_details (id_applicant, id_specialty, rating, has_original, submission_date)
                           VALUES (?, ?, ?, ?, ?)
                           """, (id_applicant, id_specialty, total_rating,
                                 applicant.application_details.has_original,
                                 applicant.application_details.submission_date))

            self.connection.commit()

            if applicant.application_details.benefits:
                # ИЗМЕНЕНО: передаем баллы при создании льготы
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

    def load_all_applicants(self) -> List[Applicant]:
        """Загрузить всех абитуриентов из БД"""
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                           SELECT a.id_applicant,
                                  a.last_name,
                                  a.first_name,
                                  a.patronymic,
                                  a.city,
                                  a.phone,
                                  e.name_education,
                                  ad.rating,
                                  ad.has_original,
                                  ad.submission_date,
                                  s.name_specialty,
                                  b.name_benefit,
                                  ai.department_visit,
                                  ai.notes,
                                  ai.dormitory_needed,
                                  isrc.name_source,
                                  p.name     as parent_name,
                                  p.phone    as parent_phone,
                                  p.relation as parent_relation
                           FROM Applicant a
                                    LEFT JOIN Education e ON a.id_education = e.id_education
                                    LEFT JOIN Application_details ad ON a.id_details = ad.id_details
                                    LEFT JOIN Specialty s ON ad.id_specialty = s.id_specialty
                                    LEFT JOIN Additional_info ai ON a.id_info = ai.id_info
                                    LEFT JOIN Information_source isrc ON ai.id_source = isrc.id_source
                                    LEFT JOIN Parent p ON a.id_parent = p.id_parent
                                    LEFT JOIN Applicant_benefit ab ON a.id_applicant = ab.id_applicant
                                    LEFT JOIN Benefit b ON ab.id_benefit = b.id_benefit
                           """)

            applicants = []
            for row in cursor.fetchall():
                # Формируем полное имя
                full_name = f"{row.last_name} {row.first_name}"
                if row.patronymic:
                    full_name += f" {row.patronymic}"

                # Создаем объекты
                education = EducationalBackground(institution=row.name_education)

                contact_info = ContactInfo(phone=row.phone)

                application_details = ApplicationDetails(
                    number=str(row.id_applicant),
                    code=row.name_specialty or "",
                    rating=row.rating or 0.0,
                    has_original=row.has_original or False,
                    benefits=row.name_benefit,
                    submission_date=row.submission_date,

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
                        phone=row.parent_phone or ""
                    )

                applicant = Applicant(
                    last_name=row.last_name,
                    first_name=row.first_name,
                    patronymic=row.patronymic,
                    phone=row.phone,
                    city=row.city,
                    application_details=application_details,
                    education=education,
                    contact_info=contact_info,
                    additional_info=additional_info,
                    parent=parent
                )

                applicants.append(applicant)

            self.logger.info(f"Загружено {len(applicants)} абитуриентов из БД")
            return applicants

        except pyodbc.Error as e:
            self.logger.error(f"Ошибка загрузки абитуриентов из БД: {e}")
            return []