# Python interpreter with the imaging and scientific stack this project's
# tooling needs: numpy, scipy, and Pillow.
#
# Built and invoked by bin/python3. The base image is pinned by digest and
# the packages by exact version so the interpreter is a property of this
# repository rather than of the host.

FROM python:3.13-slim-trixie@sha256:6771159cd4fa5d9bba1258caf0b82e6b73458c694d178ad97c5e925c2d0e1a91

# No apt layer: numpy, scipy, and Pillow all ship manylinux wheels that
# bundle their native dependencies, so nothing further is needed from the
# distribution and there is one less pin to drift.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Fail the build rather than a caller if the stack is not importable.
RUN python3 -c "import numpy, scipy, PIL; print(numpy.__version__, scipy.__version__, PIL.__version__)"

# Keep bytecode out of the mounted working tree.
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python3"]
