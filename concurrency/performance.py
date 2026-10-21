"""Concurrency and Performance benchmarking: Sequential vs Multithreading vs Multiprocessing."""

import time
import math
import random
import cProfile
import pstats
import io
from typing import Dict, Any, List, Tuple, Optional
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.logging_config import get_logger

logger = get_logger("concurrency.performance")


# Module III: Top-level picklable worker function for multiprocessing (Windows spawn safe)
def heavy_risk_simulation_worker(chunk: Tuple[int, int, float]) -> float:
    """CPU-intensive simulation worker function.
    
    Simulates stochastic Monte Carlo circulation risk scoring and depreciation
    over thousands of iterations per batch.
    Must be a top-level function for multiprocessing picklability on Windows.
    """
    start_seed, iterations, base_factor = chunk
    random.seed(start_seed)
    
    total_risk = 0.0
    for i in range(iterations):
        # Heavy numerical calculation involving trigonometry, exponentials, and logarithms
        x = (i % 1000) / 1000.0 + 0.001
        noise = random.random()
        term = math.sin(x * math.pi) * math.exp(-x * 0.1) + math.log(x + 1.0) * noise
        total_risk += term * base_factor
    
    return total_risk


class PerformanceBenchmarker:
    """Demonstrates and compares Sequential, Multithreaded, and Multiprocessing execution.
    
    Demonstrates:
    - Module III: Multiprocessing with ProcessPool
    - Module III: Multithreading with ThreadPoolExecutor
    - Module III: Precise execution timing using time.perf_counter()
    - Module III: Real reproducible speedup benchmarks
    - Module III: Profiling with cProfile
    """

    def __init__(self, total_simulations: int = 500_000, num_chunks: int = 8):
        self.total_simulations = total_simulations
        self.num_chunks = num_chunks
        self.chunk_size = total_simulations // num_chunks
        # Generate tasks: (seed, iterations, base_factor)
        self.chunks = [
            (idx * 1337 + 42, self.chunk_size, 1.05 + (idx * 0.01))
            for idx in range(num_chunks)
        ]

    def run_sequential(self) -> Tuple[float, float]:
        """Execute CPU-bound simulation sequentially on a single thread."""
        logger.info("Starting Sequential benchmark (%d iterations)...", self.total_simulations)
        t_start = time.perf_counter()
        
        results = [heavy_risk_simulation_worker(c) for c in self.chunks]
        total_score = sum(results)
        
        duration = time.perf_counter() - t_start
        logger.info("Sequential completed in %.4f seconds (Result: %.2f)", duration, total_score)
        return duration, total_score

    def run_multithreading(self, max_workers: int = 4) -> Tuple[float, float]:
        """Execute simulation using ThreadPoolExecutor.
        
        Due to Python's GIL (Global Interpreter Lock), CPU-bound multithreading
        does not achieve linear speedup and demonstrates GIL contention.
        """
        logger.info("Starting Multithreading benchmark (workers=%d)...", max_workers)
        t_start = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(heavy_risk_simulation_worker, self.chunks))
            total_score = sum(results)
            
        duration = time.perf_counter() - t_start
        logger.info("Multithreading completed in %.4f seconds (Result: %.2f)", duration, total_score)
        return duration, total_score

    def run_multiprocessing(self, processes: Optional[int] = None) -> Tuple[float, float]:
        """Execute simulation across multiple OS processes bypassing GIL.
        
        Demonstrates true parallel execution on multi-core CPUs.
        """
        workers = processes or max(1, cpu_count() - 1)
        logger.info("Starting Multiprocessing benchmark (processes=%d)...", workers)
        t_start = time.perf_counter()
        
        with Pool(processes=workers) as pool:
            results = pool.map(heavy_risk_simulation_worker, self.chunks)
            total_score = sum(results)
            
        duration = time.perf_counter() - t_start
        logger.info("Multiprocessing completed in %.4f seconds (Result: %.2f)", duration, total_score)
        return duration, total_score

    def run_full_comparison(self) -> Dict[str, Any]:
        """Run all three modes, assert consistency, and calculate relative speedups."""
        seq_time, seq_res = self.run_sequential()
        thr_time, thr_res = self.run_multithreading()
        mp_time, mp_res = self.run_multiprocessing()

        # Assert calculation correctness across implementations
        assert math.isclose(seq_res, thr_res, rel_tol=1e-5), "Threaded result mismatch!"
        assert math.isclose(seq_res, mp_res, rel_tol=1e-5), "Multiprocessing result mismatch!"

        speedup_thr = seq_time / thr_time if thr_time > 0 else 1.0
        speedup_mp = seq_time / mp_time if mp_time > 0 else 1.0

        return {
            "total_simulations": self.total_simulations,
            "sequential_time_sec": round(seq_time, 4),
            "threading_time_sec": round(thr_time, 4),
            "multiprocessing_time_sec": round(mp_time, 4),
            "threading_speedup": round(speedup_thr, 2),
            "multiprocessing_speedup": round(speedup_mp, 2),
            "cpu_cores_available": cpu_count()
        }

    @staticmethod
    def profile_function(target_fn, *args, **kwargs) -> str:
        """Profile execution of a function using standard library cProfile."""
        profiler = cProfile.Profile()
        profiler.enable()
        result = target_fn(*args, **kwargs)
        profiler.disable()

        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(20)  # Top 20 time-consuming calls
        return s.getvalue()
