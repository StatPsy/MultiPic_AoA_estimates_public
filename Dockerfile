# The base image and every Conda package are pinned to immutable hashes.
FROM mambaorg/micromamba@sha256:e1476182cd40eb1f7c0cfae4adec9bfd78f3d7f05c61368306abfdc8939c1198

COPY --chown=$MAMBA_USER:$MAMBA_USER docker/conda-linux-64.lock /opt/aoa/conda-linux-64.lock
RUN micromamba create --yes --name aoa --file /opt/aoa/conda-linux-64.lock && \
    micromamba clean --all --yes

ENV ENV_NAME=aoa \
    R_LIBS_USER=/opt/conda/aoa-r-library \
    RENV_CONFIG_CACHE_ENABLED=FALSE \
    RENV_CONFIG_PAK_ENABLED=FALSE \
    MPLBACKEND=Agg \
    QT_QPA_PLATFORM=offscreen
ARG MAMBA_DOCKERFILE_ACTIVATE=1

COPY --chown=$MAMBA_USER:$MAMBA_USER docker/renv.lock docker/restore.R docker/check-environment.R docker/check-environment.py docker/expected-python.json /opt/aoa/
WORKDIR /opt/aoa
RUN Rscript --vanilla restore.R && \
    Rscript --vanilla check-environment.R && \
    python check-environment.py

ARG IMAGE_VERSION=1.0.0
ENV AOA_IMAGE_VERSION=$IMAGE_VERSION \
    XDG_CACHE_HOME=/tmp/aoa-cache \
    MPLCONFIGDIR=/tmp/aoa-matplotlib
LABEL org.opencontainers.image.title="MultiPic AoA analysis environment" \
      org.opencontainers.image.description="Pinned R and Python packages for working with locally mounted MultiPic scripts" \
      org.opencontainers.image.version=$IMAGE_VERSION

# Keep the base image ENTRYPOINT: it activates the locked aoa environment.
# Mount a local project at /project and run its scripts manually.
WORKDIR /project
CMD ["/bin/bash"]
