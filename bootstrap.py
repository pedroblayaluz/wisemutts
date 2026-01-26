#!/usr/bin/env python3
import sys
import os

# Add lambda task root to path
sys.path.insert(0, '/var/task')
os.chdir('/tmp')

import awslambdaric
from src.main import lambda_handler

if __name__ == "__main__":
    awslambdaric.run(lambda_handler)
