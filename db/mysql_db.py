# -*- coding: utf-8 -*-
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from config import DATABASE_CONFIG

DATABASE_URL='mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
            DATABASE_CONFIG['mysql']['user'],
            DATABASE_CONFIG['mysql']['password'],
            DATABASE_CONFIG['mysql']['host'],
            DATABASE_CONFIG['mysql']['port'],
            DATABASE_CONFIG['mysql']['database'])
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autoflush=False, bind=engine))

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

class BaseItem(object):

    @staticmethod
    def to_dict(info):
        """将obj转成dict"""
        return info.data

    @classmethod
    def get_all(cls):
        """
        返回所有数据
        """
        with get_db() as session:
            try:
                return [cls.to_dict(info) for info in session.query(cls).all()]
            except BaseException as e:
                session.rollback()
                raise BaseException('数据库链接错误 == {}'.format(e))
            finally:
                session.close()

