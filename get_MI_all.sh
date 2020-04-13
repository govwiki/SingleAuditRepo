#get current date
TODAY=`date +%Y`

#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_MI.py
python get_MI.py

#deactivate virtualenv
deactivate
echo virtualenv deactivated
