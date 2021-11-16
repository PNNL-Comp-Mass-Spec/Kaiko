FROM tensorflow/tensorflow:1.2.1

RUN pip install llvmlite==0.22
RUN pip install biopython==1.69
RUN pip install numba==0.37
RUN pip install pyteomics
RUN pip install sigopt==3.2.0

COPY ./*sh /app/
COPY ./src /app/src
WORKDIR /app
