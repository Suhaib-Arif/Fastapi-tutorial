from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQL_ALCHAMY_URL = 'mysql+pymysql://root:root@127.0.0.1:3306/todoapplicationdatabase'


engine = create_engine(SQL_ALCHAMY_URL)

SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()