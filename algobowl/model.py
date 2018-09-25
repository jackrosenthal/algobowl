import enum
import datetime
import sqlalchemy as sa
from weakref import WeakValueDictionary
from types import ModuleType
from sqlalchemy.orm import relationship, relation
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from depot.io.utils import file_from_content
from depot.fields.upload import UploadedFile
from depot.fields.sqlalchemy import UploadedFileField

maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)
DeclarativeBase = declarative_base()
DeclarativeBase.query = DBSession.query_property()
metadata = DeclarativeBase.metadata


def init_model(engine):
    """
    Call me before using any of the tables or classes in the model.
    """
    DBSession.configure(bind=engine)
    return DBSession


class VerificationStatus(enum.Enum):
    waiting = 0
    accepted = 1
    rejected = 2


class UploadedPythonModule(UploadedFile):
    module_cache = WeakValueDictionary()

    def process_content(self, content, *args, **kwargs):
        mod = ModuleType('uploaded_module')
        content = file_from_content(content)
        content = content.read()
        exec(content.decode('utf-8'), mod.__dict__)
        self.ensure_module(mod)
        super().process_content(content, *args, **kwargs)
        UploadedPythonModule.module_cache[self['file_id']] = mod

    def ensure_module(self, module):
        """
        Overridden by subclasses to make assertions about
        the module's contents.
        """

    @property
    def module(self):
        mod = UploadedPythonModule.module_cache.get(self['file_id'])
        if mod is None:
            mod = ModuleType('uploaded_module')
            exec(self.file.read().decode('utf-8'), mod.__dict__)
            UploadedPythonModule.module_cache[self['file_id']] = mod
        return mod


class VerifierModule(UploadedPythonModule):
    def ensure_module(self, module):
        if not hasattr(module, 'VerificationError'):
            raise TypeError('Verifier must define VerificationError')
        if not hasattr(module, 'verify'):
            raise TypeError('Verifier must define veriy')
        if not hasattr(module.verify, '__call__'):
            raise TypeError('verify must be callable')


class Competition(DeclarativeBase):
    __tablename__ = 'competition'
    db_icon = 'fas fa-clipboard-list'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    input_verifier = sa.Column(
        UploadedFileField(upload_type=VerifierModule),
        nullable=False)
    output_verifier = sa.Column(
        UploadedFileField(upload_type=VerifierModule),
        nullable=False)

    problem_statement = sa.Column(UploadedFileField, nullable=True)
    allow_custom_team_names = sa.Column(sa.Boolean, default=True)

    input_upload_begins = sa.Column(sa.DateTime, nullable=False)
    input_upload_ends = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('input_upload_ends > input_upload_begins'),
        nullable=False)
    output_upload_begins = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('output_upload_begins >= input_upload_ends'),
        nullable=False)
    output_upload_ends = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('output_upload_ends > output_upload_begins'),
        nullable=False)
    verification_begins = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('verification_begins >= output_upload_ends'),
        nullable=True)
    verification_ends = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('verification_ends > verification_begins'),
        nullable=True)
    resolution_begins = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('resolution_begins >= verification_ends'),
        nullable=True)
    resolution_ends = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('resolution_ends > resolution_begins'),
        nullable=True)
    open_verification_begins = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('open_verification_begins >= resolution_ends'),
        nullable=True)
    open_verification_ends = sa.Column(
        sa.DateTime,
        sa.CheckConstraint(
            'open_verification_ends >= open_verification_begins'),
        nullable=True)
    evaluation_begins = sa.Column(sa.DateTime, nullable=True)
    evaluation_ends = sa.Column(
        sa.DateTime,
        sa.CheckConstraint('evaluation_ends > evaluation_begins'),
        nullable=True)

    groups = relationship(
        "Group", back_populates="competition", lazy='dynamic')

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
    def resolution_open(self):
        return (self.resolution_begins
                and (self.resolution_begins
                     <= datetime.datetime.now()
                     < self.resolution_ends))

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
                    self.resolution_ends,
                    self.open_verification_ends,
                    self.evaluation_ends))))

    def __repr__(self):
        return self.name


class User(DeclarativeBase):
    __tablename__ = 'user'
    db_icon = 'fas fa-user'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.Unicode, unique=True, nullable=False)
    email = sa.Column(sa.Unicode, unique=True, nullable=False)
    full_name = sa.Column(sa.Unicode)
    admin = sa.Column(sa.Boolean, nullable=False, default=False)

    submitted_evaluations = relationship(
        "Evaluation",
        back_populates="from_student",
        foreign_keys="Evaluation.from_student_id", lazy='dynamic')
    received_evaluations = relationship(
        "Evaluation",
        back_populates="to_student",
        foreign_keys="Evaluation.to_student_id")

    groups = relation(
        'Group', secondary='user_group_xref', back_populates='users')

    @classmethod
    def from_username(cls, username):
        return (DBSession.query(User)
                         .filter(cls.username == username)
                         .one_or_none())

    def __repr__(self):
        return self.full_name or self.username


class Group(DeclarativeBase):
    __tablename__ = 'group'
    db_icon = 'fas fa-users'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(100), nullable=True)
    penalty = sa.Column(sa.Integer, nullable=False, default=0)

    competition_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('competition.id'),
        nullable=False)
    competition = relationship("Competition", back_populates="groups")

    input = relationship("Input", uselist=False, back_populates="group")
    outputs = relationship("Output", back_populates="group", lazy='dynamic')

    users = relation('User', secondary='user_group_xref',
                     back_populates='groups', lazy='dynamic')

    evaluations = relationship(
        "Evaluation",
        back_populates="group")

    def __repr__(self):
        if self.name:
            return "{} (Group {})".format(self.name, self.id)
        return "Group {}".format(self.id)


# N users can be a part of M groups
# ---------------------------------
# Why may a user be a part of M groups? Consider the case where a user
# fails the course, or a test account that was made part of many groups
# over time.
user_group_xref = sa.Table('user_group_xref', metadata,
                           sa.Column('user_id', sa.Integer,
                                     sa.ForeignKey('user.id',
                                                   onupdate="CASCADE",
                                                   ondelete="CASCADE"),
                                     primary_key=True),
                           sa.Column('group_id', sa.Integer,
                                     sa.ForeignKey('group.id',
                                                   onupdate="CASCADE",
                                                   ondelete="CASCADE"),
                                     primary_key=True))


class Input(DeclarativeBase):
    __tablename__ = 'input'
    db_icon = 'far fa-file'

    id = sa.Column(sa.Integer, primary_key=True)
    data = sa.Column(UploadedFileField, nullable=False)

    group_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('group.id'),
        nullable=False)
    group = relationship("Group", back_populates="input")

    outputs = relationship("Output", back_populates="input", lazy='dynamic')

    def __repr__(self):
        return "Input from [{!r}]".format(self.group)


class Output(DeclarativeBase):
    __tablename__ = 'output'
    db_icon = 'far fa-copy'

    id = sa.Column(sa.Integer, primary_key=True)

    # The score is separated from the data, allowing for database
    # server-side sorting
    score = sa.Column(sa.Numeric, nullable=False)
    data = sa.Column(UploadedFileField, nullable=False)

    verification = sa.Column(
        sa.Enum(VerificationStatus),
        nullable=False,
        default=VerificationStatus.waiting)
    ground_truth = sa.Column(
        sa.Enum(VerificationStatus),
        nullable=False,
        default=VerificationStatus.waiting)
    use_ground_truth = sa.Column(sa.Boolean, nullable=False, default=False)

    input_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('input.id'),
        nullable=False)
    input = relationship("Input", back_populates="outputs")

    group_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('group.id'),
        nullable=False)
    group = relationship("Group", back_populates="outputs")

    def __repr__(self):
        return "Output from [{!r}] for {!r}".format(self.group, self.input)


class Evaluation(DeclarativeBase):
    __tablename__ = 'evaluation'
    db_icon = 'fas fa-sliders-h'

    id = sa.Column(sa.Integer, primary_key=True)
    score = sa.Column(sa.Float, nullable=False)

    from_student_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id'),
        nullable=False)
    from_student = relationship(
        "User",
        back_populates="submitted_evaluations",
        foreign_keys=from_student_id)

    to_student_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id'),
        nullable=False)
    to_student = relationship(
        "User",
        back_populates="received_evaluations",
        foreign_keys=to_student_id)

    group_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('group.id'),
        nullable=False)
    group = relationship(
        "Group",
        back_populates="evaluations")
