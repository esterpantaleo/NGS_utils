# Introduction

This repo contains a Python library, *NGS_utils*, to plot input data and output data from multiseq (an R package under development in the Stephens lab at the University of Chicago) in the [UCSC Genome Browser](http://genome.ucsc.edu/).

This library build extensively on the [genome](https://github.com/gmcvicker/genome) library by Graham McVicker. 

This document summarizes how to setup this software system and how to use the python scripts simulationToTrackHub.py, samplesheetToTrackHub.py and multiseqToTrackHub.py . If you have any questions or run into any difficulty, please don't hesitate to contact me!

# Setup

This repo has two components: a small python library *NGS_utils* and a set of python scripts for data import and plot.

### Dependencies

*NGS_utlis* depends on PyTables, which depends on [HDF5](http://www.hdfgroup.org/HDF5/), [NumPy](http://www.numpy.org/) and several other packages. 
See the detailed [PyTables installation guide](http://pytables.github.io/usersguide/installation.html). [This 
guide](http://assorted-experience.blogspot.com/2011/12/mac-os-x-install-pytables-and-h5py.html) for installing
PyTables under Mac OSX.

*NGS_utils* additionally depends on:
* [ArgParse](https://code.google.com/p/argparse/) (for Python2.6 or older)
* [pysam](https://code.google.com/p/pysam/) (for reading BAM files only)

Also the executables `wigToBigWig` and `bedToBigBed` must be in the user's PATH.


### Getting the source code

The first step is to obtain the source code from git. Let's assume you want to clone this repository 
into a directory named ~/src:

     mkdir ~/src
     cd ~/src
     git clone https://github.com/esterpantaleo/NGS_utils

     cd ~/src/NGS_utils
     git fetch
     git merge origin/master


### Setting environment variables

To use the code you need to update set several shell environment variables. 
I recommend setting these variables in your ~/.bashrc or ~/.profile files using 
something like the following:

    # update your python path by adding $HOME/src/NGS_utils/python/lib to the end
    # this tells python where to find the NGS_utils library 
    export PYTHONPATH=$PYTHONPATH:$HOME/src/NGS_utils/python/lib:$HOME/src/NGS_utils/python/script
    
    # specify the location of 'database' where the HDF5 files that you want to use are
    export GENOME_DB=/data/share/genome_db/
    
    # scripts will use this genome assembly by default 
    export GENOME_ASSEMBLY=hg19

    # specify the mountpoint and the http address associated with the mountpoint
    export MOUNTPOINT_PATH=/some/path
    export MOUNTPOINT_HTTP_ADDRESS="some https address" 

where you have to replace /some/path with the path to the mountpoint (i.e., /data/internal/solexa_mountpoint/$USER on the PPS cluster) and "some https address" with the http address of the mountpoint (ask me if you want to use the http address associated with /data/internal/solexa_mountpoint/).  

Make sure that you remember to set these variables after adding them to your .bashrc for the first time. 
You can login again, or do source ~/.bashrc

Remember that when you submit jobs to a compute cluster (e.g. using SGE's qsub), they run in "batch mode" 
and may not execute your ~/.bashrc. To ensure that your jobs have the correct environment variables set, 
you should be able to pass a flag to your cluster submission command (e.g. the -V flag to qsub).


### simulationToTrackHub.py: example of usage
This code has been created to plot in the UCSC Genome Browser some simulation data specific to our workflow. Our simulations produce a set of bigWig files that cover a small genomic region (chr5:131989505-132120576 in the example below). The code creates a Track Hub with the simulated data that can be visualized in the Genome Browser.

From the terminal cd into the repository and type:

    python simulationToTrackHub.py --hub_name testNGS/sim data/sim/samplesheet.sim.txt 

If correctly executed, the python code will print the following message:

    go to http://genome.ucsc.edu/cgi-bin/hgHubConnect and click on the My Hubs window    
    copy paste the following string in the URL field
    "some https address"/testNGS/sim/hub.txt
    center the genome browser on the region of interest
    if the track is hidden click on show and then refresh

The region of interest in this example data is chr5:131989505-132120576

This is a screenshot of the data in the Genome Browser:
![Image](plots/sim.png?raw=true)

### samplesheetToTrackHub.py: example of usage

Make sure you have enough memory to run this command (use ql 10g on the PPS cluster)

    course_repodir="/mnt/lustre/home/epantaleo/src/stat45800/"
    samplesheet=$course_repodir"data/samplesheetEncode.txt"
    python samplesheetToTrackHub.py $samplesheet Encode chr1</code></pre>


### multiseqToTrackHub.py: example of usage
After running multiseq on a specified region (chr5:131989505-132120576 in the data/multiseq folder) we obtain 3 output files: *effect_mean_var.txt.gz* a file with two columns (first column a mean effect and second column squared standard error of the effect), *multiseq.effect.2sd.bed* and *multiseq.effect.3sd.bed*, two bed files containing significant intervals (as computed by multiseq) at 2 and 3 sd (respectively).

The python script multiseqToTrackHub.py creates a track hub with:
1. the effect and the respective standard error 
2. the significant intervals at 2 and 3 sd 
in the UCSC Genome Browser.
 
    python multiseqToTrackHub.py --hub_name testNGS/multiseq --multiseq_folder data/multiseq chr5:131989505-132120576 data/chromosome.lengths.hg19.txt

If correctly executed, the python code will print the following message:
  
   go to http://genome.ucsc.edu/cgi-bin/hgHubConnect and click on the My Hubs window
   copy paste the following string in the URL field
   "some https address"/testNGS/multiseq/hub.txt
   note: center your genome browser around chr5:131989505-132120576 and make track visible

This is a screenshot of output from multiseq in the Genome Browser:
![Image](plots/multiseq.png?raw=true)