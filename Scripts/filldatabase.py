########################################
#      Conor Donohue IT Tuam		   #
#                                      #
#	Fills Database with Camera Info    #
########################################


import sqlite3, os, re, sys, time, cProfile, pstats, StringIO, zipfile, upload_to_s3
pr = cProfile.Profile()
pr.enable()
r = re.compile("WORK NUMBER|CAMERA ID")
worknumbers=[]
storage=[]
filestorage=[]
directories=[]
database_name = "C:\Users\Public\Camera_Data.db"
starting_dir=raw_input("Enter Root Directory:")
def filldatabase(root):
	i=0
	count=0
	check=0
	for root, dirs, files in os.walk(root):
		for FILENAME in files:
			#make sure file is a log file and is called ProcessHistory
			if FILENAME.endswith('.zip') and FILENAME.startswith('ProcessHistory'):
				check = searchlogs(root)
				if check == 0:
					#open it with read only privilages
					zfile = zipfile.ZipFile(root+"\\"+'ProcessHistory.zip', mode='r')
					for finfo in zfile.infolist():
						ifile = zfile.open(finfo)
						for line in ifile:
							if r.search(line):
								temp=line.strip().split('\t')
								storage.insert(i,temp[2])
								i+=1
								if i>2 and "C" not in storage[i-3] and "N" not in storage[i-3]:
									cursor.execute('''INSERT OR REPLACE INTO processhistory(camera, worknum) VALUES(?,?)''', ((storage[i-2]), (storage[i-3])))
									write_to_log_d_or_b("From File "+root+"\\"+FILENAME+" "+storage[i-2]+" and "+storage[i-3] +" were added To Processhistory Table") 
									#filesearch(root, storage[i-3])
									worknumbers.append(storage[i-3])
								if i>=6 :
									del storage[i-6]
									i-=1
									#after 4 matches it can be assumed that the previous ones are not the ones being searched for and can be deleted
						if i>2 and "C" not in storage[i-2] and "N" not in storage[i-2]:
							cursor.execute('''INSERT INTO logsprocessed(directory) VALUES(?)''', (root,))
							cursor.execute('''INSERT OR REPLACE INTO processhistory(camera, worknum) VALUES(?,?)''', ((storage[i-1]), (storage[i-2]),))
							write_to_log_d_or_b("From File "+root+"\\"+FILENAME+" "+storage[i-1]+" and "+storage[i-2] +" were added To Processhistory Table")
							#filesearch(root, storage[i-2])
							worknumbers.append(storage[i-2])
							#The last entry in the last log file of a date seemed to be missed hence why the above 4 lines are here
							#This causes a duplicate entry in some cases (<<1%) but ensures no files are missed
							#This should be resolved now
						write_to_log_d_or_b("Finished processing "+root+"\\"+FILENAME)
					write_to_log_d_or_b("-----------------------------------------------------------------------------\n\n")
					filestorage.insert(count, FILENAME)
					links=upload_file(root, filestorage)
					filesearch(worknumbers,links)
				else:
					write_to_log_d_or_b("-----------------------------------\n\n"+"Log file "+ root+" has already been processed"+"\n\n-----------------------------------\n\n")
				del filestorage[:]
				count=0
			else:
				filestorage.insert(count, FILENAME)
				count+=1
	return;
	
	
def create_databases_if_not_exist():
	# if the tables do not exist create them and set sql variables to speed up the process
	db = sqlite3.connect(database_name)
	cursor = db.cursor()
	cursor.execute('''PRAGMA synchronous=OFF''')
	cursor.execute('''PRAGMA cache_size=100000''')
	cursor.execute('''PRAGMA page_size = 4096''')
	cursor.execute('''BEGIN TRANSACTION''')	
	cursor.execute('''create table if not exists logsprocessed(indexoffiles INTEGER, directory TEXT, PRIMARY KEY(indexoffiles ASC))''')
	cursor.execute('''create table if not exists processhistory(id INTEGER, camera TEXT, worknum TEXT UNIQUE, PRIMARY KEY(id ASC)) ''')
	cursor.execute('''create table if not exists filelocation(idnum INTEGER, filelocate TEXT, FOREIGN KEY (idnum) REFERENCES processhistory(id))''')
	db.commit()
	db.close()
	
	return;

def filesearch(wnumbers, links):
		#search the folder in where the work number was found in the processhistory.log
        links.sort()
	for wnum in wnumbers:
                for url_link in links:
                        if wnum in url_link:
				#search to find the files with the worknumber in the fiel name
				cursor.execute('''SELECT id FROM processhistory  WHERE worknum= ? ''', (wnum,))
				#get the unique id in the processhistory table that corresponds to the worknumber
				all_values=cursor.fetchall()
				try:
                                        varia='{0}'.format(all_values[0]).strip("[()]").strip(",")
                                        #get the row from the table and see if the worknumber is in it
                                        cursor.execute('''INSERT OR REPLACE INTO filelocation(idnum, filelocate) VALUES(?,?)''', (str(varia), url_link))			
                                        write_to_log_d("Id "+str(varia)+" and "+url_link+"  were added To filelocation Table")
                                        #add the s3 url of the file to the new table containing the unique ids
                                except IndexError:
                                        print wnum, url_link
                                        f = open('C:\Users\Public\ERRORS.log', 'a')
                                        f.write(wnum+url_link)
        return;


def upload_file(root, filestorage):
	root = convertPath(root)+'/'
	drive_index = root.find('Archive')
	url_root = 'TUA1/'+root[drive_index+8:]
	url_link = upload_to_s3.thread_upload(root,url_root,filestorage)
	return url_link;
	
def convertPath(path):
 	# Convert windows, mac path to unix version.
	separator = os.path.normpath("/")
	if separator != "/":
		path = re.sub(re.escape(separator), "/", path)
	return path
	
	
#Check to see if this logfile has already been processed	
def searchlogs(directory_path):
	logs = []
	#adds all folders which do not have a subdirectory to a list bar the camera retest folder. The parent of it is added so as to ensure any file aren't missed
	cursor.execute('''SELECT directory FROM logsprocessed where directory = ? ''', (directory_path,))
	logs = cursor.fetchall()
	for dirs in logs:
		if directory_path in dirs:
			return 1;		#if found return 1
	return 0;
	

#Log information about the filling up of the database
def write_to_log(information):
	#get the current time of and log this also
	localtime = time.asctime( time.localtime(time.time()) )
	try:
		with open('C:\Users\Public\DataBaseLogFile.log', 'a') as logfile:			
			if "-------" not in information:		#This is used to try and help seperate out the logging of the ProcessHistory logfiles in newly created logfile
				logfile.write(localtime+" "+information+"\n")
			else :
				logfile.write(information+"\n")				
	except IOError:
		print("There was an error writing to the LogFile")
		sys.exit(0)
		#exit script if unable to open logfile
	return;


#Figure out whether the logging level is Detailed Basic or None
def log_level():
	print("Define Logging Level \nD\tDetailed\nB\tBasic\nN\tNone")
	logging_level = raw_input("Choose Logging Level:")	
	if logging_level.lower() == "d":
		return  logging_level.lower();
	elif logging_level.lower() == "b":
		return  logging_level.lower();
	elif logging_level.lower() == "n":
		write_to_log("Database was filled with no logging selected")
		return  logging_level.lower();
	else:
		log_level();
	return;
	
def write_to_log_d_or_b(info):
	if user_defined_log_level.lower() != 'n':
		write_to_log(info)
	return;
#these two functions are used to reduce duplicate code
def write_to_log_d(info):
	if user_defined_log_level == 'd':
		write_to_log(info)
	return;

#In an effort to optimise script All folders which have no subdirectories (bar one case)
# are found and saved to a list in a successful attempt to quicken up the script.

def get_bottom_dirs():
	for dirpath, dirnames, filenames in os.walk(starting_dir+"\\"):
		if dirpath.endswith("Camera Re-Test"):		
			#if the folder with no subdirectory has Camera RE-Test in its path then you save the parent of that folder
			# in an attempt to ensure no files are missed
			directories.append(dirpath[:-15])
		elif not dirnames:
			directories.append(dirpath)
	return;

	
##############################
# The script is begins here  #
#                            #
##############################
create_databases_if_not_exist()
user_defined_log_level=log_level()
get_bottom_dirs()
#go throught each folder in the list and add to the database
for direcs in directories:
	db = sqlite3.connect(database_name)
	cursor = db.cursor()
	cursor.execute('''PRAGMA synchronous=OFF''')
	cursor.execute('''PRAGMA cache_size=100000''')
	cursor.execute('''BEGIN TRANSACTION''')	
	filldatabase(direcs)
	db.commit()
	db.close()


##################
# End of Script  #
##################	
pr.disable()
s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
f = open('C:\Users\Public\Stats.log', 'a')
f.write( s.getvalue())
