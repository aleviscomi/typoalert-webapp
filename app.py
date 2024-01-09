from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt 
from src.models import *
from src.utils import *
import datetime, secrets, os

#########################################
#										#
#				CONFIG					#
#										#
#########################################

app = Flask(__name__)

database_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+ os.path.join(database_folder, "typoalert.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "RuXMp4h8XV71hdss0JcapHyvS9jVi9VmOc77B9n4OXSb4fbRGz"
bcrypt = Bcrypt(app) 

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)
with app.app_context():
	db.create_all()

@login_manager.user_loader
def loader_user(user_id):
	return db.session.get(User, user_id)


#########################################
#										#
#				ROUTES					#
#										#
#########################################

@app.route("/")
def home():
	return render_template("home.html")


@app.route('/register', methods=["GET", "POST"])
def register():
	if request.method == "POST":
		email = request.form.get("email")
		password = request.form.get("password")

		if password:
			user = User.query.filter_by(email=email).first()
			
			if not user:
				if is_email_valid(email):
					salt = secrets.token_hex(16)
					hashed_password = bcrypt.generate_password_hash(salt + password).decode('utf-8')
					api_key = secrets.token_hex(64)

					user = User(email=email, password=hashed_password, salt=salt, api_key=api_key, registered_on=datetime.datetime.now())
					db.session.add(user)
					db.session.commit()
					return redirect(url_for("login"))
				else:
					flash("The email is invalid!", "error")
			else:
					flash("The email is already registered!", "error")
		else:
			flash("You must enter a password!", "error")
	return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email")
		password = request.form.get("password")

		user = User.query.filter_by(email=email).first()

		if user:
			is_password_valid = bcrypt.check_password_hash(user.password, user.salt + password)

			if is_password_valid:
				login_user(user)
				return redirect(url_for("home"))
			else:
				flash("Wrong credentials!", "error")
		else:
			flash("Wrong credentials!", "error")

	return render_template("login.html")


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("home"))


@app.route("/settings")
@login_required
def settings():
	return render_template("settings.html")


@app.route("/profile")
@login_required
def profile():
	return render_template("profile.html")


#########################################
#										#
#				API						#
#										#
#########################################


@app.route("/scan", methods=["POST"])
def scan():
	domain_name = request.form.get('domain')
	api_key = request.form.get('api_key')
	no_cache = request.form.get('no_cache') != None

	user = User.query.filter_by(api_key=api_key).first()

	if is_domain_valid(domain_name):
		if user:
			try:
				result = analyze_domain(user, domain_name, no_cache)
			except Exception as e:
				return {"error": "Unreachable domain!"}, 400
			
			return result
		else:
			return {"error": "Invalid api key!"}, 400
		
	return {"error": "Invalid domain format!"}, 400


@app.route("/user/add/verified-domain", methods=["POST"])
@login_required
def add_verified_domain():
	if current_user.is_anonymous:
		return {"error": "User not logged in"}, 400

	domain_name = request.form.get('domain')
	if not domain_name:
		return {"error": "You need to enter a domain!"}, 400
	
	if not is_domain_valid(domain_name):
		return {"error": "Invalid domain format!"}, 400
	
	if is_top_domain(domain_name):
		return {"error": "The domain is already considered as verified!"}, 400
		
	
	user = current_user
	

	existing_domain = Domain.query.filter_by(domain_name=domain_name).first()
	if existing_domain:
		if any(existing_domain.domain_name == domain_name for existing_domain in user.domains):
			return {"error": "Domain already exists!"}, 400
		
		verified_domain = existing_domain
	else:
		verified_domain = Domain(domain_name=domain_name)
	
	user.domains.append(verified_domain)
	db.session.commit()

	return {"success": "Domain added successfully!"}


@app.route("/user/remove/verified-domain", methods=["POST"])
@login_required
def remove_verified_domain():
    if current_user.is_anonymous:
        return {"error": "User not logged in"}, 400

    domain_name = request.form.get('domain')
    user = current_user

    existing_domain = Domain.query.filter_by(domain_name=domain_name).first()
    if existing_domain:
        if any(existing_domain.domain_name == domain_name for existing_domain in user.domains):
            user.domains.remove(existing_domain)
            db.session.commit()

            return {"success": "Domain removed successfully!"}

    return {"error": "Domain not found in the user's list"}, 400



if __name__ == "__main__":
	app.run()