# Base image: a small Linux with Python
FROM python:3.12-slim

# Python settings: no .pyc files, and print logs at once
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# Work folder inside the container
WORKDIR /app

# System tools that some Python libraries need
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Step A: install libraries first (this layer is saved and reused)
COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir -r requirements.txt

# Step B: copy your code and install the package
COPY . .
RUN pip install --no-cache-dir --no-deps -e .

# Ports (8501 = Streamlit, 9999 = FastAPI inside the container)
EXPOSE 8501
EXPOSE 9999

# Start the app
CMD ["python", "-m", "app.main"]