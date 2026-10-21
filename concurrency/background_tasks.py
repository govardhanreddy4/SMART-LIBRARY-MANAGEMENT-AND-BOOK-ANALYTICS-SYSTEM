"""Thread-safe background task execution and GUI communication queue."""

import threading
import queue
from typing import Callable, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.logging_config import get_logger

logger = get_logger("concurrency.background_tasks")


class BackgroundTaskWorker:
    """Manages multithreaded worker execution with safe GUI message queue.
    
    Demonstrates:
    - Module III: Multithreading for I/O-bound background tasks
    - Thread-safe GUI queue communication (queue.Queue)
    - Prevention of GUI freezing during network and file operations
    """

    def __init__(self):
        self.result_queue: queue.Queue = queue.Queue()

    def run_in_thread(
        self,
        target_fn: Callable[..., Any],
        args: tuple = (),
        kwargs: Optional[dict] = None,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> threading.Thread:
        """Execute a function in a background worker thread.
        
        Puts `(on_success, result)` or `(on_error, exception)` into the result_queue.
        """
        if kwargs is None:
            kwargs = {}

        def worker():
            try:
                logger.info("Background thread '%s' started for %s", threading.current_thread().name, target_fn.__name__)
                result = target_fn(*args, **kwargs)
                self.result_queue.put(("SUCCESS", on_success, result))
            except Exception as e:
                logger.error("Error in background thread '%s': %s", threading.current_thread().name, e, exc_info=True)
                self.result_queue.put(("ERROR", on_error, e))

        thread = threading.Thread(target=worker, daemon=True, name=f"Worker-{target_fn.__name__}")
        thread.start()
        return thread

    def poll_gui_queue(self, root_tk, interval_ms: int = 100) -> None:
        """Periodically check the queue from the main Tkinter thread using root.after().
        
        Ensures Tkinter widgets are only ever modified on the main GUI thread.
        """
        try:
            while True:
                # Non-blocking get
                status, callback, data = self.result_queue.get_nowait()
                if callback:
                    try:
                        callback(data)
                    except Exception as cb_err:
                        logger.error("Exception in GUI callback: %s", cb_err, exc_info=True)
                self.result_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Re-schedule polling
            root_tk.after(interval_ms, self.poll_gui_queue, root_tk, interval_ms)
