FROM public.ecr.aws/lambda/python:3.12

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies with constraint to fix conflict
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    'python-dotenv>=1.1.0' \
    -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set the CMD to your handler
CMD [ "src.main.lambda_handler" ]
