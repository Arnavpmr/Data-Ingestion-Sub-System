import os
from log_config import get_logger

def get_latest_dir(base_dir):
    logger = get_logger(module_name=__name__)

    date_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    if not date_dirs:
        raise FileNotFoundError("No valid date directories found in raw missingnpf data.")

    latest_date = max(date_dirs)

    logger.debug(f"Retrieved latest date directory: {latest_date}")

    return os.path.join(base_dir, latest_date)