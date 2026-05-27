import customtkinter as ctk
from logic_memory import fifo_page_replacement, lru_page_replacement


class MemoryFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.result = None
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkLabel(self, text="Quản lý Bộ nhớ", font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=(12, 16))

        form_frame = ctk.CTkFrame(self, corner_radius=12)
        form_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.reference_entry = self._build_labeled_entry(form_frame, "Chuỗi tham chiếu:")
        self.frame_entry = self._build_labeled_entry(form_frame, "Số khung trang:")

        control_frame = ctk.CTkFrame(form_frame, corner_radius=12)
        control_frame.pack(fill="x", padx=8, pady=8)

        self.algorithm_var = ctk.StringVar(value="FIFO")
        ctk.CTkLabel(control_frame, text="Thuật toán:").grid(row=0, column=0, padx=(12, 8), pady=8, sticky="w")
        ctk.CTkOptionMenu(control_frame, values=["FIFO", "LRU"], variable=self.algorithm_var, width=140).grid(row=0, column=1, padx=(0, 12), pady=8, sticky="e")
        control_frame.grid_columnconfigure((0, 1), weight=1)

        run_button = ctk.CTkButton(form_frame, text="Chạy mô phỏng", command=self._run_simulation)
        run_button.pack(fill="x", padx=8, pady=(0, 12))

        info_frame = ctk.CTkFrame(self, corner_radius=12)
        info_frame.pack(fill="both", expand=False, padx=16, pady=(0, 12))

        self.summary_text = ctk.CTkTextbox(info_frame, width=1, height=120)
        self.summary_text.pack(fill="both", expand=True, padx=12, pady=12)
        self.summary_text.configure(state="disabled")

        self.grid_frame = ctk.CTkFrame(self, corner_radius=12)
        self.grid_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.grid_header = ctk.CTkLabel(self.grid_frame, text="Lưới trạng thái khung trang", anchor="w")
        self.grid_header.pack(fill="x", padx=12, pady=(12, 0))

        self.grid_container = ctk.CTkScrollableFrame(self.grid_frame, corner_radius=12)
        self.grid_container.pack(fill="both", expand=True, padx=12, pady=12)
        self.grid_container.grid_columnconfigure(tuple(range(10)), weight=1)

    def _build_labeled_entry(self, parent, label_text):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.pack(fill="x", padx=8, pady=8)

        label = ctk.CTkLabel(frame, text=label_text, width=140, anchor="w")
        label.pack(side="left", padx=(12, 8))

        entry = ctk.CTkEntry(frame)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=8)
        return entry

    def _run_simulation(self):
        raw_refs = self.reference_entry.get().strip()
        raw_frames = self.frame_entry.get().strip()

        if not raw_refs:
            self._print_summary("Lỗi: Chuỗi tham chiếu trống.")
            return

        try:
            references = [int(item.strip()) for item in raw_refs.split(",") if item.strip() != ""]
        except ValueError:
            self._print_summary("Lỗi: Chuỗi tham chiếu phải là các số nguyên, phân tách bằng dấu phẩy.")
            return

        if not raw_frames.isdigit() or int(raw_frames) <= 0:
            self._print_summary("Lỗi: Số khung trang phải là số nguyên dương.")
            return

        num_frames = int(raw_frames)
        algorithm = self.algorithm_var.get()

        if algorithm == "LRU":
            result = lru_page_replacement(references, num_frames)
        else:
            result = fifo_page_replacement(references, num_frames)

        self.result = result
        self._render_grid()
        self._print_summary(result)

    def _print_summary(self, result):
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")

        if isinstance(result, str):
            self.summary_text.insert("end", result)
        else:
            self.summary_text.insert("end", f"Thuật toán: {result['algorithm']}\n")
            self.summary_text.insert("end", f"Tổng page fault: {result['total_page_faults']}\n")
            faults = [str(step + 1) for step in result["page_faults"]]
            self.summary_text.insert("end", f"Bước bị fault: {', '.join(faults) if faults else 'Không có'}\n")
            self.summary_text.insert("end", "\nMỗi dòng tương ứng với một tham chiếu trang.\n")

        self.summary_text.configure(state="disabled")

    def _clear_grid(self):
        for child in self.grid_container.winfo_children():
            child.destroy()

    def _render_grid(self):
        self._clear_grid()
        if not self.result:
            return

        frames = self.result["frames"]
        page_faults = set(self.result["page_faults"])
        num_frames = len(frames[0]) if frames else 0

        ctk.CTkLabel(self.grid_container, text="Bước", width=60, anchor="center", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        ctk.CTkLabel(self.grid_container, text="Trang", width=80, anchor="center", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        for i in range(num_frames):
            ctk.CTkLabel(self.grid_container, text=f"Khung {i+1}", width=80, anchor="center", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2 + i, padx=2, pady=2, sticky="nsew")

        for index in range(2 + num_frames):
            self.grid_container.grid_columnconfigure(index, weight=1)

        for step, frame_state in enumerate(frames):
            is_fault = step in page_faults
            row_bg = "#3d3d3d" if not is_fault else "#4b0000"

            step_label = ctk.CTkLabel(self.grid_container, text=str(step + 1), width=60, anchor="center", fg_color=row_bg)
            step_label.grid(row=step + 1, column=0, padx=2, pady=2, sticky="nsew")

            requested_text = str(self.result.get("references", [""])[step]) if step < len(self.result.get("references", [])) else ""
            requested_label = ctk.CTkLabel(self.grid_container, text=requested_text, width=80, anchor="center", fg_color=row_bg)
            requested_label.grid(row=step + 1, column=1, padx=2, pady=2, sticky="nsew")

            for index, cell in enumerate(frame_state):
                label_text = "-" if cell is None else str(cell)
                cell_bg = "#2d2d2d"
                if is_fault:
                    cell_bg = "#8b0000"
                cell_label = ctk.CTkLabel(self.grid_container, text=label_text, width=80, anchor="center", fg_color=cell_bg)
                cell_label.grid(row=step + 1, column=2 + index, padx=2, pady=2, sticky="nsew")

        # Add a legend below the grid
        legend = ctk.CTkFrame(self.grid_container, corner_radius=0)
        legend.grid(row=len(frames) + 1, column=0, columnspan=2 + num_frames, sticky="ew", pady=(8, 0))
        legend.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(legend, text="Chú thích:", anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=2, pady=2, sticky="w")
        ctk.CTkLabel(legend, text="Màu đỏ = Page Fault xảy ra tại bước đó", anchor="w").grid(row=0, column=1, padx=8, pady=2, sticky="w")
