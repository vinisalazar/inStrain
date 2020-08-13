'''
Methods that make external system calls to samtools
'''

import os
import sys
import pysam
import logging
from subprocess import call

def prepare_bam_fie(bam):
    '''
    Make this a .bam file

    Args:
        bam = location of .bam file
    '''
    if bam[-4:] == '.sam':
        logging.info("You gave me a sam- I'm going to make it a .bam now")

        bam = _sam_to_bam(bam)
        bam = _sort_index_bam(bam)

    elif bam[-4:] == '.bam':
        # If there's an index, assume its sorted
        if (os.path.exists(bam + '.bai')) | ((os.path.exists(bam[:-4] + '.bai'))):
            pass

        # If there's not an index...
        else:
            bam = _sort_index_bam(bam, rm_ori=False)

    if os.stat(bam).st_size == 0:
        logging.error("Failed to generated a sorted .bam file! Make sure you have "+\
            "samtools version 1.6 or greater.")
        sys.exit()

    # Do a quick sanity check
    try:
         pysam.AlignmentFile(bam).mapped
    except ValueError:
        logging.error("It seems like the .bam file could not be indexed!"  +\
                    "Make sure you have samtools version 1.6 or greater.")
        sys.exit()

    return bam

def _sam_to_bam(sam):
    '''
    From the location of a .sam file, convert it to a bam file and retun the location
    '''
    if sam[-4:] != '.sam':
        print('Sam file needs to end in .sam')
        sys.exit()

    bam = sam[:-4] + '.bam'
    logging.info("Converting {0} to {1}".format(sam, bam))
    cmd = ['samtools', 'view','-S','-b', sam, '>', bam]
    print(' '.join(cmd))
    call(' '.join(cmd), shell=True)

    return bam

def _sort_index_bam(bam, rm_ori=False):
    '''
    From a .bam file, sort and index it. Remove original if rm_ori
    Return path of sorted and indexed bam
    '''
    if bam[-4:] != '.bam':
        logging.error('Bam file needs to end in .bam')
        sys.exit()

    if 'sorted.bam' not in bam:
        logging.info("sorting {0}".format(bam))
        sorted_bam = bam[:-4] + '.sorted.bam'
        cmd = ['samtools', 'sort', bam, '-o', sorted_bam]
        print(' '.join(cmd))
        call(cmd)
    else:
        sorted_bam = bam
        rm_ori = False

    logging.info("Indexing {0}".format(sorted_bam))
    cmd = ['samtools', 'index', sorted_bam, sorted_bam + '.bai']
    print(' '.join(cmd))
    call(cmd)

    if rm_ori:
        logging.info("Deleting {0}".format(bam))
        os.remove(bam)

    return sorted_bam