# -*- coding: utf-8 -*-
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import calendar
import os

# データベースエンジンの設定
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///medicines.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# データベースモデルの定義
class Medicine(Base):
    __tablename__ = 'medicines'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    take_time = Column(Time, nullable=False)
    dosage = Column(String(50), nullable=False)
    notes = Column(String(500), nullable=True)

class TakenRecord(Base):
    __tablename__ = 'taken_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, nullable=False)
    record_date = Column(Date, nullable=False)
    is_taken = Column(Boolean, default=False)

Base.metadata.create_all(engine)

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

# ルートURL（カレンダー表示）
@app.route('/')
def show_calendar():
    today = datetime.date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))
    selected_date_str = request.args.get('selected_date', today.strftime('%Y-%m-%d'))
    selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(year, month)

    # 前月・次月の計算
    prev_month_date = datetime.date(year, month, 1) - datetime.timedelta(days=1)
    next_month_date = datetime.date(year, month, 28) + datetime.timedelta(days=4)

    # 該当月の薬と服用記録を取得
    start_of_month = datetime.date(year, month, 1)
    end_of_month = datetime.date(year, month, calendar.monthrange(year, month)[1])

    medicines = session.query(Medicine).filter(
        Medicine.start_date <= end_of_month,
        Medicine.end_date >= start_of_month
    ).all()

    taken_records = session.query(TakenRecord).filter(
        TakenRecord.record_date >= start_of_month,
        TakenRecord.record_date <= end_of_month
    ).all()
    
    taken_dict = {(rec.medicine_id, rec.record_date): rec.is_taken for rec in taken_records}

    # 日付ごとの薬の情報を辞書にまとめる
    calendar_data = {}
    for week in month_days:
        for day in week:
            if day.month == month:
                day_data = []
                for medicine in medicines:
                    if medicine.start_date <= day <= medicine.end_date:
                        is_taken = taken_dict.get((medicine.id, day), False)
                        day_data.append({
                            'id': medicine.id,
                            'name': medicine.name,
                            'is_taken': is_taken
                        })
                calendar_data[day] = day_data
    
    # 選択した日の薬リストを取得
    medicines_for_day = session.query(Medicine).filter(
        Medicine.start_date <= selected_date,
        Medicine.end_date >= selected_date
    ).all()
    
    return render_template(
        'calendar.html',
        year=year,
        month=month,
        month_days=month_days,
        prev_month_date=prev_month_date,
        next_month_date=next_month_date,
        calendar_data=calendar_data,
        today=today,
        selected_date=selected_date,
        medicines_for_day=medicines_for_day,
    )

# 薬の登録・編集ページのコンテンツを返す
@app.route('/medicine_manage_content', methods=['GET'])
def get_medicine_manage_content():
    date_str = request.args.get('date_str')
    medicine_id = request.args.get('medicine_id', type=int)
    
    record_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    medicine = None
    if medicine_id:
        medicine = session.query(Medicine).filter_by(id=medicine_id).first()
    
    # 選択した日の薬リストを取得
    medicines_for_day = session.query(Medicine).filter(
        Medicine.start_date <= record_date,
        Medicine.end_date >= record_date
    ).all()
    
    html = render_template('medicine_form.html', medicine=medicine, record_date=record_date, medicines_for_day=medicines_for_day)
    return html

# 薬の登録・編集・削除処理
@app.route('/medicine_manage', methods=['POST'])
def manage_medicine():
    action = request.form.get('action')
    date_str = request.form.get('date')
    medicine_id = request.form.get('medicine_id', type=int)

    record_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    medicine = None
    if medicine_id:
        medicine = session.query(Medicine).filter_by(id=medicine_id).first()
    
    if action == 'save':
        name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        take_time_str = request.form.get('take_time')
        dosage = request.form.get('dosage')
        notes = request.form.get('notes')

        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        take_time = datetime.datetime.strptime(take_time_str, '%H:%M').time()

        if medicine_id:
            # 編集
            medicine.name = name
            medicine.start_date = start_date
            medicine.end_date = end_date
            medicine.take_time = take_time
            medicine.dosage = dosage
            medicine.notes = notes
            session.commit()
        else:
            # 新規登録
            new_medicine = Medicine(
                name=name,
                start_date=start_date,
                end_date=end_date,
                take_time=take_time,
                dosage=dosage,
                notes=notes
            )
            session.add(new_medicine)
            session.commit()
    elif action == 'delete':
        # 削除
        if medicine:
            session.delete(medicine)
            session.commit()
    
    return redirect(url_for('show_calendar', year=record_date.year, month=record_date.month, selected_date=record_date.strftime('%Y-%m-%d')))


# 服用記録の更新
@app.route('/toggle_taken', methods=['POST'])
def toggle_taken():
    medicine_id = request.form.get('medicine_id', type=int)
    date_str = request.form.get('date', type=str)
    
    if not medicine_id or not date_str:
        return jsonify({'success': False, 'message': 'Invalid parameters'}), 400

    record_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

    # 既存の服用記録を取得
    record = session.query(TakenRecord).filter_by(
        medicine_id=medicine_id,
        record_date=record_date
    ).first()

    if record:
        record.is_taken = not record.is_taken
        session.commit()
    else:
        # 新規記録
        new_record = TakenRecord(
            medicine_id=medicine_id,
            record_date=record_date,
            is_taken=True
        )
        session.add(new_record)
        session.commit()

    return jsonify({'success': True, 'is_taken': record.is_taken if record else True})

# 毎日の服用時間になったら通知を出すエンドポイント
@app.route('/check_notifications', methods=['GET'])
def check_notifications():
    current_time = datetime.datetime.now().time()
    current_date = datetime.date.today()

    # 現在時刻に近い薬の服用情報を取得
    medicines = session.query(Medicine).filter(
        Medicine.start_date <= current_date,
        Medicine.end_date >= current_date
    ).all()

    notifications = []
    for medicine in medicines:
        # 服用時間と現在時刻の差を計算（例: 5分以内なら通知）
        time_diff = abs((datetime.datetime.combine(current_date, medicine.take_time) - datetime.datetime.combine(current_date, current_time)).total_seconds())
        if time_diff <= 300:  # 300秒 = 5分
            notifications.append({
                'name': medicine.name,
                'take_time': medicine.take_time.strftime('%H:%M'),
                'dosage': medicine.dosage
            })

    if notifications:
        # ここでmp3ファイルを返すか、JavaScriptで再生する情報を返す
        return jsonify({
            'notifications': notifications,
            'play_sound': True
        })
    else:
        return jsonify({
            'notifications': [],
            'play_sound': False
        })

if __name__ == '__main__':
    # Flaskアプリの実行
    app.run(debug=True)

