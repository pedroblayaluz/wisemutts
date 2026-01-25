FROM public.ecr.aws/lambda/python:3.12

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies - use legacy resolver to handle conflicts
RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set the CMD to your handler
CMD [ "src.main.lambda_handler" ]
