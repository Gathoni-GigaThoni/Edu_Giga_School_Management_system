from enum import Enum


class StaffRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    MANAGER = "manager"
    TEACHER = "teacher"
    KITCHEN = "kitchen"
    UTILITY = "utility"


# Clearance levels: 1 is highest, 5 is lowest
class ClearanceLevel(int, Enum):
    LEVEL_1 = 1   # Super Admin
    LEVEL_2 = 2   # Manager
    LEVEL_3 = 3   # Senior Teacher / Kitchen Manager
    LEVEL_4 = 4   # Teacher / Kitchen Staff
    LEVEL_5 = 5   # Utility


# Skill assessment ratings
class SkillRating(str, Enum):
    EXCEEDING = "Exceeding Expectation"
    MEETING = "Meeting Expectation"
    APPROACHING = "Approaching Expectation"
    NEEDS_INTERVENTION = "Needs Intervention"


class AttendanceStatus(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"


class InfractionSeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"


class TermName(str, Enum):
    TERM_1 = "Term 1"
    TERM_2 = "Term 2"
    TERM_3 = "Term 3"


class TransportDirection(str, Enum):
    ONE_WAY_MORNING = "one_way_morning"
    ONE_WAY_EVENING = "one_way_evening"
    TWO_WAY = "two_way"


class ParentRelationship(str, Enum):
    MOTHER = "mother"
    FATHER = "father"
    GUARDIAN = "guardian"


class DocumentCategory(str, Enum):
    PREVIOUS_EDUCATION = "previous_education"
    MEDICAL_ALLERGY = "medical_allergy"
    MEDICAL_CHRONIC = "medical_chronic"
    MEDICAL_VACCINATION = "medical_vaccination"
    PARENT_ID = "parent_id"
    OTHER = "other"
