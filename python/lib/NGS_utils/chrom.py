import sys

class Chromosome(object):
    def __init__(self, idnum=None, name=None, length=None,
                 is_sex=False, is_rand=False, is_hap=False,
                 is_mito=False, is_x=False, is_y=False, is_auto=False):
        self.idnum = idnum
        self.name = name
        self.length = length

    def __str__(self):
        """returns a string representatin of this object"""
        return self.name

    def __cmp__(self, other):
        return cmp(self.idnum, other.idnum)
