# app/models/__init__.py
# Import order matters: tables with no foreign keys first, then dependents.

from app.models.enums import (
    StaffRole, ClearanceLevel, SkillRating, AttendanceStatus, InfractionSeverity,
    TermName, TransportDirection, ParentRelationship, DocumentCategory,
    FeeCategory, PaymentMethod,
)
from app.models.team import Team
from app.models.skill import Skill
from app.models.academic_level import AcademicLevel
from app.models.club import Club, StudentClub
from app.models.academic_year import AcademicYear
from app.models.route import Route
from app.models.term import Term
from app.models.class_ import SchoolClass
# SiblingGroup must be imported BEFORE Student because Student has sibling_group_id FK
from app.models.sibling_group import SiblingGroup
from app.models.student import Student
from app.models.parent_guardian import ParentGuardian      # legacy
from app.models.medical import MedicalHistory              # legacy
from app.models.attendance import Attendance
from app.models.student_supply import StudentSupply
from app.models.skill_assessment import SkillAssessment
from app.models.termly_report_comment import TermlyReportComment
from app.models.discipline import DisciplinaryLog
from app.models.previous_education import PreviousEducation
from app.models.medical_information import MedicalInformation
from app.models.parent_info import ParentInfo
from app.models.document import Document
from app.models.student_route import StudentRoute
# Finance module models
from app.models.fee_item import FeeItem
from app.models.fee_schedule import FeeSchedule
from app.models.student_fee import StudentFee
from app.models.payment import Payment
from app.models.payment_allocation import PaymentAllocation
