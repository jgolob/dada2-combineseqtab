# dada2-fast-combineseqtab
#
# VERSION               0.1.0_BCW_0.30

FROM      alpine:3.8
# For singularity on the hutch cluster
RUN mkdir /fh && mkdir /app && mkdir /src
RUN mkdir -p /mnt/inputs/file && mkdir -p /mnt/outputs/file && mkdir /scratch && mkdir /working
RUN apk add --no-cache bash \
python3==3.6.6-r0  \
python3-dev==3.6.6-r0 \
gfortran \
R==3.5.0-r1 \
R-dev==3.5.0-r1 \
build-base
RUN ln -s /usr/bin/python3 /usr/local/bin/python
RUN pip3 install pip --upgrade
RUN pip3 install \
rpy2==2.9.4 \
numpy==1.15.0 \
pandas==0.23.4 \
awscli>=1.15.14 \
boto3>=1.7.14 \
bucket_command_wrapper==0.3.0 
RUN apk del gfortran build-base
COPY dada2_combineseqtab/combine_seqtab.py /usr/local/bin/combine_seqtab
RUN chmod +x /usr/local/bin/combine_seqtab

