from app.models.enums import ClearanceLevel

# Maps field keys (and "section" keys for whole-section gating) to the
# minimum ClearanceLevel whose *value* must be <= the user's clearance value.
# Lower value = higher privilege, so LEVEL_1 sees everything, LEVEL_5 sees least.
FIELD_PERMISSIONS: dict[str, ClearanceLevel] = {
    # ── Student basic fields ────────────────────────────────────────────────
    "id":               ClearanceLevel.LEVEL_5,
    "student_id":       ClearanceLevel.LEVEL_5,
    "first_name":       ClearanceLevel.LEVEL_5,
    "last_name":        ClearanceLevel.LEVEL_5,
    "level":            ClearanceLevel.LEVEL_5,
    "section":          ClearanceLevel.LEVEL_5,
    "house":            ClearanceLevel.LEVEL_5,
    "date_of_birth":    ClearanceLevel.LEVEL_4,
    "age_months":       ClearanceLevel.LEVEL_4,
    "gender":           ClearanceLevel.LEVEL_4,
    "enrollment_year":  ClearanceLevel.LEVEL_4,
    "transport_route":  ClearanceLevel.LEVEL_3,

    # ── Parents section ─────────────────────────────────────────────────────
    "parents":                      ClearanceLevel.LEVEL_4,
    "parents.id":                   ClearanceLevel.LEVEL_4,
    "parents.full_name":            ClearanceLevel.LEVEL_4,
    "parents.relationship":         ClearanceLevel.LEVEL_4,
    "parents.phone":                ClearanceLevel.LEVEL_4,
    "parents.is_emergency_contact": ClearanceLevel.LEVEL_4,
    "parents.email":                ClearanceLevel.LEVEL_3,
    "parents.address":              ClearanceLevel.LEVEL_3,

    # ── Medical section ─────────────────────────────────────────────────────
    "medical":              ClearanceLevel.LEVEL_3,
    "medical.allergies":    ClearanceLevel.LEVEL_3,
    "medical.medications":  ClearanceLevel.LEVEL_3,
    "medical.notes":        ClearanceLevel.LEVEL_3,
    "medical.doctor_name":  ClearanceLevel.LEVEL_2,
    "medical.doctor_phone": ClearanceLevel.LEVEL_2,

    # ── Attendance section ──────────────────────────────────────────────────
    "attendance":            ClearanceLevel.LEVEL_4,
    "attendance.total_days": ClearanceLevel.LEVEL_4,
    "attendance.present":    ClearanceLevel.LEVEL_4,
    "attendance.absent":     ClearanceLevel.LEVEL_4,
    "attendance.late":       ClearanceLevel.LEVEL_4,

    # ── Skill assessments section ───────────────────────────────────────────
    "assessments":                    ClearanceLevel.LEVEL_4,
    "assessments.skill_name":         ClearanceLevel.LEVEL_4,
    "assessments.rating":             ClearanceLevel.LEVEL_4,
    "assessments.assessment_date":    ClearanceLevel.LEVEL_4,
    "assessments.teacher_comment":    ClearanceLevel.LEVEL_4,

    # ── Discipline section ──────────────────────────────────────────────────
    "discipline":                    ClearanceLevel.LEVEL_3,
    "discipline.id":                 ClearanceLevel.LEVEL_3,
    "discipline.description":        ClearanceLevel.LEVEL_3,
    "discipline.severity":           ClearanceLevel.LEVEL_3,
    "discipline.incident_date":      ClearanceLevel.LEVEL_3,
    "discipline.is_resolved":        ClearanceLevel.LEVEL_3,
    "discipline.action_taken":       ClearanceLevel.LEVEL_2,
    "discipline.resolution_notes":   ClearanceLevel.LEVEL_2,

    # ── Supplies section ────────────────────────────────────────────────────
    "supplies":           ClearanceLevel.LEVEL_4,
    "supplies.id":        ClearanceLevel.LEVEL_4,
    "supplies.item_name": ClearanceLevel.LEVEL_4,
    "supplies.quantity":  ClearanceLevel.LEVEL_4,
    "supplies.term":      ClearanceLevel.LEVEL_4,
}
