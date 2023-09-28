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
import scipy as sp


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
    # Will plan on storing things in sparse format to save on memory
    # A list to store specimen IDs
    specimen_ids = []
    # A list to store sequences
    sequence_variants = []
    # A list to store the COORdinates data [data, (i,j) ]
    coo_data = []
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
        specimens = list(R_base.rownames(seqtab))
        # Great see if the specimens have an overlap
        if len(set(specimen_ids).intersection(set(specimens))) > 0:
            logging.error(
                ", ".join(set(specimen_ids).intersection(set(specimens)))+f" \nspecimens from {seqtab_fn} are duplicates and will be skipped."
                )
            continue
        # Implicit else

        if R_base.colnames(seqtab) is rpy2.rinterface.NULL:
            logging.info("{} had no sequence variants".format(seqtab_fn))
            continue
        # Implicit else
        file_seq_variants = list(R_base.colnames(seqtab))
        # Update the master lists of sv...
        sequence_variants += [sv for sv in file_seq_variants if sv not in sequence_variants]
        # .. and specimens
        specimen_ids += [sp for sp in specimens if sp not in specimen_ids]

        for (i, sp) in enumerate(specimens):
            sp_idx = specimen_ids.index(sp)
            coo_data += [
                (
                    svc,
                    (
                        sp_idx,
                        sequence_variants.index(
                            file_seq_variants[j]
                        ) 
                    )
                )
                for (j, svc) in
                enumerate(
                    seqtab.rx(i+1, True)
                )
                if svc != 0
            ]
    logging.info("Converting to Sparse DataFrame")            
    sp.sparse.coo_matrix(
        (
            [d[0] for d in coo_data],
            (
                [d[1][0] for d in coo_data],
                [d[1][1] for d in coo_data],
            )
        ),
        dtype=int,
        shape=(len(specimen_ids), len(sequence_variants))
    )

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
