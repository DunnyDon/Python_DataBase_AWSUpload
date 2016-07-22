########################################
#      Conor Donohue IT Tuam		   #
#                                      #
#	Searches Database for Camera Info  #
########################################



import re, os, sqlite3, sys
database_name = "C:\Users\Public\Camera_Data.db"

r = re.compile('WORK NUMBER|CAMERA ID')
# traverse root directory, and list directories as dirs and files as files
def searchroot(checkvar):
	i=0
	count=0
	counter=0
	root=raw_input("Please Enter Directory you wish to search:")
	for root, dirs, files in os.walk(root):
		for FILENAME in files:
			#make sure file is a log file and is called ProcessHistory
			if FILENAME.endswith('.log') and FILENAME.startswith('ProcessHistory'):
				with open(root+"\\"+FILENAME, 'r') as fd:
					#open it with read only privilages
					for line in fd:
						if r.search(line):
							temp=line.strip().split('\t')
							storage.insert(i,temp[2])
							#save temporarily camera id and work number hits
							# you have to save the hits as the work number comes before the camera id in the file and if you don't you will have a camera id but no worknum
							i+=1
							counter+=1
							if cameraid in line:
								#if the user inputted cameras id is found print out that and the associated worknumber 
								print("Camera ID Found!")
								checkvar=1
								count=counter
							if count == counter-1 and count!=0 and "C" not in storage[i-3]: 
								#count=counter-1 is checked to ensure that the last value saved was the camera id searched for 
								#count!=0 is checked to ensure that the right camera id was found
								#Have to check for extreme cases such as where work number or camera id are N/A
								print("CameraID: "+storage[i-2])
								print("Work Number: "+storage[i-3])
								print(root)
								#check that the pervious value saved is the last work number in the file
								cursor.execute('''INSERT INTO processhistory(camera, worknum) VALUES(?,?)''', ((storage[i-2]), (storage[i-3])))
								db.commit();
								checkvar=1
								filesearch(root, storage[i-3])
								sys.exit()
								#add camera id to database so it can be found next time
						if i>=6 :
							del storage[i-6]
							i-=1
							#after 4 matches it can be assumed that the previous ones are not the ones being searched for and can be deleted
	if checkvar!=1:
		print ("No Work number associated with that Camera ID")
	return;
				
def searchdatabase(checkvar):
	cursor.execute("SELECT * FROM processhistory WHERE camera= ? ",(cameraid,))
	#select everything from the table
	all_rows = cursor.fetchall()
	for row in all_rows:
		#save each row as a variable and check if there is a match
		#even though there should only be one match looping through covers the remote possibilty of more than one match
		varia='{0} | {1} | {2}'.format(row[0],row[1],row[2])
		if cameraid in varia:
			#this if statement is also just another layer of protection to ENSURE that the correct value is found, it shouldn't be needed though
			print("CameraID Found in database")
			print("\n"+varia)
			checkvar=1
			#set variable to 1 to ensure script is exited
			cursor.execute('''SELECT * FROM filelocation  WHERE idnum= ? ''', (row[0],))
			all_files=cursor.fetchall()
			for file in all_files:
				filesfound='{0} | {1}'.format(file[0],file[1])
				print("\n"+filesfound)
				
	if checkvar!=1:
		print("Camera ID not found in database!")
		print("Database Search not found")
		searchroot(checkvar)
		#if the camera id doesn't exist in the database then check a directory location specified by the user
	return;

def filesearch(rootdir, wnum):
	for file in os.listdir(rootdir):
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
	return;
	
	
def database_exist_check():
	cursor.execute('''create table if not exists processhistory(id INTEGER, camera TEXT , worknum TEXT, PRIMARY KEY(id ASC)) ''')
	cursor.execute('''create table if not exists filelocation(idnum INTEGER, filelocate TEXT, FOREIGN KEY (idnum) REFERENCES processhistory(id))''')
	return;


	
##############################
# The script is begins here  #
#                            #
##############################
cameraid= raw_input("Please enter the Camera ID:")
storage=[]
checkvar=0
db = sqlite3.connect(database_name)
cursor = db.cursor()
cursor.execute('''PRAGMA synchronous=OFF''')
cursor.execute('''PRAGMA cache_size=100000''')
cursor.execute('''BEGIN TRANSACTION''')	
print("Looking for Camera ID")
database_exist_check()
searchdatabase(checkvar)
db.commit()
db.close()
##################
# End of Script  #
##################	