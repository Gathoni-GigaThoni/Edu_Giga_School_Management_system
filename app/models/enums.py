from enum import Enum

# Staff roles in the school
class StaffRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    MANAGER = "manager"
    TEACHER = "teacher"
    KITCHEN = "kitchen"
    UTILITY = "utility"

# Clearance levels: 1 is highest, 5 is lowest
class ClearanceLevel(int, Enum):
    LEVEL_1 = 1   # Super Admin – can do everything
    LEVEL_2 = 2   # Manager – can view all, edit most
    LEVEL_3 = 3   # Senior Teacher / Kitchen Manager
    LEVEL_4 = 4   # Teacher / Kitchen Staff – limited to own class/area
    LEVEL_5 = 5   # Utility – view only basic info

# Learning levels (our school's grade levels)
class LevelCode(str, Enum):
    BABY = "Acorn"          # Baby Class
    PLAYGROUP = "Willow"     # Playgroup
    PP1 = "Maple"        # Pre-Primary 1
    PP2 = "Oak"          # Pre-Primary 2

# Class sections (two per level)
class ClassSection(str, Enum):
    A = "A"
    B = "B"

# Houses – each level has its own house
class HouseName(str, Enum):
    SUNFLOWER = "Sunflower"   # Baby Class
    BLUEBELL = "Bluebell"     # Playgroup (Okra)
    DAFFODIL = "Daffodil"     # PP1 (Samaria)
    MARIGOLD = "Marigold"     # PP2 (Manna)

# Skill assessment ratings (instead of letter grades)
class SkillRating(str, Enum):
    EXCEEDING = "Exceeding Expectation"
    MEETING = "Meeting Expectation"
    APPROACHING = "Approaching Expectation"
    NEEDS_INTERVENTION = "Needs Intervention"

# Attendance statuses
class AttendanceStatus(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"

# Disciplinary infraction severity
class InfractionSeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
