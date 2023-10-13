#!/usr/bin/env python
import numpy as np
import pandas as pd
import argparse
import logging
import sys
import scipy
import pyreadr
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri


def R_seqtab_toLong(seqtab_fn):
    try:
        seqtab = pyreadr.read_r(seqtab_fn)[None]
    except Exception as e:
        logging.error("Could not load seqtab {} with error {}".format(
            seqtab_fn,
            e)
        )
        return None
    # Implicit else
    if len(seqtab) == 0:
        logging.error("No specimens in {}".format(
            seqtab_fn
        ))
        return None
    # Implicit else
    if len(seqtab.columns) == 0:
        logging.info("{} had no sequence variants".format(seqtab_fn))
        return None
    # Implicit else
    # Convert to long format
    stl = seqtab.melt(
        ignore_index=False,
        var_name='sv',
        value_name='count'
    ).reset_index().rename({'index': 'specimen'}, axis=1)
    # Slice away zero values
    return stl[stl['count'] > 0]

def load_seqtabs(seqtabs):
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
        stl = R_seqtab_toLong(seqtab_fn)
        if stl is None:
            continue
        # Implicit else
        file_specimens = set(stl.specimen)
        file_seq_variants = set(stl.sv)
        logging.info("Updating master lists and indicies of specimens and sequence variants.")
        if len(set(specimen_ids).intersection(file_specimens)) > 0:
            logging.warn("Duplicated specimen IDs encountered and will be combined")
        # Update the master lists of sv...
        sequence_variants += [sv for sv in (file_seq_variants - set(sequence_variants))]
        # .. and specimens
        specimen_ids += [sp for sp in (file_specimens - set(specimen_ids))]
        # and rapid lookup indicies
        sv_idx = {
            sv: i for (i, sv) in enumerate(sequence_variants)
        }
        sp_idx = {
            sp: i for (i, sp) in enumerate(specimen_ids)
        }

        coo_data += [
            (
                r['count'],
                (
                    sp_idx.get(r['specimen']),
                    sv_idx.get(r['sv'])
                )
            )
            for i, r in stl.iterrows()
        ]

    logging.info("Converting to Sparse DataFrame")            
    combined_seqtab_df = pd.DataFrame.sparse.from_spmatrix(
            scipy.sparse.coo_matrix(
            (
                [d[0] for d in coo_data],
                (
                    [d[1][0] for d in coo_data],
                    [d[1][1] for d in coo_data],
                )
            ),
            dtype=int,
            shape=(len(specimen_ids), len(sequence_variants))
        ),
        index=specimen_ids,
        columns=sequence_variants,
    )

    return combined_seqtab_df
       

def main():
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
    seqtabs = args.seqtabs

    combined_seqtab_df = load_seqtabs(seqtabs)

    if args.csv:
        logging.info("Writing combined seqtab to CSV")
        combined_seqtab_df.to_csv(args.csv)
        logging.info("Completed CSV output")

    if args.rds:
        logging.info("Converting back to R DataFrame")
        R_base = importr('base')
        pandas2ri.activate()
        combined_seqtab_R_mat = R_base.as_matrix(
            ro.conversion.py2rpy(combined_seqtab_df.astype(int))
        )
        logging.info("Saving to RDS")
        R_base.saveRDS(combined_seqtab_R_mat, args.rds)
        logging.info("Completed RDS output")
        pandas2ri.deactivate()

# Boilerplate method to run this as a script
if __name__ == '__main__':
    main()
