set -x
set -v
#get current date
TODAY=`date +%m/%d/%Y`
YESTERDAY=`date +%m/%d/%Y -d "3 day ago"`

#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_FAC_SA.py $YESTERDAY $TODAY
python get_FAC_SA.py $YESTERDAY $TODAY

#deactivate virtualenv
deactivate
echo virtualenv deactivated
set +x
set +v