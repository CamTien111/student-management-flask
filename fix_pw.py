from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'instance', 'student_mgmt.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Tìm user giaovien01
    user = User.query.filter_by(username='giaovien01').first()
    
    if not user:
        # Nếu chưa có thì tạo mới luôn
        user = User(username='giaovien01', role='giangvien')
        db.session.add(user)
        print("Đang tạo mới user giaovien01...")
    
    # Đặt mật khẩu mã hóa là 123456
    user.password_hash = generate_password_hash('123456')
    db.session.commit()
    print("--- CHÚC MỪNG: Đã đặt mật khẩu thành công là 123456 ---")