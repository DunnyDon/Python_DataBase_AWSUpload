# PythonFileSearch
Searches file for specific details and logs entries into database to make future searches quicker
Works on the basis that each block of data refers to one product

Developped on Python 2.7.1.1
https://www.python.org/downloads/

Need SQLite installed on machine for script to create Tables and log entries
http://www.tutorialspoint.com/sqlite/sqlite_installation.htm

If you are planning to use the live system. Then you will need to down load and install all the dependencies for the python watchdog package. Instructions can be found at 
http://pythonhosted.org/watchdog/installation.html#installation

-----------------------------------------------------------------

Running script to fill database

-> Enter directory of where to look for processhistory.log files and add to database

Running Script to search database and file location

->Enter Camera ID when asked 

->If it is not in the database then enter directory that must be searched for it

->If it is found at any point the Worknumber and Location of files relating to that camera will be returned

---------------------------------------------------------------

Filling Database

-> Run script and specify directory to gather data from

--------------------------------------------------------------

Live System

-> Specify The directory to monitor, changes will only be 'noticed' once a file has been created or saved.
-> If a log file is already processed, Only new entries in the log file made will be logged
-> If a new file (.bmp) is added to the file however the script won't add it to the database at this point
-> IF a new logfile is created then all entries will be logged
