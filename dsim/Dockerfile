FROM debian:bookworm AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ARG _UID=1000
ARG _GID=1000
ARG _USERNAME=builder
ENV HOME=/home/${_USERNAME}

# Create a directory for dsim
WORKDIR /root

# Install required dependencies
RUN apt-get update -y
RUN apt-get install -y build-essential ca-certificates libsqlite3-dev

# Copy the dsim binary
COPY AltairDSim2025.0.1_linux64.bin /root/
COPY dsim-license.json /root/

# Make the binary executable
RUN chmod +x /root/AltairDSim2025.0.1_linux64.bin

# Install dsim
RUN /root/AltairDSim2025.0.1_linux64.bin -i silent -DACCEPT_EULA=YES

# Remove dsim installer
RUN rm /root/AltairDSim2025.0.1_linux64.bin

# Make /root directory traversable and dsim installation accessible to all users
RUN chmod a+rx /root && \
    chmod -R a+rX /root/AltairDSim && \
    chmod a+r /root/dsim-license.json

# Setup dsim environment
ENV DSIM=dsim
ENV DSIM_HOME=/root/AltairDSim/2025
ENV DSIM_LICENSE=/root/dsim-license.json
ENV DSIM_LIB_PATH=${DSIM_HOME}/lib
ENV UVM_HOME=${DSIM_HOME}/uvm/1.2/
ENV STD_LIBS=${DSIM_HOME}/std_pkgs/lib
ENV RADFLEX_PATH=${DSIM_HOME}/radflex
ENV LLVM_HOME=${DSIM_HOME}/llvm_small
ENV PATH=${LLVM_HOME}/bin:${DSIM_HOME}/bin:$PATH
ENV LD_LIBRARY_PATH=${DSIM_HOME}/lib:${LLVM_HOME}/lib

# Symlink libuvm_dpi.so to dsim lib path
RUN ln -s ${UVM_HOME}/src/dpi/libuvm_dpi.so ${DSIM_LIB_PATH}/libuvm_dpi.so

# # Replace dsim binary
# COPY dsim /root/AltairDSim/2025/bin/dsim
# RUN chmod +x /root/AltairDSim/2025/bin/dsim
COPY dsim-license.json /root/dsim-license.json

# Command to run when container starts
CMD ["dsim"]