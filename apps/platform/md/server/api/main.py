"""
SillyMD API - DEPRECATED entry point.
This module has been replaced by src/main.py (modular architecture).
Please start the server with: python src/main.py
"""
import sys
import os

if __name__ == "__main__":
    print("DEPRECATED: This entry point has been replaced.")
    print("Please use: python src/main.py")
    print("Or: uvicorn src.main:app --host 0.0.0.0 --port 8000")
    sys.exit(1)
