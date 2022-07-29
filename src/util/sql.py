from sqlalchemy import Column, ForeignKey, Integer, String, Text, or_, and_, func, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

create_engine