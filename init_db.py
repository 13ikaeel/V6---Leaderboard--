from sqlite3 import *
import hashlib


db = connect('db.db')
c = db.cursor()


###################################################################
c.execute('''
	CREATE TABLE IF NOT EXISTS Users(
		id INTEGER PRIMARY KEY NOT NULL,
		username TEXT NOT NULL,
		name TEXT NOT NULL,
    hashedpw TEXT NOT NULL,
    email TEXT NOT NULL,
		avgRP TEXT,
		registration_date TEXT NOT NULL,
    admin INTEGER NOT NULL
	)
''')

###################################################################################
c.execute('''
	CREATE TABLE IF NOT EXISTS Exams(
		id INTEGER PRIMARY KEY NOT NULL,
		type TEXT NOT NULL,
		year TEXT NOT NULL
	)
''')
##########################################################################
c.execute('''
	CREATE TABLE IF NOT EXISTS Paper(
		id INTEGER PRIMARY KEY NOT NULL,
		subject TEXT NOT NULL,
		examID INTEGER NOT NULL REFERENCES EXAMS(id)
	)
''')
##################################################################################
c.execute('''
	CREATE TABLE IF NOT EXISTS UserGrade(
		id INTEGER PRIMARY KEY NOT NULL,
		grade INTEGER NOT NULL,
		paperID INTEGER NOT NULL REFERENCES Paper(id),
		usersID INTEGER NOT NULL REFERENCES Users(id)
	)
''')
#####################################################################
c.execute('''
	CREATE TABLE IF NOT EXISTS	RankPoints(
		id INTEGER PRIMARY KEY NOT NULL,
		usersID INTEGER NOT NULL REFERENCES Users(id),
		examID INTEGER NOT NULL REFERENCES EXAM(id),
		rp INTEGER NOT NULL,
		date TEXT NOT NULL
	)
''')

#########################################################
c.execute('''
	CREATE TABLE IF NOT EXISTS JCs(
		id INTEGER PRIMARY KEY NOT NULL,
		name TEXT NOT NULL
	)
''')

file = open('jcs.csv')
jcs = []
for name in file:
	jcs.append(name.strip())

for name in jcs:
	c.execute('''
		INSERT INTO JCs (name)
		VALUES (?)
	''',(name,))

db.commit()
db.close()
####################################################
