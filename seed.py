from app import create_app
from models import db, MonHoc

app = create_app()
with app.app_context():
    # Xóa môn cũ nếu có
    MonHoc.query.delete()
    db.session.commit()
    
    mon1 = MonHoc(ma_mon='CNW01', ten_mon='Cong nghe Web', so_tin_chi=3)
    mon2 = MonHoc(ma_mon='LTP01', ten_mon='Lap trinh Python', so_tin_chi=4)
    mon3 = MonHoc(ma_mon='MMT01', ten_mon='Mang may tinh', so_tin_chi=3)
    mon4 = MonHoc(ma_mon='LTDD01', ten_mon='Lap trinh di dong', so_tin_chi=3)
    db.session.add_all([mon1, mon2, mon3, mon4])
    db.session.commit()
    print('Tao mon hoc xong!')
    