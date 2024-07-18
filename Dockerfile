# Pull official base image
FROM python:3.11

RUN mkdir /app

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy project
COPY . /app

CMD ["sh", "-c", " \
    python manage.py makemigrations & \
    python manage.py migrate & \
    python manage.py runserver 0.0.0.0:8000 \
"]
