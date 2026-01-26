FROM linuxserver/ffmpeg as ffmpeg-stage

FROM public.ecr.aws/lambda/python:3.12

# Copy ffmpeg binary and ALL needed libraries from ffmpeg stage
COPY --from=ffmpeg-stage /usr/local/bin/ffmpeg /usr/local/bin/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libavformat.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libavcodec.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libavutil.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libswscale.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libswresample.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libavfilter.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libavdevice.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libx264.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libx265.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libvpx.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libopus.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libmp3lame.so* /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-stage /usr/lib/x86_64-linux-gnu/libstdc++.so* /usr/lib/x86_64-linux-gnu/

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
