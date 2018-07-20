#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_FL.py 2015 2017
python get_FL.py 2015 2017

#deactivate virtualenv
deactivate
echo virtualenv deactivated