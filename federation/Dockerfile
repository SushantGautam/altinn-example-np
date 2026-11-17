FROM python:3.12-slim
WORKDIR /service
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY service.py dashboard.html generate_pki.py ./
EXPOSE 8000
CMD ["uvicorn","service:app","--host","0.0.0.0","--port","8000","--proxy-headers","--no-access-log"]
