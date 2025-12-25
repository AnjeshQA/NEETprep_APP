# 1. Fix Path for Mac binaries (Node, Appium, Python)
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# 2. Git Integration
git fetch origin
git reset --hard origin/main

# 3. Virtual Environment Setup
if [ ! -d ".venv" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# 4. Sync Dependencies using your requirements.txt
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found! Installing core packages manually..."
    pip install pytest pytest-timeout pytest-rerunfailures allure-pytest appium-python-client openpyxl
fi

# 5. Clean old results
rm -rf allure-results

# 6. Run Tests
python3 -m pytest TestCases/test_loginpage.py --alluredir=allure-results

#Jenkin Shell Command is given below
#chmod +x jenkins_run.sh
#./jenkins_run.sh