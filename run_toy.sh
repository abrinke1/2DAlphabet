## Run limits, bias, and goodness-of-fit for a single toy

iToy=$1       ## Toy index
TOYSOURCE=$2  ## Data or MC
iCat=$3       ## Category to run
iMA=$4        ## GEN a boson mass (must be in masses in htoaato4b_mctoy.py)
YEAR=$5       ## Run2, 20XX, 2018, 2017, 2016
FIT=$6        ## Fit to use, e.g. 1x1C or 2s2C. Use NxM for multiple fits.
sInj=$7       ## Whether to inject signal (True/true/T/1 vs. False/false/F/0)
NTOYGOF=100   ## Number of toys 2DAlphabet will run for goodness-of-fit test
DATE="2025_09_31"
MHREG="pnet"
MAREG="34a"
FITS=("${FIT}")
if [[ ${FIT} == "NxM" ]]; then
    ## Needs to be a subset of FITLIST in htoaato4b_mctoy.py
    FITS=("0x0" "1d1C" "1x1C" "2d2C" "2s2C" "2x2C")
fi

doGOF=true
doLIM=true
doFitD=false
doMDFit=true
forceRegenerate=false
useExistingCards=false

if [[ $sInj == "True" || $sInj == "true" || $sInj == "T" || $sInj == 1 ]]; then
    SIGINJ=true
elif [[ $sInj == "False" || $sInj == "false" || $sInj == "F" || $sInj == 0 ]]; then
    SIGINJ=false
else
    echo "Signal injection option ${sInj} not valid! Quitting."
    exit
fi

echo "Running with toy #${iToy} from ${TOYSOURCE} in ${iCat} with mA=${iMA}, fit ${FITS[0]} and signal injection=${SIGINJ}"


## Signal injection string by mass(a)
## Corresponds to SIGINJ in Haa4b_makeMCtoy.py
SIN=""
if [ "$SIGINJ" = true ]; then
    if [[ "$iMA" -ge "11" && "$iMA" -le "20" ]]; then
	SIN="_mA_${iMA}_sigBr_020"
    elif [ "$iMA" -le "40" ]; then
	SIN="_mA_${iMA}_sigBr_050"
    elif [ "$iMA" -lt "63" ]; then
	SIN="_mA_${iMA}_sigBr_100"
    fi
fi

## Output EOS directory to move ROOT files (avoid disk quota issues)
source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR
EOS_OUT_DIR="${EOS_DIR}/ToyStudies/${DATE}/${iCat}/${YEAR}/"
echo "Just to be sure, you want to output to:"
echo ${EOS_OUT_DIR}
if [ ! -d ${EOS_OUT_DIR} ]; then
    mkdir -p ${EOS_OUT_DIR}
fi

## Also create temporary EOS directory to run from
## Avoids afs read/write volume issues when running Condor batch jobs
if [[ ${PWD} != ${LOC_DIR} ]]; then
    echo "PWD = ${PWD}"
    echo "LOC_DIR = ${LOC_DIR}"
    echo "These should be the same! Quitting."
    exit
else
    echo "Making temporary running directory:"
    EOS_TMP_DIR="${EOS_OUT_DIR}tmp_${iToy}_${TOYSOURCE}_${iCat}_${iMA}_${FITS[0]}_${sInj}/"
    echo "${EOS_TMP_DIR}"
    mkdir -p ${EOS_TMP_DIR}
    cd ${EOS_TMP_DIR}
    mkdir config
    cp ${LOC_DIR}/config/user.config config/
fi

## Set parameters
sToy="toy${iToy}"
## Toy "-1" corresponds to MCrounded or Datarounded, "-2" corresponds to Data
if [ "${iToy}" == "-1" ]; then
    sToy="MCrounded"
    if [[ ${TOYSOURCE} == "Data" ]]; then
	sToy="Datarounded"
    fi
fi
if [[ "${iToy}" == "-2" && ${TOYSOURCE} == "Data" ]]; then
    sToy="Data"
fi
dmToy="${TOYSOURCE}${sToy}"

INDIR="output/${DATE}/MCtoys"
OUTDIR="output/${DATE}/MCtoys/Mergecards/MC${sToy}"
if [[ ${TOYSOURCE} == "Data" ]]; then
    INDIR="output/${DATE}/Datatoys"
    OUTDIR="output/${DATE}/Datatoys/Mergecards/Data${sToy}"
fi
if [ "$iToy" -ge "0" ]; then
    INDIR="${EOS_DIR}/${INDIR}"
    OUTDIR="${EOS_DIR}/${OUTDIR}"
else
    INDIR="${LOC_DIR}/${INDIR}"
    OUTDIR="${LOC_DIR}/${OUTDIR}"
    ## Copy jsons to EOS_TMP_DIR
    mkdir -p jsons/toys/${DATE}/${iCat}/
    cp -r ${LOC_DIR}/jsons/toys/${DATE}/${iCat}/${YEAR} jsons/toys/${DATE}/${iCat}/
    cp -r ${LOC_DIR}/jsons/*.json jsons/
fi
if [ ! -d ${OUTDIR}/cards/ ]; then
    mkdir -p ${OUTDIR}/cards/
fi
if [ ! -d ${OUTDIR}/${iCat}/${YEAR}/ ]; then
    mkdir -p ${OUTDIR}/${iCat}/${YEAR}/
fi


# Start the timer
START_TIME=$SECONDS


## WARNING!!! You have to run *all* the "sub-categories" before running the "Comb" categories

## Define WP for each category type
WP="UNDEF"
if [[ $iCat == "gg0l"* || $iCat == "VBF"* || $iCat == "HadWP40"* ]]; then
    WP="WP40"
fi
if [[ $iCat == "Lep"* || $iCat == "Vjj"* || $iCat == "tt0l"* || $iCat == "HadWP60"* ]]; then
    if [[ $iCat != "LepHadComb" ]]; then
	WP="WP60"
    fi
fi
if [[ $iCat == "HadX"* || $iCat == "VVBFjj" ]]; then
    WP="WP4060"
fi

## Define component sub-categories for each super-category
subCats=(${iCat})
subCatsLep=()
subCatsHadWP40=()
subCatsHadWP60=()
if [[ ${iCat:0:7} == "LepComb" ]]; then
    subCats=(LepHi${iCat:7:7} LepLo${iCat:7:7})
fi
if [[ $iCat == "gg0lComb" ]]; then
    subCats=(gg0lHi gg0lLo)
fi
if [[ $iCat == "VBFjjComb" ]]; then
    subCats=(VBFjjHi VBFjjLo)
fi
if [[ $iCat == "VjjComb" ]]; then
    subCats=(VjjHi VjjLo)
fi
if [[ $iCat == "HadWP40Comb" ]]; then
    subCats=(gg0lHi gg0lLo VBFjjHi VBFjjLo)
fi
if [[ $iCat == "HadWP60Comb" ]]; then
    subCats=(VjjHi VjjLo tt0l)
fi
if [[ $iCat == "LepHadComb" ]]; then
    subCatsHadWP40=(gg0lHi gg0lLo VBFjjHi VBFjjLo)
    subCatsHadWP60=(VjjHi VjjLo tt0l)
    subCatsLep=(LepHi LepLo)
fi
if [[ $iCat == "LepHadCombFive" ]]; then
    subCats=()
fi


## Make toys for each category
FIT_DIR="fits_${iCat}_Htoaato4b_${MHREG}_${MAREG}_${WP}_${FITS[0]}_${YEAR}_${sToy}${SIN}"
if [[ $iCat != *"Comb"* && $YEAR != "20XX" && "$useExistingCards" = false ]]; then
    if [ "$SIGINJ" = true ]; then
    	echo ">>>>>>>>>> Making Toy #${iToy} in category ${iCat} (${WP}) ${FITS[0]} [${SIN:1}]"
	python3 ${LOC_DIR}/htoaato4b_mctoy.py "${iToy}" "${iCat}" "${TOYSOURCE}" "${YEAR}" "${FITS[0]}" "${SIN:1}"
    	echo ">>>>>>>>>> Made Toy #${iToy} in category ${iCat} (${WP}) ${FITS[0]} [${SIN:1}]"
    else
	## If not injecting signal, only need one 2DAlphabet directory for all mass points
    	cat_card="${INDIR}/${FIT_DIR}/mA_${iMA}_area/card.txt"
	echo "Looking for ${cat_card}"
	if [[ "$forceRegenerate" = true || $iMA == "12" || ! -f ${cat_card} ]]; then
    	    echo ">>>>>>>>>> Making Toy #${iToy} in category ${iCat} (${WP}) ${FITS[0]}"
	    python3 ${LOC_DIR}/htoaato4b_mctoy.py "${iToy}" "${iCat}" "${TOYSOURCE}" "${YEAR}" "${FITS[0]}"
    	    echo ">>>>>>>>>> Made Toy #${iToy} in category ${iCat} (${WP}) ${FITS[0]}"
	else
	    echo "Found it!"
	fi
    fi
    ## If running rounded or real data, copy fits workspace back to local area
    if [[ "$iToy" -le "0" && -d output/${DATE}/${TOYSOURCE}toys/${FIT_DIR} ]]; then
	echo "cp -r output/${DATE}/${TOYSOURCE}toys/${FIT_DIR} ${INDIR}/"
	cp -r output/${DATE}/${TOYSOURCE}toys/${FIT_DIR} ${INDIR}/
    fi
fi


## Merge datacards and run limits for each mA point
echo ">>>>>>>>>> Merging datacards for Toy #${iToy} in category ${iCat} (${WP})"
    
for iFit in "${FITS[@]}"; do
    echo "     <<<<< Now looking at mA = ${iMA}, fit = ${iFit}"

    in_cards=""
    for jCat in "${subCats[@]}"; do
	if [ "${YEAR}" == "20XX" ]; then
	    for iYear in "2016" "2017" "2018"; do
    		new_card="${INDIR}/fits_${jCat}_Htoaato4b_${MHREG}_${MAREG}_${WP}_${iFit}_${iYear}_${sToy}${SIN}/mA_${iMA}_area/card.txt"
		if test -f ${new_card}; then
    		    in_cards="${in_cards} ${new_card}"
		else
		    echo "Could not find input card:"
		    echo ${new_card}
		    in_cards=""
		    break
		fi
	    done
	else
    	    new_card="${INDIR}/fits_${jCat}_Htoaato4b_${MHREG}_${MAREG}_${WP}_${iFit}_${YEAR}_${sToy}${SIN}/mA_${iMA}_area/card.txt"
	    if test -f ${new_card}; then
    		in_cards="${in_cards} ${new_card}"
	    else
		echo "Could not find input card:"
		echo ${new_card}
		in_cards=""
		break
	    fi
	fi ## End conditional: if [ "${YEAR}" == "20XX" ] / else
    done ## End loop: for jCat in "${subCats[@]}"

    if [[ $iCat == "LepHadComb" ]]; then
    	in_cards=""
    	for lCat in "${subCatsLep[@]}"; do
    	    new_card="${in_cards} ${INDIR}/fits_${lCat}_Htoaato4b_${MHREG}_${MAREG}_WP60_${iFit}_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
	    if test -f ${new_card}; then
    		in_cards="${in_cards} ${new_card}"
	    else
		echo "Could not find input card:"
		echo ${new_card}
	    fi
    	done
    	for hCat40 in "${subCatsHadWP40[@]}"; do
    	    new_card="${INDIR}/fits_${hCat40}_Htoaato4b_${MHREG}_${MAREG}_WP40_${iFit}_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
	    if test -f ${new_card}; then
    		in_cards="${in_cards} ${new_card}"
	    else
		echo "Could not find input card:"
		echo ${new_card}
	    fi
    	done
    	for hCat60 in "${subCatsHadWP60[@]}"; do
    	    new_card="${INDIR}/fits_${hCat60}_Htoaato4b_${MHREG}_${MAREG}_WP60_${iFit}_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
	    if test -f ${new_card}; then
    		in_cards="${in_cards} ${new_card}"
	    else
		echo "Could not find input card:"
		echo ${new_card}
	    fi
    	done
    fi
    if [[ $iCat == "LepHadCombFive" ]]; then
    	in_cards=""
    	new_card="${INDIR}/fits_gg0lV_Htoaato4b_${MHREG}_${MAREG}_WP40_2d2C_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
	if test -f ${new_card}; then
    	    in_cards="${new_card}"
	else
	    echo "Could not find input card:"
	    echo ${new_card}
	    continue
	fi
    	new_card="${INDIR}/fits_VVBFjj_Htoaato4b_${MHREG}_${MAREG}_WP4060_1d1C_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
	if test -f ${new_card}; then
    	    in_cards="${in_cards} ${new_card}"
	else
	    echo "Could not find input card:"
	    echo ${new_card}
	    continue
	fi
    	new_card="${INDIR}/fits_HadXLo_Htoaato4b_${MHREG}_${MAREG}_WP60_1d1C_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
	if test -f ${new_card}; then
    	    in_cards="${in_cards} ${new_card}"
	else
	    echo "Could not find input card:"
	    echo ${new_card}
	    continue
	fi
    	new_card="${INDIR}/fits_LepHiT_Htoaato4b_${MHREG}_${MAREG}_WP60_0x0_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
	if test -f ${new_card}; then
    	    in_cards="${in_cards} ${new_card}"
	else
	    echo "Could not find input card:"
	    echo ${new_card}
	    continue
	fi
    	new_card="${INDIR}/fits_LepLo_Htoaato4b_${MHREG}_${MAREG}_WP60_0x0_${YEAR}_${sToy}/mA_${iMA}_area/card.txt"
	if test -f ${new_card}; then
    	    in_cards="${in_cards} ${new_card}"
	else
	    echo "Could not find input card:"
	    echo ${new_card}
	    continue
	fi
    fi
    echo $in_cards
    if [ "$in_cards" == "" ]; then
	echo "<<<<< No cards matching mA = ${iMA}, fit = ${iFit}. Skipping!"
	continue
    fi

    if [ "$useExistingCards" = false ]; then
	## Combine cards, output to workspace
	echo "combineCards.py $in_cards > ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt"
	combineCards.py $in_cards > ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt
	# echo "text2workspace.py --out ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.root"
	# text2workspace.py ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --for-fits --no-wrappers --optimize-simpdf-constraints=cms --X-pack-asympows --use-histsum  --out ${OUTDIR}/workspace_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.root
    fi

    ## Set blinding options
    runOpt="--run=both"
    fitOpt=""
    if [[ ${TOYSOURCE} == "Data" && "$iToy" -lt "0" ]]; then
	runOpt="--run=expected"
	fitOpt="-t -1"
    fi

    ## GoodnessOfFit
    ## Only need to run GoF for one mA point, since signal strength is set to 0
    if [[ "$doGOF" = true && $iMA == "12" && ! "$SIGINJ" = true ]]; then
        echo "combine -M GoodnessOfFit -d ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy} --toysFrequentist -t ${NTOYGOF} -s 123456"
        combine -M GoodnessOfFit -d ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy} --toysFrequentist -t ${NTOYGOF} -s 123456
        echo "combine -M GoodnessOfFit -d ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}"
        combine -M GoodnessOfFit -d ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --algo=saturated --fixedSignalStrength 0 -n .testGoodnessOfFit.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}
    fi
	
    if [[ "$doLIM" = true && ! "$SIGINJ" = true ]]; then
	## AsymptoticLimits
	echo "combine -M AsymptoticLimits ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt ${runOpt} --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance=0.0001 -n .testAsymptoticLimits.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}"
	combine -M AsymptoticLimits ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt ${runOpt} --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance=0.0001 -n .testAsymptoticLimits.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}
    fi

    if [[ "$doFitD" = true ]]; then
	## FitDiagnostics
	echo "combine -M FitDiagnostics ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --setParameterRanges r=0.0,1.0 --robustFit 1 --minos all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}"
	combine -M FitDiagnostics ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --setParameterRanges r=0.0,1.0 --robustFit 1 --minos all -n .testFitDiagnostics.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}
    fi

    if [[ "$doMDFit" = true ]]; then
	## MultiDimFit
	SCAN="--setParameterRanges r=-1,1 --points 1"
	if [[ "$iMA" -ge "11" && "$iMA" -le "20" ]]; then
	    SCAN="--setParameterRanges r=-0.0001,0.1001 --points 501"
	elif [ "$iMA" -le "40" ]; then
	    SCAN="--setParameterRanges r=-0.00025,0.20025 --points 401"
	elif [ "$iMA" -lt "63" ]; then
	    SCAN="--setParameterRanges r=-0.0005,0.4005 --points 401"
	fi

	echo "combine -M MultiDimFit ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --algo grid ${SCAN} --floatOtherPOIs=1 --preFitValue=0 --cminDefaultMinimizerStrategy 0 --robustFit 1 -n .testMultiDimFit.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}"
	combine -M MultiDimFit ${OUTDIR}/cards/combined_${iCat}_mA_${iMA}_${iFit}${SIN}_${YEAR}.txt --algo grid ${SCAN} --floatOtherPOIs=1 --preFitValue=0 --cminDefaultMinimizerStrategy 0 --robustFit 1 -n .testMultiDimFit.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}
    fi

    ## Move files to EOS
    if [ "$iToy" -ge 0 ]; then
	echo "mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}*root ${EOS_OUT_DIR}"
	mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}*root ${EOS_OUT_DIR}
    else
	echo "mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}*root ${OUTDIR}/${iCat}/${YEAR}/"
	mv *.test*.${iCat}.mA_${iMA}.${iFit}${SIN}.${dmToy}*root ${OUTDIR}/${iCat}/${YEAR}/
    fi
    echo "     <<<<< All done with mA = ${iMA}"

    cd ${LOC_DIR}
    rm -rf ${EOS_TMP_DIR}

    # Calculate elapsed time
    ELAPSED=$((SECONDS - START_TIME))
    hours=$((ELAPSED / 3600))
    minutes=$(((ELAPSED % 3600) / 60))
    seconds=$((ELAPSED % 60))
    echo "Runtime so far: $hours hour(s), $minutes minute(s), $seconds second(s)"
done ## End loop: for iFit in "${FITS[@]}"

echo "TOTAL runtime: $hours hour(s), $minutes minute(s), $seconds second(s)"
