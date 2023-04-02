FROM python:3.10
EXPOSE 5000
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .

CMD["flask", "run", "--host", "0.0.0.0"]