import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import json
import os
from data.db_handler import DBHandler 

# --- BẢNG MÀU MODERN UI ---
COLOR_SIDEBAR = "#2c3e50"       # Xanh đen (Sidebar)
COLOR_BG_MAIN = "#ecf0f1"       # Xám nhạt (Nền chính)
COLOR_CARD_BG = "#ffffff"       # Trắng (Nền thẻ)
COLOR_ACCENT = "#1abc9c"        # Xanh ngọc (Màu phụ)
COLOR_HOVER = "#16a085"         # Xanh ngọc đậm (Hover phụ)
COLOR_TEXT_MAIN = "#2c3e50"     # Màu chữ chính
COLOR_TEXT_SIDEBAR = "#ecf0f1"  # Màu chữ sidebar
COLOR_DANGER = "#e74c3c"        # Đỏ (Từ chối/Đăng xuất)
COLOR_SUCCESS = "#27ae60"       # Xanh lá (Duyệt)

# MÀU ĐÃ ÁP DỤNG TỪ YÊU CẦU CỦA SV/GV
COLOR_BLUE_TITLE = "#00bfff"     # Xanh da trời sáng (Tiêu đề pop-up)
TEXT_COLOR_BLACK = "#000000"     # Màu Đen cho nội dung bảng & chữ chức năng
COLOR_HOVER_LIGHTBLUE = "#c5e3f8" # Màu chọn/hover bảng
COLOR_ACTION_BLUE = "#3498db" 
COLOR_ACTION_BLUE_HOVER = "#2980b9" 

# ĐỊNH NGHĨA MÀU ICON
ICON_COLOR_LIGHTBLUE = "#00bfff" 
ICON_COLOR_PURPLE = "#9b59b6"    
ICON_COLOR_ORANGE = "#e67e22"    
ICON_COLOR_BROWN = "#a0522d"     
ICON_COLOR_GREEN = "#2ecc71"     
ICON_COLOR_RED = "#e74c3c"       


class LecturerDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DBHandler()
        self.windows = {} 
        self.active_child_window = None 

        # =========================================================================
        # 1. SIDEBAR (ĐÃ CHỈNH SỬA CHIỀU RỘNG & PADX)
        # =========================================================================
        sidebar = ctk.CTkFrame(self, width=330, corner_radius=0, fg_color=COLOR_SIDEBAR) 
        sidebar.pack(side="left", fill="y")
        
        # Logo / Tiêu đề Sidebar
        ctk.CTkLabel(sidebar, text="Xin Chào", font=("Roboto Medium", 22), text_color=COLOR_TEXT_SIDEBAR).pack(pady=(40, 50))
        
        # Hàm tạo nút sidebar
        def create_sidebar_btn(text, cmd, icon="🔹"):
            btn = ctk.CTkButton(sidebar, text=f"{icon}  {text}", font=("Roboto Medium", 14), 
                                 fg_color="transparent", text_color="#bdc3c7", hover_color="#34495e", 
                                 anchor="w", height=45, command=cmd)
            # Dịch chuyển sang trái 7px (40 - 7 = 33)
            btn.pack(fill="x", padx=(33, 15), pady=5) 
            return btn

        create_sidebar_btn("Trang chủ", self.render_home, "🏠")
        create_sidebar_btn("Hồ sơ giảng viên", self.render_profile, "👤")
        create_sidebar_btn("Cài đặt tài khoản", self.render_account, "⚙️")

        # Nút Đăng xuất
        ctk.CTkButton(sidebar, text="Đăng xuất ⎘ →", fg_color=COLOR_DANGER, hover_color="#c0392b", 
                      height=40, font=("Roboto Medium", 14),
                      command=self.confirm_logout).pack(side="bottom", pady=30, padx=40, fill="x") 

        # =========================================================================
        # 2. MAIN CONTENT (NỘI DUNG CHÍNH)
        # =========================================================================
        self.content_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.render_home()

    @property
    def current_lecturer_id(self):
        return self.controller.user_data.get('username', 'GV_TEST')
    
    @property
    def current_lecturer_name(self):
        return self.controller.user_data.get('name', 'Giảng viên')

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # =========================================================================
    # HÀM HỖ TRỢ GIAO DIỆN
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
            self.windows[name].deiconify(); self.windows[name].lift(); self.windows[name].focus(); return True
        return False
    
    def setup_treeview_style(self):
        """Style bảng phẳng hiện đại với nội dung màu đen và màu chọn xanh nhạt."""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview.Heading", font=("Roboto Medium", 13), 
                         background="#ecf0f1", foreground=COLOR_TEXT_MAIN, relief="flat")
        style.map("Treeview.Heading", background=[('active', '#bdc3c7')])
        
        # Nội dung bảng màu đen, màu chọn xanh nhạt
        style.configure("Treeview", font=("Arial", 12), rowheight=35, 
                         background="white", fieldbackground="white", 
                         foreground=TEXT_COLOR_BLACK, borderwidth=0)
        style.map("Treeview", background=[('selected', COLOR_HOVER_LIGHTBLUE)], 
                              foreground=[('selected', TEXT_COLOR_BLACK)])

    # =========================================================================
    # TRANG CHỦ (ĐÃ SỬA TIÊU ĐỀ THÀNH "CHỨC NĂNG GIẢNG VIÊN")
    # =========================================================================
    def render_home(self):
        self.clear_content()
        
        # Header Tiêu đề chức năng
        welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        welcome_frame.pack(fill="x", pady=(0, 20), padx=30)
        
        # --- THAY ĐỔI Ở ĐÂY ---
        # Đổi "XIN CHÀO..." thành "CHỨC NĂNG GIẢNG VIÊN"
        ctk.CTkLabel(welcome_frame, text="CHỨC NĂNG GIẢNG VIÊN", 
                      font=("Roboto Medium", 24), text_color=COLOR_TEXT_MAIN).pack(side="left", pady=(80, 0))

        # Grid chứa các nút chức năng (Dạng Thẻ)
        grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=30, pady=(60, 10)) 
        grid.columnconfigure((0, 1, 2), weight=1)

        # Định nghĩa màu Icon
        funcs = [
            {"text": "Phiếu chờ duyệt", "icon": "📝", "cmd": self.open_pending_forms, "icon_color": ICON_COLOR_LIGHTBLUE},
            {"text": "Danh sách lớp", "icon": "📋", "cmd": self.open_class_list, "icon_color": ICON_COLOR_PURPLE},
            {"text": "Thống kê lớp", "icon": "📊", "cmd": self.open_class_statistics, "icon_color": ICON_COLOR_ORANGE},
            {"text": "Lịch sử duyệt", "icon": "🕒", "cmd": self.open_approval_history, "icon_color": ICON_COLOR_BROWN},
            {"text": "Thống kê Khoa", "icon": "🏢", "cmd": self.open_dept_statistics, "icon_color": ICON_COLOR_GREEN},
            {"text": "Thông báo", "icon": "🔔", "cmd": self.open_notifications, "icon_color": ICON_COLOR_RED}
        ]
        
        # LOGIC TẠO NÚT BẰNG FRAME VÀ LABEL
        for i, item in enumerate(funcs):
            # 1. Tạo Frame hoạt động như nút (Viền đen)
            card_frame = ctk.CTkFrame(
                grid, 
                fg_color="white", 
                corner_radius=15,
                border_width=2, 
                border_color=TEXT_COLOR_BLACK, # Khung viền màu đen
                height=150,
            )
            card_frame.grid(row=i//3, column=i%3, padx=15, pady=15, sticky="nsew")

            # 2. Tạo Icon Label (Lớn, có màu)
            icon_label = ctk.CTkLabel(
                card_frame, 
                text=item['icon'], 
                font=("Roboto Medium", 30), # Phóng to icon
                text_color=item['icon_color'], # Màu Icon riêng biệt
                fg_color="transparent"
            )
            # Căn chỉnh vị trí icon (gần chữ hơn)
            icon_label.place(relx=0.5, rely=0.35, anchor="center") 

            # 3. Tạo Text Label (Nhỏ hơn, màu đen)
            text_label = ctk.CTkLabel(
                card_frame, 
                text=item['text'], 
                font=("Roboto Medium", 18), 
                text_color=TEXT_COLOR_BLACK, # Chữ màu đen
                wraplength=150,
                justify="center",
                fg_color="transparent"
            )
            # Đặt chữ ở vị trí thấp hơn icon
            text_label.place(relx=0.5, rely=0.7, anchor="center")
            
            # --- LOGIC GÁN SỰ KIỆN HOVER ---
            def on_enter(e, frame=card_frame):
                frame.configure(fg_color=COLOR_HOVER_LIGHTBLUE) 
            def on_leave(e, frame=card_frame):
                frame.configure(fg_color="white")
                
            # Gán sự kiện click và hover
            click_command = lambda e, cmd=item['cmd']: cmd()
            
            card_frame.bind("<Button-1>", click_command)
            icon_label.bind("<Button-1>", click_command)
            text_label.bind("<Button-1>", click_command)
            
            card_frame.bind("<Enter>", on_enter); card_frame.bind("<Leave>", on_leave)
            icon_label.bind("<Enter>", on_enter); icon_label.bind("<Leave>", on_leave)
            text_label.bind("<Enter>", on_enter); text_label.bind("<Leave>", on_leave)


    # =========================================================================
    # TRANG HỒ SƠ & TÀI KHOẢN (ĐÃ SỬA NÚT QUAY LẠI SANG PHẢI DƯỚI)
    # =========================================================================
    def render_profile(self):
        self.clear_content()
        
        # Tiêu đề 
        ctk.CTkLabel(self.content_frame, text="HỒ SƠ GIẢNG VIÊN", font=("Roboto Medium", 26), 
                      text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=30, pady=(30, 20))
        
        info_card = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=15)
        info_card.pack(fill="both", expand=True, padx=50, pady=(10, 20)) 
        
        info = self.db.get_lecturer_info(self.current_lecturer_id)
        fields = [("Mã GV", info.get("magv")), ("Họ tên", info.get("ten")), ("Khoa/Viện", info.get("khoa")), ("Email", info.get("email")), ("SĐT", info.get("sdt"))]
        
        for i, (label, value) in enumerate(fields):
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=15)
            ctk.CTkLabel(row, text=label, font=("Arial", 14), text_color="#7f8c8d", width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=("Arial", 15, "bold"), text_color="#2c3e50", anchor="w").pack(side="left")
            if i < len(fields) - 1: 
                ctk.CTkFrame(info_card, height=1, fg_color="#ecf0f1").pack(fill="x", padx=40)

        # Nút Quay lại
        ctk.CTkButton(self.content_frame, text="← Quay lại", width=100, fg_color="transparent", 
                      text_color=COLOR_TEXT_MAIN, hover_color="#dfe6e9", border_width=1, 
                      command=self.render_home).pack(anchor="e", padx=30, pady=(0, 20))

    def render_account(self):
        self.clear_content()
        
        # Tiêu đề
        ctk.CTkLabel(self.content_frame, text="CÀI ĐẶT TÀI KHOẢN", font=("Roboto Medium", 26), 
                      text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=30, pady=(30, 20))
        
        menu_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=15)
        menu_frame.pack(fill="both", expand=True, padx=50, pady=(10, 20)) 
        
        def create_setting_item(text, cmd):
            btn = ctk.CTkButton(menu_frame, text=text, font=("Arial", 16), height=60, anchor="w",
                                 fg_color="transparent", text_color="#2c3e50", hover_color="#f1f2f6",
                                 command=cmd)
            btn.pack(fill="x", padx=20, pady=5)
            ctk.CTkFrame(menu_frame, height=1, fg_color="#ecf0f1").pack(fill="x", padx=20)

        create_setting_item("📖  Hướng dẫn sử dụng hệ thống", self.open_guide)
        create_setting_item("🔒  Đổi mật khẩu đăng nhập", self.open_change_password)

        # Nút Quay lại
        ctk.CTkButton(self.content_frame, text="← Quay lại", width=100, fg_color="transparent", 
                      text_color=COLOR_TEXT_MAIN, hover_color="#dfe6e9", border_width=1,
                      command=self.render_home).pack(anchor="e", padx=30, pady=(0, 20))

    # =========================================================================
    # 6 CHỨC NĂNG CHÍNH (POPUP WINDOWS)
    # =========================================================================

    # 1. PHIẾU CHỜ DUYỆT
    def open_pending_forms(self):
        if self.check_window_exists("pending"): return
        window = ctk.CTkToplevel(self)
        window.title("Phiếu chờ duyệt")
        self.center_window(window, 1100, 600)
        window.transient(self.controller) 
        window.configure(fg_color="white")
        self.windows["pending"] = window
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text="DANH SÁCH PHIẾU CHỜ DUYỆT", font=("Roboto Medium", 20), text_color=COLOR_BLUE_TITLE).pack(pady=20)
        self.setup_treeview_style()
        
        cols = ("Mã SV", "Tên SV", "Lớp", "Ngày nộp", "Mã Phiếu")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        for col in cols: tree.heading(col, text=col); tree.column(col, anchor="center", width=120)
        tree.column("Tên SV", width=200)
        tree.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        data = self.db.get_pending_forms(self.current_lecturer_id)
        self.pending_data_map = {} 

        if not data:
            ctk.CTkLabel(window, text="Hiện không có phiếu nào cần duyệt.", text_color="gray", font=("Arial", 14)).pack()
        
        for item in data:
            row_id = tree.insert("", "end", values=item[:5])
            self.pending_data_map[row_id] = item[5] # item[5] là full_details

        def process():
            selected = tree.selection()
            if not selected: messagebox.showwarning("Lỗi", "Vui lòng chọn phiếu!", parent=window); return
            row_id = selected[0]
            full_details = self.pending_data_map[row_id]
            item_values = tree.item(row_id, 'values')
            window.withdraw() # Ẩn cửa sổ danh sách
            self.open_review_dialog(item_values, full_details, tree, row_id, window)

        ctk.CTkButton(window, text="XEM CHI TIẾT & DUYỆT", fg_color=COLOR_ACTION_BLUE, hover_color=COLOR_ACTION_BLUE_HOVER, 
                      height=45, font=("Roboto Medium", 14), command=process).pack(fill="x", padx=50, pady=20)

    def open_review_dialog(self, basic_info, details, tree, row_id, parent_window):
        masv, tensv, lop, ngay, maphieu_str = basic_info
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Duyệt phiếu: {maphieu_str}")
        self.center_window(dialog, 800, 700)
        dialog.transient(parent_window)
        dialog.configure(fg_color="white")
        
        def on_close():
            parent_window.deiconify(); dialog.destroy()
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Header Dialog
        ctk.CTkLabel(dialog, text=f"DUYỆT PHIẾU: {tensv.upper()}", font=("Roboto Medium", 20), text_color=COLOR_SIDEBAR).pack(pady=20)
        
        # Info Box
        info_frame = ctk.CTkFrame(dialog, fg_color="#f1f2f6", corner_radius=10)
        info_frame.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(info_frame, text=f"Mã SV: {masv}  |  Lớp: {lop}  |  Ngày nộp: {ngay}", font=("Arial", 14), text_color="#333").pack(pady=10)
        ctk.CTkLabel(info_frame, text=f"ĐIỂM TỰ CHẤM: {details.get('diem_tu_cham', 0)} điểm", font=("Roboto Medium", 16), text_color=COLOR_DANGER).pack(pady=(0, 10))

        # Tiêu chí
        ctk.CTkLabel(dialog, text="Các mục sinh viên đã chọn:", font=("Roboto Medium", 14), text_color=COLOR_SIDEBAR).pack(fill="x", padx=30, pady=(15, 5))
        scroll = ctk.CTkScrollableFrame(dialog, fg_color="white", height=180, border_color="#bdc3c7", border_width=1)
        scroll.pack(fill="both", expand=True, padx=30, pady=5)
        
        ticked_items = details.get("chi_tiet_tich", [])
        if not ticked_items:
            ctk.CTkLabel(scroll, text="(Không có dữ liệu tiêu chí)", text_color="gray").pack(anchor="w")
        else:
            for item in ticked_items:
                ctk.CTkLabel(scroll, text=f"✅ {item}", anchor="w", justify="left", wraplength=680, text_color="#2c3e50", font=("Arial", 13)).pack(fill="x", pady=2)

        # File minh chứng
        ev_name = details.get("ten_minh_chung", "Không có")
        ev_file_path = details.get("file_dinh_kem", "")
        
        file_frame = ctk.CTkFrame(dialog, fg_color="#ecf0f1", corner_radius=8)
        file_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(file_frame, text=f"Minh chứng: {ev_name}", font=("Arial", 13, "bold"), text_color="#2980b9").pack(side="left", padx=15, pady=10)
        
        def open_file():
            if not ev_file_path: messagebox.showinfo("Thông báo", "Không có file!", parent=dialog); return
            first_file = ev_file_path.split(';')[0]
            if os.path.exists(first_file):
                try: os.startfile(first_file)
                except Exception as e: messagebox.showerror("Lỗi", str(e), parent=dialog)
            else: messagebox.showerror("Lỗi", f"Không tìm thấy file:\n{first_file}", parent=dialog)

        if ev_file_path:
            ctk.CTkButton(file_frame, text="👁 Xem file", width=100, height=30, fg_color="#34495e", hover_color="#2c3e50", command=open_file).pack(side="right", padx=15)
        else:
            ctk.CTkLabel(file_frame, text="(Không có file)", text_color="gray").pack(side="right", padx=15)

        # Nhận xét
        ctk.CTkLabel(dialog, text="Ghi chú / Nhận xét:", anchor="w", font=("Roboto Medium", 14), text_color=COLOR_SIDEBAR).pack(fill="x", padx=30)
        txt = ctk.CTkTextbox(dialog, height=60, border_color="#bdc3c7", border_width=1, fg_color="white", text_color="black"); txt.pack(fill="x", padx=30, pady=5)
        
        def confirm(status):
            id_goc = details['id_goc']
            if self.db.approve_form(id_goc, self.current_lecturer_name, status, txt.get("0.0", "end")):
                messagebox.showinfo("Xong", f"Đã {status} phiếu!", parent=dialog)
                tree.delete(row_id); on_close()
            else: messagebox.showerror("Lỗi", "Lỗi cập nhật Database!", parent=dialog)

        # Footer Button
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        ctk.CTkButton(btn_frame, text="TỪ CHỐI", fg_color=COLOR_DANGER, width=150, height=40, hover_color="#c0392b", command=lambda: confirm("Từ chối")).pack(side="left")
        ctk.CTkButton(btn_frame, text="DUYỆT PHIẾU", fg_color=COLOR_ACTION_BLUE, width=150, height=40, hover_color=COLOR_ACTION_BLUE_HOVER, command=lambda: confirm("Đã duyệt")).pack(side="right")

    # 2. DANH SÁCH LỚP
    def open_class_list(self):
        if self.check_window_exists("class_list"): return
        window = ctk.CTkToplevel(self)
        window.title("Danh sách lớp")
        self.center_window(window, 1000, 600)
        window.transient(self.controller) 
        window.configure(fg_color="white")
        self.windows["class_list"] = window
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text="DANH SÁCH SINH VIÊN QUẢN LÝ", font=("Roboto Medium", 20), text_color=COLOR_BLUE_TITLE).pack(pady=20)
        self.setup_treeview_style()
        cols = ("STT", "Mã SV", "Họ Tên", "Ngày sinh", "Giới tính", "Lớp")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        tree.column("STT", width=50, anchor="center"); tree.column("Họ Tên", width=250)
        for col in cols: tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        data = self.db.get_class_list(self.current_lecturer_id)
        for item in data: tree.insert("", "end", values=item)

    # 3. THỐNG KÊ LỚP
    def open_class_statistics(self):
        if self.check_window_exists("stats_class"): return
        window = ctk.CTkToplevel(self)
        window.title("Thống kê theo lớp")
        self.center_window(window, 700, 550)
        window.transient(self.controller) 
        window.configure(fg_color="white")
        self.windows["stats_class"] = window
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text="THỐNG KÊ LỚP", font=("Roboto Medium", 22), text_color=COLOR_BLUE_TITLE).pack(pady=15)

        input_frame = ctk.CTkFrame(window, fg_color="transparent")
        input_frame.pack(pady=10)
        entry_lop = ctk.CTkEntry(input_frame, placeholder_text="Nhập mã lớp (VD: CNTT1)", width=220, height=35)
        entry_lop.pack(side="left", padx=10)
        
        content_frame = ctk.CTkFrame(window, fg_color="white")
        content_frame.pack(fill="both", expand=True, padx=40, pady=10)

        def load_stats():
            for widget in content_frame.winfo_children(): widget.destroy()
            lop = entry_lop.get().strip()
            if not lop: messagebox.showwarning("Lỗi", "Nhập tên lớp!", parent=window); return

            stats_data = self.db.get_class_statistics(class_name=lop)
            total = sum([x[1] for x in stats_data])
            
            if total == 0: ctk.CTkLabel(content_frame, text=f"Không có dữ liệu cho {lop}", text_color="red").pack(pady=20); return
            ctk.CTkLabel(content_frame, text=f"Lớp: {lop} | Tổng: {total}", font=("Arial", 16, "bold"), text_color="#2c3e50").pack(pady=(0, 20), anchor="w")
            
            for label, count, color in stats_data:
                pct = (count/total)*100
                row = ctk.CTkFrame(content_frame, fg_color="transparent")
                row.pack(fill="x", pady=8)
                ctk.CTkLabel(row, text=label, width=120, anchor="w", font=("Arial", 14), text_color="black").pack(side="left")
                bg_bar = ctk.CTkFrame(row, height=18, width=300, fg_color="#ecf0f1", corner_radius=9); bg_bar.pack(side="left", padx=10)
                if pct > 0: ctk.CTkFrame(bg_bar, height=18, width=300*(pct/100), fg_color=color, corner_radius=9).place(x=0,y=0)
                ctk.CTkLabel(row, text=f"{count} ({pct:.1f}%)", width=100, anchor="e", font=("Arial", 13, "bold"), text_color="black").pack(side="right")

        ctk.CTkButton(input_frame, text="Xem thống kê", command=load_stats, width=120, height=35, fg_color=COLOR_ACTION_BLUE, hover_color=COLOR_ACTION_BLUE_HOVER).pack(side="left")

    # 4. LỊCH SỬ DUYỆT
    def open_approval_history(self):
        if self.check_window_exists("history"): return
        window = ctk.CTkToplevel(self)
        window.title("Lịch sử duyệt")
        self.center_window(window, 900, 500)
        window.transient(self.controller) 
        window.configure(fg_color="white")
        self.windows["history"] = window
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text=f"LỊCH SỬ DUYỆT BÀI", font=("Roboto Medium", 20), text_color=COLOR_BLUE_TITLE).pack(pady=20)
        self.setup_treeview_style()
        cols = ("Mã SV", "Tên SV", "Ngày duyệt", "Trạng thái", "Kết quả")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        for col in cols: tree.heading(col, text=col); tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        data = self.db.get_lecturer_history(self.current_lecturer_name)
        for item in data: tree.insert("", "end", values=item)

    # 5. THỐNG KÊ KHOA
    def open_dept_statistics(self):
        if self.check_window_exists("stats_dept"): return
        window = ctk.CTkToplevel(self)
        window.title("Thống kê toàn Khoa")
        self.center_window(window, 700, 500)
        window.transient(self.controller) 
        window.configure(fg_color="white")
        self.windows["stats_dept"] = window
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text="THỐNG KÊ TOÀN KHOA", font=("Roboto Medium", 22), text_color=COLOR_BLUE_TITLE).pack(pady=20)
        
        stats_data = self.db.get_class_statistics() 
        total = sum([x[1] for x in stats_data])
        
        frame = ctk.CTkFrame(window, fg_color="white")
        frame.pack(fill="both", expand=True, padx=50, pady=10)
        ctk.CTkLabel(frame, text=f"Tổng số phiếu toàn khoa: {total}", font=("Arial", 16, "bold"), text_color="#2c3e50").pack(pady=(0, 20), anchor="w")

        for label, count, color in stats_data:
            pct = (count/total)*100 if total else 0
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=8)
            ctk.CTkLabel(row, text=label, width=120, anchor="w", font=("Arial", 14), text_color="black").pack(side="left")
            bg_bar = ctk.CTkFrame(row, height=18, width=300, fg_color="#ecf0f1", corner_radius=9); bg_bar.pack(side="left", padx=10)
            if pct > 0: ctk.CTkFrame(bg_bar, height=18, width=300*(pct/100), fg_color=color, corner_radius=9).place(x=0,y=0)
            ctk.CTkLabel(row, text=f"{count} ({pct:.1f}%)", width=100, anchor="e", font=("Arial", 13, "bold"), text_color="black").pack(side="right")

    # 6. THÔNG BÁO (MODERN + DETAIL VIEW)
    def open_notifications(self):
        if self.check_window_exists("notif"): return
        window = ctk.CTkToplevel(self)
        window.title("Thông báo")
        self.center_window(window, 1000, 600)
        window.transient(self.controller) 
        window.configure(fg_color="white")
        self.windows["notif"] = window
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text="THÔNG BÁO DÀNH CHO GIẢNG VIÊN", font=("Roboto Medium", 20), text_color=COLOR_BLUE_TITLE).pack(pady=20)
        
        table_frame = ctk.CTkFrame(window, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self.setup_treeview_style()
        cols = ("Tiêu đề", "Nội dung", "Người gửi", "Thời gian", "Loại")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        tree.heading("Tiêu đề", text="Tiêu đề"); tree.column("Tiêu đề", width=250)
        tree.heading("Nội dung", text="Nội dung (Nhấp đúp xem chi tiết)"); tree.column("Nội dung", width=400)
        tree.heading("Người gửi", text="Người gửi"); tree.column("Người gửi", width=120, anchor="center")
        tree.heading("Thời gian", text="Thời gian"); tree.column("Thời gian", width=100, anchor="center")
        tree.heading("Loại", text="Loại"); tree.column("Loại", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        
        data = self.db.get_notifications("GV")
        for item in data: tree.insert("", "end", values=item)

        def view_detail(event=None):
            selected = tree.selection()
            if not selected: messagebox.showinfo("Nhắc nhở", "Chọn thông báo để xem!", parent=window); return
            
            item = tree.item(selected[0]); values = item['values']
            if not values: return

            tieu_de, noi_dung, nguoi_gui, thoi_gian, loai = values

            detail = ctk.CTkToplevel(self)
            detail.title("Chi tiết")
            self.center_window(detail, 600, 450)
            detail.transient(window)
            detail.configure(fg_color="white")

            ctk.CTkLabel(detail, text=str(tieu_de).upper(), font=("Roboto Medium", 18), text_color=COLOR_SIDEBAR, wraplength=550).pack(pady=(25, 5), padx=20)
            info = f"Người gửi: {nguoi_gui}  |  Ngày: {thoi_gian}  |  Loại: {loai}"
            ctk.CTkLabel(detail, text=info, font=("Arial", 13, "italic"), text_color="gray").pack(pady=(0, 20))

            txt_content = ctk.CTkTextbox(detail, font=("Arial", 15), wrap="word", fg_color="#f9f9f9", text_color="#333", border_width=0)
            txt_content.pack(fill="both", expand=True, padx=30, pady=10)
            txt_content.insert("0.0", str(noi_dung)); txt_content.configure(state="disabled")

            ctk.CTkButton(detail, text="Đóng", width=120, fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER, command=detail.destroy).pack(pady=20)

        tree.bind("<Double-1>", view_detail)
        ctk.CTkButton(window, text="👁 Xem chi tiết nội dung", font=("Arial", 14, "bold"), 
                      fg_color=COLOR_ACTION_BLUE, hover_color=COLOR_ACTION_BLUE_HOVER, 
                      width=220, height=45, command=view_detail).pack(pady=20)

    # =========================================================================
    # HỖ TRỢ & POPUP KHÁC
    # =========================================================================
    def confirm_logout(self):
        if messagebox.askokcancel("Đăng xuất", "Bạn muốn đăng xuất?"):
            self.controller.show_frame("LoginView")

    def open_guide(self):
        if self.check_window_exists("guide"): return
        window = ctk.CTkToplevel(self)
        window.title("Hướng dẫn sử dụng")
        self.center_window(window, 700, 500)
        window.transient(self.controller) 
        window.configure(fg_color="white")
        self.windows["guide"] = window
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text="HƯỚNG DẪN GIẢNG VIÊN", font=("Roboto Medium", 20), text_color=COLOR_BLUE_TITLE).pack(pady=20)
        textbox = ctk.CTkTextbox(window, font=("Arial", 14), wrap="word", fg_color="#f8f9fa", text_color="#333", border_width=0)
        textbox.pack(fill="both", expand=True, padx=30, pady=10)
        content = """1. Phiếu chờ duyệt: Xem và xử lý phiếu điểm sinh viên. Nhấp đúp hoặc chọn phiếu rồi bấm Xem chi tiết để duyệt.\n\n2. Danh sách lớp: Xem danh sách sinh viên thuộc lớp quản lý.\n\n3. Thống kê: Xem biểu đồ xếp loại rèn luyện."""
        textbox.insert("0.0", content); textbox.configure(state="disabled")
        ctk.CTkButton(window, text="Đóng", fg_color=COLOR_SIDEBAR, width=100, command=window.withdraw).pack(pady=10)

    def open_change_password(self):
        if self.check_window_exists("change_pass"): return
        window = ctk.CTkToplevel(self)
        window.title("Đổi mật khẩu")
        self.center_window(window, 450, 450)
        window.transient(self.controller) 
        window.configure(fg_color="white")
        self.windows["change_pass"] = window
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text="ĐỔI MẬT KHẨU", font=("Roboto Medium", 20), text_color=COLOR_BLUE_TITLE).pack(pady=30)
        entry_conf = {"width": 320, "height": 45, "fg_color": "#f1f2f6", "text_color": "#333", "border_width": 0, "corner_radius": 8}
        entry_old = ctk.CTkEntry(window, placeholder_text="Mật khẩu cũ", show="*", **entry_conf); entry_old.pack(pady=10)
        entry_new = ctk.CTkEntry(window, placeholder_text="Mật khẩu mới", show="*", **entry_conf); entry_new.pack(pady=10)
        entry_confirm = ctk.CTkEntry(window, placeholder_text="Nhập lại", show="*", **entry_conf); entry_confirm.pack(pady=10)

        def save():
            old, new, confirm = entry_old.get(), entry_new.get(), entry_confirm.get()
            if not old or not new: messagebox.showwarning("Lỗi", "Nhập đủ thông tin!", parent=window); return
            if new != confirm: messagebox.showerror("Lỗi", "Không khớp!", parent=window); return
            if self.db.change_password(self.current_lecturer_id, old, new):
                messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=window); window.withdraw()
            else: messagebox.showerror("Lỗi", "Mật khẩu cũ sai!", parent=window)

        ctk.CTkButton(window, text="LƯU THAY ĐỔI", fg_color=COLOR_HOVER, 
                      hover_color=COLOR_ACCENT, height=45, width=320, command=save).pack(pady=30)