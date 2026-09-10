from app import db
from datetime import datetime


class CrewMember(db.Model):
    """Imperial personnel record for Death Star crew."""

    __tablename__ = "crew_members"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imperial_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    rank = db.Column(db.String(64), default="Ensign")
    clearance_level = db.Column(db.Integer, default=1)
    department = db.Column(db.String(64))
    duty_station = db.Column(db.String(128))
    homeworld = db.Column(db.String(64))
    species = db.Column(db.String(64), default="Human")
    midichlorian_count = db.Column(db.Integer, default=0)
    medical_records = db.Column(db.Text)
    bank_account = db.Column(db.String(64))
    comm_frequency = db.Column(db.String(32))
    password_hash = db.Column(db.String(256))
    email = db.Column(db.String(128))
    quarters_assignment = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(32), default="crew")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "imperial_id": self.imperial_id,
            "name": self.name,
            "rank": self.rank,
            "clearance_level": self.clearance_level,
            "department": self.department,
            "duty_station": self.duty_station,
            "homeworld": self.homeworld,
            "species": self.species,
            "midichlorian_count": self.midichlorian_count,
            "medical_records": self.medical_records,
            "bank_account": self.bank_account,
            "comm_frequency": self.comm_frequency,
            "email": self.email,
            "quarters_assignment": self.quarters_assignment,
            "is_active": self.is_active,
            "role": self.role,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    def __repr__(self):
        return f"<CrewMember {self.imperial_id}: {self.name}>"


class DutyAssignment(db.Model):
    """Shift and duty assignment records."""

    __tablename__ = "duty_assignments"

    id = db.Column(db.Integer, primary_key=True)
    crew_member_id = db.Column(db.Integer, db.ForeignKey("crew_members.id"))
    station = db.Column(db.String(128))
    shift_start = db.Column(db.DateTime)
    shift_end = db.Column(db.DateTime)
    sector = db.Column(db.String(32))
    notes = db.Column(db.Text)

    crew_member = db.relationship("CrewMember", backref="assignments")


class AuditLog(db.Model):
    """Audit trail for personnel actions."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(64))
    target_id = db.Column(db.Integer)
    performed_by = db.Column(db.String(128))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
