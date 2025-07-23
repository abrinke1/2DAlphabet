#!/bin/bash

########################################################
# Prepare input ROOT files to be used in generatetoys.sh
########################################################

DATE="2025_07_14"
source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR
OUTDIR="${EOS_DIR}/raw_inputs/${DATE}"

# Do you want to re-copy input ROOT files to local area?
FETCH_INPUTS=true # true or false; takes ~5 minutes

# Do you want to run merge_files_mctoy.py (necessary to generate toys)
MERGE_INPUTS=true # true or false; takes 20 - 30 minutes for **each** category per year, with systematics

# Start the timer
START_TIME=$SECONDS

## Copy input ROOT files to local area
if $FETCH_INPUTS; then

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
    # # -- Leptonic categories from Hichem (Zll, Wlv, ttlv, ttll) --
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

fi ## End conditional: if $FETCH_INPUTS


if $MERGE_INPUTS; then
    ## Prepare inputs
    #echo " > Merging categories (LepLo LepHi LepHiT gg0lV VVBFjj HadXLo LepIncl gg0lIncl VBFjjIncl VjjIncl tt0lIncl)"
    #for CAT in LepLo LepHi LepHiT gg0lV VVBFjj HadXLo LepIncl gg0lIncl VBFjjIncl VjjIncl tt0lIncl; do
    echo " > Merging categories (LepHiT LepLo gg0lIncl HadXLo)"
    for CAT in LepHiT LepLo gg0lIncl HadXLo; do
	for YEAR in 2016preVFP 2016postVFP 2017 2018; do
	#for YEAR in 2018; do
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
    # 	for YEAR in 2016pre 2016post 2017 2018; do
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

    #python3 merge_years_mctoy.py ${CAT}

fi  ## End conditional: if $MERGE_INPUTS

ELAPSED=$((SECONDS - START_TIME))
hours=$((ELAPSED / 3600))
minutes=$(((ELAPSED % 3600) / 60))
seconds=$((ELAPSED % 60))
echo "Total runtime: $hours hour(s), $minutes minute(s), $seconds second(s)"
