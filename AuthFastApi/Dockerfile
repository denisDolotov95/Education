FROM python:3.12-slim

ENV LANG='ru_RU.UTF-8' \
    LANGUAGE='ru_RU:ru' \
    LC_ALL='ru_RU.UTF-8' \
    LC_MESSAGES='en_US.UTF-8'

RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen && \
    apt-get update && \
    apt-get -y install --no-install-recommends locales tzdata && \
    locale-gen en_US.UTF-8 ru_RU.UTF-8 && \
    ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt1
COPY . .

CMD ["uvicorn", "run:app", "--reload", "--port $FAST_API_PORT"]