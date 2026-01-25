FROM public.ecr.aws/lambda/python:3.12

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install python-dotenv 1.0.1 first (required by runware)
# Then install all other requirements
RUN pip install --no-cache-dir python-dotenv==1.0.1 && \
    pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set the CMD to your handler
CMD [ "src.main.lambda_handler" ]
