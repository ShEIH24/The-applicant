"""classes.py"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import datetime

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
    def has_original_documents(self) -> bool:
        pass

    @abstractmethod
    def get_benefits(self) -> Optional[str]:
        pass


# Основные классы
class Person:
    def __init__(self, full_name: str, phone: str, city: str):
        self.full_name = full_name
        self.phone = phone
        self.city = city


class Parent(Person):
    def __init__(self, full_name: str, phone: str, city: str, relation: str = "Родитель"):
        super().__init__(full_name, phone, city)
        self.relation = relation


class EducationalBackground:
    def __init__(self, institution: str, graduation_year: Optional[int] = None, average_score: Optional[float] = None):
        self.institution = institution
        self.graduation_year = graduation_year
        self.average_score = average_score


class ContactInfo:
    def __init__(self, phone: str, vk: Optional[str] = None, email: Optional[str] = None):
        self.phone = phone
        self.vk = vk
        self.email = email


class ApplicationDetails:
    def __init__(self, code: str, rating: float, has_original: bool = False, benefits: Optional[str] = None):
        self.code = code
        self.rating = rating
        self.has_original = has_original
        self.benefits = benefits


class AdditionalInfo:
    def __init__(self,
                 department_visit: Optional[datetime] = None,
                 notes: Optional[str] = None,
                 information_source: Optional[str] = None,
                 dormitory_needed: bool = False):
        self.department_visit = department_visit
        self.notes = notes
        self.information_source = information_source
        self.dormitory_needed = dormitory_needed


class Applicant(Person, IPersonalData, IApplicationData):
    def __init__(self,
                 full_name: str,
                 phone: str,
                 city: str,
                 application_details: ApplicationDetails,
                 education: EducationalBackground,
                 contact_info: Optional[ContactInfo] = None,
                 additional_info: Optional[AdditionalInfo] = None,
                 parent: Optional[Parent] = None):
        super().__init__(full_name, phone, city)
        self.application_details = application_details
        self.education = education
        self.contact_info = contact_info or ContactInfo(phone)
        self.additional_info = additional_info or AdditionalInfo()
        self.parent = parent

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

    def has_original_documents(self) -> bool:
        return self.application_details.has_original

    def get_benefits(self) -> Optional[str]:
        return self.application_details.benefits


class ApplicantRegistry:
    def __init__(self):
        self.applicants: List[Applicant] = []

    def add_applicant(self, applicant: Applicant) -> None:
        self.applicants.append(applicant)

    def get_applicants_by_city(self, city: str) -> List[Applicant]:
        return [a for a in self.applicants if a.get_city().lower() == city.lower()]

    def get_dormitory_requests(self) -> List[Applicant]:
        return [a for a in self.applicants if a.additional_info.dormitory_needed]

    def get_dormitory_requests_by_city(self, city: str) -> List[Applicant]:
        return [a for a in self.applicants if a.get_city().lower() == city.lower() and a.additional_info.dormitory_needed]
