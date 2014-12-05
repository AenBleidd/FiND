import MySQLdb
import sys
import os

host = '127.0.0.1'

try:
    conn = MySQLdb.connect(host, "boinc", "boinc", "fmah")
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE tasks")
    conn.commit()
    
except Exception, e:
    print e
    sys.exit(1)
    
cursor.close()
conn.close()

try:
    conn = MySQLdb.connect(host, "boinc", "boinc", "boinc")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE workunit")
    cursor.execute("TRUNCATE result")
    conn.commit()
    
except Exception, e:
    print e
    sys.exit(1)
    
cursor.close()
conn.close()
print "Done!"