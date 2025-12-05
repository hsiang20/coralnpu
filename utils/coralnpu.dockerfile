# Dockerfile to create a stable CoralNPU build environment
#
# Build command:
# docker build -t coralnpu -f utils/coralnpu.dockerfile .
#
# Run command:
# docker run -it coralnpu /bin/bash

FROM dsim

ENV TZ=UTC
ARG _UID=1000
ARG _GID=1000
ARG _USERNAME=builder
ENV HOME=/home/${_USERNAME}

RUN ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime && \
    echo "${TZ}" > /etc/timezone && \
    echo "APT::Get::Assume-Yes \"true\";" > /etc/apt/apt.conf.d/90assumeyes && \
    apt-get update && \
    apt-get install -y -qq \
        apt-transport-https \
        autoconf \
        build-essential \
        ca-certificates \
        ccache \
        curl \
        fuse3 \
        gawk \
        git \
        gnupg \
        libmpfr-dev \
        lsb-release \
        python-is-python3 \
        python3 \
        python3-pip \
        srecord \
        tzdata \
        unzip \
        xxd \
        zip && \
    update-ca-certificates && \
    curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > /tmp/bazel-archive-keyring.gpg && \
    mv /tmp/bazel-archive-keyring.gpg /usr/share/keyrings/ && \
    echo "deb [arch=$(dpkg-architecture -q DEB_HOST_ARCH) signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list && \
    apt update && \
    apt install bazel bazel-7.4.1

# Install Python dependencies for UVM tests
RUN pip3 install --no-cache-dir --break-system-packages pyelftools

# Create builder user
RUN addgroup --gid ${_GID} ${_USERNAME} && \
    adduser \
        --home ${HOME} \
        --disabled-password \
        --gecos "" \
        --uid ${_UID} \
        --gid ${_GID} \
        ${_USERNAME} && \
    chown ${_USERNAME}:${_USERNAME} ${HOME} && \
    mkdir -p ${HOME}/.cache && \
    chown -R ${_USERNAME}:${_USERNAME} ${HOME}/.cache
# Work around differeing libmpfr versions between distros
RUN ln -sf /lib/x86_64-linux-gnu/libmpfr.so.6.2.0 /lib/x86_64-linux-gnu/libmpfr.so.4
USER ${_USERNAME}
WORKDIR ${HOME}

# Default to bash for interactive development
CMD ["/bin/bash"]
