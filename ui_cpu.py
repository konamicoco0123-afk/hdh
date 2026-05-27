import customtkinter as ctk
from tkinter import messagebox as mb
from logic_cpu import fcfs_scheduling, sjf_scheduling, rr_scheduling


class CPUFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.processes = []
        self.next_pid = 1
        self.current_result = None
        self.animation_steps = []
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkLabel(self, text="Lập lịch CPU", font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=(12, 16))

        form_frame = ctk.CTkFrame(self, corner_radius=12)
        form_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.arrival_entry = self._build_labeled_entry(form_frame, "Arrival Time:")
        self.burst_entry = self._build_labeled_entry(form_frame, "Burst Time:")
        self.quantum_entry = self._build_labeled_entry(form_frame, "Quantum:")
        self.quantum_entry.insert(0, "2")

        button_frame = ctk.CTkFrame(self, corner_radius=12)
        button_frame.pack(fill="x", padx=16, pady=(0, 12))

        add_button = ctk.CTkButton(button_frame, text="Thêm tiến trình", command=self._add_process)
        add_button.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        run_button = ctk.CTkButton(button_frame, text="Chạy mô phỏng", command=self._run_simulation)
        run_button.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        self.algorithm_var = ctk.StringVar(value="FCFS")
        algorithm_frame = ctk.CTkFrame(button_frame, corner_radius=12)
        algorithm_frame.grid(row=0, column=2, padx=8, pady=8, sticky="ew")
        algorithm_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(algorithm_frame, text="Thuật toán:").grid(row=0, column=0, padx=(12, 0), pady=8, sticky="w")
        self.algorithm_menu = ctk.CTkOptionMenu(
            algorithm_frame,
            values=["FCFS", "SJF", "Round Robin"],
            variable=self.algorithm_var,
            width=120,
        )
        self.algorithm_menu.grid(row=0, column=1, padx=(0, 12), pady=8, sticky="e")

        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        list_frame = ctk.CTkFrame(self, corner_radius=12)
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        list_label = ctk.CTkLabel(list_frame, text="Danh sách tiến trình", anchor="w")
        list_label.pack(fill="x", padx=12, pady=(12, 0))

        self.process_text = ctk.CTkTextbox(list_frame, width=1, height=180)
        self.process_text.pack(fill="both", expand=True, padx=12, pady=12)
        self.process_text.configure(state="disabled")

        chart_frame = ctk.CTkFrame(self, corner_radius=12)
        chart_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        chart_label = ctk.CTkLabel(chart_frame, text="Gantt Chart", anchor="w")
        chart_label.pack(fill="x", padx=12, pady=(12, 0))

        bg_color = chart_frame.cget("fg_color")
        if isinstance(bg_color, (list, tuple)):
            bg_color = bg_color[1] if ctk.get_appearance_mode().lower() == "dark" else bg_color[0]

        self.canvas = ctk.CTkCanvas(chart_frame, width=1, height=220, highlightthickness=0, bg=bg_color)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=12)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self._refresh_process_display()

    def _build_labeled_entry(self, parent, label_text):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.pack(fill="x", padx=8, pady=8)

        label = ctk.CTkLabel(frame, text=label_text, width=120, anchor="w")
        label.pack(side="left", padx=(12, 8))

        entry = ctk.CTkEntry(frame)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=8)
        return entry

    def _add_process(self):
        arrival_text = self.arrival_entry.get().strip()
        burst_text = self.burst_entry.get().strip()

        if not arrival_text.isdigit() or not burst_text.isdigit():
            self._show_error("Arrival và Burst phải là số nguyên không âm.")
            return

        arrival = int(arrival_text)
        burst = int(burst_text)

        if burst <= 0:
            self._show_error("Burst Time phải lớn hơn 0.")
            return

        process = {"pid": self.next_pid, "arrival": arrival, "burst": burst}
        self.processes.append(process)
        self.next_pid += 1

        self.arrival_entry.delete(0, "end")
        self.burst_entry.delete(0, "end")
        self._refresh_process_display()
        self._show_info(f"Đã thêm tiến trình: PID={process['pid']}, arrival={arrival}, burst={burst}")

    def _refresh_process_display(self):
        self.process_text.configure(state="normal")
        self.process_text.delete("1.0", "end")

        if not self.processes:
            self.process_text.insert("end", "(Chưa có tiến trình nào được thêm vào.)")
        else:
            self.process_text.insert("end", f"{'PID':<6}{'Arrival':<10}{'Burst':<10}\n")
            self.process_text.insert("end", "-" * 28 + "\n")
            for proc in self.processes:
                self.process_text.insert(
                    "end",
                    f"{proc['pid']:<6}{proc['arrival']:<10}{proc['burst']:<10}\n",
                )

        self.process_text.configure(state="disabled")

    def _run_simulation(self):
        if not self.processes:
            self._show_error("Chưa có tiến trình nào để mô phỏng.")
            return

        algorithm = self.algorithm_var.get()
        if algorithm == "FCFS":
            result = fcfs_scheduling(self.processes)
        elif algorithm == "SJF":
            result = sjf_scheduling(self.processes)
        else:
            quantum_text = self.quantum_entry.get().strip()
            if not quantum_text.isdigit() or int(quantum_text) <= 0:
                self._show_error("Quantum phải là số nguyên dương.")
                return
            quantum = int(quantum_text)
            result = rr_scheduling(self.processes, quantum)

        self.current_result = result
        self._show_result_summary(result)
        self._draw_gantt_chart(result)

    def _show_result_summary(self, result):
        history_lines = [f"PID={item['pid']}  start={item['start']}  end={item['end']}" for item in result["history"]]
        summary = (
            f"Thuật toán: {result['algorithm']}\n"
            f"Average Waiting Time: {result['average_waiting_time']}\n"
            f"Average Turnaround Time: {result['average_turnaround_time']}\n\n"
            "Lịch sử thực thi:\n"
            + "\n".join(history_lines)
        )
        self._show_info(summary, title="Kết quả mô phỏng CPU")

    def _show_info(self, message, title="Thông báo"):
        mb.showinfo(title, message)

    def _show_error(self, message, title="Lỗi"):
        mb.showerror(title, message)

    def _on_canvas_resize(self, event):
        if self.current_result:
            self._draw_gantt_chart(self.current_result)

    def _draw_gantt_chart(self, result):
        self.canvas.delete("all")
        history = result.get("history", [])
        if not history:
            return

        width = max(self.canvas.winfo_width(), 600)
        height = max(self.canvas.winfo_height(), 200)
        margin_x = 40
        margin_y = 30
        row_height = 40
        available_width = width - margin_x * 2

        start_times = [item["start"] for item in history]
        end_times = [item["end"] for item in history]
        total_time = max(end_times) if end_times else 1
        scale = available_width / total_time if total_time > 0 else 1

        colors = ["#4B8BBE", "#306998", "#FFE873", "#FFD43B", "#646464", "#6A5ACD", "#20B2AA", "#FF6F61"]
        pid_colors = {}

        self.animation_steps = []
        y = margin_y
        for index, item in enumerate(history):
            pid = item["pid"]
            if pid not in pid_colors:
                pid_colors[pid] = colors[len(pid_colors) % len(colors)]
            x1 = margin_x + item["start"] * scale
            x2 = margin_x + item["end"] * scale
            self.animation_steps.append((x1, y, x2, y + row_height * 0.8, pid, pid_colors[pid], item["start"], item["end"]))
            y += row_height

        axis_y = y + 10
        self.canvas.create_line(margin_x, axis_y, margin_x + available_width, axis_y, width=2, fill="#888")

        tick_count = min(total_time + 1, 11)
        for i in range(tick_count):
            tick_time = round(i * total_time / (tick_count - 1))
            x = margin_x + tick_time * scale
            self.canvas.create_line(x, axis_y - 6, x, axis_y + 6, width=1, fill="#888")
            self.canvas.create_text(x, axis_y + 18, text=str(tick_time), font=("Arial", 10), fill="#fff")

        self._animate_gantt(0)

    def _animate_gantt(self, step_index):
        if step_index >= len(self.animation_steps):
            return

        x1, y1, x2, y2, pid, color, start, end = self.animation_steps[step_index]
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ffffff", width=1)
        self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=f"PID {pid}", fill="#000", font=("Arial", 11, "bold"))
        self.canvas.create_text(x1 + 5, y1 + 5, anchor="nw", text=str(start), fill="#000", font=("Arial", 9))
        self.canvas.create_text(x2 - 5, y1 + 5, anchor="ne", text=str(end), fill="#000", font=("Arial", 9))

        self.after(250, lambda: self._animate_gantt(step_index + 1))
