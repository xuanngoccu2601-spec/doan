import customtkinter as ctk
from tkinter import messagebox, ttk
from data.db_handler import DBHandler 

# --- BẢNG MÀU ---
COLOR_SIDEBAR = "#2c3e50"       
COLOR_BG_MAIN = "#ecf0f1"       
COLOR_TEXT_MAIN = "#2c3e50"     
COLOR_TEXT_SIDEBAR = "#ecf0f1"  
COLOR_DANGER = "#c0392b"
COLOR_ACCENT = "#2980b9"
COLOR_SUCCESS = "#27ae60"

class ManagerDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DBHandler()
        self.windows = {}

        # 1. SIDEBAR
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR)
        sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(sidebar, text="QUẢN LÝ", font=("Roboto Medium", 22), text_color=COLOR_TEXT_SIDEBAR).pack(pady=(40, 50))
        
        # Nút menu bên trái
        ctk.CTkButton(sidebar, text="🏠 Tổng quan", font=("Roboto Medium", 14), fg_color="transparent", anchor="w", 
                      command=self.render_home).pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(sidebar, text="🚪 Đăng xuất", fg_color=COLOR_DANGER, height=40, 
                      command=self.confirm_logout).pack(side="bottom", pady=30, padx=20, fill="x")

        # 2. MAIN CONTENT
        self.content_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.render_home()

    def clear_content(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()

    @property
    def current_manager_name(self):
        return self.controller.user_data.get('name', 'Admin')

    # =========================================================================
    # HÀM HỖ TRỢ CHUNG
    # =========================================================================
    def center_window(self, window, width, height):
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def check_window_exists(self, name):
        for key, win in self.windows.items():
            if key != name and win.winfo_exists(): win.withdraw()
        if name in self.windows and self.windows[name].winfo_exists():
            self.windows[name].deiconify(); self.windows[name].lift(); return True
        return False
    
    def setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Roboto Medium", 12), background="#bdc3c7", foreground="#333")
        style.configure("Treeview", font=("Arial", 11), rowheight=30)

    # =========================================================================
    # TRANG CHỦ: HIỂN THỊ 6 Ô CHỨC NĂNG
    # =========================================================================
    def render_home(self):
        self.clear_content()
        
        # Tiêu đề
        ctk.CTkLabel(self.content_frame, text="QUẢN TRỊ HỆ THỐNG", font=("Roboto Medium", 28), text_color=COLOR_TEXT_MAIN).pack(pady=(50, 30))

        # Grid Container nằm giữa màn hình
        grid_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid_container.pack(expand=True, fill="both", padx=50, pady=(0, 50))
        
        grid_container.columnconfigure((0, 1, 2), weight=1)
        grid_container.rowconfigure((0, 1), weight=1)

        # Danh sách 6 chức năng chuẩn
        buttons = [
            {"text": "Hồ sơ Sinh viên", "icon": "🎓", "cmd": self.open_manage_student, "col": "#3498db"},
            {"text": "Hồ sơ Giảng viên", "icon": "💼", "cmd": self.open_manage_lecturer, "col": "#e67e22"},
            {"text": "Hệ thống phiếu", "icon": "⚙️", "cmd": self.open_manage_periods, "col": "#1abc9c"},
            
            {"text": "Thống kê khoa", "icon": "📊", "cmd": self.open_dept_statistics, "col": "#9b59b6"},
            {"text": "Chỉnh sửa phiếu", "icon": "📝", "cmd": self.open_manage_criteria, "col": "#e74c3c"},
            {"text": "Tạo thông báo", "icon": "🔔", "cmd": self.open_create_notification, "col": "#34495e"}
        ]

        for i, btn in enumerate(buttons):
            card = ctk.CTkButton(
                grid_container,
                text=f"{btn['icon']}\n\n{btn['text']}",
                font=("Roboto Medium", 20),
                fg_color="white",
                text_color=btn["col"],
                hover_color="#f5f6fa",
                corner_radius=15,
                border_width=2,
                border_color=btn["col"],
                command=btn["cmd"]
            )
            card.grid(row=i//3, column=i%3, padx=15, pady=15, sticky="nsew")

    # =========================================================================
    # 1 & 2. QUẢN LÝ USER (SV & GV)
    # =========================================================================
    def open_manage_student(self): self.simple_user_manager("SV", "Quản lý Sinh viên")
    def open_manage_lecturer(self): self.simple_user_manager("GV", "Quản lý Giảng viên")

    def simple_user_manager(self, role, title):
        if self.check_window_exists(f"m_{role}"): return
        w = ctk.CTkToplevel(self); w.title(title); self.center_window(w, 900, 600)
        w.attributes("-topmost", True); w.configure(fg_color="white"); self.windows[f"m_{role}"] = w
        
        ctk.CTkLabel(w, text=title, font=("Roboto Medium", 20), text_color=COLOR_TEXT_MAIN).pack(pady=15)
        
        self.setup_treeview_style()
        cols = ("Mã", "Họ Tên", "Vai trò")
        tree = ttk.Treeview(w, columns=cols, show="headings")
        tree.column("Mã", width=150, anchor="center"); tree.column("Họ Tên", width=300)
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        def load():
            for i in tree.get_children(): tree.delete(i)
            for u in self.db.get_all_users(role): tree.insert("", "end", values=u)
        load()
        
        btn_frame = ctk.CTkFrame(w, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        def add(): self.open_add_user_dialog(w, role, load)
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno("Xóa", "Bạn chắc chắn xóa?"):
                self.db.delete_user_system(tree.item(sel[0])['values'][0]); load()
        
        ctk.CTkButton(btn_frame, text="+ Thêm mới", fg_color=COLOR_SUCCESS, width=150, command=add).pack(side="left")
        ctk.CTkButton(btn_frame, text="- Xóa bỏ", fg_color=COLOR_DANGER, width=150, command=delete).pack(side="right")

    def open_add_user_dialog(self, parent, role, callback):
        d = ctk.CTkToplevel(self); d.title(f"Thêm {role}"); self.center_window(d, 400, 450); d.attributes("-topmost", True)
        ctk.CTkLabel(d, text=f"THÊM MỚI {role}", font=("Roboto Medium", 18)).pack(pady=20)
        e1 = ctk.CTkEntry(d, placeholder_text="Mã đăng nhập"); e1.pack(pady=5)
        e2 = ctk.CTkEntry(d, placeholder_text="Họ tên"); e2.pack(pady=5)
        e3 = ctk.CTkEntry(d, placeholder_text="Mật khẩu"); e3.pack(pady=5)
        e4 = ctk.CTkEntry(d, placeholder_text="Lớp")
        if role == "SV": e4.pack(pady=5)
        
        def save():
            ex = {"lop": e4.get()} if role == "SV" else {}
            if self.db.add_user_full(e1.get(), e3.get(), e2.get(), role, ex):
                messagebox.showinfo("Xong", "Đã thêm!", parent=d); callback(); d.destroy()
            else: messagebox.showerror("Lỗi", "Trùng mã!", parent=d)
        ctk.CTkButton(d, text="Lưu", command=save).pack(pady=20)

    # =========================================================================
    # 3. HỆ THỐNG PHIẾU (ĐÓNG/MỞ ĐỢT)
    # =========================================================================
    def open_manage_periods(self):
        if self.check_window_exists("m_period"): return
        window = ctk.CTkToplevel(self)
        window.title("Hệ thống quản lý phiếu")
        self.center_window(window, 900, 600)
        window.attributes("-topmost", True); window.configure(fg_color="white")
        self.windows["m_period"] = window

        ctk.CTkLabel(window, text="QUẢN LÝ HỆ THỐNG PHIẾU ĐÁNH GIÁ", font=("Roboto Medium", 20), text_color=COLOR_SIDEBAR).pack(pady=15)
        
        self.setup_treeview_style()
        cols = ("ID", "Tên đợt", "Bắt đầu", "Kết thúc", "Trạng thái")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        tree.column("ID", width=50, anchor="center"); tree.column("Tên đợt", width=250)
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, padx=30, pady=10)

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            data = self.db.get_periods()
            for r in data: tree.insert("", "end", values=(r[0], r[1], r[2], r[4], r[5]))
        refresh()

        action_frame = ctk.CTkFrame(window, fg_color="#ecf0f1", corner_radius=10)
        action_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(action_frame, text="Điều khiển trạng thái:", font=("Arial", 13, "bold"), text_color="#333").pack(side="left", padx=15, pady=10)

        def change_status(status_text):
            sel = tree.selection()
            if not sel: messagebox.showwarning("Lỗi", "Chọn đợt cần đổi!", parent=window); return
            period_id = tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Xác nhận", f"Bạn muốn chuyển thành: {status_text}?", parent=window):
                if self.db.set_period_status(period_id, status_text): refresh(); messagebox.showinfo("OK", "Đã cập nhật!")
                else: messagebox.showerror("Lỗi", "Lỗi DB!")

        ctk.CTkButton(action_frame, text="🔓 MỞ PHIẾU", fg_color=COLOR_SUCCESS, width=150, command=lambda: change_status("Hoạt động")).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔒 ĐÓNG PHIẾU", fg_color=COLOR_DANGER, width=150, command=lambda: change_status("Đã đóng")).pack(side="left", padx=5)

        add_frame = ctk.CTkFrame(window, fg_color="white", border_width=1, border_color="#ccc")
        add_frame.pack(fill="x", padx=30, pady=10)
        e1 = ctk.CTkEntry(add_frame, placeholder_text="Tên đợt (VD: HK2 2025)", width=200); e1.pack(side="left", padx=5, pady=10)
        e2 = ctk.CTkEntry(add_frame, placeholder_text="Bắt đầu (yyyy-mm-dd)", width=140); e2.pack(side="left", padx=5)
        e3 = ctk.CTkEntry(add_frame, placeholder_text="Kết thúc (yyyy-mm-dd)", width=140); e3.pack(side="left", padx=5)
        
        def add():
            if self.db.create_period(e1.get(), e2.get(), e3.get()): messagebox.showinfo("Xong", "Đã tạo & MỞ!"); refresh()
            else: messagebox.showerror("Lỗi", "Lỗi tạo đợt!")
        ctk.CTkButton(add_frame, text="+ Tạo Mới", width=100, fg_color=COLOR_ACCENT, command=add).pack(side="right", padx=10)

    # =========================================================================
    # 4. THỐNG KÊ KHOA
    # =========================================================================
    def open_dept_statistics(self):
        if self.check_window_exists("stats"): return
        w = ctk.CTkToplevel(self); w.title("Thống kê"); self.center_window(w, 500, 400); w.attributes("-topmost", True)
        self.windows["stats"] = w; w.configure(fg_color="white")
        
        ctk.CTkLabel(w, text="THỐNG KÊ TOÀN KHOA", font=("Roboto Medium", 20), text_color=COLOR_TEXT_MAIN).pack(pady=20)
        s = self.db.get_department_stats()
        
        grid = ctk.CTkFrame(w, fg_color="transparent")
        grid.pack(fill="both", padx=50)
        items = [("Tổng Sinh viên", s['sv']), ("Tổng Giảng viên", s['gv']), ("Phiếu đã nộp", s['phieu']), ("Phiếu đã duyệt", s['duyet'])]
        
        for lb, val in items:
            row = ctk.CTkFrame(grid, fg_color="transparent")
            row.pack(fill="x", pady=10)
            ctk.CTkLabel(row, text=lb, font=("Arial", 14), text_color="gray", anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(val), font=("Arial", 16, "bold"), text_color=COLOR_ACCENT).pack(side="right")
            ctk.CTkFrame(grid, height=1, fg_color="#eee").pack(fill="x")

    # =========================================================================
    # 5. CHỈNH SỬA PHIẾU (QUẢN LÝ TIÊU CHÍ)
    # =========================================================================
    def open_manage_criteria(self):
        if self.check_window_exists("manage_criteria"): return
        window = ctk.CTkToplevel(self)
        window.title("Chỉnh sửa cấu trúc phiếu")
        self.center_window(window, 1000, 700)
        window.attributes("-topmost", True); window.configure(fg_color="white")
        self.windows["manage_criteria"] = window

        ctk.CTkLabel(window, text="CHỈNH SỬA TIÊU CHÍ ĐÁNH GIÁ (GỐC)", font=("Roboto Medium", 20), text_color=COLOR_TEXT_MAIN).pack(pady=15)
        
        scroll = ctk.CTkScrollableFrame(window, fg_color="#f8f9fa", border_width=1, border_color="#ccc")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        current_data = self.db.get_grading_criteria() 
        self.criteria_entries = [] 

        def render_list():
            for w in scroll.winfo_children(): w.destroy()
            self.criteria_entries = []

            for nhom_idx, (nhom_title, items) in enumerate(current_data):
                gr_frame = ctk.CTkFrame(scroll, fg_color="#e1e8ed", corner_radius=5)
                gr_frame.pack(fill="x", pady=(15, 5))
                
                e_nhom = ctk.CTkEntry(gr_frame, font=("Arial", 14, "bold"), width=500, fg_color="transparent", border_width=0)
                e_nhom.insert(0, nhom_title); e_nhom.pack(side="left", padx=10, pady=5)
                
                ctk.CTkButton(gr_frame, text="+ Thêm dòng", width=80, height=25, fg_color="#2980b9", 
                              command=lambda idx=nhom_idx: add_item(idx)).pack(side="right", padx=10)

                item_widgets = []
                for item_idx, (noi_dung, diem) in enumerate(items):
                    row = ctk.CTkFrame(scroll, fg_color="white")
                    row.pack(fill="x", pady=2, padx=10)
                    
                    e_nd = ctk.CTkEntry(row, width=600, border_color="#ddd"); e_nd.insert(0, noi_dung)
                    e_nd.pack(side="left", padx=5, fill="x", expand=True)
                    
                    e_diem = ctk.CTkEntry(row, width=50, justify="center", border_color="#ddd"); e_diem.insert(0, str(diem))
                    e_diem.pack(side="left", padx=5)
                    ctk.CTkLabel(row, text="điểm", width=30).pack(side="left")

                    ctk.CTkButton(row, text="Xóa", width=50, fg_color=COLOR_DANGER, 
                                  command=lambda g=nhom_idx, i=item_idx: delete_item(g, i)).pack(side="right", padx=5)

                    item_widgets.append((e_nd, e_diem))
                
                self.criteria_entries.append((e_nhom, item_widgets))

        def save_temp_state():
            new_state = []
            for e_nhom, item_ws in self.criteria_entries:
                try:
                    nhom_title = e_nhom.get()
                    items = []
                    for e_nd, e_diem in item_ws:
                        try:
                            d = int(e_diem.get())
                            items.append((e_nd.get(), d))
                        except: pass
                    new_state.append((nhom_title, items))
                except: pass
            return new_state

        def add_item(group_index):
            nonlocal current_data
            current_data = save_temp_state()
            current_data[group_index][1].append(("", 0))
            render_list()

        def delete_item(group_index, item_index):
            nonlocal current_data
            current_data = save_temp_state()
            del current_data[group_index][1][item_index]
            render_list()

        def add_new_group():
            nonlocal current_data
            current_data = save_temp_state()
            current_data.append(("Nhóm Mới", [("Nội dung mới", 0)]))
            render_list()

        def save_to_db():
            final_data = save_temp_state()
            if self.db.update_grading_criteria(final_data):
                messagebox.showinfo("Thành công", "Đã cập nhật tiêu chí!", parent=window); window.destroy()
            else: messagebox.showerror("Lỗi", "Lỗi lưu DB!", parent=window)

        render_list() 

        ft = ctk.CTkFrame(window, fg_color="white", height=60)
        ft.pack(fill="x", pady=10)
        ctk.CTkButton(ft, text="+ Thêm Nhóm Lớn", fg_color="#34495e", command=add_new_group).pack(side="left", padx=20)
        ctk.CTkButton(ft, text="LƯU CẤU HÌNH", fg_color=COLOR_SUCCESS, width=200, height=40, command=save_to_db).pack(side="right", padx=20)

    # =========================================================================
    # 6. TẠO THÔNG BÁO
    # =========================================================================
    def open_create_notification(self):
        if self.check_window_exists("noti"): return
        w = ctk.CTkToplevel(self); w.title("Tạo thông báo"); self.center_window(w, 500, 400); w.attributes("-topmost", True)
        self.windows["noti"] = w; w.configure(fg_color="white")
        
        ctk.CTkLabel(w, text="TẠO THÔNG BÁO", font=("Arial", 18, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=15)
        e1 = ctk.CTkEntry(w, placeholder_text="Tiêu đề"); e1.pack(fill="x", padx=30, pady=5)
        e2 = ctk.CTkTextbox(w, height=150); e2.pack(fill="x", padx=30, pady=5)
        c = ctk.CTkComboBox(w, values=["ALL", "SV", "GV"]); c.pack(pady=5)
        
        def send(): 
            self.db.create_notification(e1.get(), e2.get("0.0", "end"), "Admin", c.get()); messagebox.showinfo("OK", "Đã gửi!"); w.destroy()
        ctk.CTkButton(w, text="Gửi", command=send).pack(pady=10)

    def confirm_logout(self):
        if messagebox.askokcancel("Đăng xuất", "Bạn muốn đăng xuất?"): self.controller.show_frame("LoginView")