set -x
set -v
#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_IL.py
python get_IL.py

#deactivate virtualenv
deactivate
echo virtualenv deactivated
set +x
set +v