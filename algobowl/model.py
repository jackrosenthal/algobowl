import enum
import datetime
import flask_sqlalchemy
from depot.fields.sqlalchemy import UploadedFileField

db = flask_sqlalchemy.SQLAlchemy()


class VerificationStatus(enum.Enum):
    waiting = 0
    accepted = 1
    rejected = 2


class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    input_verifier_code = db.Column(db.Unicode, nullable=False, default='')
    output_verifier_code = db.Column(db.Unicode)
    problem_statement = db.Column(UploadedFileField, nullable=True)
    allow_custom_team_names = db.Column(db.Boolean, default=True)

    input_upload_begins = db.Column(db.DateTime, nullable=False)
    input_upload_ends = db.Column(
        db.DateTime,
        db.CheckConstraint('input_upload_ends > input_upload_begins'),
        nullable=False)
    output_upload_begins = db.Column(
        db.DateTime,
        db.CheckConstraint('output_upload_begins > input_upload_ends'),
        nullable=False)
    output_upload_ends = db.Column(
        db.DateTime,
        db.CheckConstraint('output_upload_ends > output_upload_begins'),
        nullable=False)
    verification_begins = db.Column(
        db.DateTime,
        db.CheckConstraint('verification_begins > output_upload_ends'),
        nullable=True)
    verification_ends = db.Column(
        db.DateTime,
        db.CheckConstraint('verification_ends > verification_begins'),
        nullable=True)
    open_verification_begins = db.Column(
        db.DateTime,
        db.CheckConstraint('open_verification_begins > verification_ends'),
        nullable=True)
    open_verification_ends = db.Column(
        db.DateTime,
        db.CheckConstraint(
            'open_verification_ends > open_verification_begins'),
        nullable=True)
    evaluation_begins = db.Column(db.DateTime, nullable=True)
    evaluation_ends = db.Column(
        db.DateTime,
        db.CheckConstraint('evaluation_ends > evaluation_begins'),
        nullable=True)

    groups = db.relationship("Group", back_populates="competition")
    evaluations = db.relationship(
        "Evaluation",
        back_populates="competition")

    @property
    def input_upload_open(self):
        return (self.input_upload_begins
                <= datetime.datetime.now()
                < self.input_upload_ends)

    @property
    def output_upload_open(self):
        return (self.output_upload_begins
                <= datetime.datetime.now()
                < self.output_upload_ends)

    @property
    def verification_open(self):
        return (self.verification_begins
                and (self.verification_begins
                     <= datetime.datetime.now()
                     < self.verification_ends))

    @property
    def open_verification_open(self):
        return (self.open_verification_begins
                and (self.open_verification_begins
                     <= datetime.datetime.now()
                     < self.open_verification_ends))

    @property
    def evaluation_open(self):
        return (self.evaluation_begins
                and (self.evaluation_begins
                     <= datetime.datetime.now()
                     < self.evaluation_ends))

    @property
    def active(self):
        return (self.input_upload_begins
                <= datetime.datetime.now()
                < max(filter(lambda x: x, (
                    self.output_upload_ends,
                    self.verification_ends,
                    self.open_verification_ends,
                    self.evaluation_ends))))

    def __repr__(self):
        return self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode, unique=True, nullable=False)
    email = db.Column(db.Unicode, unique=True, nullable=False)
    full_name = db.Column(db.Unicode)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    submitted_evaluations = db.relationship(
        "Evaluation",
        back_populates="from_student",
        foreign_keys="Evaluation.from_student_id")
    received_evaluations = db.relationship(
        "Evaluation",
        back_populates="to_student",
        foreign_keys="Evaluation.to_student_id")

    submitted_protests = db.relationship(
        "VerificationProtest",
        back_populates="submitter")

    groups = db.relation(
        'Group', secondary='user_group_xref', back_populates='users')

    @property
    def is_authenticated(self) -> bool:
        """
        Return ``True`` if the user is authenticated.
        """
        return True

    @property
    def is_active(self) -> bool:
        """
        Return ``True`` if the current user has been "activated".

        Potentially, subclasses may wish to override this.
        """
        return True

    @property
    def is_anonymous(self) -> bool:
        """
        Return ``True`` if the user is **not** authenticated.
        """
        return not self.is_authenticated

    def get_id(self) -> str:
        """
        Return a unique string for the user.
        """
        return self.username

    def __repr__(self):
        return self.full_name or self.username


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(100), nullable=False)
    penalty = db.Column(db.Integer, nullable=False, default=0)

    competition_id = db.Column(
        db.Integer,
        db.ForeignKey('competition.id'),
        nullable=False)
    competition = db.relationship("Competition", back_populates="groups")

    input = db.relationship("Input", uselist=False, back_populates="group")
    outputs = db.relationship("Output", back_populates="group")

    users = db.relation('User', secondary='user_group_xref',
                        back_populates='groups')

    def __repr__(self):
        if self.name:
            return "{} (Group {})".format(self.name, self.id)
        return "Group {}".format(self.id)


# N users can be a part of M groups
# ---------------------------------
# Why may a user be a part of M groups? Consider the case where a user
# fails the course, or a test account that was made part of many groups
# over time.
user_group_xref = db.Table('user_group_xref', db.metadata,
                           db.Column('user_id', db.Integer,
                                     db.ForeignKey('user.id',
                                                   onupdate="CASCADE",
                                                   ondelete="CASCADE"),
                                     primary_key=True),
                           db.Column('group_id', db.Integer,
                                     db.ForeignKey('group.id',
                                                   onupdate="CASCADE",
                                                   ondelete="CASCADE"),
                                     primary_key=True))


class Input(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(UploadedFileField, nullable=False)

    group_id = db.Column(
        db.Integer,
        db.ForeignKey('group.id'),
        nullable=False)
    group = db.relationship("Group", back_populates="input")

    outputs = db.relationship("Output", back_populates="input")

    def __repr__(self):
        return "Input from [{!r}]".format(self.group)


class Output(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # The score is separated from the data, allowing for database
    # server-side sorting
    score = db.Column(db.Numeric, nullable=False)
    data = db.Column(UploadedFileField, nullable=False)

    verification = db.Column(
        db.Enum(VerificationStatus),
        nullable=False,
        default=VerificationStatus.waiting)
    verification_reason = db.Column(db.Unicode(1000))

    input_id = db.Column(
        db.Integer,
        db.ForeignKey('input.id'),
        nullable=False)
    input = db.relationship("Input", back_populates="outputs")

    group_id = db.Column(
        db.Integer,
        db.ForeignKey('group.id'),
        nullable=False)
    group = db.relationship("Group", back_populates="outputs")

    protests = db.relationship("VerificationProtest", back_populates="output")

    def __repr__(self):
        return "Output from [{!r}] for {!r}".format(self.group, self.input)


class VerificationProtest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correction = db.Column(
        db.Enum(VerificationStatus),
        nullable=False)
    message = db.Column(db.Unicode(1000), nullable=False)

    submitter_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False)
    submitter = db.relationship("User", back_populates="submitted_protests")

    output_id = db.Column(
        db.Integer,
        db.ForeignKey('output.id'),
        nullable=False)
    output = db.relationship("Output", back_populates="protests")

    def __repr__(self):
        return "Protest {}, from [{!r}] on {!r}".format(
            self.id, self.submitter, self.output)


class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False)

    from_student_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False)
    from_student = db.relationship(
        "User",
        back_populates="submitted_evaluations",
        foreign_keys=from_student_id)

    to_student_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False)
    to_student = db.relationship(
        "User",
        back_populates="received_evaluations",
        foreign_keys=to_student_id)

    competition_id = db.Column(
        db.Integer,
        db.ForeignKey('competition.id'),
        nullable=False)
    competition = db.relationship(
        "Competition",
        back_populates="evaluations")
