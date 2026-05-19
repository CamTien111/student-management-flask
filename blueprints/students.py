from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, SinhVien, LopHoc, User, BangDiem
from blueprints.auth import giangvien_required
from werkzeug.security import generate_password_hash

students_bp = Blueprint('students', __name__)

@students_bp.route('/')
@login_required
@giangvien_required
def index():
    search = request.args.get('search', '')
    lop_id = request.args.get('lop_id', '')
    query = SinhVien.query
    if search:
        query = query.filter(SinhVien.ho_ten.contains(search) | SinhVien.ma_sv.contains(search))
    if lop_id:
        query = query.filter_by(lop_id=lop_id)
    sinh_viens = query.all()
    lop_hocs = LopHoc.query.all()
    return render_template('students/index.html', sinh_viens=sinh_viens, lop_hocs=lop_hocs, search=search)

@students_bp.route('/them', methods=['GET', 'POST'])
@login_required
@giangvien_required
def them():
    if request.method == 'POST':
        ma_sv = request.form.get('ma_sv')
        ho_ten = request.form.get('ho_ten')
        email = request.form.get('email')
        gioi_tinh = request.form.get('gioi_tinh')
        password = request.form.get('password', '123456')
        
        # Lấy hoặc tự tạo lớp mới
        ma_lop = request.form.get('ma_lop', '').strip()
        ten_lop = request.form.get('ten_lop', '').strip()
        
        lop = LopHoc.query.filter_by(ma_lop=ma_lop).first()
        if not lop:
            lop = LopHoc(ma_lop=ma_lop, ten_lop=ten_lop or ma_lop, nien_khoa='2024-2028')
            db.session.add(lop)
            db.session.flush()

        if SinhVien.query.filter_by(ma_sv=ma_sv).first():
            flash('Ma sinh vien da ton tai!', 'danger')
            return redirect(url_for('students.them'))

        if User.query.filter_by(username=ma_sv).first():
            flash('Tai khoan da ton tai!', 'danger')
            return redirect(url_for('students.them'))

        user = User(
            username=ma_sv,
            password_hash=generate_password_hash(password),
            role='sinhvien'
        )
        db.session.add(user)
        db.session.flush()

        sv = SinhVien(
            ma_sv=ma_sv, ho_ten=ho_ten,
            email=email, gioi_tinh=gioi_tinh,
            lop_id=lop.id, user_id=user.id
        )
        db.session.add(sv)
        db.session.commit()
        flash('Them sinh vien ' + ho_ten + ' thanh cong!', 'success')
        return redirect(url_for('students.index'))

    lop_hocs = LopHoc.query.all()
    return render_template('students/them.html', lop_hocs=lop_hocs)


@students_bp.route('/sua/<int:id>', methods=['GET', 'POST'])
@login_required
@giangvien_required
def sua(id):
    sv = SinhVien.query.get_or_404(id)
    if request.method == 'POST':
        # 1. Cập nhật thông tin cơ bản
        sv.ho_ten = request.form.get('ho_ten')
        sv.email = request.form.get('email')
        sv.gioi_tinh = request.form.get('gioi_tinh')
        
        # 2. Xử lý tên lớp (Lấy từ input có name="class_name")
        ten_lop_moi = request.form.get('class_name')
        
        if ten_lop_moi:
            # Tìm xem lớp này đã có trong database chưa
            lop = LopHoc.query.filter_by(ten_lop=ten_lop_moi).first()
            
            if not lop:
                # Nếu chưa có thì tạo mới và phải điền ĐỦ ma_lop để không bị lỗi
                lop = LopHoc(
                    ma_lop=ten_lop_moi, 
                    ten_mon=ten_lop_moi, 
                    nien_khoa="2022-2026"
                )
                db.session.add(lop)
                db.session.flush()
            
            # Gán ID lớp cho sinh viên
            sv.lop_id = lop.id
        
        try:
            db.session.commit()
            flash('Cập nhật thông tin sinh viên thành công!', 'success')
            return redirect(url_for('students.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật: {str(e)}', 'danger')
    
    return render_template('students/sua.html', sv=sv)

@students_bp.route('/xoa/<int:id>')
@login_required
@giangvien_required
def xoa(id):
    sv = SinhVien.query.get_or_404(id)
    
    # Xóa điểm của sinh viên trước
    BangDiem.query.filter_by(sv_id=sv.id).delete()
    
    # Xóa tài khoản user
    user = User.query.get(sv.user_id)
    
    # Xóa sinh viên
    db.session.delete(sv)
    if user:
        db.session.delete(user)
    
    db.session.commit()
    flash('Da xoa sinh vien!', 'success')
    return redirect(url_for('students.index'))