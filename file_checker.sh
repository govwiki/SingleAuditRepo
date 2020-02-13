cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running file_checker.py
python file_checker.py

#deactivate virtualenv
deactivate
echo virtualenv deactivated