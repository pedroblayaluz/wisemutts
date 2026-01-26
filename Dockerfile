FROM ubuntu:22.04 as builder

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && \
    mkdir -p /opt/ffmpeg && \
    cp /usr/bin/ffmpeg /opt/ffmpeg/ && \
    cp /usr/bin/ffprobe /opt/ffmpeg/ && \
    # Copy all lib directories that ffmpeg depends on
    cp -r /lib/x86_64-linux-gnu /opt/ffmpeg/lib && \
    cp -r /usr/lib/x86_64-linux-gnu /opt/ffmpeg/usrlib

FROM public.ecr.aws/lambda/python:3.12

# Copy ffmpeg binaries and all libraries from builder
COPY --from=builder /opt/ffmpeg/ffmpeg /usr/local/bin/ffmpeg
COPY --from=builder /opt/ffmpeg/ffprobe /usr/local/bin/ffprobe
COPY --from=builder /opt/ffmpeg/lib /lib/x86_64-linux-gnu
COPY --from=builder /opt/ffmpeg/usrlib /usr/lib/x86_64-linux-gnu

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
