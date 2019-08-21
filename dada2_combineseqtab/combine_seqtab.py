#!/usr/bin/env python
import os
import numpy as np
import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import argparse
import logging
import sys
import rpy2


def main():
    pandas2ri.activate()
    logging.basicConfig(format='Combine Seqtab:%(levelname)s:%(asctime)s:%(message)s', level=logging.INFO)
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        '--seqtabs', '-s',
        help="Sequence tables from dada2, in RDS format",
        nargs='+',
        required=True)
    args_parser.add_argument(
        '--rds', '-R',
        help='Combined Seqtable (RDS out)')
    args_parser.add_argument(
        '--csv', '-C',
        help='Combined Seqtable (CSV out)')

    args = args_parser.parse_args()

    if (args.rds is None) and (args.csv is None):
        logging.error("No output selected. Exiting")
        sys.exit("Nothing to do.")
    # Implicit else
    R_base = importr('base')
    seqtabs = args.seqtabs
    combined_seqtab_dict = {}
    for seqtab_i, seqtab_fn in enumerate(seqtabs):
        logging.info("Adding seqtab {:,} of {:,}".format(
            seqtab_i + 1,
            len(seqtabs)
        ))
        try:
            seqtab = R_base.readRDS(seqtab_fn)
        except Exception as e:
            logging.error("Could not load seqtab {} with error {}".format(
                seqtab_fn,
                e)
            )
            continue
        if R_base.rownames(seqtab) is rpy2.rinterface.NULL:
            logging.error("No specimens in {}".format(
                seqtab_fn
            ))
            continue
        for sp_idx, spec in enumerate(R_base.rownames(seqtab)):
            if R_base.colnames(seqtab) is rpy2.rinterface.NULL:
                logging.info("{} had no sequence variants".format(spec))
                combined_seqtab_dict[spec] = {}
            else:
                combined_seqtab_dict[spec] = {
                    p[0]: p[1]
                    for p in
                    zip(seq_variants, seqtab.rx(sp_idx+1, True))
                    if p[1] != 0
                }
    logging.info("Converting to DataFrame")
    combined_seqtab_df = pd.DataFrame.from_dict(combined_seqtab_dict).fillna(0).astype(np.int64).T

    if args.csv:
        logging.info("Writing combined seqtab to CSV")
        combined_seqtab_df.to_csv(args.csv)
        logging.info("Completed CSV output")

    if args.rds:
        logging.info("Writing out RDS combined seqtab")
        logging.info("Converting back to R DataFrame")
        combined_seqtab_R_df = pandas2ri.py2ri(combined_seqtab_df)
        logging.info("Converting into an R Matrix")
        combined_seqtab_R_mat = R_base.as_matrix(combined_seqtab_R_df)
        logging.info("Saving to RDS")
        R_base.saveRDS(combined_seqtab_R_mat, args.rds)
        logging.info("Completed RDS output")

# Boilerplate method to run this as a script
if __name__ == '__main__':
    main()
