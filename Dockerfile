FROM python:3.10-slim-bullseye

# install deps
COPY requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y libxml2 libxml2-dev libxslt-dev gcc python3-dev
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy and install app code
COPY . /app
RUN pip install --no-deps /app