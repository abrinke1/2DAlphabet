#!/bin/bash

CFG="config/user.config"
USER="UNKNOWN"
EOS_DIR="UNKNOWN"

printf "\nCurrent working directory is:\n"
printf $PWD

if [[ $PWD == *abrinke1* ]]; then
    USER="abrinke1"
    EOS_DIR="/eos/cms/store/user/abrinke1/HiggsToAA/2DAlphabet"
elif [[ $PWD == *ssawant* ]]; then
    USER="ssawant"
elif [[ $PWD == *hboucham* ]]; then
    USER="hboucham"
elif [[ $PWD == *moanwar* ]]; then
    USER="moanwar"
else
    printf "\n\nNo valid user found!!!\n"
    printf "\nDeleting $CFG if it exists, then quitting.\n\n"
    rm $CFG
    exit
fi

printf "\n\nConfiguring for user $USER.\n"
printf "\nEOS output directory is:"
printf "\n$EOS_DIR\n"
if [[ $EOS_DIR == "UNKNOWN" ]]; then
    printf "\nProblem!!! No good EOS_DIR!\n"
    printf "\nDeleting $CFG if it exists.\n"
    rm $CFG
else
    printf "\nWriting configuration to:"
    printf "\n$CFG\n"
    printf "USER=$USER\n" > $CFG
    printf "LOC_DIR=$PWD\n" >> $CFG
    printf "EOS_DIR=$EOS_DIR\n" >> $CFG
fi
printf "\nAll done!\n\n"
