import customtkinter as ctk
from views.login_view import LoginView
from views.student_view import StudentDashboard
from views.lecturer_view import LecturerDashboard
from views.manager_view import ManagerDashboard

# Cấu hình giao diện chung
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Cấu hình tiêu đề
        self.title("HỆ THỐNG QUẢN LÝ ĐIỂM RÈN LUYỆN KHOA CNTT - UNETI")
        
        # 2. Cấu hình kích thước và CĂN GIỮA MÀN HÌNH
        window_width = 1100
        window_height = 700
        
        # Cập nhật thông tin màn hình trước khi tính toán
        self.update_idletasks() 
        
        # Lấy kích thước màn hình máy tính
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Tính toán tọa độ x, y để căn giữa
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Áp dụng kích thước và vị trí
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 3. Quản lý container (Nơi chứa các view)
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Biến lưu thông tin user đang đăng nhập (để truyền qua các view)
        self.user_data = {}

        # Danh sách các màn hình (Frames)
        self.frames = {}
        
        # 4. Đăng ký các View (QUAN TRỌNG: Đã bỏ try/except để hiện lỗi nếu có)
        for F in (LoginView, StudentDashboard, LecturerDashboard, ManagerDashboard):
            page_name = F.__name__
            
            # Khởi tạo view. Nếu lỗi ở đây (do code View hoặc Database),
            # chương trình sẽ dừng và báo lỗi đỏ ở Terminal ngay.
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Mặc định hiển thị màn hình Đăng nhập
        self.show_frame("LoginView")

    def show_frame(self, page_name, user_data=None):
        """Hàm chuyển đổi màn hình"""
        if user_data:
            self.user_data = user_data # Lưu thông tin user nếu có
            
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise() # Đưa frame lên trên cùng
            
            # Nếu frame có hàm update_ui (để load lại dữ liệu mới), thì gọi nó
            if hasattr(frame, "update_ui"):
                frame.update_ui()
            
            # Riêng các Dashboard cần render lại trang chủ để cập nhật tên người dùng
            if page_name == "StudentDashboard" and hasattr(frame, "show_home_page"):
                frame.show_home_page()
            elif page_name == "LecturerDashboard" and hasattr(frame, "render_home"):
                frame.render_home()
            elif page_name == "ManagerDashboard" and hasattr(frame, "render_home"):
                frame.render_home()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()