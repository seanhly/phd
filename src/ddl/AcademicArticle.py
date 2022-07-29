from sqlalchemy import Column, ForeignKey, Integer, String, Text, or_, and_, func, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
 
Base = declarative_base()

class AcademicArticle(Base):
	id = Column(Integer, primary_key=True)
	title = Column(Text(), nullable=False)
	name = Column(Text(), nullable=False)