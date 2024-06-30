from flask import *
from sqlite3 import *
from hashlib import *
import random
import yagmail
from datetime import *
from csv import *
from tools import *


def calc_sha256_salted(data):
    data = 'mypersonal' + str(data) + 'website'
    if isinstance(data,str):
        data = data.encode()
    return sha256(data).hexdigest()


app = Flask(__name__)
app.secret_key = 'gradaholic2024mikaeel'
##########################################################################################
@app.route('/',methods=['GET','POST'])
def index():
	return render_template('index.html')


#############################################################################################
@app.route('/register-pesonal-details',methods=['POST','GET'])
def register_personal_details():
	email = request.form.get('email')
	print('email:',email)
 	
	db = connect('db.db')
	c = db.cursor()
	c.execute('''
		SELECT * FROM Users
		WHERE email = ?
	''', (email,))
	duplicate = bool(c.fetchone())
	db.close()
	if duplicate:
		flash('Email has already been used. Login instead')
		return redirect(url_for('index'))
	else:
		return render_template('register-personal-details.html',email=email)
	


#########################################################################################
	
@app.route('/signin',methods=["POST","GET"])
def signin():
	return render_template('signin.html')



############################################################################################
@app.route('/profile',methods=["POST","GET"])
def profile():
	if request.method=="GET":
		username = session.get('username')
		db = connect('db.db')
		c = db.cursor()
		c.execute('''
			SELECT id FROM Users
			WHERE username=?
		''',(username,))
		userid = c.fetchone()[0]
		avgrp = session.get('avgrp')


		c.execute('''
			SELECT COUNT(grade) FROM UserGrade
			WHERE grade=? AND usersID=?
		''',('A',userid))
		distinctions=c.fetchone()[0]

		c.execute('''
			SELECT COUNT(grade) FROM UserGrade
			WHERE grade IN ('S','U') AND usersID=?
		''',(userid,))
		failures=c.fetchone()[0]

		c.execute('''
			SELECT COUNT(usersID) FROM RankPoints
			WHERE usersID=?
		''',(userid,))
		submissions=c.fetchone()[0]

		c.execute('''
			SELECT registration_date FROM Users
			WHERE id=?
		''',(userid,))
		date=c.fetchone()[0]

		c.execute('''
			SELECT rp, type, date FROM RankPoints,Exams
			WHERE usersID=? And examID=exams.id
			ORDER BY date DESC
			LIMIT 20
		''',(userid,))
		history = c.fetchall()

		c.execute('''
			SELECT grade from UserGrade
			WHERE usersID=?
		''',(userid,))
		grades = c.fetchall()
		print("grades:",grades)
		if len(grades) == 0:
			mode_grade = 'None'
		else:
			grades = modal_grade(grades)
			mode_grade = ""
			for grade in grades:
				mode_grade += grade[0]+", "
			mode_grade = mode_grade[:len(mode_grade)-2]

		print('mode_grade:',mode_grade)

		if submissions==0:
			national_ranking = 'None'
		else:
			c.execute('''
				SELECT COUNT(id) FROM Users
				WHERE avgRP > ?
			''',(avgrp,))
			national_ranking = c.fetchone()[0] + 1
		db.close()
		return render_template('profile.html', username=username, school_rank='NIL', national_ranking=national_ranking, avgrp=avgrp, mode_grade=mode_grade, distinctions=distinctions, failures=failures, submissions=submissions, date=date[:10], rank='NIL', history=history)
	
	prevpage = request.form.get('currpage')
	print('prevpage:',prevpage)

	if prevpage == 'login':
		username = request.form.get("username")
		session['username'] = username
		pw = request.form.get("pw")
		hashpw = calc_sha256_salted(pw)
		print((username,pw,hashpw))
		db = connect('db.db')
		c = db.cursor()
		c.execute('''
			SELECT * FROM Users
			WHERE username = ? AND hashedpw=?
		''',(username,hashpw))
		valid = c.fetchone()
		print('valid:',valid)
		db.close()
		print(username)

		if valid!=None:
			db = connect('db.db')
			c = db.cursor()
			c.execute('''
				SELECT id FROM Users
				WHERE username=?
			''',(username,))
			userid = c.fetchone()[0]
			session['userid'] = userid
			c.execute('''
			SELECT rp FROM RankPoints
			WHERE usersID=?
			''',(userid,))
			rp_list = c.fetchall()
			avgrp = avg_rp(rp_list)
			session['avgrp'] = avgrp

			c.execute('''
				SELECT COUNT(grade) FROM UserGrade
				WHERE grade=? AND usersID=?
			''',('A',userid))
			distinctions=c.fetchone()[0]
			session['distinctions'] = distinctions

			c.execute('''
				SELECT COUNT(grade) FROM UserGrade
				WHERE grade IN ('S','U') AND usersID=?
			''',(userid,))
			failures=c.fetchone()[0]
			session['failures'] = failures

			c.execute('''
				SELECT COUNT(usersID) FROM RankPoints
				WHERE usersID=?
			''',(userid,))
			submissions=c.fetchone()[0]
			session['submissions'] = submissions

			c.execute('''
				SELECT registration_date FROM Users
				WHERE id=?
			''',(userid,))
			date=c.fetchone()[0]

			c.execute('''
				SELECT rp, type, date FROM RankPoints,Exams
				WHERE usersID=? And examID=exams.id
				ORDER BY date DESC
				LIMIT 20
			''',(userid,))
			history = c.fetchall()

			c.execute('''
			SELECT grade from UserGrade
			WHERE usersID=?
		''',(userid,))
			grades = c.fetchall()
			print("grades:",grades)

			if len(grades) == 0:
				mode_grade = 'None'
			else:
				grades = modal_grade(grades)
				mode_grade = ""
				for grade in grades:
					mode_grade += grade[0]+", "
				mode_grade = mode_grade[:len(mode_grade)-2]

			if submissions>0:
				c.execute('''
				SELECT COUNT(id) FROM Users
				WHERE avgRP > ?
				''',(avgrp,))
				national_ranking = c.fetchone()[0] + 1
			else:
				national_ranking = 'none'	

			db.close()
			return render_template('profile.html', username=username, school_rank='NIL', national_ranking=national_ranking, avgrp=avgrp, mode_grade=mode_grade, distinctions=distinctions, failures=failures, submissions=submissions, date=date[:10], rank='NIL',history=history)
		else:
			flash('Invalid Username/Password')
			return redirect(url_for('signin'))
		
		
	# elif prevpage == 'register-personal-details':
	username = request.form.get('username')
	name = request.form.get('name')
	pw = request.form.get('pw')
	rpw = request.form.get('rpw')
	hashpw = calc_sha256_salted(pw)
	# email = session.get('email')
	email = request.form.get('email')
	date_time=str(datetime.now())

	print((username,name,pw,email,date_time,0))
	if pw!=rpw:
		flash('Passwords do not match')
		return redirect(url_for('register_personal_details'))
	
	db = connect('db.db')
	c = db.cursor()
	c.execute('''
		SELECT * FROM USERS WHERE username=?
	''',(username,))
	duplicate = c.fetchone()
	print("duplicate: ",duplicate)
	if duplicate!=None:
		flash('Username taken')
		db.close()
		return redirect(url_for('register_personal_details'))
	
	print('hi')
	c.execute('''
		INSERT INTO Users (username,name,hashedpw,email,registration_date,admin) 
		VALUES(?,?,?,?,?,?)
	''', (username,name,hashpw,email,date_time,0))

	db.commit()
	db.close()

	flash('Account Created Successfully')
	return redirect(url_for('signin'))

###########################################################################
@app.route('/add',methods=["POST","GET"])
def add():
	file = open('h2-subjects.csv')
	h2_subjects = []
	for subject in file:
			h2_subjects.append(subject.strip())
	session['h2_subjects'] = h2_subjects

	file = open('h2-subjects.csv')
	h1_subjects = []
	for subject in file:
			h1_subjects.append(subject.strip())
	session['h1_subjects'] = h1_subjects
	username = session.get('username')
	return render_template('add.html',username=username,h2=h2_subjects,h1=h1_subjects)

@app.route('/add-success',methods=["POST","GET"])
def addsuccess():
	year = str(datetime.now())[:4]
	message="Grades Added"
	username = session.get('username')
	examtype = request.form.get('examtype')
	
	h2_1 = request.form.get('h2_1_grade')
	h2_2 = request.form.get('h2_2_grade')
	h2_3 = request.form.get('h2_3_grade')
	h2_h1 = request.form.get('h2_h1')
	gp = request.form.get('gp')
	pw = request.form.get('pw')
	grades = [h2_1,h2_2,h2_3,h2_h1,gp,pw]

	sub1 = request.form.get('h2_1')
	sub2 = request.form.get('h2_2')
	sub3 = request.form.get('h2_3')
	sub4 = request.form.get('h2or1')
	sub5 = 'gp'
	sub6 = 'pw'
	subjects = [sub1,sub2,sub3,sub4,sub5,sub6]

	print(grades)
	print(subjects)
	db = connect('db.db')
	c = db.cursor()
	c.execute('''
		INSERT INTO Exams (type,year)
		VALUES (?,?)
	''', (examtype,year))
	print('examtype:',examtype)
	print('year:',year)
	
	c.execute('''
		SELECT id FROM Exams 
		WHERE type=? and year=?
	''',(examtype,year))
	examid = c.fetchone()[0]

	c.execute('''
		SELECT id FROM Users
		WHERE username=?
	''',(username,))
	userid = c.fetchone()[0]
	print('userid:',userid)


	for i in range(0,len(subjects)):
		c.execute('''
			INSERT INTO Paper (subject,examID)
			VALUES (?,?)
		''',(subjects[i],examid))

		c.execute('''
			SELECT id FROM Paper
			WHERE subject=?
		''',(subjects[i],))
		paperid=c.fetchone()[0]


		c.execute('''
			INSERT INTO UserGrade (grade, paperID, usersID)
			VALUES (?,?,?)
		''',(grades[i],paperid,userid))


	h1dict = {'A':10,'B':8.75,'C':7.5,'D':6.25,'E':5,'S':2.5,'U':0}
	h2dict = {'A':20,'B':17.5,'C':15,'D':12.5,'E':10,'S':5,'U':0}
	total_rp = h1dict[gp]+h1dict[pw]+h1dict[h2_h1]+h2dict[h2_1]+h2dict[h2_2]+h2dict[h2_3]

	c.execute('''
		INSERT INTO RankPoints (usersID,examID,rp,date)
		VALUES (?,?,?,?)
	''',(userid,examid,total_rp,str(datetime.now())[:10]))


	c.execute('''
			SELECT rp FROM RankPoints
			WHERE usersID=?
	''',(userid,))
	rp_list = c.fetchall()
	avgrp = avg_rp(rp_list)
	print('avgrp(type):',type(avgrp))
	print('avgrp:',avgrp)
	if isinstance(avgrp,tuple):
		avgrp=avgrp[0]
	
	session['avgrp'] = avgrp
	print(avgrp)

	c.execute('''
		UPDATE Users
		SET avgRP = ?
		WHERE id = ?
	''', (avgrp, userid))


	db.commit()
	db.close()
	
	return render_template('add.html',message=message,username=username,h2=session.get('h2_subjects'),h1=session.get('h1_subjects'))

##############################################################################
@app.route('/leaderboard',methods=['GET'])
def leaderboard():
	username = session.get('username')
	lb = [] #list of tuples
	db = connect('db.db')
	c = db.cursor()
	# userid = session.get('useid')
	c.execute('''
    SELECT username, avgRP, ROW_NUMBER() OVER (ORDER BY avgRP DESC) AS rank
    FROM Users
    ORDER BY avgRP DESC
    LIMIT 50
	''')
	rankings = c.fetchall()
	print(rankings)
	db.close()


	return render_template('leaderboard.html',username=username, rankings=rankings)
##############################################################################
@app.route('/notifications',methods=['GET'])
def notifications():
	username = session.get('username')
	return render_template('notifications.html',username=username)
#########################################################################
@app.route('/settings',methods=['GET'])
def settings():
	username = session.get('username')
	return render_template('settings.html',username=username)
###############################################################################
@app.route('/help', methods=["GET"])
def help():
	username = session.get('username')
	return render_template('help.html',username=username)


if __name__ == '__main__':
	app.run(debug=True,port=5055)
