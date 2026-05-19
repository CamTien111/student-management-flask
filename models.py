from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LopHoc(db.Model):
    __tablename__ = 'lop_hoc'
    id = db.Column(db.Integer, primary_key=True)
    ma_lop = db.Column(db.String(20), unique=True, nullable=False)
    ten_lop = db.Column(db.String(100), nullable=False)
    nien_khoa = db.Column(db.String(20))
    sinh_viens = db.relationship('SinhVien', backref='lop', lazy=True)

class SinhVien(db.Model):
    __tablename__ = 'sinh_vien'
    id = db.Column(db.Integer, primary_key=True)
    ma_sv = db.Column(db.String(20), unique=True, nullable=False)
    ho_ten = db.Column(db.String(100), nullable=False)
    ngay_sinh = db.Column(db.Date)
    gioi_tinh = db.Column(db.String(10))
    email = db.Column(db.String(120))
    lop_id = db.Column(db.Integer, db.ForeignKey('lop_hoc.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bang_diems = db.relationship('BangDiem', backref='sinh_vien', lazy=True)

class MonHoc(db.Model):
    __tablename__ = 'mon_hoc'
    id = db.Column(db.Integer, primary_key=True)
    ma_mon = db.Column(db.String(20), unique=True, nullable=False)
    ten_mon = db.Column(db.String(150), nullable=False)
    so_tin_chi = db.Column(db.Integer, nullable=False)

class BangDiem(db.Model):
    __tablename__ = 'bang_diem'
    id = db.Column(db.Integer, primary_key=True)
    sv_id = db.Column(db.Integer, db.ForeignKey('sinh_vien.id'), nullable=False)
    mon_id = db.Column(db.Integer, db.ForeignKey('mon_hoc.id'), nullable=False)
    hoc_ky = db.Column(db.String(20), nullable=False)
    diem_cc = db.Column(db.Float)
    diem_giua_ky = db.Column(db.Float)
    diem_cuoi_ky = db.Column(db.Float)
    mon = db.relationship('MonHoc', backref='bang_diems')

    @property
    def diem_tong_ket(self):
        if None in [self.diem_cc, self.diem_giua_ky, self.diem_cuoi_ky]:
            return None
        return round(self.diem_cc * 0.2 + self.diem_giua_ky * 0.2 + self.diem_cuoi_ky * 0.6, 2)

    @property
    def diem_he4(self):
        d = self.diem_tong_ket
        if d is None: return None
        if d >= 8.5: return 4.0
        elif d >= 8.0: return 3.7
        elif d >= 7.5: return 3.5
        elif d >= 7.0: return 3.0
        elif d >= 6.5: return 2.5
        elif d >= 6.0: return 2.0
        elif d >= 5.5: return 1.5
        elif d >= 5.0: return 1.0
        else: return 0.0

    @property
    def xep_loai(self):
        d = self.diem_tong_ket
        if d is None: return "Chưa có điểm"
        if d >= 9.0: return "Xuất sắc"
        elif d >= 8.0: return "Giỏi"
        elif d >= 7.0: return "Khá"
        elif d >= 6.0: return "Trung bình khá"
        elif d >= 5.0: return "Trung bình"
        else: return "Không đạt"