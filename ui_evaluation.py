import random
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from logic_cpu import fcfs_scheduling, sjf_scheduling, rr_scheduling


class EvaluationFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.figure = None
        self.canvas = None
        self.current_results = None
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkLabel(self, text="Đánh giá hiệu năng", font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=(12, 16))

        control_frame = ctk.CTkFrame(self, corner_radius=12)
        control_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.run_button = ctk.CTkButton(control_frame, text="Chạy thử nghiệm tổng thể", command=self._run_benchmark)
        self.run_button.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        self.save_button = ctk.CTkButton(control_frame, text="Xuất báo cáo", command=self._save_report, state="disabled")
        self.save_button.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        control_frame.grid_columnconfigure((0, 1), weight=1)

        summary_frame = ctk.CTkFrame(self, corner_radius=12)
        summary_frame.pack(fill="both", expand=False, padx=16, pady=(0, 12))

        self.summary_text = ctk.CTkTextbox(summary_frame, width=1, height=140)
        self.summary_text.pack(fill="both", expand=True, padx=12, pady=12)
        self.summary_text.configure(state="disabled")

        chart_frame = ctk.CTkFrame(self, corner_radius=12)
        chart_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)

        self.canvas_container = ctk.CTkFrame(chart_frame, corner_radius=12)
        self.canvas_container.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

    def _run_benchmark(self):
        processes = self._generate_test_case()
        fcfs_result = fcfs_scheduling(processes)
        sjf_result = sjf_scheduling(processes)
        rr_result = rr_scheduling(processes, quantum=2)

        self.current_results = {
            "FCFS": fcfs_result,
            "SJF": sjf_result,
            "Round Robin": rr_result,
        }

        self._render_summary(processes)
        self._render_chart()
        self.save_button.configure(state="normal")

    def _generate_test_case(self):
        count = 5
        processes = []
        for pid in range(1, count + 1):
            arrival = random.randint(0, 5)
            burst = random.randint(1, 10)
            processes.append({"pid": pid, "arrival": arrival, "burst": burst})
        processes.sort(key=lambda proc: (proc["arrival"], proc["pid"]))
        return processes

    def _render_summary(self, processes):
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", "Dữ liệu thử nghiệm:\n")
        self.summary_text.insert("end", "PID\tArrival\tBurst\n")
        self.summary_text.insert("end", "-------------------------\n")
        for proc in processes:
            self.summary_text.insert("end", f"{proc['pid']}\t{proc['arrival']}\t{proc['burst']}\n")

        self.summary_text.insert("end", "\nKết quả trung bình:\n")
        for name, result in self.current_results.items():
            if name == "Round Robin":
                self.summary_text.insert("end", f"{name} (quantum=2):\n")
            else:
                self.summary_text.insert("end", f"{name}:\n")
            self.summary_text.insert("end", f"  Average Waiting Time = {result['average_waiting_time']}\n")
            self.summary_text.insert("end", f"  Average Turnaround Time = {result['average_turnaround_time']}\n")
        self.summary_text.configure(state="disabled")

    def _render_chart(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        algorithms = list(self.current_results.keys())
        waiting = [self.current_results[name]["average_waiting_time"] for name in algorithms]
        turnaround = [self.current_results[name]["average_turnaround_time"] for name in algorithms]

        self.figure = Figure(figsize=(8, 4), dpi=100)
        ax = self.figure.add_subplot(111)

        bar_width = 0.35
        indices = list(range(len(algorithms)))

        ax.bar([i - bar_width / 2 for i in indices], waiting, width=bar_width, label="Average Waiting Time", color="#4B8BBE")
        ax.bar([i + bar_width / 2 for i in indices], turnaround, width=bar_width, label="Average Turnaround Time", color="#306998")

        ax.set_xticks(indices)
        ax.set_xticklabels(algorithms)
        ax.set_ylabel("Time")
        ax.set_title("So sánh hiệu năng thuật toán lập lịch CPU")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        for i, value in enumerate(waiting):
            ax.text(i - bar_width / 2, value + 0.1, str(value), ha="center", va="bottom", fontsize=9)
        for i, value in enumerate(turnaround):
            ax.text(i + bar_width / 2, value + 0.1, str(value), ha="center", va="bottom", fontsize=9)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _save_report(self):
        if not self.figure:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            title="Lưu báo cáo biểu đồ",
        )
        if file_path:
            self.figure.savefig(file_path)
