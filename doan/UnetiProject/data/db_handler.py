import pyodbc
import datetime
import json
import shutil
import os

# --- CẤU HÌNH KẾT NỐI ---
SERVER = '.\\SQLEXPRESS' 
DATABASE = 'QuanLyRenLuyen'
USE_TRUSTED_CONNECTION = True 

class DBHandler:
    # =========================================================================
    # 0. KHỞI TẠO & KẾT NỐI (CORE)
    # =========================================================================
    def __init__(self):
        self.conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={SERVER};'
            f'DATABASE={DATABASE};'
        )
        if USE_TRUSTED_CONNECTION:
            self.conn_str += 'Trusted_Connection=yes;'
        
        self.conn = None
        try:
            self.conn = pyodbc.connect(self.conn_str)
            print("--- DB: Kết nối SQL Server thành công ---")
        except Exception as e:
            print(f"--- LỖI KẾT NỐI: {e} ---")

    def __del__(self):
        if self.conn: 
            try:
                self.conn.close()
            except: pass

    def _execute_query(self, query, params=None, fetch_one=False, commit=False):
        if not self.conn: 
            try:
                self.conn = pyodbc.connect(self.conn_str)
            except:
                return None

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            if commit:
                self.conn.commit()
                return True
            
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                if fetch_one:
                    row = cursor.fetchone()
                    return dict(zip(columns, row)) if row else None
                else:
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return True
        except Exception as e:
            print(f"Lỗi SQL: {e}\nQuery: {query}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    # =========================================================================
    # 1. XÁC THỰC & TÀI KHOẢN (SHARED)
    # =========================================================================
    def check_login(self, username, password):
        query = "SELECT ten, vai_tro FROM Users WHERE ma_dang_nhap = ? AND mat_khau = ?"
        return self._execute_query(query, (username, password), fetch_one=True)

    def change_password(self, username, old_pass, new_pass):
        query = "UPDATE Users SET mat_khau = ? WHERE ma_dang_nhap = ? AND mat_khau = ?"
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, (new_pass, username, old_pass))
            if cursor.rowcount > 0:
                self.conn.commit() 
                return True
            return False
        except Exception as e:
            print(f"Lỗi đổi mật khẩu: {e}")
            return False
        finally:
            cursor.close()

    # =========================================================================
    # 2. CHỨC NĂNG CHO SINH VIÊN (STUDENT)
    # =========================================================================
    def get_student_info(self, student_id):
        query = "SELECT * FROM SinhVien WHERE masv = ?"
        res = self._execute_query(query, (student_id,), fetch_one=True)
        if not res:
            return {"masv": student_id, "ten": "Chưa cập nhật", "lop": "", "ngay_sinh": "", "gioi_tinh": "", "que_quan": "", "nien_khoa": "", "chuyen_nganh": "", "email": ""}
        return res

    def get_student_scores(self, student_id):
        query = """
            SELECT d.ten_dot, p.diem_tong
            FROM PhieuRenLuyen p
            JOIN DotDanhGia d ON p.ma_dot = d.id
            WHERE p.masv = ? AND p.trang_thai = N'Đã duyệt'
        """
        data = self._execute_query(query, (student_id,))
        result = []
        if data:
            for row in data:
                full_name = row['ten_dot']
                hk, nam = "Kỳ ?", "Năm ?"
                if " " in full_name:
                    parts = full_name.split(" ", 1)
                    hk = parts[0]
                    nam = parts[1] if len(parts) > 1 else ""
                
                diem = row['diem_tong'] if row['diem_tong'] is not None else 0
                xl = "Kém"
                if diem >= 90: xl = "Xuất sắc"
                elif diem >= 80: xl = "Tốt"
                elif diem >= 65: xl = "Khá"
                elif diem >= 50: xl = "Trung bình"
                result.append((hk, nam, str(diem), xl))
        return result

    def get_student_history(self, student_id):
        query = """
            SELECT id, ngay_nop, diem_tong, trang_thai, nguoi_duyet 
            FROM PhieuRenLuyen 
            WHERE masv = ? 
            ORDER BY ngay_nop DESC
        """
        data = self._execute_query(query, (student_id,))
        result = []
        if data:
            for row in data:
                ngay = row['ngay_nop'].strftime("%d/%m/%Y %H:%M") if row['ngay_nop'] else ""
                diem = str(row['diem_tong']) if row['diem_tong'] is not None else "Wait"
                gv = row['nguoi_duyet'] if row['nguoi_duyet'] else "---"
                result.append((f"PH{row['id']:03d}", ngay, diem, row['trang_thai'], gv))
        return result

    def submit_form(self, student_id, score, evidence_files, evidence_name, selected_criteria, form_id=None):
        # 1. Tìm đợt đang mở (CHỈ CẦN TRẠNG THÁI HOẠT ĐỘNG, BỎ QUA NGÀY THÁNG)
        query_dot = """
            SELECT TOP 1 id FROM DotDanhGia 
            WHERE trang_thai = N'Hoạt động'
            ORDER BY id DESC
        """
        dot = self._execute_query(query_dot, fetch_one=True)
        
        if not dot:
            print("Không tìm thấy đợt đánh giá nào đang mở!")
            return False
        period_id = dot['id']

        # 2. Xử lý File Minh Chứng
        saved_file_paths = []
        if evidence_files:
            file_list = evidence_files.split(';') if isinstance(evidence_files, str) else evidence_files
            upload_dir = "uploads"
            if not os.path.exists(upload_dir): os.makedirs(upload_dir)
            
            for file_path in file_list:
                if file_path and os.path.exists(file_path):
                    try:
                        filename = os.path.basename(file_path)
                        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                        new_filename = f"{student_id}_{timestamp}_{filename}"
                        destination = os.path.join(upload_dir, new_filename)
                        shutil.copy(file_path, destination)
                        saved_file_paths.append(destination)
                    except Exception as e:
                        print(f"Lỗi copy file: {e}")

        final_file_string = ";".join(saved_file_paths)
        criteria_json = json.dumps(selected_criteria, ensure_ascii=False)

        # 3. Insert
        query = """
            INSERT INTO PhieuRenLuyen 
            (masv, ma_dot, diem_tu_cham, diem_tong, file_minh_chung, ten_minh_chung, chi_tiet_tieu_chi, ngay_nop, trang_thai)
            VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), N'Chờ duyệt')
        """
        params = (student_id, period_id, score, score, final_file_string, evidence_name, criteria_json)
        return self._execute_query(query, params, commit=True)

    # =========================================================================
    # 3. CHỨC NĂNG CHO GIẢNG VIÊN (LECTURER)
    # =========================================================================
    def get_lecturer_info(self, lecturer_id):
        query = "SELECT ten, vai_tro FROM Users WHERE ma_dang_nhap = ?"
        row = self._execute_query(query, (lecturer_id,), fetch_one=True)
        if row:
            return {
                "magv": lecturer_id,
                "ten": row['ten'],
                "khoa": "Công nghệ thông tin", 
                "email": f"{lecturer_id}@uneti.edu.vn",
                "sdt": "0987654321"
            }
        return {"magv": lecturer_id, "ten": "Unknown", "khoa": "", "email": "", "sdt": ""}

    def get_pending_forms(self, lecturer_id=None):
        query = """
            SELECT p.id, p.masv, sv.ten, sv.lop, p.ngay_nop, p.diem_tu_cham, 
                   p.ten_minh_chung, p.file_minh_chung, p.chi_tiet_tieu_chi
            FROM PhieuRenLuyen p
            JOIN SinhVien sv ON p.masv = sv.masv
            WHERE p.trang_thai = N'Chờ duyệt'
        """
        data = self._execute_query(query)
        result = []
        if data:
            for row in data:
                ngay = row['ngay_nop'].strftime("%d/%m/%Y") if row['ngay_nop'] else ""
                chi_tiet = []
                if row['chi_tiet_tieu_chi']:
                    try: chi_tiet = json.loads(row['chi_tiet_tieu_chi'])
                    except: chi_tiet = []

                result.append((
                    row['masv'], row['ten'], row['lop'], ngay, f"PH{row['id']:03d}",
                    {
                        "id_goc": row['id'],
                        "diem_tu_cham": row['diem_tu_cham'],
                        "ten_minh_chung": row['ten_minh_chung'],
                        "file_dinh_kem": row['file_minh_chung'],
                        "chi_tiet_tich": chi_tiet
                    }
                ))
        return result

    def approve_form(self, form_id_original, lecturer_name, status, note=""):
        query = "UPDATE PhieuRenLuyen SET trang_thai = ?, nguoi_duyet = ? WHERE id = ?"
        return self._execute_query(query, (status, lecturer_name, form_id_original), commit=True)

    def get_class_list(self, lecturer_id=None):
        query = "SELECT masv, ten, ngay_sinh, gioi_tinh, lop FROM SinhVien"
        data = self._execute_query(query)
        result = []
        if data:
            for i, row in enumerate(data):
                ns = row['ngay_sinh'].strftime("%d/%m/%Y") if row['ngay_sinh'] else ""
                result.append((i + 1, row['masv'], row['ten'], ns, row['gioi_tinh'], row['lop']))
        return result

    def get_lecturer_history(self, lecturer_name):
        query = """
            SELECT p.masv, sv.ten, p.ngay_nop, p.trang_thai, p.diem_tong
            FROM PhieuRenLuyen p
            JOIN SinhVien sv ON p.masv = sv.masv
            WHERE p.nguoi_duyet = ?
            ORDER BY p.ngay_nop DESC
        """
        data = self._execute_query(query, (lecturer_name,))
        result = []
        if data:
            for row in data:
                ngay = row['ngay_nop'].strftime("%d/%m/%Y") if row['ngay_nop'] else ""
                result.append((row['masv'], row['ten'], ngay, row['trang_thai'], f"{row['diem_tong']} điểm"))
        return result

    # =========================================================================
    # 4. CHỨC NĂNG CHUNG (THỐNG KÊ & THÔNG BÁO)
    # =========================================================================
    def get_class_statistics(self, student_id=None, class_name=None):
        try:
            target_class = class_name
            if not target_class and student_id:
                row_lop = self._execute_query("SELECT lop FROM SinhVien WHERE masv = ?", (student_id,), fetch_one=True)
                if row_lop: target_class = row_lop['lop']

            if target_class:
                query = """
                    SELECT p.diem_tong FROM PhieuRenLuyen p
                    JOIN SinhVien sv ON p.masv = sv.masv
                    WHERE sv.lop = ? AND p.trang_thai = N'Đã duyệt'
                """
                params = (target_class,)
            else:
                query = "SELECT diem_tong FROM PhieuRenLuyen WHERE trang_thai = N'Đã duyệt'"
                params = ()

            data = self._execute_query(query, params)
            stats = {"Xuất sắc": 0, "Giỏi": 0, "Khá": 0, "TB/Yếu": 0}
            
            if data:
                for row in data:
                    d = row['diem_tong']
                    if d is None: continue
                    if d >= 90: stats["Xuất sắc"] += 1
                    elif d >= 80: stats["Giỏi"] += 1
                    elif d >= 65: stats["Khá"] += 1
                    else: stats["TB/Yếu"] += 1
            
            return [
                ("Xuất sắc", stats["Xuất sắc"], "#2ecc71"),
                ("Giỏi", stats["Giỏi"], "#3498db"),
                ("Khá", stats["Khá"], "#f1c40f"),
                ("TB/Yếu", stats["TB/Yếu"], "#e74c3c")
            ]
        except Exception as e:
            print(f"Lỗi thống kê: {e}")
            return []

    def get_notifications(self, role):
        query = "SELECT * FROM ThongBao WHERE doi_tuong_nhan = ? OR doi_tuong_nhan = 'ALL' ORDER BY ngay_gui DESC"
        data = self._execute_query(query, (role,))
        result = []
        if data:
            for row in data:
                ngay = row['ngay_gui'].strftime("%d/%m") if row['ngay_gui'] else ""
                result.append((row['tieu_de'], row['noi_dung'], row['nguoi_gui'], ngay, row['loai_thong_bao']))
        return result
    
    def get_periods(self):
        query = "SELECT id, ten_dot, ngay_bat_dau_sv, ngay_ket_thuc_sv, trang_thai FROM DotDanhGia ORDER BY id DESC"
        data = self._execute_query(query)
        result = []
        if data:
            for i, row in enumerate(data):
                bd = row['ngay_bat_dau_sv'].strftime('%d/%m/%Y') if row['ngay_bat_dau_sv'] else "..."
                kt = row['ngay_ket_thuc_sv'].strftime('%d/%m/%Y') if row['ngay_ket_thuc_sv'] else "..."
                
                # Trả về 5 giá trị chuẩn để View dùng
                result.append((
                    row['id'],          # 0. ID thật
                    row['ten_dot'],     # 1. Tên
                    bd,                 # 2. Bắt đầu
                    kt,                 # 3. Kết thúc
                    row['trang_thai']   # 4. Trạng thái
                ))
        return result

    # =========================================================================
    # 5. CHỨC NĂNG CHO QUẢN LÝ (MANAGER / ADMIN)
    # =========================================================================

    def get_all_users(self, role=None):
        query = "SELECT ma_dang_nhap, ten, vai_tro FROM Users"
        params = ()
        if role:
            query += " WHERE vai_tro = ?"
            params = (role,)
        query += " ORDER BY ma_dang_nhap"
        
        data = self._execute_query(query, params)
        return [(row['ma_dang_nhap'], row['ten'], row['vai_tro']) for row in data] if data else []

    def add_user_full(self, username, password, fullname, role, extra_info=None):
        try:
            self._execute_query(
                "INSERT INTO Users (ma_dang_nhap, mat_khau, ten, vai_tro) VALUES (?, ?, ?, ?)", 
                (username, password, fullname, role), commit=True
            )
            if role == 'SV' and extra_info:
                query_sv = """
                    INSERT INTO SinhVien (masv, ten, lop, ngay_sinh, gioi_tinh, que_quan, email, sdt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                email = extra_info.get('email', f"{username}@uneti.edu.vn")
                self._execute_query(query_sv, (
                    username, fullname, 
                    extra_info.get('lop', 'K15'), 
                    extra_info.get('ngaysinh', '2000-01-01'),
                    extra_info.get('gioitinh', 'Nam'),
                    extra_info.get('quequan', 'Hà Nội'),
                    email,
                    extra_info.get('sdt', '')
                ), commit=True)
            return True
        except Exception as e:
            print(f"Lỗi thêm user: {e}")
            return False

    def delete_user_system(self, username):
        try:
            self._execute_query("DELETE FROM PhieuRenLuyen WHERE masv = ?", (username,), commit=True)
            self._execute_query("DELETE FROM SinhVien WHERE masv = ?", (username,), commit=True)
            return self._execute_query("DELETE FROM Users WHERE ma_dang_nhap = ?", (username,), commit=True)
        except Exception as e:
            print(f"Lỗi xóa user: {e}")
            return False

    def create_period(self, name, start_date, end_date):
        try:
            query = """
                INSERT INTO DotDanhGia (ten_dot, ngay_bat_dau_sv, ngay_ket_thuc_sv, trang_thai)
                VALUES (?, ?, ?, N'Hoạt động')
            """
            return self._execute_query(query, (name, start_date, end_date), commit=True)
        except: return False

    def delete_period(self, period_id):
        """Xóa đợt đánh giá và toàn bộ phiếu liên quan"""
        try:
            # 1. Xóa phiếu rèn luyện trước
            self._execute_query("DELETE FROM PhieuRenLuyen WHERE ma_dot = ?", (period_id,), commit=True)
            # 2. Xóa đợt
            query = "DELETE FROM DotDanhGia WHERE id = ?"
            return self._execute_query(query, (period_id,), commit=True)
        except Exception as e:
            print(f"Lỗi xóa đợt: {e}")
            return False

    def set_period_status(self, period_id, status):
        try:
            query = "UPDATE DotDanhGia SET trang_thai = ? WHERE id = ?"
            return self._execute_query(query, (status, period_id), commit=True)
        except Exception as e:
            print(f"Lỗi set status: {e}")
            return False

    def get_school_statistics(self):
        try:
            count_sv = self._execute_query("SELECT COUNT(*) as c FROM Users WHERE vai_tro='SV'", fetch_one=True)['c']
            count_gv = self._execute_query("SELECT COUNT(*) as c FROM Users WHERE vai_tro='GV'", fetch_one=True)['c']
            count_phieu = self._execute_query("SELECT COUNT(*) as c FROM PhieuRenLuyen", fetch_one=True)['c']
            return {"sv": count_sv, "gv": count_gv, "phieu": count_phieu}
        except:
            return {"sv": 0, "gv": 0, "phieu": 0}

    def create_notification(self, title, content, sender, target):
        try:
            query = """
                INSERT INTO ThongBao (tieu_de, noi_dung, nguoi_gui, ngay_gui, doi_tuong_nhan, loai_thong_bao)
                VALUES (?, ?, ?, GETDATE(), ?, N'Thông báo')
            """
            return self._execute_query(query, (title, content, sender, target), commit=True)
        except Exception as e:
            print(f"Lỗi tạo thông báo: {e}")
            return False

    def get_department_stats(self):
        try:
            total_sv = self._execute_query("SELECT COUNT(*) as c FROM Users WHERE vai_tro='SV'", fetch_one=True)['c']
            total_gv = self._execute_query("SELECT COUNT(*) as c FROM Users WHERE vai_tro='GV'", fetch_one=True)['c']
            total_forms = self._execute_query("SELECT COUNT(*) as c FROM PhieuRenLuyen", fetch_one=True)['c']
            approved_forms = self._execute_query("SELECT COUNT(*) as c FROM PhieuRenLuyen WHERE trang_thai = N'Đã duyệt'", fetch_one=True)['c']
            
            return {
                "sv": total_sv,
                "gv": total_gv,
                "phieu": total_forms,
                "duyet": approved_forms
            }
        except:
            return {"sv": 0, "gv": 0, "phieu": 0, "duyet": 0}

    # =========================================================================
    # 6. QUẢN LÝ TIÊU CHÍ (DYNAMIC)
    # =========================================================================
    def init_criteria_table(self):
        try:
            sql_create = """
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[TieuChiMau]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE TieuChiMau (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        nhom_tieu_chi NVARCHAR(255),
                        noi_dung NVARCHAR(MAX),
                        diem_toi_da INT
                    )
                END
            """
            self._execute_query(sql_create, commit=True)

            check = self._execute_query("SELECT COUNT(*) as c FROM TieuChiMau", fetch_one=True)
            if check['c'] == 0:
                print("--- Đang khởi tạo bộ tiêu chí gốc ---")
                default_data = [
                    ("I. Ý thức tham gia học tập", "Đạt điểm TB học tập trên 9.0", 5),
                    ("I. Ý thức tham gia học tập", "Đạt điểm TB học tập từ 8.0 đến 9.0", 3),
                    ("I. Ý thức tham gia học tập", "Đạt điểm TB học tập từ 7.0 đến 8.0", 2),
                    ("I. Ý thức tham gia học tập", "Có tinh thần vượt khó, vươn lên", 2),
                    ("I. Ý thức tham gia học tập", "Tham gia CLB học thuật, NCKH, thi Olympic", 2),
                    ("II. Ý thức chấp hành nội quy", "Có hành động tích cực trên MXH", 5),
                    ("II. Ý thức chấp hành nội quy", "Tham gia thực tập, hội thảo kỹ năng mềm", 2),
                    ("III. Hoạt động chính trị, xã hội", "Là Đảng viên/Đoàn viên ưu tú", 3),
                    ("III. Hoạt động chính trị, xã hội", "Tham gia tình nguyện, hiến máu", 3),
                    ("III. Hoạt động chính trị, xã hội", "Tham gia hoạt động CLB Đoàn/Hội", 2),
                    ("IV. Ý thức công dân", "Tuyên truyền chủ trương Đảng, pháp luật", 3),
                    ("IV. Ý thức công dân", "Giữ gìn an ninh trật tự", 2),
                    ("V. Cán bộ lớp & Thành tích", "Lớp trưởng, Bí thư (Tốt)", 5),
                    ("V. Cán bộ lớp & Thành tích", "Lớp phó, Phó bí thư", 3),
                    ("V. Cán bộ lớp & Thành tích", "Tổ trưởng, Cán sự", 2)
                ]
                
                insert_query = "INSERT INTO TieuChiMau (nhom_tieu_chi, noi_dung, diem_toi_da) VALUES (?, ?, ?)"
                cursor = self.conn.cursor()
                for nhom, nd, diem in default_data:
                    cursor.execute(insert_query, (nhom, nd, diem))
                self.conn.commit()
                
        except Exception as e:
            print(f"Lỗi init tiêu chí: {e}")

    def get_grading_criteria(self):
        self.init_criteria_table() 
        query = "SELECT nhom_tieu_chi, noi_dung, diem_toi_da FROM TieuChiMau ORDER BY id"
        data = self._execute_query(query)
        grouped = {}
        order = []
        if data:
            for row in data:
                nhom = row['nhom_tieu_chi']
                if nhom not in grouped: 
                    grouped[nhom] = []
                    order.append(nhom)
                grouped[nhom].append((row['noi_dung'], row['diem_toi_da']))
        return [(nhom, grouped[nhom]) for nhom in order]

    def update_grading_criteria(self, new_data_list):
        try:
            self._execute_query("DELETE FROM TieuChiMau", commit=True)
            insert_query = "INSERT INTO TieuChiMau (nhom_tieu_chi, noi_dung, diem_toi_da) VALUES (?, ?, ?)"
            cursor = self.conn.cursor()
            for nhom, items in new_data_list:
                for noi_dung, diem in items:
                    cursor.execute(insert_query, (nhom, noi_dung, diem))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi cập nhật tiêu chí: {e}")
            self.conn.rollback()
            return False
            
    # HÀM CHO ADMIN SỬA PHIẾU
    def get_all_forms_admin(self):
        query = """
            SELECT p.id, p.masv, sv.ten, p.diem_tong, p.trang_thai, d.ten_dot, p.chi_tiet_tieu_chi
            FROM PhieuRenLuyen p
            JOIN SinhVien sv ON p.masv = sv.masv
            JOIN DotDanhGia d ON p.ma_dot = d.id
            ORDER BY p.ngay_nop DESC
        """
        data = self._execute_query(query)
        result = []
        if data:
            for row in data:
                criteria_list = []
                if row['chi_tiet_tieu_chi']:
                    try: criteria_list = json.loads(row['chi_tiet_tieu_chi'])
                    except: criteria_list = []

                result.append((
                    f"PH{row['id']:03d}", 
                    row['masv'],
                    row['ten'],
                    str(row['diem_tong']),
                    row['trang_thai'],
                    row['ten_dot'],
                    row['id'],
                    criteria_list
                ))
        return result

    def update_form_detailed(self, form_id, new_status, new_total_score, new_criteria_list):
        try:
            json_criteria = json.dumps(new_criteria_list, ensure_ascii=False)
            query = """
                UPDATE PhieuRenLuyen 
                SET trang_thai = ?, diem_tong = ?, chi_tiet_tieu_chi = ?
                WHERE id = ?
            """
            return self._execute_query(query, (new_status, new_total_score, json_criteria, form_id), commit=True)
        except Exception as e:
            print(f"Lỗi update phiếu: {e}")
            return False

# --- HÀM HỖ TRỢ ---
def validate_login(username, password):
    db = DBHandler()
    res = db.check_login(username, password)
    if res:
        return {"username": username, "name": res['ten'], "role": res['vai_tro']}
    return None