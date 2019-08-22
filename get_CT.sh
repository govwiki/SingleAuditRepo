set -x
set -v
#get current date
YESTERDAY=`date +%m/%d/%Y -d "3 day ago"`

#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_CT.py --year $YESTERDAY
python get_CT.py --year $YESTERDAY

#deactivate virtualenv
deactivate
echo virtualenv deactivated
set +x
set +v