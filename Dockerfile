FROM amazonlinux:2023 as builder

# Install ffmpeg
RUN yum install -y ffmpeg && \
    cp /usr/bin/ffmpeg /ffmpeg

FROM public.ecr.aws/lambda/python:3.12

# Copy ffmpeg from builder
COPY --from=builder /ffmpeg /usr/local/bin/ffmpeg

# Copy requirements
COPY requirements.lock ${LAMBDA_TASK_ROOT}/

# Install all requirements from lock file (exact versions from local venv)
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.lock

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set working directory to /tmp (writable in Lambda)
WORKDIR /tmp

# Add LAMBDA_TASK_ROOT to Python path so imports work
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}:${PYTHONPATH}

# Set the CMD to your handler
CMD [ "src.main.lambda_handler" ]
