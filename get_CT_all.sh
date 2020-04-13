#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_CT.py --year 01/01/2010
python get_CT.py --year 01/01/2010

#deactivate virtualenv
deactivate
echo virtualenv deactivated
