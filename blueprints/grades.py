from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, SinhVien, BangDiem, MonHoc
from blueprints.auth import giangvien_required

grades_bp = Blueprint('grades', __name__)

@grades_bp.route('/')
@login_required
@giangvien_required
def index():
    bang_diems = BangDiem.query.all()
    return render_template('grades/index.html', bang_diems=bang_diems)

@grades_bp.route('/nhap-diem', methods=['GET', 'POST'])
@login_required
@giangvien_required
def nhap_diem():
    if request.method == 'POST':
        sv_id = request.form.get('sv_id')
        mon_id = request.form.get('mon_id')
        hoc_ky = request.form.get('hoc_ky')
        bang_diem = BangDiem.query.filter_by(
            sv_id=sv_id, mon_id=mon_id, hoc_ky=hoc_ky
        ).first()
        if not bang_diem:
            bang_diem = BangDiem(sv_id=sv_id, mon_id=mon_id, hoc_ky=hoc_ky)
        diem_cc = request.form.get('diem_cc', '').strip()
        diem_gk = request.form.get('diem_giua_ky', '').strip()
        diem_ck = request.form.get('diem_cuoi_ky', '').strip()
        bang_diem.diem_cc = float(diem_cc) if diem_cc else None
        bang_diem.diem_giua_ky = float(diem_gk) if diem_gk else None
        bang_diem.diem_cuoi_ky = float(diem_ck) if diem_ck else None
        db.session.add(bang_diem)
        db.session.commit()
        flash('Cap nhat diem thanh cong!', 'success')
        return redirect(url_for('grades.index'))
    sinh_viens = SinhVien.query.all()
    mon_hocs = MonHoc.query.all()
    return render_template('grades/nhap_diem.html',
                           sinh_viens=sinh_viens, mon_hocs=mon_hocs)

@grades_bp.route('/my-grades')
@login_required
def my_grades():
    sv = SinhVien.query.filter_by(user_id=current_user.id).first()
    if not sv:
        flash('Khong tim thay thong tin sinh vien!', 'warning')
        return redirect(url_for('auth.login'))
    diem_theo_hky = {}
    for bd in sv.bang_diems:
        if bd.hoc_ky not in diem_theo_hky:
            diem_theo_hky[bd.hoc_ky] = []
        diem_theo_hky[bd.hoc_ky].append(bd)
    gpa_data = _tinh_gpa(sv)
    du_bao = _du_bao_gpa(sv, 3.2)
    return render_template('grades/my_grades.html',
                           sv=sv, diem_theo_hky=diem_theo_hky,
                           gpa_data=gpa_data, du_bao=du_bao)

def _tinh_gpa(sv):
    hky_data = {}
    for bd in sv.bang_diems:
        if bd.mon is None:
            continue
        if bd.diem_he4 is None:
            continue
        hky = bd.hoc_ky
        if hky not in hky_data:
            hky_data[hky] = {'tong': 0, 'tc': 0}
        hky_data[hky]['tong'] += bd.diem_he4 * bd.mon.so_tin_chi
        hky_data[hky]['tc'] += bd.mon.so_tin_chi
    return {hky: round(v['tong']/v['tc'], 2)
            for hky, v in sorted(hky_data.items()) if v['tc'] > 0}

def _du_bao_gpa(sv, target=3.2):
    co_diem, chua_diem = [], []
    for bd in sv.bang_diems:
        if bd.mon is None:
            continue
        (co_diem if bd.diem_he4 is not None else chua_diem).append(bd)
    if not chua_diem:
        return None
    tong_diem = sum(bd.diem_he4 * bd.mon.so_tin_chi for bd in co_diem)
    tc_co = sum(bd.mon.so_tin_chi for bd in co_diem)
    tc_chua = sum(bd.mon.so_tin_chi for bd in chua_diem)
    tc_tong = tc_co + tc_chua
    can_dat = (target * tc_tong - tong_diem) / tc_chua if tc_chua else 0
    return {
        'target_gpa': target,
        'diem_can_dat_he4': round(can_dat, 2),
        'gpa_hien_tai': round(tong_diem / tc_co, 2) if tc_co else 0,
        'so_mon_con_lai': len(chua_diem)
    }