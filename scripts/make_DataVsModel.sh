for CAT in HadXHi HadXLo LepHiT LepLo; do
    #for DM in MC Data; do
    for DM in Data; do
	#python3 htoaato4b_mctoy_plots.py -1 ${CAT} ${DM} Run2
	python3 htoaato4b_mctoy_plots.py -2 ${CAT} ${DM} Run2
    done
done

for CAT in gg0lVHi gg0lVLo; do
    #for DM in MC Data; do
    for DM in Data; do
	for YEAR in 2016 2017 2018 Run2; do
	    #python3 htoaato4b_mctoy_plots.py -1 ${CAT} ${DM} ${YEAR}
	    python3 htoaato4b_mctoy_plots.py -2 ${CAT} ${DM} ${YEAR}
	done
    done
done
