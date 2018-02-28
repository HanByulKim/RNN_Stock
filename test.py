import psycopg2 as pg2
import sys

print("PSYCOPG2 VERSION : " + pg2.__version__)
conn = None

try:
	conn = pg2.connect("host=localhost dbname=testdb user=shinestar password=rlagks30")
	print("PSYCOPG2 : DB connect ok")

	cur = conn.cursor();
	cur.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, Name VARCHAR(20), Price INT)")

	cur.execute("INSERT INTO test VALUES(1,'Milk',5)")
	cur.execute("INSERT INTO test VALUES(2,'Sugar',7)")
	cur.execute("INSERT INTO test VALUES(3,'fuck',10)")

	cur.execute("SELECT * FROM test;")
	print(cur.fetchone())

	conn.commit()
	cur.close()
	conn.close()

except pg2.DatabaseError as e:
	if conn:
		conn.rollback()
	print("ERROR %s" % e)
	sys.exit(1)

finally:
	if conn:
		conn.close()

