FROM python:3
ENV PYTHONUNBUFFERED=1
EXPOSE 5000
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
