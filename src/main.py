from typing import List, Tuple, Dict, Optional
import os
import logging

def setup_logging(name: str) -> logging.Logger:
    path_to_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs"))
    path_to_log = os.path.abspath(os.path.join(path_to_dir, f"{name}.log"))

    if not os.path.exists(path_to_dir):
        os.mkdir(path_to_dir)

    file_handler = logging.FileHandler(path_to_log)    
    file_handler.setFormatter(logging.Formatter("%(levelname)-7s %(processName)s %(threadName)s %(asctime)s %(funcName)s: %(message)s"))

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    
    return logger

def main():
    pass

if __name__ == "__main__":
    main()