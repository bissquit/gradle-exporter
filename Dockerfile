FROM python:3.9-slim

LABEL description="Prometheus exporter for Gradle Enterprise Server" \
      source="https://github.com/bissquit/gradle-server-exporter"

# nobody user in base image
ARG UID=65534

COPY --chown=$UID:$UID gradle_server_exporter.py \
                       handler.py \
                       requirements.txt \
                       /app/

WORKDIR /app

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8080

USER $UID

CMD ["python3", "gradle_server_exporter.py"]
