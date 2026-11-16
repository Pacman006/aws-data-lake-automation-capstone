# Local test runner only. The deployed AWS workload uses Lambda and Glue.
FROM python:3.12-slim
WORKDIR /project
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt \
    && useradd --system --uid 10001 runner
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY glue/ ./glue/
COPY cloudformation/ ./cloudformation/
COPY .github/ ./.github/
COPY docs/images/ ./docs/images/
COPY docs/source/ ./docs/source/
COPY README.md .
RUN chown -R runner /project
USER runner
CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
