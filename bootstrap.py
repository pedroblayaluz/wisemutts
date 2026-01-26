#!/usr/bin/env python3
import sys
import os

# Add lambda task root to path
sys.path.insert(0, '/var/task')
os.chdir('/tmp')

from awsruntimeclient.invoke_context import InvokeContext
from awsruntimeclient.lambda_runtime_client import LambdaRuntimeClient
from src.main import lambda_handler

if __name__ == "__main__":
    lambda_runtime_client = LambdaRuntimeClient("http://" + os.environ["AWS_LAMBDA_RUNTIME_API"] + "/")

    while True:
        invocation = lambda_runtime_client.wait_next_invocation()
        try:
            response = lambda_handler(invocation.event, invocation.invoke_context)
            lambda_runtime_client.post_invocation_response(invocation.invoke_id, response)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            lambda_runtime_client.post_invocation_error(invocation.invoke_id, str(e))
