"""Concurrency and Multiprocessing Benchmark Router."""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from server.schemas import BenchmarkRequest
from concurrency.performance import PerformanceBenchmarker

router = APIRouter(prefix="/api/concurrency", tags=["Concurrency & Performance"])

_benchmark_executor = ThreadPoolExecutor(max_workers=1)


def _run_bench(simulations: int, chunks: int) -> Dict[str, Any]:
    benchmarker = PerformanceBenchmarker(total_simulations=simulations, num_chunks=chunks)
    return benchmarker.run_full_comparison()


@router.post("/benchmark")
async def run_benchmark(payload: BenchmarkRequest = BenchmarkRequest()) -> Dict[str, Any]:
    """Execute live performance benchmark comparing Sequential vs Multithreading vs Multiprocessing."""
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            _benchmark_executor,
            _run_bench,
            payload.total_simulations,
            payload.num_chunks
        )
        return {
            "success": True,
            "message": "Benchmark completed successfully across Sequential, ThreadPool, and ProcessPool.",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Benchmark error: {str(e)}")
