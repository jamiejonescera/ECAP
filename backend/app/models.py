from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# Create instances here
db = SQLAlchemy()
bcrypt = Bcrypt()

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    position_in_school = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    password_reset_token = db.Column(db.String(100), nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for JSON response"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'position_in_school': self.position_in_school,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'email_verified': self.email_verified
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

# Accreditation Model
class Accreditation(db.Model):
    __tablename__ = 'accreditations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    programs = db.relationship('Program', backref='accreditation', lazy=True, cascade='all, delete-orphan')
    members = db.relationship('AccreditationMember', backref='accreditation', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_accreditations', foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'creator_name': self.creator.name if self.creator else None
        }
    
    def __repr__(self):
        return f'<Accreditation {self.name} ({self.year})>'

# Program Model
class Program(db.Model):
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    accreditation_id = db.Column(db.Integer, db.ForeignKey('accreditations.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    areas = db.relationship('Area', backref='program', lazy=True, cascade='all, delete-orphan')
    progress_tracking = db.relationship('ProgressTracking', backref='program', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'accreditation_id': self.accreditation_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'accreditation_name': self.accreditation.name if self.accreditation else None
        }
    
    def __repr__(self):
        return f'<Program {self.name}>'

# Area Model
class Area(db.Model):
    __tablename__ = 'areas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    chairperson_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    parameters = db.relationship('Parameter', backref='area', lazy=True, cascade='all, delete-orphan')
    chairperson = db.relationship('User', backref='chaired_areas', foreign_keys=[chairperson_id])
    notifications = db.relationship('Notification', backref='related_area', foreign_keys='Notification.related_area_id')
    progress_tracking = db.relationship('ProgressTracking', backref='area', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'program_id': self.program_id,
            'chairperson_id': self.chairperson_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'program_name': self.program.name if self.program else None,
            'chairperson_name': self.chairperson.name if self.chairperson else None
        }
    
    def __repr__(self):
        return f'<Area {self.name}>'

# Parameter Model
class Parameter(db.Model):
    __tablename__ = 'parameters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    assigned_member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    assigned_member = db.relationship('User', backref='assigned_parameters', foreign_keys=[assigned_member_id])
    submissions = db.relationship('Submission', backref='parameter', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'area_id': self.area_id,
            'assigned_member_id': self.assigned_member_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'area_name': self.area.name if self.area else None,
            'assigned_member_name': self.assigned_member.name if self.assigned_member else None
        }
    
    def __repr__(self):
        return f'<Parameter {self.name}>'

# AccreditationMember Model (Many-to-Many)
class AccreditationMember(db.Model):
    __tablename__ = 'accreditation_members'
    
    id = db.Column(db.Integer, primary_key=True)
    accreditation_id = db.Column(db.Integer, db.ForeignKey('accreditations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='accreditation_memberships')
    added_by_user = db.relationship('User', foreign_keys=[added_by], backref='added_members')
    
    # Unique constraint to prevent duplicate memberships
    __table_args__ = (db.UniqueConstraint('accreditation_id', 'user_id', name='unique_accreditation_member'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'accreditation_id': self.accreditation_id,
            'user_id': self.user_id,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'is_active': self.is_active,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'added_by_name': self.added_by_user.name if self.added_by_user else None
        }
    
    def __repr__(self):
        return f'<AccreditationMember {self.user.email} in {self.accreditation.name}>'

# Submission Model
class Submission(db.Model):
    __tablename__ = 'submissions'
    
    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_APPROVED_BY_CHAIR = 'approved_by_chair'
    STATUS_REJECTED_BY_CHAIR = 'rejected_by_chair'
    STATUS_APPROVED_BY_ADMIN = 'approved_by_admin'
    STATUS_REJECTED_BY_ADMIN = 'rejected_by_admin'
    
    SUBMISSION_STATUSES = [
        STATUS_PENDING,
        STATUS_APPROVED_BY_CHAIR,
        STATUS_REJECTED_BY_CHAIR,
        STATUS_APPROVED_BY_ADMIN,
        STATUS_REJECTED_BY_ADMIN
    ]
    
    # File type constants
    FILE_TYPES = ['pdf', 'doc', 'docx', 'video', 'link']
    
    id = db.Column(db.Integer, primary_key=True)
    parameter_id = db.Column(db.Integer, db.ForeignKey('parameters.id'), nullable=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.Enum(*FILE_TYPES, name='file_type_enum'), nullable=True)
    website_link = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Enum(*SUBMISSION_STATUSES, name='submission_status_enum'), default=STATUS_PENDING)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    version = db.Column(db.Integer, default=1)
    
    # Relationships
    submitter = db.relationship('User', foreign_keys=[submitted_by], backref='submissions')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_submissions')
    notifications = db.relationship('Notification', backref='related_submission', foreign_keys='Notification.related_submission_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'parameter_id': self.parameter_id,
            'submitted_by': self.submitted_by,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'website_link': self.website_link,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': self.reviewed_by,
            'comments': self.comments,
            'version': self.version,
            'parameter_name': self.parameter.name if self.parameter else None,
            'submitter_name': self.submitter.name if self.submitter else None,
            'reviewer_name': self.reviewer.name if self.reviewer else None
        }
    
    def __repr__(self):
        return f'<Submission {self.id} - {self.status}>'

# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    # Notification type constants
    TYPE_ASSIGNMENT = 'assignment'
    TYPE_APPROVAL = 'approval'
    TYPE_REJECTION = 'rejection'
    TYPE_DEADLINE = 'deadline'
    TYPE_GENERAL = 'general'
    
    NOTIFICATION_TYPES = [
        TYPE_ASSIGNMENT,
        TYPE_APPROVAL,
        TYPE_REJECTION,
        TYPE_DEADLINE,
        TYPE_GENERAL
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(*NOTIFICATION_TYPES, name='notification_type_enum'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=True)
    related_area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='notifications', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'email_sent': self.email_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'related_submission_id': self.related_submission_id,
            'related_area_id': self.related_area_id,
            'user_name': self.user.name if self.user else None
        }
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        db.session.commit()
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.type}>'

# ProgressTracking Model
class ProgressTracking(db.Model):
    __tablename__ = 'progress_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=True)
    total_parameters = db.Column(db.Integer, nullable=False, default=0)
    completed_parameters = db.Column(db.Integer, nullable=False, default=0)
    progress_percentage = db.Column(db.Float, nullable=False, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_progress(self):
        """Calculate and update progress percentage"""
        if self.total_parameters > 0:
            self.progress_percentage = (self.completed_parameters / self.total_parameters) * 100
        else:
            self.progress_percentage = 0.0
        self.last_updated = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'program_id': self.program_id,
            'area_id': self.area_id,
            'total_parameters': self.total_parameters,
            'completed_parameters': self.completed_parameters,
            'progress_percentage': round(self.progress_percentage, 2),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'program_name': self.program.name if self.program else None,
            'area_name': self.area.name if self.area else None
        }
    
    def __repr__(self):
        return f'<ProgressTracking {self.id} - {self.progress_percentage}%>'