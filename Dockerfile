# dada2-fast-combineseqtab
#
# VERSION               golob/dada2-fast-combineseqtab:0.5.0__1.12.0__BCW_0.3.1

FROM      golob/dada2:1.12.0.ub.1804__bcw.0.3.1

RUN pip3 install \
rpy2==2.9.5 \
numpy>=1.15.0 \
pandas>=0.23.4 \
tzlocal
RUN ln -s /usr/bin/python3 /usr/local/bin/python
COPY dada2_combineseqtab/combine_seqtab.py /usr/local/bin/combine_seqtab
RUN chmod +x /usr/local/bin/combine_seqtab

