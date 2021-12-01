# NOTE: That dockerfile is for development purposes only, and NOT to use in for production

# UID/GID should be set to UID/GID of docker-compose-dev/container-data owner in order to make it work
# PWD may be left unchanged

# SHH is to update image when some scripts downloaded with wget are changed (see below)
# Set SHH externally to hashes combination of those files

FROM   ubuntu:20.04

ARG    UID=1000
ARG    GID=1000
ARG    PWD=2OYyoafdd2RFtSB8L1y
ARG    SHH=""

RUN    apt-get update \
    && apt-get install -y \
        python3 pip \
        libpq-dev \
        ghostscript \
        openjdk-8-jdk-headless \
        wget \
    && apt-get clean \
    && pip3 install anvil-app-server \
    && anvil-app-server \
    || test -f /usr/local/lib/python3*/dist-packages/anvil_app_server/anvil-app-server.*.jar
# NOTE: Need to run anvil-app-server in order to download server jar even though it would fail in the end

# TODO: Google chrome is required for PDF rendering. Dunno yet how it would work in headless mode

# RUN    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
#    && dpkg -i google-chrome-stable_current_amd64.deb \
#    && rm google-chrome-stable_current_amd64.deb

RUN    groupadd -g ${GID} schems-fun \
    && useradd -m -u ${UID} -g ${GID} schems-fun \
    && echo "schems-fun:${PWD}" | chpasswd \
    && mkdir /home/schems-fun/anvil.apps \
    && cd    /home/schems-fun/anvil.apps \
    && wget https://raw.githubusercontent.com/Godhart/schems-fun-misc-tools/main/running/migrate_schems_fun.sh \
    && chmod +x migrate_schems_fun.sh \
    && wget https://raw.githubusercontent.com/Godhart/schems-fun-misc-tools/main/running/run_schems_fun.sh \
    && chmod +x run_schems_fun.sh \
    && echo ${SHH} > shh \
    && chown schems-fun:schems-fun /home/schems-fun/anvil.apps

# Change working dir
WORKDIR /home/schems-fun/anvil.apps

# Switch user at last
USER   schems-fun

# Set default command to run
CMD    /bin/bash /home/schems-fun/anvil.apps/migrate_schems_fun.sh
