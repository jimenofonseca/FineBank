#!/bin/sh

export PATH="~/anaconda3/bin:$PATH"
#ask the user if you would like to install the app
echo "HELLO FONNACHT!";
echo "IM DOING SOME CHECKS IN YOUR SYSTEM";

if conda --version;
then
    echo "CONDA IS INSTALLED" ;
else
    echo "CONDA IS NOT INSTALLED, THIS IS A PRE-REQUIREMENT" ;
    echo "INSTALLING CONDA, THIS MIGHT TAKE A WHILE..." ;

    curl -Ok https://repo.continuum.io/archive/Anaconda3-4.1.1-MacOSX-x86_64.sh
    bash Anaconda3-4.1.1-MacOSX-x86_64.sh -b -p ~/anaconda3
    rm Anaconda3-4.1.1-MacOSX-x86_64.sh
    echo 'export PATH="~/anaconda3/bin:$PATH"' >> ~/.bash_profile

    # Refresh basically
    source .bash_profile
    conda update conda
fi ;

#check if the installation exists
directory=$(pwd);
if [[ -d "${directory}/my_env" ]]
then
    echo "THE FONNACHT'S APP IS ALREADY INSTALLED!";
    echo "ALL RIGHT!";
    echo "LET'S GO INTO BUSINESS!";

    # Run script
    ./my_env/bin/python login.py;
else
    echo "ALL GOOD, WE ARE INSTALLING THE FONNACHT'S BANKAPP...";
    # Unpack environment into directory `my_env`
    mkdir -p my_env;
    tar -xzf env/my_env.tar.gz -C my_env;

    # Activate the environment. This adds `my_env/bin` to your path
    source my_env/bin/activate;

    # Cleanup prefixes from in the active environment.
    conda-unpack;

    echo "THE INSTALLATION WAS SUCCESSFUL!";
    echo "LET'S GO INTO BUSINESS!";

    # Run script
    ./my_env/bin/python login.py;
fi