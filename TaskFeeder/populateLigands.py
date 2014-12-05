#!/usr/bin/python
import MySQLdb
import sys
import os
import getopt

host = '127.0.0.1'
user = ''
passwd = ''
db = ''

# idligands name pdb dataset

def populate(path, dataset, cursor, conn):
        listing = os.listdir(path)
        done = len(listing)
        current = 0
        for infile in listing:
                try:    
                    data = open(path + "/" + infile, "r")
                    ligandBlob = data.read()
                    data.close()
                    sql = "INSERT INTO ligands VALUES(0, %s, %s, %s)"
                    cursor.execute(sql, (MySQLdb.escape_string(infile.split(".")[0]), ligandBlob, dataset))
                    conn.commit()

                    print '{0} -- {1}\r'.format(int(float(current)/float(done)*100), str(current)+"/"+str(done)),
                    sys.stdout.flush()
                    current += 1

                except Exception, e:
                    print e
                    cursor.close()
                    conn.close()
                    sys.exit(1)

def start(path, dataset):
	try:
		conn = MySQLdb.connect(host, user, passwd, db);
		cursor = conn.cursor()

		#sql = "TRUNCATE ligands"
		#cursor.execute(sql)
		#conn.commit()

		populate(path, dataset, cursor, conn)
        
		cursor.close()
		conn.close()
		print "Done!"

	except Exception, e:
		print e
		sys.exit(1)

def main(argv):
	path = ''
	dataset = ''

	try:
		opts, args = getopt.getopt(argv,"hp:d:",["path=","dataset="])
	except getopt.GetoptError:
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-p", "--path"):
			if arg[-1] == '/':
				path = arg
			else:
				path = arg+'/'
		elif opt in ("-d", "--dataset"):
			dataset = arg

	if path=='' or dataset=='':
		print "-p --path -d --dataset"
		sys.exit(2)
		
	start(path, dataset)

if __name__ == "__main__":
   main(sys.argv[1:])
