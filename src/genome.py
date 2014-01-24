#!/usr/bin/env python

from feature_tbl_entry import FeatureTblEntry
from translate import *
import sys
import os.path

class Genome:

    def __init__(self):
        self.fasta = None
        self.gff = None
        self.annot = None
        self.entries = []

    def verify_file(self, filename):
        return os.path.exists(filename) 

    def addEntry(self, entry):
        entries.append(entry)
    
    def addEntries(self, entries):
        [self.entries.append(entry) for entry in entries]

    # this also removes empty genes; could use a better name maybe...
    def remove_mrnas_with_cds_shorter_than(self, min_length):
        if self.gff:
            self.gff.remove_mrnas_with_cds_shorter_than(min_length)

    def remove_first_cds_segment_if_shorter_than(self, min_length):
        if self.gff:
            self.gff.remove_first_cds_segment_if_shorter_than(min_length)

    # maybe should be called 'create_start_codon_GenePart if sequence contains start codon'
    def create_starts_and_stops(self):
        for gene in self.gff.genes:
            gene.create_starts_and_stops(self.fasta)

    def generateEntries(self):
        for gene in self.gff.genes:
            newEntries = gene.to_tbl_entries(self.annot)
            for entry in newEntries:
                self.entries.append(entry)

    def write_string(self, genes = None, errors = None):
        output = ''

        if self.fasta == None or self.gff == None or self.annot == None:
            return output
       
        output += '>Feature SeqId\n'

        for seq in self.fasta.entries:
            if genes != None and not genes:
                return output

            entries = []
            for gene in self.gff.genes:
                if gene.seq_name != seq[0]:
                    continue

                if genes != None and gene.name not in genes:
                    continue

                if genes != None:
                    genes.remove(gene.name)

                newEntries = gene.to_tbl_entries(self.annot)
                for entry in newEntries:
                    if entry.type == 'gene':
                        self.annot.annotate_gene(entry)
                    elif entry.type == 'CDS':
                        self.annot.annotate_cds(entry)
                    elif entry.type == 'mRNA':
                        self.annot.annotate_mrna(entry)
                    entries.append(entry)

            # If there are any entries, write this section of the tbl file
            if len(entries) > 0:
                output += '>Feature '+seq[0]+'\n'
                output += '1\t'+str(len(seq[1]))+'\tREFERENCE\n\t\t\tPBARC\t12345\n'

                for entry in entries:    
                    output += entry.write_to_string()+'\n'
        return output

    def remove_all_gene_segments(self, prefix):
        self.gff.remove_all_gene_segments(prefix)

    def obliterate_genes_related_to_mrnas(self, mrna_names):
        self.gff.obliterate_genes_related_to_mrnas(mrna_names)

    def rename_maker_mrnas(self):
        count = 1000000
        for gene in self.gff.genes:
            for mrna in gene.mrnas:
                if mrna.is_maker_mrna():
                    old_name = mrna.name
                    new_name = 'BDOR_' + str(count)
                    mrna.name = new_name
                    self.annot.rename_mrna(old_name, new_name)
                    count += 1

    def invalidate_region(self, seq, start, stop):
        self.gff.invalidate_region(seq, start, stop)

    def trim_region(self, seq, start, stop):
        if self.fasta:
            self.fasta.trim_seq(seq, start, stop)
        if self.gff and self.gff.genes:
            offset = -(stop - start + 1)
            for gene in self.gff.genes:
                gene.adjust_indices(offset, stop)

