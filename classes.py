from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date, datetime

# Интерфейсы
class IPersonalData(ABC):
    @abstractmethod
    def get_full_name(self) -> str:
        pass

    @abstractmethod
    def get_phone(self) -> str:
        pass

    @abstractmethod
    def get_city(self) -> str:
        pass


class IApplicationData(ABC):
    @abstractmethod
    def get_code(self) -> str:
        pass

    @abstractmethod
    def get_rating(self) -> float:
        pass

    @abstractmethod
    def get_number(self) -> str:
        pass

    @abstractmethod
    def has_original_documents(self) -> bool:
        pass

    @abstractmethod
    def get_benefits(self) -> Optional[str]:
        pass

# Основные классы
class Person:
    def __init__(self, full_name: str, phone: str, city: str = None):
        self.full_name = full_name
        self.phone = phone
        self.city = city


class Parent:
    def __init__(self, full_name: str, phone: str, relation: str = "Родитель"):
        self.full_name = full_name
        self.phone = phone
        self.relation = relation


class EducationalBackground:
    def __init__(self, institution: str):
        self.institution = institution

class ContactInfo:
    def __init__(self, phone: str, email: Optional[str] = None, vk: Optional[str] = None, nickname: Optional[str] = None):
        self.phone = phone
        self.email = email
        self.vk = vk
        self.nickname = nickname

class ApplicationDetails:
    def __init__(self, number: str, code: str, rating: float, has_original: bool = False,
                 benefits: Optional[str] = None, submission_date: date = None):
        self.number = number
        self.code = code
        self.rating = rating
        self.has_original = has_original
        self.benefits = benefits
        self.submission_date = submission_date

    def get_submission_date_formatted(self) -> str:
        """Возвращает дату подачи в формате ДД.ММ.ГГГГ"""
        if not self.submission_date:
            return ""
        # Обработка NaN (float('nan'))
        if isinstance(self.submission_date, float) and (self.submission_date != self.submission_date):  # NaN check
            return ""
        if isinstance(self.submission_date, (datetime, date)):
            return self.submission_date.strftime("%d.%m.%Y")
        elif isinstance(self.submission_date, str):
            # Попробуем распарсить строку, если это дата
            try:
                dt = datetime.strptime(self.submission_date.strip(), "%d.%m.%Y")
                return dt.strftime("%d.%m.%Y")
            except ValueError:
                return self.submission_date.strip()
        elif isinstance(self.submission_date, (int, float)):
            try:
                dt = datetime.fromtimestamp(self.submission_date)
                return dt.strftime("%d.%m.%Y")
            except (ValueError, OSError, OverflowError):
                return ""
        return str(self.submission_date)

class AdditionalInfo:
    def __init__(self,
                 department_visit: Optional[date] = None,
                 notes: Optional[str] = None,
                 information_source: Optional[str] = None,
                 dormitory_needed: bool = False):
        self.department_visit = department_visit
        self.notes = notes
        self.information_source = information_source
        self.dormitory_needed = dormitory_needed

    def get_department_visit_formatted(self) -> str:
        """Возвращает дату посещения в формате ДД.ММ.ГГГГ"""
        if self.department_visit:
            return self.department_visit.strftime("%d.%m.%Y")
        return ""


class ExamScores:
    def __init__(self, russian: int = 0, math: int = 0, informatics: int = 0):
        self._russian = self._validate_score(russian)
        self._math = self._validate_score(math)
        self._informatics = self._validate_score(informatics)

    @staticmethod
    def _validate_score(score: int) -> int:
        """Валидация оценки (должна быть от 0 до 100)"""
        if not isinstance(score, (int, float)):
            return 0
        score = int(score)
        return max(0, min(100, score))

    @property
    def russian(self) -> int:
        return self._russian

    @russian.setter
    def russian(self, value: int):
        self._russian = self._validate_score(value)

    @property
    def math(self) -> int:
        return self._math

    @math.setter
    def math(self, value: int):
        self._math = self._validate_score(value)

    @property
    def informatics(self) -> int:
        return self._informatics

    @informatics.setter
    def informatics(self, value: int):
        self._informatics = self._validate_score(value)

    def get_total_score(self) -> int:
        """Возвращает сумму всех баллов"""
        return self._russian + self._math + self._informatics

class Applicant(Person, IPersonalData, IApplicationData):
    def __init__(self,
                 full_name: str,
                 phone: str,
                 city: str,
                 application_details: ApplicationDetails,
                 education: EducationalBackground,
                 contact_info: Optional[ContactInfo] = None,
                 additional_info: Optional[AdditionalInfo] = None,
                 parent: Optional[Parent] = None,
                 exam_scores: Optional[ExamScores] = None):
        super().__init__(full_name, phone, city)
        self.application_details = application_details
        self.education = education
        self.contact_info = contact_info or ContactInfo(phone)
        self.additional_info = additional_info or AdditionalInfo()
        self.parent = parent
        self.exam_scores = exam_scores or ExamScores()

    # Реализация методов интерфейсов
    def get_full_name(self) -> str:
        return self.full_name

    def get_phone(self) -> str:
        return self.phone

    def get_city(self) -> str:
        return self.city

    def get_code(self) -> str:
        return self.application_details.code

    def get_rating(self) -> float:
        return self.application_details.rating

    def get_number(self) -> str:
        return self.application_details.number

    def has_original_documents(self) -> bool:
        return self.application_details.has_original

    def get_benefits(self) -> Optional[str]:
        return self.application_details.benefits

class ApplicantRegistry:
    def __init__(self):
        self.applicants: List[Applicant] = []
        self._last_number = 0  # Для отслеживания последнего присвоенного номера

    def add_applicant(self, applicant: Applicant) -> None:
        # Если номер не указан или пустой, назначаем следующий порядковый номер
        if not applicant.application_details.number or applicant.application_details.number.strip() == '':
            self._last_number += 1
            applicant.application_details.number = str(self._last_number)
        # Если номер уже существует (например, при импорте), обновляем _last_number
        elif applicant.application_details.number.isdigit():
            num = int(applicant.application_details.number)
            if num > self._last_number:
                self._last_number = num

        self.applicants.append(applicant)

    def renumber_all_applicants(self) -> None:
        """Перенумеровывает всех абитуриентов последовательно"""
        for i, applicant in enumerate(self.applicants, 1):
            applicant.application_details.number = str(i)
        self._last_number = len(self.applicants)

    def get_applicants_by_city(self, city: str) -> List[Applicant]:
        return [a for a in self.applicants if a.get_city().lower() == city.lower()]

    def get_dormitory_requests(self) -> List[Applicant]:
        return [a for a in self.applicants if a.additional_info.dormitory_needed]

    def get_dormitory_requests_by_city(self, city: str) -> List[Applicant]:
        return [a for a in self.applicants if a.get_city().lower() == city.lower() and a.additional_info.dormitory_needed]