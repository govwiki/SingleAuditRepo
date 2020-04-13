set -x
set -v
cd /home/sibers/python_scripts/SingleAuditRepo
echo changed workdir

# activate virtualenv
source ./demoenv/bin/activate
echo virtualenv activated

# run the script
echo running file_checker_gp.py
python file_checker_sc.py

#deactivate virtualenv
deactivate
echo virtualenv deactivated
set +x
set +v
