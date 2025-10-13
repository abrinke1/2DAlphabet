#!/bin/bash

#########################################################
# Prepare input ROOT files to be used in generatetoys.sh
# 20 - 30 minutes per category per year, with systematics
# Run in 4 separate lxplus sessions, one per year/era
#########################################################

iYear=$1  ## 2016preVFP, 2016postVFP, 2017, or 2018
iSyst=$2
source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR

if [[ $iYear != "2016preVFP" && $iYear != "2016postVFP" && $iYear != "2017" && $iYear != "2018" ]]; then
    echo "Invalid year $iYear! Quitting."
    exit
fi
if [[ $iSyst != "True" && $iSyst != "False" ]]; then
    echo "Invalid year $iSyst! Quitting."
    exit
fi

## Prepare inputs
echo " > Merging categories (gg0lVHi gg0lVLo HadXHi HadXLo LepHiT LepLo VjjTLo VjjHi400 VBFjjHiPtLo VBFjjHiPtHi)"
for CAT in gg0lVHi gg0lVLo HadXHi HadXLo LepHiT LepLo VjjTLo VjjHi400 VBFjjHiPtLo VBFjjHiPtHi; do
    #for YEAR in 2016preVFP 2016postVFP 2017 2018; do
    for YEAR in $iYear; do
	## Producing "Incl" categories also produces Hi/Lo plots
	echo " > python3 merge_files_mctoy.py ${CAT} ${YEAR} ${iSyst} >& merge_files_${CAT}_${YEAR}_${iSyst}.txt &"
	python3 merge_files_mctoy.py ${CAT} ${YEAR} ${iSyst} >& merge_files_${CAT}_${YEAR}_${iSyst}.txt &
    done
done

top

# ## Optional for optimization studies, disabled by default
# echo " > Merging modified LepHi and LepLo categories (A - H)"
# for mod in A B C D E F G H; do
# 	for YEAR in 2016preVFP 2016postVFP 2017 2018; do
# 	    echo " > python3 merge_files_mctoy.py LepLo${mod} ${YEAR}"
# 	    python3 merge_files_mctoy.py LepLo${mod} ${YEAR}
# 	    echo " > python3 merge_files_mctoy.py LepHi${mod} ${YEAR}"
# 	    python3 merge_files_mctoy.py LepHi${mod} ${YEAR}
# 	done
# done
