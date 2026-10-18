# Teaching base tag. Release workflows should pin a reviewed digest and refresh it deliberately.
FROM python:3.11-slim AS verify
WORKDIR /src
COPY algorithms.py inference_api.py ./
RUN python -m py_compile algorithms.py inference_api.py

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=verify --chown=10001:10001 /src/algorithms.py /src/inference_api.py ./
USER 10001:10001
EXPOSE 8000
# Supply DEMO_API_KEY at runtime; never bake a secret into an image layer.
CMD ["python", "inference_api.py", "--host", "0.0.0.0", "--port", "8000"]
