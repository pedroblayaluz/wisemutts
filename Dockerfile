FROM python:3.12-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create Lambda directories
ENV LAMBDA_TASK_ROOT=/var/task
RUN mkdir -p ${LAMBDA_TASK_ROOT}

# Copy requirements
COPY requirements.lock ${LAMBDA_TASK_ROOT}/

# Install all requirements from lock file (exact versions from local venv)
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.lock && \
    pip install --no-cache-dir aws-lambda-ric

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set working directory to /tmp (writable in Lambda)
WORKDIR /tmp

# Add LAMBDA_TASK_ROOT to Python path so imports work
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}:${PYTHONPATH}

# Set the CMD to your handler with Lambda RIC
CMD [ "aws_lambda_ric.bootstrap.handler", "src.main.lambda_handler" ]
