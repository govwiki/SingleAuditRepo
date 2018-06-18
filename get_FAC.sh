#! /bin/bash
# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_FAC_SA.py
python get_FAC_SA.py

#deactivate virtualenv
deactivate
echo virtualenv deactivated
