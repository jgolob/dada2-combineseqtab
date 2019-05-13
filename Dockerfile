# dada2-fast-combineseqtab
#
# VERSION               0.2.0_BCW_0.30

FROM      ubuntu:18.04
# For singularity on the hutch cluster
RUN export DEBIAN_FRONTEND=noninteractive
RUN mkdir /fh && mkdir /app && mkdir /src
RUN mkdir -p /mnt/inputs/file && mkdir -p /mnt/outputs/file && mkdir /scratch && mkdir /working
RUN apt-get update && apt-get install -y \
python3-dev \
python3-pip \
gnupg \
software-properties-common \
libssl-dev \
libssh2-1-dev \
curl \
libcurl4-gnutls-dev \
libgit2-dev
RUN ln -s /usr/bin/python3 /usr/local/bin/python

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 && \
add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/'
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get install -y r-base
RUN pip3 install pip --upgrade
RUN pip3 install \
rpy2==2.9.4 \
numpy==1.15.0 \
pandas==0.23.4 \
awscli>=1.15.14 \
boto3>=1.7.14 \
tzlocal \
bucket_command_wrapper==0.3.0 
COPY dada2_combineseqtab/combine_seqtab.py /usr/local/bin/combine_seqtab
RUN chmod +x /usr/local/bin/combine_seqtab

