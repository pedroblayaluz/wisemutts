#!/usr/bin/env python3
import sys
import os
import awslambdaric
from src.main import lambda_handler

# Add lambda task root to path
sys.path.insert(0, '/var/task')
os.chdir('/tmp')

if __name__ == "__main__":
    awslambdaric.run(lambda_handler)
