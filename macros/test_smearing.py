import numpy as np
import statistics as stat
nevt = 1000000  ## Number of random events thrown for each smearing
#for smr in [0.03+0.01*ii for ii in range(3)]:  ## Smearing factor
#for smr in [0.07]:  ## Smearing factor
for smr in [0.20]:  ## Smearing factor
    #for mass in [125.0, 175.0]:      ## Resonance peak (GeV)
    #    for wid in [15.0, 20.0, 25.0]:  ## Resonance width (GeV)
    # for mass in [125.0]:      ## Resonance peak (GeV)
    #     for wid in [125.0*14.0/172.0, 14.0]:  ## Resonance width (GeV)
    #         smr_sc = 0.023
    # for mass in [125.0]:
    #     for wid in [10.0]:  ## PNet regressed m(H) width
    #         smr_sc = 0.03   ## Smearing factor to increase width by 7%
    for mass in [15.0,30.0,55.0]:
        for wid in [mass*0.068]:  ## PNet regressed m(a) width
            smr_sc = 0.045        ## Smearing factor to increase width by 20%

            #smr_sc = np.sqrt(2.0*smr)*wid/mass
            nom = np.random.normal(mass, wid, nevt)
            nom_med = stat.median(nom)
            nom_mn = stat.mean(nom)
            nom_std = stat.stdev(nom)
            smear = np.random.normal(1.0, smr_sc, nevt)
            smr_med = stat.median(nom*smear)
            smr_mn = stat.mean(nom*smear)
            smr_std = stat.stdev(nom*smear)
            print('\nResults for %.1f GeV resonance with %.2f GeV width, %.2f%% smearing (%.2f%% base)' % (mass, wid, smr_sc*100, smr*100))
            print('Nominal median = %.3f, mean = %.3f, std. dev. = %.4f' % (nom_med, nom_mn, nom_std))
            print('Smeared median = %.3f, mean = %.3f, std. dev. = %.4f' % (smr_med, smr_mn, smr_std))
            print('Smeared width %.2f%% larger than nominal' % (100.0*((smr_std/nom_std) - 1.0)))
        ## End loop: for wid in [
    ## End loop: for mass in [
## End loop: for smr in [
