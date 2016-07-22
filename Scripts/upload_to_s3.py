import boto, re, os, threading,time
from multiprocessing.pool import ThreadPool
bucketname = 'place name here'
links = []
	
def upload_file (root, url_root,filename):
	from boto.s3.connection import S3Connection
	c = S3Connection('Public', 'Secret')
	b = c.get_bucket(bucketname) # substitute your bucket name here
	from boto.s3.key import Key
	k = Key(b)
	k.key = os.path.join(url_root,filename)
	k.set_contents_from_filename(root+filename)
	url = k.generate_url(expires_in=0, query_auth=False)
	tua_url = url.replace('https://'+bucketname+'.s3.amazonaws.com/', '')
	global links
	#if not tua_url in links:
	links.append(tua_url)
        #        else:
        #               print "Duplicate ", tua_url
        return tua_url
	

def thread_upload (directory, url_directory, imagefiles):
	threads=[]
	num_limit = 675
	div = len(imagefiles)
	index = 0
	count = 0
	for fname in imagefiles:
                t = threading.Thread(target = upload_file, args=(directory, url_directory, fname,))
		threads.append(t)
        for thre in threads:
                index= index + 1
                thre.start()
                if(index%num_limit==0):
                        for x in threads[count:index]:
                                x.join()
                                #print threading.activeCount()                                
                        count = index
        while(len(links)<div):
                time.sleep(.1)
        return links
	
	

 

