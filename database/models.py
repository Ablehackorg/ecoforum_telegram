from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from utils.config import tashkent_now

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String)
    region = Column(String)
    age = Column(Integer)
    sex = Column(String)
    regist_at = Column(DateTime, default=tashkent_now)

    projects = relationship("Projects", back_populates="user")
    helpers = relationship("Helpers", back_populates="user")
    donaters = relationship("Donaters", back_populates="user")
    blogs = relationship("Blogs", back_populates="user")

class Projects(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, unique=True)
    description = Column(String)
    photo_id = Column(String)
    helper_quantity = Column(Integer, default=0)
    total_quantity = Column(Integer, default=0)
    cash_amount = Column(Integer, default=0)
    total_amount = Column(Integer, default=0)
    status = Column(String, default="wait")
    created_at = Column(DateTime, default=tashkent_now)

    user = relationship("Users", back_populates="projects")
    helpers = relationship("Helpers", back_populates="project")
    donaters = relationship("Donaters", back_populates="project")


class Helpers(Base):
    __tablename__ = "helpers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    joined_at = Column(DateTime, default=tashkent_now)  

    user = relationship("Users", back_populates="helpers")
    project = relationship("Projects", back_populates="helpers")


class Donaters(Base):
    __tablename__ = "donaters"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    amount = Column(Integer)
    donated_at = Column(DateTime, default=tashkent_now)

    user = relationship("Users", back_populates="donaters")
    project = relationship("Projects", back_populates="donaters")


class Blogs(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, unique=True)
    content = Column(String)
    photo_id = Column(String)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=tashkent_now)

    user = relationship("Users", back_populates="blogs")