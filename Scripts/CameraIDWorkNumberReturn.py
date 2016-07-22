import re
import os
r = re.compile('WORK NUMBER|CAMERA ID')
os.chdir("D:")
print("Everything entered needs to be surrounded by \"\"")
root=input("Please Enter Directory you wish to search:")
cameraid= input("Please enter the Camera ID:")
storage=[]
i=0
count=0
counter=0
checkvar=0
print("Looking for Camera ID")
# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk(root):
	for FILENAME in files:
		#make sure file is a log file and is called ProcessHistory
		if FILENAME.endswith('.log') and FILENAME.startswith('Process'):
			fd = open(root+"\\"+FILENAME, 'r')
			#print(FILENAME)
			#open it with read only privilages
			for line in fd:
				if r.search(line):
					storage.insert(i,line)
					#save temporarily camera id and work number hits
					i+=1
					counter+=1
					if cameraid in line:
						#if the uesr inputted cameras id is found print out that and the associated worknumber 
						print("Camera ID Found!")
						print(line)
						checkvar=1
						count=counter
					if count == counter-1 and count!=0 and "CAMERA ID" not in storage[i-3]: 
						print(storage[i-3])
						print(root+FILENAME)
						print(os.path.dirname(FILENAME))
						
						#check that the pervious value saved is the last work number in the file
					#else:
						#print ("No Work number associated with that Camera ID")
				if i>8 :
					del storage[i-4]
					i-=1
					#after 4 matches it can be assumed that the previous ones are not the ones being searched for and can be deleted
			fd.close()
if checkvar==0:
	print("Camera ID not found!")
