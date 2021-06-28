FROM continuumio/miniconda3:latest

WORKDIR /app

COPY testing-modules-list.txt /app 

RUN chmod 777 /app && \
    conda config --add channels conda-forge && \
    conda install --file=testing-modules-list.txt

ENTRYPOINT ["/opt/conda/bin/python3"]
