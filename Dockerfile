FROM python:latest AS dep-builder

COPY requirements.txt /build/requirements.txt
RUN pip wheel --no-deps -w /build/dist -r /build/requirements.txt

FROM python:slim AS base

COPY --from=dep-builder [ "/build/dist/*.whl", "/install/" ]
RUN pip install --no-index /install/*.whl \
    && rm -rf /install

FROM python:latest as app-builder

COPY . /build
RUN pip wheel --no-deps -w /build/dist /build

FROM base AS final

COPY --from=app-builder [ "/build/dist/*.whl", "/install/" ]
RUN pip install --no-index /install/*.whl \
    && rm -rf /install