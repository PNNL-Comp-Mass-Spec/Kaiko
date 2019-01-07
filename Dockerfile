FROM tensorflow/tensorflow:1.2.0

RUN pip install biopython
RUN pip install pyteomics
RUN pip install numba
RUN pip install sigopt

COPY . /app
WORKDIR /app
