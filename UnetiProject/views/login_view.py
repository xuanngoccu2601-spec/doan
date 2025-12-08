from data.db_handler import validate_login
import customtkinter as ctk
from tkinter import messagebox
import os


# --- XỬ LÝ LỖI PIL ---
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#174260") # Màu nền xanh Uneti

        self.selected_role = ""
        self.target_dashboard = ""

        # --- TỰ ĐỘNG TÌM ĐƯỜNG DẪN ẢNH ---
        try:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            project_dir = os.path.dirname(current_dir)
            assets_path = os.path.join(project_dir, "assets")
        except Exception:
            assets_path = ""

        self.icons = {}
        image_files = {
            "sv": "login1 (1).jpg",  
            "gv": "login2.jpg",      
            "ql": "login3.jpg"       
        }

        for role, filename in image_files.items():
            self.icons[role] = None 
            if HAS_PIL and os.path.exists(assets_path):
                try:
                    full_path = os.path.join(assets_path, filename)
                    if os.path.exists(full_path):
                        pil_img = Image.open(full_path)
                        self.icons[role] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(50, 50))
                except Exception:
                    pass

        # --- GIAO DIỆN ---
        self.lbl_title = ctk.CTkLabel(self, 
                                      text="Xin chào,\nTrường Đại học Kinh tế - Kỹ thuật Công nghiệp", 
                                      font=("Arial", 28, "bold"), 
                                      text_color="white")
        self.lbl_title.pack(pady=(40, 10))

        # KHUNG CHỌN VAI TRÒ
        self.frame_roles = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_roles.pack(expand=True)

        ctk.CTkLabel(self.frame_roles, text="Vui lòng chọn vai trò để tiếp tục", font=("Arial", 16), text_color="#ddd").pack(pady=(0, 20))

        self.create_role_btn("SINH VIÊN", "StudentDashboard", self.icons.get("sv"))
        self.create_role_btn("GIẢNG VIÊN", "LecturerDashboard", self.icons.get("gv"))
        self.create_role_btn("QUẢN LÝ", "ManagerDashboard", self.icons.get("ql"))

        # KHUNG ĐĂNG NHẬP
        self.frame_login = ctk.CTkFrame(self, fg_color="white", width=360, corner_radius=20)
        
        self.lbl_role_login = ctk.CTkLabel(self.frame_login, text="ĐĂNG NHẬP", font=("Arial", 22, "bold"), text_color="#174260")
        self.lbl_role_login.pack(pady=(30, 20))

        # --- CẤU HÌNH MÀU SẮC Ô NHẬP (MÀU ĐEN/XÁM ĐẬM) ---
        INPUT_BG = "#343638"     # Màu nền đen xám
        INPUT_BORDER = "#565B5E" # Màu viền
        INPUT_TEXT = "white"     # Màu chữ trắng

        # 1. Ô MÃ SỐ (Đã chỉnh màu tối)
        self.entry_user = ctk.CTkEntry(self.frame_login, 
                                       placeholder_text="Mã số đăng nhập", 
                                       width=280, height=45,
                                       fg_color=INPUT_BG,        # Nền tối
                                       border_color=INPUT_BORDER, 
                                       text_color=INPUT_TEXT)
        self.entry_user.pack(pady=10)
        
        # 2. KHUNG MẬT KHẨU (Container giả lập ô nhập)
        self.pass_container = ctk.CTkFrame(self.frame_login, 
                                           fg_color=INPUT_BG,    # Nền tối (giống ô trên)
                                           border_width=2, 
                                           border_color=INPUT_BORDER,
                                           width=280, height=45,
                                           corner_radius=6)
        self.pass_container.pack(pady=10)
        self.pass_container.pack_propagate(False) 

        # 3. Ô NHẬP MẬT KHẨU (Trong suốt)
        self.entry_pass = ctk.CTkEntry(self.pass_container, 
                                       placeholder_text="Mật khẩu", 
                                       show="*",
                                       fg_color="transparent",  # Trong suốt để lộ nền đen của container
                                       border_width=0,          
                                       height=40,
                                       width=230,
                                       font=("Arial", 14),
                                       text_color=INPUT_TEXT)   # Chữ trắng
        self.entry_pass.pack(side="left", padx=(5, 0), pady=2)

        # 4. NÚT MẮT (Trong suốt, icon trắng)
        self.btn_eye = ctk.CTkButton(self.pass_container, text="👁", width=30, 
                                     fg_color="transparent",    # Trong suốt
                                     hover_color=INPUT_BORDER,  # Hover màu xám viền
                                     text_color="gray",         # Icon màu xám
                                     font=("Arial", 18),
                                     command=self.toggle_password)
        self.btn_eye.pack(side="right", padx=(0, 5))
        # --------------------------------------------------------

        ctk.CTkButton(self.frame_login, text="ĐĂNG NHẬP", width=280, height=45, fg_color="#e67e22", hover_color="#d35400",
                      font=("Arial", 16, "bold"), command=self.check_login).pack(pady=20)

        ctk.CTkButton(self.frame_login, text="Quay lại", fg_color="transparent", text_color="#555",
                      command=self.back_to_roles).pack(pady=(0, 20))

    def create_role_btn(self, text, dashboard, icon):
        btn = ctk.CTkButton(self.frame_roles, text=f"  {text}", image=icon, compound="left",
                            width=320, height=80, font=("Arial", 20, "bold"),
                            fg_color="white", text_color="#174260", hover_color="#eee", corner_radius=15,
                            command=lambda: self.show_login(text, dashboard))
        btn.pack(pady=10)

    # --- HÀM ẨN/HIỆN MẬT KHẨU ---
    def toggle_password(self):
        if self.entry_pass.cget("show") == "*":
            self.entry_pass.configure(show="") 
            self.btn_eye.configure(text="O")   
        else:
            self.entry_pass.configure(show="*") 
            self.btn_eye.configure(text="👁")

    def show_login(self, role_text, dashboard):
        """Chuyển sang màn hình đăng nhập"""
        self.selected_role = role_text
        self.target_dashboard = dashboard
        self.lbl_role_login.configure(text=f"ĐĂNG NHẬP {role_text}")
        
        self.lbl_title.pack_forget()     
        self.frame_roles.pack_forget()   

        # Reset
        self.entry_user.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.entry_pass.configure(show="*") 
        self.btn_eye.configure(text="👁")
        
        self.entry_user.configure(placeholder_text="Mã số đăng nhập")
        self.entry_pass.configure(placeholder_text="Mật khẩu")
        
        try: self.lbl_role_login.focus_set()
        except: pass
        
        self.frame_login.pack(ipadx=5, ipady=5, expand=True)

    def back_to_roles(self):
        self.entry_user.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.frame_login.pack_forget()   
        self.lbl_title.pack(pady=(40, 10)) 
        self.frame_roles.pack(expand=True) 
        
    def check_login(self):
        user_input = self.entry_user.get()
        pass_input = self.entry_pass.get()

        # Gọi hàm kiểm tra từ db_handler
        # result trả về dạng: {'username': 'svtest', 'name': 'Nguyễn Văn Test', 'role': 'SV'}
        result = validate_login(user_input, pass_input)

        if result:
            # --- SỬA LẠI ĐOẠN NÀY ĐỂ KHÔNG BỊ LỖI UNPACK ---
            
            # 1. Lưu toàn bộ thông tin user vào controller để các màn hình sau dùng lại
            if hasattr(self.controller, 'user_data'):
                self.controller.user_data = result 
            
            # 2. Lấy thông tin từ Dictionary (thay vì ten, vaitro = result)
            ten_user = result['name']
            vai_tro_trong_db = result['role'] # Giá trị nhận được: 'SV', 'GV', hoặc 'QL'

            # 3. Mapping vai trò (Đồng bộ chữ HOA với Database)
            bang_vai_tro = {
                "SINH VIÊN": "SV", 
                "GIẢNG VIÊN": "GV", 
                "QUẢN LÝ":    "QL"  
            }
            
            # Lấy vai trò user đang chọn trên giao diện (Tab đang active)
            vai_tro_dang_chon = bang_vai_tro.get(self.selected_role)

            # 4. So sánh vai trò
            if vai_tro_trong_db == vai_tro_dang_chon:
                print(f"Đăng nhập thành công! Xin chào {ten_user}")
                
                if self.target_dashboard:
                    self.controller.show_frame(self.target_dashboard)
                    # Reset giao diện login
                    self.entry_user.delete(0, 'end')
                    self.entry_pass.delete(0, 'end')
                    self.back_to_roles() 
            else:
                # Đúng tài khoản nhưng chọn sai Tab vai trò
                messagebox.showerror("Lỗi", f"Tài khoản này là {vai_tro_trong_db}, không phải {self.selected_role}!")
        else:
            messagebox.showerror("Lỗi", "Sai mã đăng nhập hoặc mật khẩu!")