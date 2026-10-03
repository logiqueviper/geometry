FROM python:3.12.14-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
# Optional trusted enterprise/cloud CA bundle; TLS and apt signature checks stay on.
RUN --mount=type=secret,id=proxy_ca,target=/tmp/proxy-ca.pem \
    if [ -f /tmp/proxy-ca.pem ]; then cat /tmp/proxy-ca.pem >> /etc/ssl/certs/ca-certificates.crt; fi; \
    sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base texlive-latex-recommended texlive-fonts-recommended make \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace/geometry
COPY requirements-study.txt .
RUN pip install --no-cache-dir -r requirements-study.txt
COPY . .
ENV MPLCONFIGDIR=/tmp/platonic-matplotlib XDG_CACHE_HOME=/tmp/platonic-cache
CMD ["make", "all"]
