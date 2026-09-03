# base image
FROM python:3.12-slim

# workdir
WORKDIR /app

# copy
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy app files/REST OF THE APPLICATION
COPY . .

# port
EXPOSE 8000

# command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]