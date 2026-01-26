FROM linuxserver/ffmpeg AS ffmpeg-stage

# Create output directories and copy ffmpeg binary + all needed libraries
RUN mkdir -p /ffmpeg-output/bin /ffmpeg-output/lib && \
    cp /usr/local/bin/ffmpeg /ffmpeg-output/bin/ && \
    cp /usr/local/bin/ffprobe /ffmpeg-output/bin/ && \
    # Copy ALL libraries ffmpeg needs (use script to get all dependencies)
    for lib in $(ldd /usr/local/bin/ffmpeg | grep -oP '(?<= => )[^ ]+' | sort -u); do \
      if [ -f "$lib" ]; then cp "$lib" /ffmpeg-output/lib/ 2>/dev/null || true; fi; \
    done && \
    # Also get transitive deps from those libraries
    for lib in /ffmpeg-output/lib/*.so*; do \
      if [ -f "$lib" ] && file "$lib" | grep -q ELF; then \
        for dep in $(ldd "$lib" 2>/dev/null | grep -oP '(?<= => )[^ ]+' | sort -u); do \
          if [ -f "$dep" ]; then cp "$dep" /ffmpeg-output/lib/ 2>/dev/null || true; fi; \
        done; \
      fi; \
    done

FROM public.ecr.aws/lambda/python:3.12

# Copy ffmpeg binary and all its dependencies
COPY --from=ffmpeg-stage /ffmpeg-output/bin/ffmpeg /usr/local/bin/
COPY --from=ffmpeg-stage /ffmpeg-output/bin/ffprobe /usr/local/bin/
COPY --from=ffmpeg-stage /ffmpeg-output/lib/* /usr/lib/x86_64-linux-gnu/

# Update library cache
RUN ldconfig || true

# Copy requirements
COPY requirements.lock ${LAMBDA_TASK_ROOT}/

# Install all requirements from lock file (exact versions from local venv)
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.lock

# Copy function code and test script
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY test-ffmpeg.sh /opt/test-ffmpeg.sh
RUN chmod +x /opt/test-ffmpeg.sh

# Set working directory to /tmp (writable in Lambda)
WORKDIR /tmp

# Add LAMBDA_TASK_ROOT to Python path so imports work
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "src.main.lambda_handler" ]
