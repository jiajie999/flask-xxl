from basemodels import BaseMixin
from flask import url_for
from ext import db
from LoginUtils import encrypt_password, check_password

#import sqlalchemy to global namespace
for attr in dir(db):
    if not attr.startswith('_'):
        globals()[attr] = getattr(db,attr)


class UnknownUser(object):
    is_unknown = True

class Role(BaseMixin,Model):
    __tablename__ = 'roles'

    name = Column(String(255))
    can_view = Column(Boolean,default=True,nullable=False)
    can_add = Column(Boolean,default=False,nullable=False)
    can_edit = Column(Boolean,default=False,nullable=False)
    can_delete = Column(Boolean,default=False,nullable=False)

class User(BaseMixin,Model):
    __tablename__ = 'users'

    first_name = Column(String(255),default="")
    last_name = Column(String(255),default="")
    email = Column(String(255),nullable=False,unique=True)
    role_id = Column(Integer,ForeignKey('roles.id'))
    role = relationship('Role',backref=backref(
                    'users',lazy='dynamic'))
    add_date = Column(DateTime,default=func.now())
    _pw_hash = Column(UnicodeText,nullable=False)
    articles = relationship('Article',backref=backref(
                    'author'),lazy='dynamic',passive_deletes='all')
    age = Column(Integer)


    def __init__(self,*args,**kwargs):
        if 'first_name' in kwargs:
            self.first_name = kwargs.pop('first_name')
        if 'last_name' in kwargs:
            self.last_name = kwargs.pop('last_name')
        if 'email' in kwargs:
            self.email = kwargs.pop('email')
        if 'role' in kwargs:
            self.role = kwargs.pop('role')
        if 'role_id' in kwargs:
            self.role_id = kwargs.pop('role_id')
        if 'password' in kwargs:
            self.password = kwargs.pop('password')

    @property
    def is_unknown(self):
        return False
    
    def check_password(self, pw):
        return check_password(pw,self._pw_hash)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @property
    def password(self):
        raise ValueError('Private Value!!!!')

    @password.setter
    def password(self,pw):
        self._pw_hash = encrypt_password(pw)

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name.title(),self.last_name.title())

    def __str__(self):
        if self.first_name != "":
            rtn = self.full_name
        else:
            rtn = self.email
        return rtn

    def __repr__(self):
        return 'User<{} {}'.format(self.email,self.first_name)

    def _get_absolute_url(self):
        return url_for('member.profile',member_id=str(int(self.id)))

    def _get_edit_url(self):
        return '#'

    @property 
    def article_count(self):
        return self.articles.query.count()

