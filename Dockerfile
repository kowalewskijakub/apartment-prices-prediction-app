
FROM python:3.13-slim


WORKDIR /app


COPY . .


RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
