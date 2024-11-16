ARG PYTHON_IMAGE_BASE=python:3.13-bullseye
FROM $PYTHON_IMAGE_BASE

ARG BUILD_DEPS="\
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
"
ARG RUNTIME_DEPS=""

WORKDIR /srv/app/

ENV PYTHONPATH="${PYTHONPATH}:/srv/app"

RUN apt-get -qq update \
    && apt-get -qqy --no-install-recommends install $BUILD_DEPS $RUNTIME_DEPS \
    && apt-get -qy upgrade \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /srv/app/src/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
