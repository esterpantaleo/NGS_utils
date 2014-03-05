#!/bin/bash 

# Example of usage:     sh count_signed_reads_starting_in_windows.sh 10000000 reads.bed.gz my_mm9.txt +   
# Warning:              no check is done on args  

#*******************************************************************************#
#            count_signed_reads_starting_in_windows.sh                          #
#                   written by Ester Pantaleo                                   #
#                      February 11, 2013                                        #
#                                                                               #
# ARGUMENT 1 (windowSize): window size in bps                                   #
# ARGUMENT 2 (readFile)  : path to the (gzipped) bed file of the reads          #  
# ARGUMENT 3 (chromSizes): a tabulated file with chromosome names               #
#                          in the first column and chromosome sizes             # 
#                          in the second column                                 #
# ARGUMENT 4 (strand)    : the strand we are interested in (+ or -)             #      
#                                                                               #
# This script divides the chromosomes (whose length is in file                  #
# $chromSizes) in adjacent intervals of size $windowSize. Then it               #
# computes how many reads in the bed  file $readFile start in each              #
# of these intervals. Note that:                                                #
# 1: Option -counts in coverageBed only outputs the counts                      #                                
# 2: Since we are interested in the count of reads that START                   #
#    in a window (and not that COVER a window) we shorten the                   # 
#    reads to length 1 (using awk)                                              #    
# 3: We select reads on $strand with awk                                        #
#*******************************************************************************#

# Get arguments
windowSize=$1
readFile=$2
chromSizes=$3
strand=$4    
if [ -z $4 ]; then
    echo "ERROR: incorrect number of argumemts. Aborting. "
    exit 1
fi


# Make the fifo "tmp_"$RANDOM"_windows" (a named pipe) to pass the output of bedtools makewindows to coverageBed
my_fifo="tmp_"$RANDOM"_windows"
mkfifo $my_fifo

# Create intervals of size $windowsSize
bedtools makewindows -g $chromSizes -w $windowSize > $my_fifo &

# Shorten read, select reads with $strand, compute coverage
zcat $readFile | awk -v "str=$strand" 'BEGIN{OFS="\t"}{if ($6==str) print $1, $2, $2+1, $4, $5, $6}'| \
coverageBed -counts -a stdin -b $my_fifo | awk '{print $4}'

rm $my_fifo
