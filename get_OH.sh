#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_OH.py
python get_OH.py

#deactivate virtualenv
deactivate
echo virtualenv deactivated
