import MySQLdb
import sys
import os

host = '127.0.0.1'
user = 'boinc'
passwd = 'boinc'
db = 'fmah'

def populate(path, cursor, conn):
        dataset = "plop"
        listing = os.listdir(path)
        for infile in listing:
                try:    
                    data = open(path + "/" + infile, "r")
                    ligandBlob = data.read()
                    data.close()
                    sql = "INSERT INTO ligands VALUES(0, %s, %s, %s)"
                    cursor.execute(sql, (MySQLdb.escape_string(infile.split(".")[0]), ligandBlob, dataset))
                    conn.commit()
                        
                except Exception, e:
                    print e
                    cursor.close()
                    conn.close()
                    sys.exit(1)

try:
        conn = MySQLdb.connect(host, user, passwd, db);
        cursor = conn.cursor()

        sql = "TRUNCATE ligands"
        cursor.execute(sql)
        conn.commit()

        populate("/home/oxis/workspace/cpp_project/boinc/Pfal_Xray_ligs_taut_pdbqt/", cursor, conn)
        
        cursor.close()
        conn.close()
        print "Done!"

except Exception, e:
    print e
    sys.exit(1)
