import MySQLdb
import sys
import os

host = '127.0.0.1'
user = 'boinc'
passwd = 'boinc'
db = 'fmah'


try:
    conn = MySQLdb.connect(host, user, passwd, db);
    cursor = conn.cursor()
    
    sql = "TRUNCATE receptors"
    cursor.execute(sql)
    conn.commit()
    
    path = '/home/oxis/workspace/cpp_project/boinc/PDB_Xray_rec_fixed_configs/'
    listing = os.listdir(path + "fixed/pdbqt")
    
    confs = []
    receptors = []
    for infile in listing:
    	try:
            receptor = infile.split(".")[0]
            conf = receptor + ".config"

            f = open(path + "fixed/pdbqt/" + receptor + ".pdbqt", "r")
            receptorBlob = f.read()
            f.close()
            
            f = open(path + "config/" + conf, "r")
            confBlob = f.read()
            f.close()
    
            sql = "INSERT INTO receptors VALUES(0, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (receptor, receptorBlob, conf.split(".")[0]+"_conf", confBlob, 0, "plop", 0))
            conn.commit()
    		
    	except Exception, e:
    	    print "Error: cannot import receptor"
            print e

    cursor.close()
    conn.close()
    print "Done!"

except Exception, e:
    print e
    sys.exit(1)
	
