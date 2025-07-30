## Copy 2DAlphabet data vs. model profile and 2D plots

source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR
YEAR="2018"
DATE="2025_07_25"
MHREG="pnet"
MAREG="34a"
#CATS=("gg0lV" "VVBFjj" "HadXLo" "LepHiT" "LepLo")
#FITS=("0x0" "1d1C" "1x1C" "2d2C" "2s2C" "2d2C" "0x0smr" "1d1Csmr" "1x1Csmr" "2d2Csmr" "2s2Csmr" "2x2C")
DMCS=("MC" "Data")
#CATS=("gg0lHi" "gg0lLo" "VVBFjj")
CATS=("gg0lLo")
FITS=("2s2C")
#DMCS=("Data")
WPS=("WP40" "WP60" "WP4060")
PLOTS=("postfit_projx" "postfit_projy" "data_obs_Pass_2D" "data_obs_Fail_2D" "TotalBkg_Pass_2D" "TotalBkg_Fail_2D")

OUT_DIR="figures/DataVsModel/${DATE}/"
echo "Just to be sure, you want to output to:"
echo ${OUT_DIR}
if [ ! -d ${OUT_DIR} ]; then
    mkdir -p ${OUT_DIR}
fi

for iCat in "${CATS[@]}"; do
    for iDMC in "${DMCS[@]}"; do
	for iFit in "${FITS[@]}"; do
	    for iWP in "${WPS[@]}"; do
		for iToy in {-1..9}; do
		    isToy="toy${iToy}"
		    osToy="${iDMC}toy${iToy}"
		    topDir="${EOS_DIR}/"
		    if [ "${iToy}" == "-1" ]; then
			isToy="${iDMC}rounded"
			osToy="${iDMC}rounded"
			topDir=""
		    fi
		    dirStr="${iCat}_Htoaato4b_${MHREG}_${MAREG}_${iWP}_${iFit}_${YEAR}"
		    inDir="${topDir}output/${iDMC}toys/fits_${dirStr}_${isToy}/mA_all_area/plots_fit_b/"
		    for iPlot in "${PLOTS[@]}"; do
			if [ -f "${inDir}${iPlot}.pdf" ]; then
			    echo "Making ${OUT_DIR}${dirStr}_${osToy}_${iPlot}.pdf"
			    #echo "cp ${inDir}${iPlot}.pdf"
			    cp "${inDir}${iPlot}.pdf" "${OUT_DIR}${dirStr}_${osToy}_${iPlot}.pdf"
			    if [ "${iPlot}" == "TotalBkg_Pass_2D" ]; then
				echo "Making ${OUT_DIR}${dirStr}_${osToy}_${iCat}Background_${iFit}_Pass_2D.pdf"
				cp "${inDir}${iCat}Background_${iFit}_Pass_2D.pdf" "${OUT_DIR}${dirStr}_${osToy}_${iCat}Background_${iFit}_Pass_2D.pdf"
				echo "Making ${OUT_DIR}${dirStr}_${osToy}_${iCat}Background_Fail_2D.pdf"
				cp "${inDir}${iCat}Background_Fail_2D.pdf" "${OUT_DIR}${dirStr}_${osToy}_${iCat}Background_Fail_2D.pdf"
			    fi
			fi
		    done
		done
	    done
	done
    done
done
