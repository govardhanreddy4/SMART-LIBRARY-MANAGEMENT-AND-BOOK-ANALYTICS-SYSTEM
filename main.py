"""Application Entry Point for Smart Library Management and Book Analytics System."""

import sys
import multiprocessing
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.schema import init_db
from gui.main_window import MainWindow
from utils.logging_config import setup_logging, get_logger

logger = get_logger("main")


def main() -> None:
    """Bootstraps database, logging, and launches the graphical interface."""
    # Module III: Support for multiprocessing on Windows
    multiprocessing.freeze_support()

    setup_logging()
    logger.info("==================================================")
    logger.info("Starting Smart Library Management and Book Analytics System")
    logger.info("Runtime Python Version: %s", sys.version)
    logger.info("Project Root Directory: %s", PROJECT_ROOT)
    logger.info("==================================================")

    # Initialize SQLite database with tables, indexes, and default admin
    init_db(seed_samples=True)

    # Launch GUI application
    app = MainWindow()
    try:
        app.mainloop()
    except Exception as e:
        logger.critical("Unhandled fatal exception in GUI event loop: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
