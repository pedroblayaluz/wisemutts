FROM ubuntu:22.04 as builder

# Install ffmpeg and dependencies
RUN apt-get update && apt-get install -y ffmpeg && \
    mkdir -p /opt/ffmpeg/bin /opt/ffmpeg/lib && \
    cp /usr/bin/ffmpeg /opt/ffmpeg/bin/ && \
    cp /usr/bin/ffprobe /opt/ffmpeg/bin/ && \
    ldd /usr/bin/ffmpeg | grep "=>" | awk '{print $3}' | xargs -I {} cp {} /opt/ffmpeg/lib/ 2>/dev/null || true && \
    ldd /usr/bin/ffprobe | grep "=>" | awk '{print $3}' | xargs -I {} cp {} /opt/ffmpeg/lib/ 2>/dev/null || true

FROM public.ecr.aws/lambda/python:3.12

# Copy ffmpeg and libraries from builder
COPY --from=builder /opt/ffmpeg/bin/ffmpeg /usr/local/bin/ffmpeg
COPY --from=builder /opt/ffmpeg/lib/* /usr/local/lib/

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
ENV PATH=/usr/local/bin:${PATH}

# Set the CMD to your handler
CMD [ "src.main.lambda_handler" ]
