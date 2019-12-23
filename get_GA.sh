YESTERDAY=`date +%Y -d "1 year ago"`
TODAY=`date +%Y`

#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_GA.py $YESTERDAY $TODAY
python get_GA.py $YESTERDAY $TODAY

#deactivate virtualenv
deactivate
echo virtualenv deactivated