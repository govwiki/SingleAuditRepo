#get current date
TODAY=`date +%m/%d/%Y`
#TODAY="04/11/2019"
YESTERDAY="05/23/2019"

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
