FROM ubuntu:24.04@sha256:fe81560990fae86dc4743202b2cb4d3df98d0bcf949173cecef15ce1127ef852

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Africa/Nairobi

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      apache2 php8.3-fpm php8.3-cli php8.3-sqlite3 sqlite3 cron openssh-server \
      curl ca-certificates python3 tzdata nano vim-tiny less procps psmisc file iproute2 \
 && rm -rf /var/lib/apt/lists/*

COPY config/college.example.org.conf /etc/apache2/sites-available/college.example.org.conf
COPY site/ /var/www/college.example.org/
COPY handover/ /root/handover/
COPY start-site /usr/local/sbin/start-site

RUN --mount=type=bind,source=setup,target=/tmp/setup bash /tmp/setup/build-site.sh
RUN --mount=type=bind,source=setup,target=/tmp/setup bash /tmp/setup/plant.sh

WORKDIR /root
ENTRYPOINT ["/usr/local/sbin/start-site"]
CMD ["sleep", "infinity"]
