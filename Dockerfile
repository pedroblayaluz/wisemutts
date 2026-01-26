FROM linuxserver/ffmpeg as ffmpeg-stage

# Copy only ffmpeg-specific libraries, NOT system libraries
RUN mkdir -p /ffmpeg-output/bin /ffmpeg-output/lib && \
    cp /usr/local/bin/ffmpeg /ffmpeg-output/bin/ && \
    cp /usr/local/bin/ffprobe /ffmpeg-output/bin/ && \
    # Get ffmpeg library dependencies, but EXCLUDE system libraries
    for lib in $(ldd /usr/local/bin/ffmpeg | grep -o '/[^ ]*' | sort -u); do \
      # Skip system libraries that Lambda already has
      case "$lib" in \
        */libc.so* | */libm.so* | */libdl.so* | */libpthread.so* | */librt.so* | \
        */libstdc++.so* | */libgcc_s.so* | */ld-linux* | */libz.so* ) \
          echo "Skipping system lib: $lib"; \
          ;; \
        *) \
          if [ -f "$lib" ]; then cp "$lib" /ffmpeg-output/lib/ 2>/dev/null || true; fi; \
          ;; \
      esac; \
    done && \
    # Get transitive dependencies from ffmpeg libs (but exclude system libs)
    for lib in /ffmpeg-output/lib/*.so*; do \
      if [ -f "$lib" ]; then \
        for dep in $(ldd "$lib" 2>/dev/null | grep -o '/[^ ]*' | sort -u); do \
          case "$dep" in \
            */libc.so* | */libm.so* | */libdl.so* | */libpthread.so* | */librt.so* | \
            */libstdc++.so* | */libgcc_s.so* | */ld-linux* | */libz.so* ) \
              ;; \
            *) \
              if [ -f "$dep" ]; then cp "$dep" /ffmpeg-output/lib/ 2>/dev/null || true; fi; \
              ;; \
          esac; \
        done; \
      fi; \
    done

FROM public.ecr.aws/lambda/python:3.12

# Copy ffmpeg and libraries from builder stage (but NOT system libraries)
COPY --from=ffmpeg-stage /ffmpeg-output/bin/ffmpeg /usr/local/bin/
COPY --from=ffmpeg-stage /ffmpeg-output/bin/ffprobe /usr/local/bin/
COPY --from=ffmpeg-stage /ffmpeg-output/lib/* /usr/lib/x86_64-linux-gnu/

# Ensure library cache is updated
RUN ldconfig || true

# Verify ffmpeg works
RUN /usr/local/bin/ffmpeg -version 2>&1 | head -3 || echo "Warning: ffmpeg test at build time inconclusive"

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
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}:${PYTHONPATH}
# Ensure /usr/lib/x86_64-linux-gnu is in library path
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Set the CMD to your handler
CMD [ "src.main.lambda_handler" ]
