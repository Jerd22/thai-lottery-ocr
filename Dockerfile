FROM python:3-slim-buster AS builder
 
WORKDIR /app
 
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
 
RUN python3 -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt
 
# Stage 2
FROM python:3.10-alpine AS runner
 
WORKDIR /app
 
COPY --from=builder /app/venv venv
COPY app.py app.py
 
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

EXPOSE 8000

CMD [ "python3", "app.py" ]