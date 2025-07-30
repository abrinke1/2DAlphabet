#!/bin/bash

#########################################################
# Prepare input ROOT files to be used in generatetoys.sh
# 20 - 30 minutes per category per year, with systematics
#########################################################

DATE="2025_07_25"
source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR
OUTDIR="${EOS_DIR}/raw_inputs/${DATE}"

# Start the timer
START_TIME=$SECONDS

## Prepare inputs
# echo " > Merging categories (gg0lHi gg0lVLo VVBFjj LepHiT LepLo HadXLo gg0lV LepHi LepIncl gg0lIncl VBFjjIncl VjjIncl tt0lIncl)"
# for CAT in gg0lHi gg0lVLo VVBFjj LepHiT LepLo HadXLo gg0lV LepHi LepIncl gg0lIncl VBFjjIncl VjjIncl tt0lIncl; do
echo " > Merging categories (gg0lHi gg0lVLo VVBFjj LepHiT LepLo HadXLo)"
for CAT in gg0lHi gg0lVLo VVBFjj LepHiT LepLo HadXLo; do
    #for YEAR in 2016preVFP 2016postVFP 2017 2018; do
    for YEAR in XXXX; do
	## Producing "Incl" categories also produces Hi/Lo plots
	echo " > python3 merge_files_mctoy.py ${CAT} ${YEAR}"
	python3 merge_files_mctoy.py ${CAT} ${YEAR}
	echo " > Done with python3 merge_files_mctoy.py ${CAT} ${YEAR}"
	ELAPSED=$((SECONDS - START_TIME))
	hours=$((ELAPSED / 3600))
	minutes=$(((ELAPSED % 3600) / 60))
	seconds=$((ELAPSED % 60))
	echo "Time to merge ${CAT} ${YEAR}: $hours hour(s), $minutes minute(s), $seconds second(s)"
    done
done

ELAPSED=$((SECONDS - START_TIME))
hours=$((ELAPSED / 3600))
minutes=$(((ELAPSED % 3600) / 60))
seconds=$((ELAPSED % 60))
echo "Time to merge standard categories: $hours hour(s), $minutes minute(s), $seconds second(s)"

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

ELAPSED=$((SECONDS - START_TIME))
hours=$((ELAPSED / 3600))
minutes=$(((ELAPSED % 3600) / 60))
seconds=$((ELAPSED % 60))
echo "Time for all category merging: $hours hour(s), $minutes minute(s), $seconds second(s)"
