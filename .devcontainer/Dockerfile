FROM ubuntu:22.04

# Setup workspace directory
RUN mkdir /workspace
WORKDIR /workspace

# Install useful system utilities
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes \
    apt-transport-https \
    build-essential \
    ca-certificates \
    curl \
    debian-keyring \
    debian-archive-keyring \
    git \
    gnupg \
    locales \
    software-properties-common \
    sudo \
    tzdata \
    wget \
    zsh \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install the PostgreSQL 15 client
RUN apt-get update && apt-get install -y wget gnupg lsb-release && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && apt-get install -y postgresql-client-15 && \
    rm -rf /var/lib/apt/lists/*

# Install Caddy web server
RUN curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt update \
    && apt install caddy

# Install Node.js 22 from https://github.com/nodesource
ENV NODE_MAJOR 22
RUN mkdir -p /etc/apt/keyrings \ 
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install nodejs -y \
    && npm install -g npm@latest \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.12
RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt update \
    && apt install --yes \
    python3.12 \
    libpq-dev \
    python3.12-venv \
    python3.12-dev \
    && rm -rf /var/lib/apt/lists* \
    && unlink /usr/bin/python3 \
    && ln -s /usr/bin/python3.12 /usr/bin/python3

# Install dependencies required to run Elixir
RUN apt-get update && apt-get install -y \
    curl unzip git ca-certificates gnupg libssl-dev \
    libncurses-dev autoconf m4 libwxgtk3.0-gtk3-dev libgl1-mesa-dev \
    libglu1-mesa-dev libpng-dev libssh-dev unixodbc-dev xsltproc fop \
    libxml2-utils build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Erlang/OTP with crypto support
# Using OTP 26.2.5 (latest 26.x) which includes all crypto functions
ENV OTP_VERSION=26.2.5
RUN curl -fsSL https://github.com/erlang/otp/releases/download/OTP-$OTP_VERSION/otp_src_$OTP_VERSION.tar.gz -o otp.tar.gz \
    && mkdir -p /opt/erlang \
    && tar -xzf otp.tar.gz -C /opt/erlang --strip-components=1 \
    && cd /opt/erlang \
    && ./configure \
    --enable-threads \
    --enable-smp-support \
    --enable-kernel-poll \
    --enable-hipe \
    --with-ssl \
    --enable-ssl-dynamic-linking \
    --enable-crypto \
    && make -j$(nproc) && make install \
    && cd / && rm -rf /opt/erlang otp.tar.gz

# Install Elixir (compatible with OTP 26)
ENV ELIXIR_VERSION=1.16.2
RUN curl -LO https://repo.hex.pm/builds/elixir/v$ELIXIR_VERSION.zip \
    && unzip -d /opt/elixir v$ELIXIR_VERSION.zip \
    && rm v$ELIXIR_VERSION.zip

ENV PATH="$PATH:/opt/elixir/bin"

# Use a non-root user per https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Add non-root user and add to sudoers
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /usr/bin/zsh \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set code to default git commit editor
RUN git config --system core.editor "code --wait"
# Set Safe Directory
RUN git config --system safe.directory '/workspace'

# Make node_modules volume for the monorepo (includes commitlint config)
RUN mkdir -p /workspace/node_modules && chown $USERNAME /workspace/node_modules
VOLUME /workspace/node_modules

# Make node_modules volume for the web app
RUN mkdir -p /workspace/web/node_modules && chown $USERNAME /workspace/web/node_modules
VOLUME /workspace/web/node_modules

# Configure zsh
USER $USERNAME
ENV HOME /home/$USERNAME

# Add zsh theme
RUN curl https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh | bash - \
    && sed -i 's/robbyrussell/kennethreitz/g' ~/.zshrc \
    && echo 'export PATH=$PATH:$HOME/.local/bin' >>~/.zshrc

# Set Locale for Functional Autocompletion in zsh
RUN sudo locale-gen en_US.UTF-8

# Add `oc` OpenShift Client to DevContainer for compatibility with UNC CloudApps
RUN arch="$(arch)"; \
    case "$arch" in \
    x86_64) export TARGET='' ;; \
    aarch64) export TARGET='arm64-' ;; \
    esac; \
    wget -O /tmp/oc.tgz "https://github.com/okd-project/okd/releases/download/4.15.0-0.okd-2024-03-10-010116/openshift-client-linux-${TARGET}4.15.0-0.okd-2024-03-10-010116.tar.gz" && \
    cd /tmp && \
    tar -xvzf oc.tgz && \
    sudo mv oc /usr/bin/oc && \
    rm kubectl oc.tgz README.md

# Install server dependencies
COPY server/requirements.txt /workspace/server/requirements.txt
WORKDIR /workspace/server
RUN python3 -m ensurepip
RUN python3 -m pip install -r requirements.txt


# Expose server ports
EXPOSE 8000