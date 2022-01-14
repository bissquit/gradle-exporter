FROM python:3.7-slim

# nobody user in base image
ARG UID=65534

COPY --chown=$UID:$UID gradle_exporter.py requirements.txt /app/

WORKDIR /app

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8080

USER $UID

CMD ["python3", "gradle_exporter.py"]
