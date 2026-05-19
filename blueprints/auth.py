from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def giangvien_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'giangvien':
            flash('Ban khong co quyen truy cap!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'giangvien':
            return redirect(url_for('reports.dashboard'))
        return redirect(url_for('grades.my_grades'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            if user.role == 'giangvien':
                return redirect(url_for('reports.dashboard'))
            return redirect(url_for('grades.my_grades'))
        flash('Sai ten dang nhap hoac mat khau!', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Da dang xuat thanh cong!', 'success')
    return redirect(url_for('auth.login'))