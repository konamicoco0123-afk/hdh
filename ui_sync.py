import random
import threading
import time
import queue

import customtkinter as ctk


class SyncFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.buffer_size = 5
        self.buffer_queue = queue.Queue(maxsize=self.buffer_size)
        self.empty_slots = threading.Semaphore(self.buffer_size)
        self.full_slots = threading.Semaphore(0)
        self.mutex = threading.Lock()
        self.mutex_locked = False
        self.running = False
        self.producer_thread = None
        self.consumer_thread = None
        self.speed_var = ctk.DoubleVar(value=1.0)
        self._build_ui()
        self._update_status_labels()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="Đồng bộ hóa tiến trình", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(12, 16))

        control_frame = ctk.CTkFrame(self, corner_radius=12)
        control_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.start_button = ctk.CTkButton(control_frame, text="Bắt đầu mô phỏng", command=self._start_simulation)
        self.start_button.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        self.stop_button = ctk.CTkButton(control_frame, text="Dừng", command=self._stop_simulation, fg_color="#D32F2F", hover_color="#F44336")
        self.stop_button.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.stop_button.configure(state="disabled")

        speed_frame = ctk.CTkFrame(control_frame, corner_radius=12)
        speed_frame.grid(row=0, column=2, padx=8, pady=8, sticky="ew")
        speed_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(speed_frame, text="Tốc độ (thấp = rất chậm, cao = nhanh):").grid(row=0, column=0, padx=(12, 8), pady=8, sticky="w")
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0.2,
            to=2.0,
            number_of_steps=19,
            variable=self.speed_var,
            command=self._update_speed_label,
        )
        self.speed_slider.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.speed_label = ctk.CTkLabel(speed_frame, text=f"Delay hiện tại: {self._get_delay():.1f}s", anchor="w")
        self.speed_label.grid(row=2, column=0, padx=(12, 8), pady=(0, 12), sticky="w")

        status_frame = ctk.CTkFrame(self, corner_radius=12)
        status_frame.pack(fill="x", padx=16, pady=(0, 12))
        status_frame.grid_columnconfigure((0, 1), weight=1)

        self.mutex_label = ctk.CTkLabel(status_frame, text="Mutex: Mở", anchor="w", fg_color="#4CAF50", corner_radius=8)
        self.mutex_label.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        self.semaphore_label = ctk.CTkLabel(status_frame, text="Semaphore: empty=5 full=0", anchor="w", fg_color="#546E7A", corner_radius=8)
        self.semaphore_label.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        buffer_frame = ctk.CTkFrame(self, corner_radius=12)
        buffer_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        buffer_title = ctk.CTkLabel(buffer_frame, text="Buffer cố định", anchor="w")
        buffer_title.pack(fill="x", padx=12, pady=(12, 0))

        self.buffer_boxes = []
        box_row = ctk.CTkFrame(buffer_frame, corner_radius=0)
        box_row.pack(fill="x", padx=12, pady=12)
        for i in range(self.buffer_size):
            box = ctk.CTkFrame(box_row, fg_color="#616161", corner_radius=12)
            box.grid(row=0, column=i, padx=6, pady=6)
            inner = ctk.CTkLabel(
                box,
                text="",
                width=76,
                height=76,
                fg_color="#424242",
                corner_radius=12,
                text_color="#ffffff",
                font=ctk.CTkFont(size=18, weight="bold"),
            )
            inner.pack(expand=True, fill="both", padx=2, pady=2)
            self.buffer_boxes.append(inner)

        legend_frame = ctk.CTkFrame(self, corner_radius=12)
        legend_frame.pack(fill="x", padx=16, pady=(0, 12))
        legend_frame.grid_columnconfigure((0, 1), weight=1)

        producer_label = ctk.CTkLabel(legend_frame, text="Producer: xanh", fg_color="#388E3C", corner_radius=8)
        producer_label.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        consumer_label = ctk.CTkLabel(legend_frame, text="Consumer: xám", fg_color="#424242", corner_radius=8)
        consumer_label.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

    def _start_simulation(self):
        if self.running:
            return

        self.running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self._reset_buffer()

        self.producer_thread = threading.Thread(target=self._producer_loop, daemon=True)
        self.consumer_thread = threading.Thread(target=self._consumer_loop, daemon=True)
        self.producer_thread.start()
        self.consumer_thread.start()
        self._schedule_update()

    def _stop_simulation(self):
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        if self.producer_thread is not None:
            self.producer_thread.join(timeout=0.5)
        if self.consumer_thread is not None:
            self.consumer_thread.join(timeout=0.5)

    def _reset_buffer(self):
        self.buffer_queue = queue.Queue(maxsize=self.buffer_size)
        self.empty_slots = threading.Semaphore(self.buffer_size)
        self.full_slots = threading.Semaphore(0)
        self.mutex = threading.Lock()
        self.mutex_locked = False
        self._update_buffer_ui()
        self._update_status_labels()

    def _get_delay(self):
        # Giá trị slider nhỏ -> chậm, lớn -> nhanh
        # Dùng công thức nghịch đảo với hệ số lớn hơn để items ở buffer hiển thị lâu.
        speed = max(self.speed_var.get(), 0.1)
        return 3.0 / speed

    def _producer_loop(self):
        while self.running:
            time.sleep(self._get_delay())
            acquired = self.empty_slots.acquire(timeout=0.1)
            if not acquired:
                self._schedule_update()
                continue

            self._set_mutex_state(True)
            try:
                item = random.randint(1, 99)
                self.buffer_queue.put(item)
                self._schedule_update()
            finally:
                self._set_mutex_state(False)
                self.full_slots.release()

    def _consumer_loop(self):
        while self.running:
            time.sleep(self._get_delay())
            acquired = self.full_slots.acquire(timeout=0.1)
            if not acquired:
                self._schedule_update()
                continue

            self._set_mutex_state(True)
            try:
                item = self.buffer_queue.get()
                self._schedule_update()
            finally:
                self._set_mutex_state(False)
                self.empty_slots.release()

    def _set_mutex_state(self, locked):
        self.mutex_locked = locked
        self._schedule_update()

    def _update_speed_label(self, value=None):
        self.speed_label.configure(text=f"Delay hiện tại: {self._get_delay():.1f}s")

    def _schedule_update(self):
        self.after(0, self._update_ui)

    def _update_ui(self):
        self._update_buffer_ui()
        self._update_status_labels()

    def _update_buffer_ui(self):
        contents = list(self.buffer_queue.queue)
        for index, box in enumerate(self.buffer_boxes):
            if index < len(contents):
                box.configure(text=str(contents[index]), fg_color="#1976D2")
            else:
                box.configure(text="", fg_color="#424242")

    def _update_status_labels(self):
        mutex_text = "Mutex: Khóa" if self.mutex_locked else "Mutex: Mở"
        mutex_color = "#D32F2F" if self.mutex_locked else "#4CAF50"
        self.mutex_label.configure(text=mutex_text, fg_color=mutex_color)

        empty_count = getattr(self.empty_slots, "_value", None)
        full_count = getattr(self.full_slots, "_value", None)
        if empty_count is None or full_count is None:
            empty_count = self.buffer_size - self.buffer_queue.qsize()
            full_count = self.buffer_queue.qsize()
        self.semaphore_label.configure(text=f"Semaphore: empty={empty_count} full={full_count}")
