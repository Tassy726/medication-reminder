# -*- coding: utf-8 -*-
import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベースエンジンの設定
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///medicines.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# データベースモデルの定義
# 薬の情報を格納するテーブル
class Medicine(Base):
    __tablename__ = 'medicines'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    take_time = Column(Time, nullable=False)
    dosage = Column(String(50), nullable=False)
    notes = Column(String(500), nullable=True)

# 服用記録を格納するテーブル
class TakenRecord(Base):
    __tablename__ = 'taken_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, nullable=False)
    record_date = Column(Date, nullable=False)
    is_taken = Column(Boolean, default=False)

# データベースの初期化
def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized.")

if __name__ == '__main__':
    init_db()

