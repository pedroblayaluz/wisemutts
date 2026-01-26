FROM linuxserver/ffmpeg as ffmpeg-builder

FROM public.ecr.aws/lambda/python:3.12

# Copy ffmpeg binaries from linuxserver/ffmpeg
COPY --from=ffmpeg-builder /usr/local/bin/ffmpeg /usr/local/bin/ffprobe /usr/local/bin/

# Copy ffmpeg libraries from linuxserver/ffmpeg
COPY --from=ffmpeg-builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

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
