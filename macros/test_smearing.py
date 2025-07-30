import numpy as np
import statistics as stat
nevt = 10000000  ## Number of random events thrown for each smearing
#for smr in [0.03+0.01*ii for ii in range(3)]:  ## Smearing factor
for smr in [0.04]:  ## Smearing factor
    #for mass in [125.0, 175.0]:      ## Resonance peak (GeV)
    #    for wid in [15.0, 20.0, 25.0]:  ## Resonance width (GeV)
    for mass in [125.0]:      ## Resonance peak (GeV)
        for wid in [125.0*14.0/172.0, 14.0]:  ## Resonance width (GeV)
        #for wid in [20.0]:  ## Resonance width (GeV)
            #smr_sc = np.sqrt(2.0*smr)*wid/mass
            smr_sc = 0.023
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
