FROM linuxserver/ffmpeg as ffmpeg-stage

# Create a script to copy ffmpeg and all its dependencies
RUN mkdir -p /ffmpeg-output/bin /ffmpeg-output/lib && \
    cp /usr/local/bin/ffmpeg /ffmpeg-output/bin/ && \
    cp /usr/local/bin/ffprobe /ffmpeg-output/bin/ && \
    # Get all library dependencies and copy them
    for lib in $(ldd /usr/local/bin/ffmpeg | grep -o '/[^ ]*' | sort -u); do \
      if [ -f "$lib" ]; then cp "$lib" /ffmpeg-output/lib/ 2>/dev/null || true; fi; \
    done && \
    # Also get transitive dependencies by examining each library
    for lib in /ffmpeg-output/lib/*.so*; do \
      if [ -f "$lib" ]; then \
        for dep in $(ldd "$lib" 2>/dev/null | grep -o '/[^ ]*' | sort -u); do \
          if [ -f "$dep" ]; then cp "$dep" /ffmpeg-output/lib/ 2>/dev/null || true; fi; \
        done; \
      fi; \
    done

FROM public.ecr.aws/lambda/python:3.12

# Copy ffmpeg and libraries from builder stage
COPY --from=ffmpeg-stage /ffmpeg-output/bin/ffmpeg /usr/local/bin/
COPY --from=ffmpeg-stage /ffmpeg-output/bin/ffprobe /usr/local/bin/
COPY --from=ffmpeg-stage /ffmpeg-output/lib/* /usr/lib/x86_64-linux-gnu/

# Ensure library cache is updated
RUN ldconfig || true

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
