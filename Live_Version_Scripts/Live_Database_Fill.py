######################################## 
#      Conor Donohue IT		           #
#                                      #
#	Fills Database with Camera Info    #
########################################


import sqlite3, os, re, sys, time
r = re.compile("WORK NUMBER|CAMERA ID")
storage=[]
filestorage=[]
database_name = "Testing.db"
def filldatabase(root):
	db = sqlite3.connect(database_name)
	cursor = db.cursor()
	cursor.execute('''PRAGMA synchronous=OFF''')
	cursor.execute('''PRAGMA cache_size=100000''')
	cursor.execute('''BEGIN TRANSACTION''')	
	
	i=0
	count=0
	check=0
	for root, dirs, files in os.walk(root):
		for FILENAME in files:
			#make sure file is a log file and is called ProcessHistory
			if FILENAME.endswith('.log') and FILENAME.startswith('ProcessHistory'):
				check = searchlogs(root)
				with open(root+"\\"+FILENAME, 'r', 32768) as fd:
					if check == 0:
						#open it with read only privilages
						for line in fd:
							if r.search(line):
								temp=line.strip().split('\t')
								storage.insert(i,temp[2])
								i+=1
								if i>2 and "C" not in storage[i-3] and "N" not in storage[i-3]:
									cursor.execute('''INSERT INTO processhistory(camera, worknum) VALUES(?,?)''', ((storage[i-2]), (storage[i-3])))
									db.commit()
									write_to_log_d_or_b("From File "+root+"\\"+FILENAME+" "+storage[i-2]+" and "+storage[i-3] +" were added To Processhistory Table") 
									filesearch(root, storage[i-3])	
								if i>=6 :
									del storage[i-6]
									i-=1
									#after 4 matches it can be assumed that the previous ones are not the ones being searched for and can be deleted
						cursor.execute('''INSERT INTO logsprocessed(directory) VALUES(?)''', (root,))
						cursor.execute('''INSERT INTO processhistory(camera, worknum) VALUES(?,?)''', ((storage[i-1]), (storage[i-2]),))
						db.commit()
						write_to_log_d_or_b("From File "+root+"\\"+FILENAME+" "+storage[i-1]+" and "+storage[i-2] +" were added To Processhistory Table")
						filesearch(root, storage[i-2])
						#The last entry in the last log file of a date seemed to be missed hence why the above 4 lines are here
						#This causes a duplicate entry in some cases (<<1%) but ensures no files are missed
						write_to_log_d_or_b("Finished processing "+root+"\\"+FILENAME)
						write_to_log_d_or_b("-----------------------------------------------------------------------------\n\n")
					else:		#must check for new entries
						write_to_log_d_or_b("-----------------------------------\n\n"+"Log file "+ root+" has already been processed"+"\n\n-----------------------------------\n\n")
						#with open(root+"\\"+FILENAME, 'r', 32768) as fd:
						#open it with read only privilages
						for line in fd:
							if r.search(line):
								temp=line.strip().split('\t')
								storage.insert(i,temp[2])
								i+=1
								#for values in all_values:
								if i>2 and "C" not in storage[i-3] and "N" not in storage[i-3] :
									cursor.execute('''SELECT camera, worknum FROM processhistory WHERE worknum = ? AND camera = ?''', ((storage[i-3]),(storage[i-2])))
									all_values=cursor.fetchall()
									#print(all_values, len(all_values))
									if len(all_values)==0:
										print "in here"
										cursor.execute('''INSERT INTO processhistory(camera, worknum) VALUES(?,?)''', ((storage[i-2]), (storage[i-3])))
										db.commit()
										write_to_log_d_or_b("From File "+root+"\\"+FILENAME+" "+storage[i-2]+" and "+storage[i-3] +" were added To Processhistory Table") 
										filesearch(root, storage[i-3])	
								if i>=6 :
									del storage[i-6]
									i-=1
									#after 4 matches it can be assumed that the previous ones are not the ones being searched for and can be deleted
						cursor.execute('''SELECT camera, worknum FROM processhistory WHERE worknum = ? AND camera = ?''', ((storage[i-3]),(storage[i-2])))
						all_values=cursor.fetchall()
						#print(all_values, len(all_values))
						if len(all_values)==0:
							cursor.execute('''INSERT INTO logsprocessed(directory) VALUES(?)''', (root,))
							cursor.execute('''INSERT INTO processhistory(camera, worknum) VALUES(?,?)''', ((storage[i-1]), (storage[i-2]),))
							db.commit()
							write_to_log_d_or_b("From File "+root+"\\"+FILENAME+" "+storage[i-1]+" and "+storage[i-2] +" were added To Processhistory Table")
							filesearch(root, storage[i-2])
							#The last entry in the last log file of a date seemed to be missed hence why the above 4 lines are here
							#This causes a duplicate entry in some cases (<<1%) but ensures no files are missed
						write_to_log_d_or_b("Finished processing "+root+"\\"+FILENAME)
						write_to_log_d_or_b("-----------------------------------------------------------------------------\n\n")
				del filestorage[:]
				count=0
			else:
				filestorage.insert(count, FILENAME)
				count+=1
	db.commit()
	db.close()
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
	cursor.execute('''create table if not exists processhistory(id INTEGER, camera TEXT , worknum TEXT, PRIMARY KEY(id ASC)) ''')
	cursor.execute('''create table if not exists filelocation(idnum INTEGER, filelocate TEXT, FOREIGN KEY (idnum) REFERENCES processhistory(id))''')
	db.commit()
	db.close()
	
	return;

def filesearch(rootdir, wnum):
	db = sqlite3.connect(database_name)
	cursor = db.cursor()
	cursor.execute('''PRAGMA synchronous=OFF''')
	cursor.execute('''PRAGMA cache_size=100000''')
	cursor.execute('''BEGIN TRANSACTION''')	
	
	for file in filestorage:
		#search the folder in where the work number was found in the processhistory.log
		if wnum in file:
			#search to find the files with the worknumber in the fiel name
			cursor.execute('''SELECT id FROM processhistory  WHERE worknum= ? ''', (wnum,))
			#get the unique id in the processhistory table that corresponds to the worknumber
			all_values=cursor.fetchall()
			varia='{0}'.format(all_values[0]).strip("[()]").strip(",")
			#get the row from the table and see if the worknumber is in it
			cursor.execute('''INSERT INTO filelocation(idnum, filelocate) VALUES(?,?)''', (str(varia), rootdir+"\\"+file))
			write_to_log_d("Id "+str(varia)+" and "+rootdir+"\\"+file+"  were added To filelocation Table")
			#add the file to the new table containing the unique ids and the files with the worknumber in them
	db.commit()
	db.close()
	return;


	
#Check to see if this logfile has already been processed	
def searchlogs(directory_path):
	db = sqlite3.connect(database_name)
	cursor = db.cursor()
	cursor.execute('''PRAGMA synchronous=OFF''')
	cursor.execute('''PRAGMA cache_size=100000''')
	cursor.execute('''BEGIN TRANSACTION''')	
	logs = []
	#adds all folders which do not have a subdirectory to a list bar the camera retest folder. The parent of it is added so as to ensure any file aren't missed
	cursor.execute('''SELECT directory FROM logsprocessed ''')
	logs = cursor.fetchall()
	for dirs in logs:
		dirsfound='{0}'.format(dirs[0])
		if directory_path == dirsfound:
			db.close()
			print("Log already processed")
			return 1;		#if found return 1
	db.close()
	return 0;
	

#Log information about the filling up of the database
def write_to_log(information):
	#get the current time of and log this also
	localtime = time.asctime( time.localtime(time.time()) )
	try:
		with open('DataBaseLogFile.log', 'a') as logfile:			
			if "-------" not in information:		#This is used to try and help seperate out the logging of the ProcessHistory logfiles in newly created logfile
				logfile.write(localtime+" "+information+"\n")
			else :
				logfile.write(information+"\n")				
	except IOError:
		print("There was an error writing to the LogFile")
		sys.exit(0)
		#exit script if unable to open logfile
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

def start(rootdirectory):
	starting_dir=rootdirectory
	#go throught each folder in the list and add to the database
	db = sqlite3.connect(database_name)
	cursor = db.cursor()
	cursor.execute('''PRAGMA synchronous=OFF''')
	cursor.execute('''PRAGMA cache_size=100000''')
	cursor.execute('''BEGIN TRANSACTION''')	
	filldatabase(starting_dir)
	db.commit()
	db.close()
##############################
# The script is begins here  #
#                            #
##############################
user_defined_log_level='d'
create_databases_if_not_exist()
if __name__ == '__main__':
	create_databases_if_not_exist()	
	
	


##################
# End of Script  #
##################	
