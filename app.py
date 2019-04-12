
from flask import Flask, jsonify, request, render_template
from sqlalchemy.inspection import inspect
from flask_cors import CORS
import datetime
from models import db, User, Auth


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:yarakhuda@127.0.0.1:5432/samlog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.cli.command('resetdb')
def resetdb_command():
	"""Destroys and creates the database + tables."""

	from sqlalchemy_utils import database_exists, create_database, drop_database
	if database_exists(DB_URL):
		print('Deleting database.')
		drop_database(DB_URL)
	if not database_exists(DB_URL):
		print('Creating database.')
		create_database(DB_URL)

	print('Creating tables.')
	db.create_all()
	print('Shiny!')





@app.route('/isauthenticated', methods=['POST'])
def isauthenticated():
	if not 'authorization' in request.headers or request.headers['authorization'] in ['null','undefined','','true','1','undefined','null','false']:
		return jsonify({'status': 'error', 'result':'Not authenticated'})
	else:
		auth_usr = Auth.query.filter_by(id = request.headers['authorization'].split("._brk.")[0]).first()
		if not auth_usr is None:
			det = User.query.filter_by(id = int(auth_usr.user_id)).first()
			return jsonify({'status': 'ok', 'result': {c: getattr(det, c) for c in inspect(det).attrs.keys()} })
		else:
			return jsonify({'status': 'error', 'result':'Not authenticated'})


@app.route('/register', methods=['POST'])
def register():
	if not request.json or not 'reg_email' in request.json or not 'reg_pass' in request.json or not 'reg_name' in request.json:
		return jsonify({'status': 'error', 'result':'Error reading values. Please try again'})
	elif db.session.query(User).filter(User.email == request.json['reg_email']).count():
		return jsonify({'status': 'error', 'result':'Email already exists!'})
	else:
		nuser = User(name=request.json['reg_name'], email=request.json['reg_email'], password=request.json['reg_pass'])
		db.session.add(nuser)
		db.session.commit()
		return jsonify({'status': 'ok', 'result':'success'})


@app.route('/login', methods=['POST'])
def login():
	if not request.json or not 'log_email' in request.json or not 'log_pass':
		return jsonify({'status': 'error', 'result':'Error reading values. Please try again'})
	else:
		usr = User.query.filter_by(email = request.json['log_email']).first()
		if not usr is None:
			if str(usr.password) != str(request.json['log_pass']):
				return jsonify({'status': 'error', 'result':'Incorrect password'})
			else:
				nuser = Auth(user_id=usr.id)
				db.session.add(nuser)
				db.session.commit()
				atk = str(nuser.id) + '._brk.'
				return jsonify({'status': 'ok', 'result': 'success', 'auth_token':atk})
		else:
			return jsonify({'status': 'error', 'result':'User does not exists!'})


@app.route('/logout', methods=['POST'])
def logout():
	if not 'authorization' in request.headers or request.headers['authorization'] in ['null','undefined','','true','1','undefined','null','false']:
		return jsonify({'status': 'ok', 'result':'Already logged out'})
	else:
		auth_usr = Auth.query.filter_by(id = request.headers['authorization'].split("._brk.")[0]).first()
		if not auth_usr is None:
			auth_usr.log_out = datetime.datetime.now()
			db.session.commit()
			return jsonify({'status': 'ok', 'result': 'Logged Out' })
		else:
			return jsonify({'status': 'ok', 'result':'Already logged out'})		


@app.route('/get_logs', methods=['POST'])
def get_logs():
	users = User.query.filter_by().all()
	#to json array
	fin_res = [{c: getattr(det, c) for c in inspect(det).attrs.keys()} for det in users]
	for i in range(len(fin_res)):
		#get every log
		auths = Auth.query.filter_by(user_id = int(fin_res[i]['id'])).all()
		total_time = None
		auths = [{c: getattr(det, c) for c in inspect(det).attrs.keys()} for det in auths]
		for j in range(len(auths)):
			if not auths[j]['log_out'] is None:
				diff = auths[j]['log_out'] - auths[j]['log_in']
			else:
				diff = datetime.datetime.now() - auths[j]['log_in']
			if total_time == None : total_time = diff
			else: total_time = total_time + diff

		fin_res[i]['uptime'] = str(total_time)
		fin_res[i]['upt'] = total_time

	fin_res.sort(key=lambda k: k['upt'], reverse=True)
	fin_res = [ {**i, 'upt':''} for i in fin_res]

	return jsonify({'status': 'ok', 'result':fin_res})	





@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	return render_template('index.html')
	#return 'You want path: %s' % path








if __name__ == '__main__':
	app.run(host="127.0.0.1", port=int("3002"), debug=True)