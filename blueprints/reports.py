from flask import Blueprint, render_template, make_response
from flask_login import login_required
from blueprints.auth import giangvien_required
from models import SinhVien, BangDiem, LopHoc
import pandas as pd
import io
from collections import defaultdict

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/dashboard')
@login_required
@giangvien_required
def dashboard():
    tong_sv = SinhVien.query.count()
    tong_lop = LopHoc.query.count()
    all_diems = BangDiem.query.all()
    stats = {'Xuất sắc': 0, 'Giỏi': 0, 'Khá': 0,
             'Trung bình khá': 0, 'Trung bình': 0, 'Không đạt': 0}
    for bd in all_diems:
        xl = bd.xep_loai
        if xl in stats:
            stats[xl] += 1
    gpa_chart = _gpa_trend()
    return render_template('dashboard/index.html',
                           tong_sv=tong_sv, tong_lop=tong_lop,
                           stats=stats, gpa_chart=gpa_chart)

@reports_bp.route('/export/excel')
@login_required
@giangvien_required
def export_excel():
    rows = []
    for sv in SinhVien.query.all():
        for bd in sv.bang_diems:
            if bd.mon is None:
                continue
            rows.append({
                'MSSV': sv.ma_sv,
                'Ho va Ten': sv.ho_ten,
                'Lop': sv.lop.ma_lop if sv.lop else '',
                'Mon hoc': bd.mon.ten_mon,
                'Hoc ky': bd.hoc_ky,
                'Diem CC': bd.diem_cc,
                'Diem GK': bd.diem_giua_ky,
                'Diem CK': bd.diem_cuoi_ky,
                'Tong ket': bd.diem_tong_ket,
                'Thang 4': bd.diem_he4,
                'Xep loai': bd.xep_loai,
            })
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Bang diem', index=False)
        ws = writer.sheets['Bang diem']
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col) + 2
            ws.column_dimensions[col[0].column_letter].width = min(max_len, 30)
    output.seek(0)
    response = make_response(output.read())
    response.headers['Content-Disposition'] = 'attachment; filename=bang_diem.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def _gpa_trend():
    hky_map = defaultdict(lambda: {'tong': 0, 'count': 0})
    for sv in SinhVien.query.all():
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
        for hky, v in hky_data.items():
            if v['tc'] > 0:
                hky_map[hky]['tong'] += round(v['tong'] / v['tc'], 2)
                hky_map[hky]['count'] += 1
    sorted_hky = sorted(hky_map.keys())
    return {
        'labels': sorted_hky,
        'data': [round(hky_map[h]['tong'] / hky_map[h]['count'], 2)
                 for h in sorted_hky if hky_map[h]['count'] > 0]
    }