#!/bin/bash

#######################################################
# Fetch input ROOT files to be used in mergetoyinput.sh
# Takes 5 - 10 minutes
#######################################################

DATE="2025_08_15"
source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR
OUTDIR="${EOS_DIR}/raw_inputs/${DATE}"

HADDIR="/eos/cms/store/user/ssawant/htoaa/analysis/20250811_DatacardsFullSyst"
VBFDIR="/afs/cern.ch/work/m/moanwar/public/hto2ato4b/newVBFCat/2DAlphabet_inputFiles"
LEPDIR="/eos/user/h/hboucham/public/2D_Alphabet_Inputs"
LEPTAG="081425"

DOHAD=true
DOVBF=true
DOLEP=true

# Start the timer
START_TIME=$SECONDS

# # Emptying the input directory
# echo " > Make new directory ${OUTDIR}"
# if [ -d $OUTDIR ]; then
#     rm -rf $OUTDIR
# fi
# mkdir -p $OUTDIR

# Copy all 2D plots
echo " > Copy all input 2D histogram files to raw_inputs ..."
# -- Hadronic categories from Siddhesh (gg0l, Vjj, tt0l, Zvv) --
echo "Starting hadronic ..."
for CAT in gg0lLo gg0lHi VjjLo VjjHi VjjLo350 VjjHi350 VjjLo400 VjjHi400 tt0l0b tt0l1b ZvvLo ZvvHi; do
    if [ "$DOHAD" = false ]; then
	echo "... actually, skipping!"
	break
    fi
    mkdir -p ${OUTDIR}/${CAT}/Run2
    rm -r ${OUTDIR}/${CAT}/Run2/*
    for YEAR in 2016preVFP 2016postVFP 2017 2018; do
	mkdir -p ${OUTDIR}/${CAT}/${YEAR}
	rm -r ${OUTDIR}/${CAT}/${YEAR}/*
	echo "cp -r ${HADDIR}/${YEAR}/*/2DAlphabet_inputFiles/${CAT}/*root ${OUTDIR}/${CAT}/${YEAR}/"
	cp -r ${HADDIR}/${YEAR}/*/2DAlphabet_inputFiles/${CAT}/*root ${OUTDIR}/${CAT}/${YEAR}/
    done
done

# -- VBF --
echo "Starting VBF ..."
declare -A CATS
CATS["VBFjjLo"]="VBFLo"
CATS["VBFjjHi"]="VBFHi"
CATS["VBFjjLoPtLo"]="VBFLoPTLo"
CATS["VBFjjLoPtHi"]="VBFLoPTHi"
CATS["VBFjjHiPtLo"]="VBFHiPTLo"
CATS["VBFjjHiPtHi"]="VBFHiPTHi"
for CAT in ${!CATS[@]}; do
    if [ "$DOVBF" = false ]; then
	echo "... actually, skipping!"
	break
    fi
    mkdir -p ${OUTDIR}/${CAT}/Run2
    rm -r ${OUTDIR}/${CAT}/Run2/*
    for YEAR in 2016preVFP 2016postVFP 2017 2018; do
	CATIN="${CATS[${CAT}]}"
	INDIR="${VBFDIR}/${YEAR}/VBFjj/2DAlphabet_inputFiles/${CATIN}"
	mkdir -p ${OUTDIR}/${CAT}/${YEAR}
	rm -r ${OUTDIR}/${CAT}/${YEAR}/*
	echo "cp -r ${INDIR}/*root ${OUTDIR}/${CAT}/${YEAR}/"
	cp -r ${INDIR}/*root ${OUTDIR}/${CAT}/${YEAR}/
	echo "Changing file names from ${CATIN} to ${CAT}"
	cd ${OUTDIR}/${CAT}/${YEAR}/
	for FILEIN in *root; do
	    FILEOUT=${FILEIN/"$CATIN"/"$CAT"}
	    #echo "mv ${FILEIN} ${FILEOUT}"
	    mv ${FILEIN} ${FILEOUT}
	done
	cd -
    done
done

# -- Leptonic categories from Hichem (Zll, Wlv, ttlv, ttll) --
echo "Starting leptonic ..."
for CAT in Zll WlvLo WlvHi ttblv ttbblv ttbll; do
    if [ "$DOLEP" = false ]; then
	echo "... actually, skipping!"
	break
    fi
    for WP in WP60; do
	mkdir -p ${OUTDIR}/${CAT}/${WP}/Run2
	rm -r ${OUTDIR}/${CAT}/${WP}/Run2/*
	for YEAR in 2016preVFP 2016postVFP 2017 2018; do
	    mkdir -p ${OUTDIR}/${CAT}/${WP}/${YEAR}
	    rm -r ${OUTDIR}/${CAT}/${WP}/${YEAR}/*
	    YEARIN=${YEAR:2:2}  ## Last 2 digits of  year (16, 17, 18)
	    if [[ "${YEAR}" == "2016preVFP" ]]; then
		YEARIN="16APV"
	    elif [[ "${YEAR}" == "2016postVFP" ]]; then
		YEARIN="16"
	    fi
	    echo "cp ${LEPDIR}/2D${YEARIN}_*_${LEPTAG}/${WP}/${CAT}_*root ${OUTDIR}/${CAT}/${WP}/${YEAR}/"
	    cp ${LEPDIR}/2D${YEARIN}_*_${LEPTAG}/${WP}/${CAT}_*root ${OUTDIR}/${CAT}/${WP}/${YEAR}/
	done
    done
done

ELAPSED=$((SECONDS - START_TIME))
hours=$((ELAPSED / 3600))
minutes=$(((ELAPSED % 3600) / 60))
seconds=$((ELAPSED % 60))
echo "Time to fetch inputs: $hours hour(s), $minutes minute(s), $seconds second(s)"
