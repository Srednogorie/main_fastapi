FROM public.ecr.aws/lambda/python:3.11

RUN yum install which -y

RUN mkdir -p /var/task/
COPY . /var/task/

RUN curl -sSL https://install.python-poetry.org | python3.11 -
RUN cp $HOME/.local/bin/poetry /usr/local/bin
WORKDIR /var/task/
RUN poetry config virtualenvs.create false
RUN poetry install

# Expose the port on which the application will run
EXPOSE 8080

# Run the FastAPI application using uvicorn server
CMD ["uvicorn", "app:main:app", "--host", "0.0.0.0", "--port", "8080"]