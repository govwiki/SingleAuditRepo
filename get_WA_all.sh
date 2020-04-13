#get current date
YESTERDAY=`date +%Y -d "1 year ago"`
TODAY=`date +%Y`
#change working folder
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running get_WA.py --year 2005 $YESTERDAY
python3 get_WA.py 2005 $YESTERDAY

#deactivate virtualenv
deactivate
echo virtualenv deactivated
