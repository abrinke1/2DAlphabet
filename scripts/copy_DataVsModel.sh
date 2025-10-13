## Copy 2DAlphabet data vs. model profile and 2D plots

source config/user.config  ## Loads USER, LOC_DIR, and EOS_DIR
YEAR="Run2"
DATE="2025_09_31"
MHREG="pnet"
MAREG="34a"
#CATS=("LepHiT" "LepLo" "gg0lVHi" "gg0lVLo" "HadXHi" "HadXLo")
#FITS=("1x1C" "2s2C")
CATS=("LepHiT" "LepLo")
FITS=("1d1C")
DMCS=("MC" "Data")
WPS=("WP40" "WP60" "WP4060")
#CATS=("LepHiT" "LepLo" "HadXHi" "HadXLo")
#CATS=("gg0lVHi" "gg0lVLo")
#DMCS=("Data")
#WPS=("WP4060")
#PLOTS=("postfit_projx" "postfit_projy" "data_obs_Pass_2D" "data_obs_Fail_2D" "TotalBkg_Pass_2D" "TotalBkg_Fail_2D")
PLOTS=("postfit_projx" "postfit_projy" "postfit_projx_logy" "postfit_projy_logy")

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
		for iToy in {-2..9}; do
		    isToy="toy${iToy}"
		    osToy="${iDMC}toy${iToy}"
		    topDir="${EOS_DIR}/"
		    if [ "${iToy}" == "-1" ]; then
			isToy="${iDMC}rounded"
			osToy="${iDMC}rounded"
			topDir=""
		    elif [ "${iToy}" == "-2" ]; then
			isToy="${iDMC}"
			osToy="${iDMC}"
			topDir=""
		    fi
		    dirStr="${iCat}_Htoaato4b_${MHREG}_${MAREG}_${iWP}_${iFit}_${YEAR}"
		    #inDir="${topDir}output/${DATE}/${iDMC}toys/plots_${dirStr}_${isToy}/mA_all_area/plots_fit_b/"
		    inDir="${topDir}output/${DATE}/${iDMC}toys/fits_${dirStr}_${isToy}/mA_all_area/plots_fit_b/"
		    echo ${inDir}
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
