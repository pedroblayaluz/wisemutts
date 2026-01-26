FROM linuxserver/ffmpeg

# Install Python 3.12 and pip
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN ln -sf /usr/bin/python3.12 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.12 /usr/bin/python

# Create Lambda task root
ENV LAMBDA_TASK_ROOT=/var/task
RUN mkdir -p ${LAMBDA_TASK_ROOT}
WORKDIR ${LAMBDA_TASK_ROOT}

# Create a virtual environment
RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV=/opt/venv

# Install AWS Lambda runtime interface client for Python
RUN pip install --no-cache-dir awslambdaric

# Copy requirements and install dependencies
COPY requirements.lock ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.lock

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set working directory to /tmp (writable in Lambda)
WORKDIR /tmp

# Set Python path
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}

# Set entrypoint to run Lambda runtime interface client
ENTRYPOINT [ "/opt/venv/bin/python", "-m", "awslambdaric" ]
CMD [ "src.main.lambda_handler" ]
