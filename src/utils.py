import os

def get_latest_dir(base_dir):
    date_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    if not date_dirs:
        raise FileNotFoundError("No valid date directories found in raw missingnpf data.")

    latest_date = max(date_dirs)

    return os.path.join(base_dir, latest_date)