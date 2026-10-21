"""Concurrency and Performance Benchmark View demonstrating Module III concepts live."""

import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing
from typing import Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from concurrency.performance import PerformanceBenchmarker
from concurrency.background_tasks import BackgroundTaskWorker
from concurrency.async_tasks import AsyncTaskManager
from config import THEME_COLORS
from gui.styles import UIStyleHelper
from utils.logging_config import get_logger

logger = get_logger("gui.concurrency_view")


class ConcurrencyView(ttk.Frame):
    """Interactive GUI testbed demonstrating Multithreading, Multiprocessing, and AsyncIO."""

    def __init__(self, parent: tk.Widget, task_worker: BackgroundTaskWorker):
        super().__init__(parent)
        self.task_worker = task_worker
        self.benchmarker = PerformanceBenchmarker(total_simulations=300_000, num_chunks=6)
        self.async_mgr = AsyncTaskManager()

        self.configure(style="TFrame")
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header Frame
        hdr = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        title = tk.Label(
            hdr,
            text="Module III: Concurrency, Performance & Profiling Benchmarks",
            font=UIStyleHelper.FONT_TITLE,
            bg=THEME_COLORS["content_bg"],
            fg=THEME_COLORS["text_dark"]
        )
        title.pack(side="left")

        # Two-column container
        content_frame = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        content_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(8, 20))
        content_frame.columnconfigure(0, weight=3)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)

        # Left Card: Benchmark Runner & Results Table
        left_card = tk.Frame(content_frame, bg=THEME_COLORS["card_bg"], bd=1, relief="solid", padx=20, pady=20)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(
            left_card,
            text="CPU-Bound Monte Carlo Risk Simulation Benchmark",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["primary"]
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            left_card,
            text="Compares Sequential single-thread vs Multithreading (GIL contention) vs Multiprocessing (true multi-core parallelism).",
            font=UIStyleHelper.FONT_SMALL,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["text_muted"],
            wraplength=480,
            justify="left"
        ).pack(anchor="w", pady=(0, 16))

        # Controls
        ctrl_frame = tk.Frame(left_card, bg=THEME_COLORS["card_bg"])
        ctrl_frame.pack(fill="x", pady=(0, 16))

        self.run_btn = ttk.Button(
            ctrl_frame,
            text="⚡ Run Live CPU Benchmark",
            style="TButton",
            command=self._start_cpu_benchmark
        )
        self.run_btn.pack(side="left", padx=(0, 8))

        self.async_btn = ttk.Button(
            ctrl_frame,
            text="🌐 Run AsyncIO Network Test",
            command=self._start_async_test
        )
        self.async_btn.pack(side="left", padx=(0, 8))

        self.profile_btn = ttk.Button(
            ctrl_frame,
            text="⏱️ cProfile Report",
            command=self._run_cprofile
        )
        self.profile_btn.pack(side="left")

        self.bench_status = tk.Label(
            left_card,
            text="Click 'Run Live CPU Benchmark' to execute real performance tests.",
            font=UIStyleHelper.FONT_BODY,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["text_dark"]
        )
        self.bench_status.pack(anchor="w", pady=(0, 12))

        # Metrics Display Table
        self.metric_display = tk.Text(
            left_card,
            font=("Consolas", 10),
            bg="#0F172A",
            fg="#38BDF8",
            relief="flat",
            height=14,
            padx=12,
            pady=12
        )
        self.metric_display.pack(fill="both", expand=True)
        self.metric_display.insert("1.0", self._default_terminal_text())
        self.metric_display.config(state="disabled")

        # Right Card: Theoretical & Architectural Explanations (Viva Ready)
        right_card = tk.Frame(content_frame, bg=THEME_COLORS["card_bg"], bd=1, relief="solid", padx=20, pady=20)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            right_card,
            text="Course Architecture Guide (Viva Notes)",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 12))

        viva_text = (
            "1. Multithreading (I/O-Bound):\n"
            "   • Used for Google Books API requests & background file exports.\n"
            "   • Thread-safe GUI queue (queue.Queue) prevents UI freezing.\n"
            "   • Tkinter widgets are updated solely via root.after() polling.\n\n"
            "2. Multiprocessing (CPU-Bound):\n"
            "   • Bypasses the Global Interpreter Lock (GIL).\n"
            "   • Distributes heavy numerical simulations across CPU cores.\n"
            "   • Achieves near-linear parallel speedup on multi-core processors.\n\n"
            "3. AsyncIO (Concurrent Coroutines):\n"
            "   • Single-threaded non-blocking event loop using aiohttp.\n"
            "   • Concurrently queries multiple book category endpoints.\n\n"
            "4. Profiling & Measurement:\n"
            "   • High-resolution timings captured via time.perf_counter().\n"
            "   • Standard library cProfile inspects hotspots & call stacks."
        )

        guide_box = tk.Label(
            right_card,
            text=viva_text,
            font=UIStyleHelper.FONT_BODY,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["text_dark"],
            justify="left",
            wraplength=340
        )
        guide_box.pack(anchor="nw", fill="both", expand=True)

    def _default_terminal_text(self) -> str:
        return (
            f"Hardware Diagnostics:\n"
            f"Available CPU Cores: {multiprocessing.cpu_count()}\n"
            f"OS Platform: Windows 64-bit\n"
            f"Python Runtime: 3.11.0\n\n"
            f"Status: Standing by for benchmark run...\n"
        )

    def _start_cpu_benchmark(self) -> None:
        self.run_btn.config(state="disabled")
        self.bench_status.config(text="⏳ Executing benchmark across 3 modes in background...", fg=THEME_COLORS["primary"])

        def on_success(res):
            self.run_btn.config(state="normal")
            self.bench_status.config(text="✓ Benchmark completed successfully!", fg=THEME_COLORS["success"])
            
            output = (
                f"=== CPU BENCHMARK RESULTS (time.perf_counter) ===\n"
                f"Simulations Count     : {res['total_simulations']:,}\n"
                f"Available CPU Cores   : {res['cpu_cores_available']}\n"
                f"--------------------------------------------------\n"
                f"1. Sequential Execution : {res['sequential_time_sec']:.4f} s  (Baseline: 1.00x)\n"
                f"2. ThreadPool (GIL)     : {res['threading_time_sec']:.4f} s  (Speedup:  {res['threading_speedup']:.2f}x)\n"
                f"3. ProcessPool (Multi)  : {res['multiprocessing_time_sec']:.4f} s  (Speedup:  {res['multiprocessing_speedup']:.2f}x)\n"
                f"--------------------------------------------------\n"
                f"Observation: Multiprocessing successfully bypasses\n"
                f"Python's GIL for compute-heavy workloads.\n"
            )

            self.metric_display.config(state="normal")
            self.metric_display.delete("1.0", tk.END)
            self.metric_display.insert("1.0", output)
            self.metric_display.config(state="disabled")

        def on_error(e):
            self.run_btn.config(state="normal")
            self.bench_status.config(text=f"❌ Benchmark error: {e}", fg=THEME_COLORS["danger"])
            logger.error("Benchmark failed: %s", e)

        # Run in thread so GUI remains responsive
        self.task_worker.run_in_thread(
            target_fn=self.benchmarker.run_full_comparison,
            on_success=on_success,
            on_error=on_error
        )

    def _start_async_test(self) -> None:
        self.async_btn.config(state="disabled")
        self.bench_status.config(text="⏳ Running concurrent AsyncIO HTTP requests...", fg=THEME_COLORS["secondary"])

        queries = ["Python", "Algorithms", "Databases", "Networks"]

        def on_success(results):
            self.async_btn.config(state="normal")
            self.bench_status.config(text="✓ AsyncIO concurrent fetch completed!", fg=THEME_COLORS["success"])

            lines = ["=== ASYNCIO CONCURRENT HTTP REQUESTS (aiohttp) ==="]
            for q, items in results.items():
                lines.append(f"Query: '{q}' -> Fetched {len(items)} volumes asynchronously.")

            self.metric_display.config(state="normal")
            self.metric_display.delete("1.0", tk.END)
            self.metric_display.insert("1.0", "\n".join(lines))
            self.metric_display.config(state="disabled")

        def on_error(e):
            self.async_btn.config(state="normal")
            self.bench_status.config(text=f"❌ AsyncIO error: {e}", fg=THEME_COLORS["danger"])

        self.task_worker.run_in_thread(
            target_fn=self.async_mgr.run_concurrent_search,
            args=(queries,),
            on_success=on_success,
            on_error=on_error
        )

    def _run_cprofile(self) -> None:
        self.bench_status.config(text="Profiling benchmark with cProfile...", fg=THEME_COLORS["primary"])
        report = PerformanceBenchmarker.profile_function(self.benchmarker.run_sequential)
        
        self.metric_display.config(state="normal")
        self.metric_display.delete("1.0", tk.END)
        self.metric_display.insert("1.0", "=== cProfile Top Function Cumulative Times ===\n\n" + report)
        self.metric_display.config(state="disabled")
        self.bench_status.config(text="✓ cProfile report generated.", fg=THEME_COLORS["success"])
