#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :   task
   Project   :   scravisor
   Author    :   bgspider
   date      :   2025/5/22
-------------------------------------------------
"""
from sqlalchemy import INTEGER, VARCHAR, Column, func, TEXT, DATETIME, JSON

from .mysql_db import Base, BaseItem, get_db


class Task(BaseItem, Base):
    """规则表"""
    __tablename__ = 'task'

    id = Column(INTEGER, primary_key=True)
    crawl_type = Column(INTEGER)
    run_type = Column(INTEGER)
    status=Column(INTEGER)
    crawl_interval_type = Column(INTEGER)
    config = Column(TEXT)
    class_name = Column(VARCHAR(50))
    main_host = Column(VARCHAR(100))
    remark = Column(VARCHAR(255))
    website_name = Column(VARCHAR(100))
    crawl_interval=Column(VARCHAR(50))
    index_url=Column(TEXT)
    crawl_start_time = Column(DATETIME)
    crawl_end_time = Column(DATETIME)
    next_crawl_time = Column(DATETIME)
    update_time = Column(DATETIME)

    def get_task(self, site_id=None,site_name=None):
        """查询指定规则"""
        with get_db() as session:
            try:
                if site_id:
                    query= session.query(Task).filter(Task.id == site_id).first()
                else:
                    return 0, []
                if query:
                    return query.id, query.config
                else:
                    return 0, []
            except BaseException as e:
                session.rollback()
                raise BaseException(e)

    def exit_field(self,spec):
        with get_db() as session:
            try:
                number = session.query(func.count(func.distinct(Task.id))).filter(*spec).scalar()
                return number
            except BaseException as e:
                session.rollback()
                raise BaseException(e)
            finally:
                session.close()


    def insert(self, item):
        """插入"""
        with get_db() as session:
            try:
                session.add(item)
                session.commit()
            except BaseException as e:
                raise BaseException('数据插入失败==>{}=={}'.format(e, item))
            finally:
                session.close()
    def serach_all(self, spec,field_name=None):
        """更新"""
        with get_db() as session:
            try:
                if field_name:
                    data=session.query(*field_name).filter(*spec).all()
                else:
                    data=session.query(Task).filter(*spec).all()
                # data=session.query(Task).filter(*spec).all()
                return data
            except BaseException as e:
                raise BaseException('数据更新失败')
            finally:
                session.close()
    def update(self, spec,data):
        """更新"""
        with get_db() as session:
            try:
                session.query(Task).filter(*spec).update(data)
                session.commit()
            except BaseException as e:
                raise BaseException('数据更新失败')
            finally:
                session.close()