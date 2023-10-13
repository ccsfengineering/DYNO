# DYNO
Scripts for the Dynamometer  
  
Links to Documentation:  
https://www.ato.com/Content/doc/Digita-rotary-torque-sensor-user-manual-ATO-TQS-DYN-200.pdf  
https://www.ato.com/Content/doc/digital-rotary-torque-sensor-user-manual-upgrade-version.pdf  
  
Start:
1) Create a python virtual environment:
   In the DYNO folder open a terminal and run `python3 -m venv .venv`
   If you are using Visual Studio Code a notification will appear on the bottom right corner that will ask if you want to switch into this new virtual environment. Accept.
   Alternatively, to use this virtual environment you will have to run `source /PATH_TO_YOUR_REPOSITORY/DYNO/.venv/bin/activate`(Tested on Linux/Mac) before you start running scripts from here.
  
2) Install dependencies:
   In your virtual environment run `pip install -r requirements.txt`
  
3) Run Script!
   To use this script from your virtual environment either click run in VS Code or in your terminal enter `python /PATH_TO_YOUR_REPOSITORY/DYNO/Dyno.py`
   Alternatively, if you are not in your virtual environment, you can run `/PATH_TO_YOUR_REPOSITORY/DYNO/.venv/bin/python /PATH_TO_YOUR_REPOSITORY/DYNO/Dyno.py`
