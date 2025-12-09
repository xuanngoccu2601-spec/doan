import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
import os
import datetime
import shutil
from data.db_handler import DBHandler

# --- BẢNG MÀU MODERN UI ---
COLOR_SIDEBAR = "#2c3e50"       
COLOR_BG_MAIN = "#ecf0f1"       
COLOR_TEXT_MAIN = "#2c3e50"     
COLOR_TEXT_SIDEBAR = "#ecf0f1"  
COLOR_DANGER = "#c0392b"
COLOR_ACCENT = "#1abc9c"
COLOR_HOVER = "#16a085"

class StudentDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DBHandler()
        self.windows = {} 

        # 1. SIDEBAR
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR)
        sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(sidebar, text="SINH VIÊN", font=("Roboto Medium", 22), text_color=COLOR_TEXT_SIDEBAR).pack(pady=(40, 50))
        
        def create_sidebar_btn(text, cmd, icon="🔹"):
            btn = ctk.CTkButton(sidebar, text=f"{icon}  {text}", font=("Roboto Medium", 14), 
                                fg_color="transparent", text_color="#bdc3c7", hover_color="#34495e", 
                                anchor="w", height=45, command=cmd)
            btn.pack(fill="x", padx=15, pady=5)

        create_sidebar_btn("Trang chủ", self.show_home_page, "🏠")
        create_sidebar_btn("Hồ sơ cá nhân", self.show_profile_page, "👤")
        create_sidebar_btn("Tài khoản", self.show_account_page, "⚙️")

        ctk.CTkButton(sidebar, text="🚪 Đăng xuất", fg_color=COLOR_DANGER, hover_color="#e74c3c", 
                      height=40, font=("Roboto Medium", 14),
                      command=self.confirm_logout).pack(side="bottom", pady=30, padx=20, fill="x")

        # 2. MAIN CONTENT
        self.right_panel = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.page_home = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.setup_home_page() 
        self.page_profile = None
        self.page_account = None

        self.show_home_page()

    @property
    def current_user_id(self):
        return self.controller.user_data.get('username', '')

    # =========================================================================
    # HÀM HỖ TRỢ
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
        style.configure("Treeview.Heading", font=("Roboto Medium", 13), background="#ecf0f1", foreground=COLOR_TEXT_MAIN, relief="flat")
        style.configure("Treeview", font=("Arial", 12), rowheight=35, background="white", fieldbackground="white", foreground="#2c3e50", borderwidth=0)

    # =========================================================================
    # LOGIC CHUYỂN TRANG
    # =========================================================================
    def hide_all_pages(self):
        self.page_home.pack_forget()
        if self.page_profile: self.page_profile.pack_forget()
        if self.page_account: self.page_account.pack_forget()

    def show_home_page(self):
        self.hide_all_pages()
        self.page_home.pack(fill="both", expand=True, padx=30, pady=30)

    def show_profile_page(self):
        self.hide_all_pages()
        if self.page_profile: self.page_profile.destroy()
        self.page_profile = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.setup_profile_page()
        self.page_profile.pack(fill="both", expand=True, padx=30, pady=30)

    def show_account_page(self):
        self.hide_all_pages()
        if not self.page_account:
            self.page_account = ctk.CTkFrame(self.right_panel, fg_color="transparent")
            self.setup_account_page()
        self.page_account.pack(fill="both", expand=True, padx=30, pady=30)

    # =========================================================================
    # TRANG CHỦ
    # =========================================================================
    def setup_home_page(self):
        welcome_frame = ctk.CTkFrame(self.page_home, fg_color="transparent")
        welcome_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(welcome_frame, text="CHỨC NĂNG SINH VIÊN", font=("Roboto Medium", 28), text_color=COLOR_TEXT_MAIN).pack(side="left")
        
        grid = ctk.CTkFrame(self.page_home, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1, 2), weight=1)

        buttons = [
            {"text": "Xem điểm\nRèn luyện", "icon": "📊", "cmd": self.open_view_scores, "color": "#3498db"},
            {"text": "Đợt đánh giá", "icon": "📅", "cmd": self.open_periods, "color": "#9b59b6"},
            {"text": "Thống kê lớp", "icon": "📈", "cmd": self.open_class_statistics, "color": "#e67e22"},
            {"text": "Lịch sử nộp", "icon": "🕒", "cmd": self.open_history, "color": "#2ecc71"},
            {"text": "Chấm điểm", "icon": "✍️", "cmd": self.open_grading, "color": COLOR_ACCENT},
            {"text": "Thông báo", "icon": "🔔", "cmd": self.open_notifications, "color": "#e74c3c"}
        ]
        
        for i, btn in enumerate(buttons):
            card = ctk.CTkButton(
                grid, 
                text=f"{btn['icon']}\n\n{btn['text']}", 
                font=("Roboto Medium", 18),
                fg_color="white", text_color=btn["color"],
                hover_color="#f5f6fa", corner_radius=15,
                border_width=2, border_color=btn["color"],
                height=150, command=btn["cmd"]
            )
            card.grid(row=i//3, column=i%3, padx=15, pady=15, sticky="nsew")

    # =========================================================================
    # TRANG CON
    # =========================================================================
    def setup_profile_page(self):
        ctk.CTkButton(self.page_profile, text="← Quay lại", width=100, fg_color="transparent", 
                      text_color=COLOR_TEXT_MAIN, hover_color="#dfe6e9", border_width=1, 
                      command=self.show_home_page).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(self.page_profile, text="HỒ SƠ SINH VIÊN", font=("Roboto Medium", 26), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 20))

        info = self.db.get_student_info(self.current_user_id)
        info_card = ctk.CTkFrame(self.page_profile, fg_color="white", corner_radius=15)
        info_card.pack(fill="both", expand=True, padx=50)

        fields = [
            ("Mã sinh viên", info.get("masv", "")), ("Họ và tên", info.get("ten", "")),
            ("Lớp hành chính", info.get("lop", "")), ("Ngày sinh", str(info.get("ngay_sinh", ""))),
            ("Giới tính", info.get("gioi_tinh", "")), ("Quê quán", info.get("que_quan", "")),
            ("Niên khóa", info.get("nien_khoa", "")), ("Chuyên ngành", info.get("chuyen_nganh", "")),
            ("Email", info.get("email", "")), ("Số điện thoại", info.get("sdt", ""))
        ]

        for i, (label, value) in enumerate(fields):
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=12)
            ctk.CTkLabel(row, text=label, font=("Arial", 14), text_color="#7f8c8d", width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=("Arial", 15, "bold"), text_color="#2c3e50", anchor="w").pack(side="left", fill="x")
            if i < len(fields) - 1: ctk.CTkFrame(info_card, height=1, fg_color="#ecf0f1").pack(fill="x", padx=40)

    def setup_account_page(self):
        ctk.CTkButton(self.page_account, text="← Quay lại", width=100, fg_color="transparent", 
                      text_color=COLOR_TEXT_MAIN, hover_color="#dfe6e9", border_width=1,
                      command=self.show_home_page).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(self.page_account, text="CÀI ĐẶT TÀI KHOẢN", font=("Roboto Medium", 26), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 20))

        menu_frame = ctk.CTkFrame(self.page_account, fg_color="white", corner_radius=15)
        menu_frame.pack(fill="both", expand=True, padx=50)

        def create_setting_item(text, cmd):
            btn = ctk.CTkButton(menu_frame, text=text, font=("Arial", 16), height=60, anchor="w",
                                fg_color="transparent", text_color="#2c3e50", hover_color="#f1f2f6", command=cmd)
            btn.pack(fill="x", padx=20, pady=5)
            ctk.CTkFrame(menu_frame, height=1, fg_color="#ecf0f1").pack(fill="x", padx=20)

        create_setting_item("📖  Hướng dẫn sử dụng", self.open_guide)
        create_setting_item("🔒  Đổi mật khẩu", self.open_change_password)

    # =========================================================================
    # POPUP & CHỨC NĂNG
    # =========================================================================
    def confirm_logout(self):
        if messagebox.askokcancel("Xác nhận", "Bạn muốn đăng xuất?"): 
            self.show_home_page()
            self.controller.show_frame("LoginView")

    def open_guide(self):
        if self.check_window_exists("guide"): return
        window = ctk.CTkToplevel(self)
        window.title("Hướng dẫn")
        self.center_window(window, 700, 500)
        window.attributes("-topmost", True); window.configure(fg_color="white")
        
        ctk.CTkLabel(window, text="HƯỚNG DẪN", font=("Roboto Medium", 20), text_color=COLOR_SIDEBAR).pack(pady=20)
        textbox = ctk.CTkTextbox(window, font=("Arial", 14), wrap="word", fg_color="#f8f9fa", text_color="#333")
        textbox.pack(fill="both", expand=True, padx=30, pady=10)
        content = "1. Xem điểm: Theo dõi kết quả.\n2. Chấm điểm: Chọn đợt, tích tiêu chí, đính kèm minh chứng.\n..."
        textbox.insert("0.0", content); textbox.configure(state="disabled")

    def open_change_password(self):
        if self.check_window_exists("change_pass"): return
        window = ctk.CTkToplevel(self)
        window.title("Đổi mật khẩu")
        self.center_window(window, 450, 450)
        window.attributes("-topmost", True); window.configure(fg_color="white")
        
        ctk.CTkLabel(window, text="ĐỔI MẬT KHẨU", font=("Roboto Medium", 20), text_color=COLOR_SIDEBAR).pack(pady=30)
        entry_conf = {"width": 320, "height": 45, "fg_color": "#f1f2f6", "text_color": "#333", "border_width": 0, "corner_radius": 8}
        e_old = ctk.CTkEntry(window, placeholder_text="Mật khẩu cũ", show="*", **entry_conf); e_old.pack(pady=10)
        e_new = ctk.CTkEntry(window, placeholder_text="Mật khẩu mới", show="*", **entry_conf); e_new.pack(pady=10)
        e_cfm = ctk.CTkEntry(window, placeholder_text="Nhập lại", show="*", **entry_conf); e_cfm.pack(pady=10)

        def save():
            old, new, cfm = e_old.get(), e_new.get(), e_cfm.get()
            if not old or not new: messagebox.showwarning("Lỗi", "Nhập đủ thông tin!", parent=window); return
            if new != cfm: messagebox.showerror("Lỗi", "Không khớp!", parent=window); return
            if self.db.change_password(self.current_user_id, old, new):
                messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=window); window.destroy()
            else: messagebox.showerror("Thất bại", "Mật khẩu cũ sai!", parent=window)

        ctk.CTkButton(window, text="LƯU THAY ĐỔI", fg_color=COLOR_ACCENT, height=45, width=320, command=save).pack(pady=30)

    # 1. XEM ĐIỂM
    def open_view_scores(self):
        if self.check_window_exists("scores"): return
        window = ctk.CTkToplevel(self)
        window.title("Kết quả Rèn luyện")
        self.center_window(window, 900, 500)
        window.attributes("-topmost", True); window.configure(fg_color="white")
        
        ctk.CTkLabel(window, text="BẢNG ĐIỂM RÈN LUYỆN", font=("Roboto Medium", 20), text_color=COLOR_SIDEBAR).pack(pady=20)
        self.setup_treeview_style()
        cols = ("Học kỳ", "Năm học", "Điểm số", "Xếp loại")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center", width=150)
        tree.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        data = self.db.get_student_scores(self.current_user_id)
        for row in data: tree.insert("", "end", values=row)

    # 2. XEM ĐỢT (ĐÃ SỬA LỖI HIỂN THỊ)
    def open_periods(self):
        if self.check_window_exists("periods"): return
        window = ctk.CTkToplevel(self)
        window.title("Đợt đánh giá")
        self.center_window(window, 1000, 500)
        window.attributes("-topmost", True); window.configure(fg_color="white")
        
        ctk.CTkLabel(window, text="CÁC ĐỢT ĐÁNH GIÁ", font=("Roboto Medium", 20), text_color=COLOR_SIDEBAR).pack(pady=20)
        self.setup_treeview_style()
        cols = ("ID", "Tên đợt", "Bắt đầu", "Kết thúc", "Trạng thái")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        tree.column("ID", width=50, anchor="center"); tree.column("Tên đợt", width=300)
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # --- SỬA Ở ĐÂY: insert thẳng row vì row đã chuẩn từ DB ---
        data = self.db.get_periods()
        for row in data: tree.insert("", "end", values=row)

    # 3. THỐNG KÊ LỚP
    def open_class_statistics(self):
        if self.check_window_exists("stats"): return
        window = ctk.CTkToplevel(self)
        window.title("Thống kê lớp")
        self.center_window(window, 700, 500)
        window.attributes("-topmost", True); window.configure(fg_color="white")

        ctk.CTkLabel(window, text="THỐNG KÊ LỚP", font=("Roboto Medium", 22), text_color=COLOR_SIDEBAR).pack(pady=20)
        stats_data = self.db.get_class_statistics(self.current_user_id) 
        total_sv = sum([x[1] for x in stats_data])

        frame = ctk.CTkFrame(window, fg_color="white")
        frame.pack(fill="both", expand=True, padx=50, pady=10)
        ctk.CTkLabel(frame, text=f"Tổng số phiếu đã duyệt: {total_sv}", font=("Arial", 16, "bold"), text_color="#2c3e50").pack(pady=(0, 20), anchor="w")

        for label, count, color in stats_data:
            pct = (count / total_sv) * 100 if total_sv > 0 else 0
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=8)
            ctk.CTkLabel(row, text=label, width=140, anchor="w", font=("Arial", 14), text_color="#34495e").pack(side="left")
            bg_bar = ctk.CTkFrame(row, height=18, width=350, fg_color="#ecf0f1", corner_radius=9)
            bg_bar.pack(side="left", padx=10)
            if pct > 0: ctk.CTkFrame(bg_bar, height=18, width=350*(pct/100), fg_color=color, corner_radius=9).place(x=0, y=0)
            ctk.CTkLabel(row, text=f"{count} ({pct:.1f}%)", width=100, anchor="e", font=("Arial", 14, "bold"), text_color="#2c3e50").pack(side="right")

    # 4. LỊCH SỬ
    def open_history(self):
        if self.check_window_exists("history"): return
        window = ctk.CTkToplevel(self)
        window.title("Lịch sử nộp phiếu")
        self.center_window(window, 900, 500)
        window.attributes("-topmost", True); window.configure(fg_color="white")
        
        ctk.CTkLabel(window, text="LỊCH SỬ NỘP PHIẾU", font=("Roboto Medium", 20), text_color=COLOR_SIDEBAR).pack(pady=20)
        self.setup_treeview_style()
        cols = ("ID", "Ngày nộp", "Tổng điểm", "Trạng thái", "Người duyệt")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        data = self.db.get_student_history(self.current_user_id)
        for row in data: tree.insert("", "end", values=row)

    # 5. CHẤM ĐIỂM (ĐÃ SỬA LỖI GIAO DIỆN)
    def open_grading(self):
        if self.check_window_exists("grading"): return
        window = ctk.CTkToplevel(self)
        window.title("Chấm điểm rèn luyện")
        self.center_window(window, 1100, 750) 
        window.attributes("-topmost", True); window.configure(fg_color="#f5f6fa")

        if not hasattr(self, 'selected_files'): self.selected_files = []
        self.auto_form_code = f"MP{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        header = ctk.CTkFrame(window, height=60, fg_color="white", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="PHIẾU ĐÁNH GIÁ RÈN LUYỆN", font=("Roboto Medium", 22), text_color=COLOR_SIDEBAR).place(relx=0.5, rely=0.5, anchor="center")

        content_frame = ctk.CTkFrame(window, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        left_frame = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=10)
        left_frame.place(relx=0, rely=0, relwidth=0.68, relheight=1)
        ctk.CTkLabel(left_frame, text="DANH SÁCH TIÊU CHÍ ĐÁNH GIÁ", font=("Roboto Medium", 16), text_color=COLOR_ACCENT).pack(anchor="w", padx=20, pady=(15, 5))
        
        scroll_frame = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        data_sheet = self.db.get_grading_criteria() 
        self.check_vars = [] 
        for title, items in data_sheet:
            ctk.CTkLabel(scroll_frame, text=title, font=("Arial", 15, "bold"), text_color=COLOR_SIDEBAR, anchor="w").pack(fill="x", pady=(10, 5))
            for content, score in items:
                var = ctk.BooleanVar()
                chk = ctk.CTkCheckBox(scroll_frame, text=f"{content} (+{score}đ)", variable=var, font=("Arial", 14), 
                                      text_color="#333", fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER, command=self.update_total_score)
                chk.pack(anchor="w", padx=10, pady=3)
                self.check_vars.append((var, score, content)) 
            ctk.CTkFrame(scroll_frame, height=1, fg_color="#eee").pack(fill="x", pady=5)

        right_frame = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=10)
        right_frame.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)
        
        ctk.CTkLabel(right_frame, text="THÔNG TIN BỔ SUNG", font=("Roboto Medium", 16), text_color=COLOR_ACCENT).pack(pady=(15, 10))
        ctk.CTkLabel(right_frame, text="Mã phiếu (Tự động):", font=("Arial", 13), text_color="gray").pack(anchor="w", padx=15)
        ctk.CTkLabel(right_frame, text=self.auto_form_code, font=("Arial", 16, "bold"), text_color=COLOR_DANGER).pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkLabel(right_frame, text="Tên minh chứng:", font=("Arial", 13), text_color="gray").pack(anchor="w", padx=15)
        self.evidence_name_entry = ctk.CTkEntry(right_frame, placeholder_text="VD: Giấy khen...", height=35, border_color="#ccc")
        self.evidence_name_entry.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(right_frame, text="File đính kèm:", font=("Arial", 13), text_color="gray").pack(anchor="w", padx=15)
        
        def select_files_grading():
            window.attributes("-topmost", False)
            file_paths = filedialog.askopenfilenames(parent=window, title="Chọn minh chứng", filetypes=[("Minh chứng", "*.jpg *.png *.pdf")])
            window.attributes("-topmost", True)
            if file_paths:
                for f in file_paths:
                    if f not in self.selected_files: self.selected_files.append(f)
                self.update_file_list_display()

        ctk.CTkButton(right_frame, text="📂 Tải file lên", fg_color="#34495e", hover_color="#2c3e50", height=35, command=select_files_grading).pack(fill="x", padx=15)
        
        self.txt_file_list = ctk.CTkTextbox(right_frame, height=120, fg_color="#f8f9fa", text_color="#333", border_width=0)
        self.txt_file_list.pack(fill="x", padx=15, pady=10)
        self.txt_file_list.insert("0.0", "Chưa có file nào..."); self.txt_file_list.configure(state="disabled")

        bottom_bar = ctk.CTkFrame(window, height=70, fg_color="white")
        bottom_bar.pack(fill="x", side="bottom")
        
        ctk.CTkButton(bottom_bar, text="Hủy bỏ", fg_color="#95a5a6", hover_color="#7f8c8d", width=100, command=window.withdraw).pack(side="left", padx=20)
        ctk.CTkButton(bottom_bar, text="Làm mới", fg_color="transparent", border_width=1, border_color="#95a5a6", text_color="#555", width=100, command=self.deselect_all).pack(side="left")
        
        ctk.CTkButton(bottom_bar, text="GỬI PHIẾU ĐÁNH GIÁ", font=("Roboto Medium", 15), fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER, width=200, height=40, command=lambda: self.submit_grading(window)).pack(side="right", padx=20)
        
        self.lbl_total = ctk.CTkLabel(bottom_bar, text="Tổng: 65/100", font=("Roboto Medium", 24), text_color=COLOR_SIDEBAR)
        self.lbl_total.pack(side="right", padx=30)
        self.update_total_score()

    def update_file_list_display(self):
        self.txt_file_list.configure(state="normal"); self.txt_file_list.delete("0.0", "end")
        if not self.selected_files: self.txt_file_list.insert("0.0", "Chưa có file nào...")
        else: self.txt_file_list.insert("0.0", "\n".join([f"- {os.path.basename(f)}" for f in self.selected_files]))
        self.txt_file_list.configure(state="disabled")

    def deselect_all(self):
        for var, score, content in self.check_vars: var.set(False)
        self.update_total_score()
        if hasattr(self, 'evidence_name_entry'): self.evidence_name_entry.delete(0, "end")
        self.selected_files = []; self.update_file_list_display()

    def update_total_score(self):
        total = 65 
        for var, score, content in self.check_vars:
            if var.get(): total += score
        if total > 100: total = 100
        self.total_score_val = total 
        self.lbl_total.configure(text=f"Tổng: {total}/100")

    def submit_grading(self, window):
        evidence_name = self.evidence_name_entry.get()
        num_files = len(self.selected_files)
        ticked_items = []
        for var, score, content in self.check_vars:
            if var.get(): ticked_items.append(f"{content} (+{score}đ)")

        display_names = ", ".join([os.path.basename(f) for f in self.selected_files]) if num_files > 0 else ""
        msg = f"Xác nhận nộp phiếu {self.auto_form_code}?\nTổng điểm: {self.total_score_val}\nSố tiêu chí: {len(ticked_items)}"
        if num_files > 0: msg += f"\n\nMinh chứng: {evidence_name}\nFile: {num_files} files ({display_names})"
            
        if messagebox.askokcancel("Xác nhận nộp", msg, parent=window):
            success = self.db.submit_form(
                student_id=self.current_user_id, 
                score=self.total_score_val,
                evidence_files=self.selected_files,
                evidence_name=evidence_name,
                selected_criteria=ticked_items,
                form_id=self.auto_form_code
            )
            if success:
                messagebox.showinfo("Thành công", f"Nộp phiếu {self.auto_form_code} thành công!", parent=window)
                window.withdraw()
                self.deselect_all()
                self.auto_form_code = f"MP{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            else:
                 messagebox.showerror("Lỗi", "Không thể nộp phiếu (Có thể chưa có đợt nào MỞ hoặc lỗi kết nối)!", parent=window)

    # 6. THÔNG BÁO (MODERN STYLE)
    def open_notifications(self):
        if self.check_window_exists("notifications"): return
        window = ctk.CTkToplevel(self)
        window.title("Bảng thông báo")
        self.center_window(window, 1000, 600)
        window.attributes("-topmost", True); window.configure(fg_color="white")
        window.protocol("WM_DELETE_WINDOW", window.withdraw)

        ctk.CTkLabel(window, text="DANH SÁCH THÔNG BÁO", font=("Roboto Medium", 22), text_color=COLOR_SIDEBAR).pack(pady=20)

        table_frame = ctk.CTkFrame(window, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self.setup_treeview_style()
        cols = ("Tiêu đề", "Nội dung", "Người tạo", "Ngày tạo", "Trạng thái")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        tree.heading("Tiêu đề", text="Tiêu đề"); tree.column("Tiêu đề", width=250)
        tree.heading("Nội dung", text="Nội dung (Nhấp đúp để xem)"); tree.column("Nội dung", width=450) 
        tree.heading("Người tạo", text="Người tạo"); tree.column("Người tạo", width=100, anchor="center")
        tree.heading("Ngày tạo", text="Ngày tạo"); tree.column("Ngày tạo", width=100, anchor="center")
        tree.heading("Trạng thái", text="Trạng thái"); tree.column("Trạng thái", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        data = self.db.get_notifications("SV")
        for row in data: tree.insert("", "end", values=row)

        def view_detail(event=None):
            selected = tree.selection()
            if not selected: messagebox.showinfo("Nhắc nhở", "Chọn thông báo để xem!", parent=window); return
            
            item = tree.item(selected[0]); values = item['values']
            if not values: return

            tieu_de, noi_dung, nguoi_tao, ngay, trang_thai = values

            detail = ctk.CTkToplevel(self)
            detail.title("Chi tiết")
            self.center_window(detail, 600, 450)
            detail.attributes("-topmost", True); detail.configure(fg_color="white")

            ctk.CTkLabel(detail, text=str(tieu_de).upper(), font=("Roboto Medium", 18), text_color=COLOR_SIDEBAR, wraplength=550).pack(pady=(25, 5), padx=20)
            ctk.CTkLabel(detail, text=f"Gửi bởi: {nguoi_tao} | Ngày: {ngay}", font=("Arial", 13, "italic"), text_color="gray").pack(pady=(0, 20))

            txt_content = ctk.CTkTextbox(detail, font=("Arial", 15), wrap="word", fg_color="#f9f9f9", text_color="#333", border_width=0)
            txt_content.pack(fill="both", expand=True, padx=30, pady=10)
            txt_content.insert("0.0", str(noi_dung)); txt_content.configure(state="disabled")

            ctk.CTkButton(detail, text="Đóng", width=120, fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER, command=detail.destroy).pack(pady=20)

        tree.bind("<Double-1>", view_detail)
        ctk.CTkButton(window, text="👁 Xem chi tiết nội dung", font=("Arial", 14, "bold"), fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER, width=220, height=45, command=view_detail).pack(pady=20)