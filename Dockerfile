FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m leftovers.domain.recommend.service.train

# 스레드 수 조정
ENV OMP_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=4
ENV MKL_NUM_THREADS=4

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
