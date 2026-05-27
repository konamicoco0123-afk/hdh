import customtkinter as ctk
from ui_cpu import CPUFrame
from ui_memory import MemoryFrame
from ui_sync import SyncFrame
from ui_evaluation import EvaluationFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mô phỏng Hệ điều hành")
        self.geometry("1000x650")
        self.minsize(900, 600)

        self._create_sidebar()
        self._create_main_area()
        self._show_frame("Lập lịch CPU")

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        title = ctk.CTkLabel(self.sidebar, text="Menu", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(20, 10))

        buttons = [
            ("Lập lịch CPU", self._show_cpu),
            ("Bộ nhớ", self._show_memory),
            ("Đồng bộ hóa", self._show_synchronization),
            ("Đánh giá hiệu năng", self._show_performance),
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(self.sidebar, text=text, command=command, width=180)
            btn.pack(pady=8)

        self.sidebar.pack_propagate(False)

    def _create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.frames = {
            "Lập lịch CPU": CPUFrame(self.main_frame),
            "Bộ nhớ": MemoryFrame(self.main_frame),
            "Đồng bộ hóa": SyncFrame(self.main_frame),
            "Đánh giá hiệu năng": EvaluationFrame(self.main_frame),
        }

    def _build_placeholder_frame(self, title_text):
        frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        label = ctk.CTkLabel(frame, text=title_text, font=ctk.CTkFont(size=22, weight="bold"))
        label.pack(pady=30)

        description = ctk.CTkLabel(
            frame,
            text="Khu vực hiển thị nội dung cho phần này. Chưa triển khai chi tiết.",
            wraplength=700,
            justify="left",
            font=ctk.CTkFont(size=14),
        )
        description.pack(padx=20)
        return frame

    def _show_frame(self, name):
        for frame in self.frames.values():
            frame.grid_forget()
        frame = self.frames.get(name)
        if frame:
            frame.grid(row=0, column=0, sticky="nsew")

    def _show_cpu(self):
        self._show_frame("Lập lịch CPU")

    def _show_memory(self):
        self._show_frame("Bộ nhớ")

    def _show_synchronization(self):
        self._show_frame("Đồng bộ hóa")

    def _show_performance(self):
        self._show_frame("Đánh giá hiệu năng")


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue")
    app = App()
    app.mainloop()
