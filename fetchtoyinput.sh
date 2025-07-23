#!/bin/bash

#######################################################
# Fetch input ROOT files to be used in mergetoyinput.sh
# Takes ~5 minutes (not including VBFjj)               
#######################################################

DATE="2025_07_14"
source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR
OUTDIR="${EOS_DIR}/raw_inputs/${DATE}"

# Start the timer
START_TIME=$SECONDS

# Emptying the input directory
echo " > Make new directory ${OUTDIR}"
if [ -d $OUTDIR ]; then
    rm -rf $OUTDIR
fi
mkdir -p $OUTDIR

# Copy all 2D plots
echo " > Copy all input 2D histogram files to raw_inputs ..."
# -- Hadronic categories from Siddhesh (gg0l, Vjj, tt0l, Zvv) --
echo "Starting hadronic ..."
for CAT in gg0lLo gg0lHi VjjLo VjjHi tt0l0b tt0l1b ZvvLo ZvvHi; do
    mkdir -p ${OUTDIR}/${CAT}/Run2
    for YEAR in 2016preVFP 2016postVFP 2017 2018; do
	mkdir -p ${OUTDIR}/${CAT}/${YEAR}
	echo "cp -r /eos/cms/store/user/ssawant/htoaa/analysis/20250713_DatacardsFull*/${YEAR}/*/2DAlphabet_inputFiles/${CAT}/*root ${OUTDIR}/${CAT}/${YEAR}/"
	cp -r /eos/cms/store/user/ssawant/htoaa/analysis/20250713_DatacardsFull*/${YEAR}/*/2DAlphabet_inputFiles/${CAT}/*root ${OUTDIR}/${CAT}/${YEAR}/
    done
done

# # -- VBF --
# echo "Starting VBF ..."
# mkdir ${OUTDIR}/VBFjj
# cp /afs/cern.ch/user/m/moanwar/public/2DAlphabet_2018_4June/analyze_htoaa_stage1.root ${OUTDIR}/VBFjj/
# # -- tt0l (tighter top tagger, separated by AK4 b-tags) --
# cp -r /eos/cms/store/user/ssawant/htoaa/analysis/20250626_tt0lDatacardsFullSyst/2018/2DAlphabet_inputFiles/* ${OUTDIR}/

# -- Leptonic categories from Hichem (Zll, Wlv, ttlv, ttll) --
echo "Starting leptonic ..."
for CAT in Zll WlvLo WlvHi ttblv ttbblv ttbll; do
    for WP in WP60; do
	mkdir -p ${OUTDIR}/${CAT}/${WP}/Run2
	for YEAR in 2016preVFP 2016postVFP 2017 2018; do
	    mkdir -p ${OUTDIR}/${CAT}/${WP}/${YEAR}
	    YEARIN=${YEAR:2:2}  ## Last 2 digits of  year (16, 17, 18)
	    if [[ "${YEAR}" == "2016preVFP" ]]; then
		YEARIN="16APV"
	    elif [[ "${YEAR}" == "2016postVFP" ]]; then
		YEARIN="16"
	    fi
	    echo "cp /eos/user/h/hboucham/public/2D_Alphabet_Inputs/2D${YEARIN}_*_072225/${WP}/${CAT}_*root ${OUTDIR}/${CAT}/${WP}/${YEAR}/"
	    cp /eos/user/h/hboucham/public/2D_Alphabet_Inputs/2D${YEARIN}_*_072225/${WP}/${CAT}_*root ${OUTDIR}/${CAT}/${WP}/${YEAR}/
	done
    done
done

ELAPSED=$((SECONDS - START_TIME))
hours=$((ELAPSED / 3600))
minutes=$(((ELAPSED % 3600) / 60))
seconds=$((ELAPSED % 60))
echo "Time to fetch inputs: $hours hour(s), $minutes minute(s), $seconds second(s)"
