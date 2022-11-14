FROM python:3.10-alpine3.16
WORKDIR /app

COPY ./backend/requirements.txt requirements.txt
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY ./backend .

EXPOSE 8000
CMD ["python3", "-m", "uvicorn", "main:app", "--reload"]