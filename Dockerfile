FROM python:3.7-slim


WORKDIR /app

# libz and libjpeg are needed for pillow (PIL)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libz-dev \
    libjpeg-dev

COPY requirements.txt /app/requirements.txt
COPY dev-requirements.txt /app/dev-requirements.txt
RUN pip install -r /app/requirements.txt
# Just to fix an issue installing black, uninstall typing
# https://stackoverflow.com/questions/55833509/attributeerror-type-object-callable-has-no-attribute-abc-registry
RUN pip uninstall -y typing
RUN pip install -r /app/dev-requirements.txt

# Clean some space
# RUN apt-get autoremove -y gcc

# COPY . /app

CMD [ "python", "runserver.py" ]

