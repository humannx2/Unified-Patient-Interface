from uhr import app,db,bcrypt
from flask import render_template,redirect,url_for,request,flash, make_response, current_app, send_file, url_for
from uhr.model import User, Patient,Doctor,MedicalReport,DiagnosisHistory
from flask_login import login_user,login_required,current_user,logout_user
from flask_bcrypt import check_password_hash
from werkzeug.utils import secure_filename
import os



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/diagnosis',methods=['GET','POST'])
@login_required
def diagnosis():
    if request.method=='POST':
         pat_id=request.form.get('patient_id')
         doc_id=current_user.doctor_id
         diagnosis=request.form.get('diagnosis_text')
         new_diagnoses=DiagnosisHistory(patient_id=pat_id,doctor_id=doc_id,diagnosis_text=diagnosis)
         db.session.add(new_diagnoses)
         db.session.commit()
         return redirect('/docdash')
         flash('Diagnosis Updated!','success')
    return render_template('doctorview.html')

@app.route('/docdash', methods=['GET','POST'])
@login_required
def docdash():
    pat_id=0 #initially giving it zero so that no records are accessed
    if request.method=='POST':
        # takes the username(email) from the patient
        username=request.form.get('email')
        if username=='':
            flash('Please Enter a Username','danger')
        else:
            user=User.query.filter_by(username=username).first() # finds that user in the user database
            if user is not None:
                pat_id=user.patient_id # if the user is found takes it patient_id
                # print(current_user.doctor_id)
            else:
                flash('Wrong Username','danger')
    reports = MedicalReport.query.filter_by(patient_id=pat_id).all()
    diagnoses = DiagnosisHistory.query.filter_by(patient_id=pat_id).all()
    return render_template('doctorview.html', reports=reports, pat_id=pat_id, diagnoses=diagnoses)

@app.route('/patdash',methods=['GET','POST'])
@login_required
def patdash():
    if request.method=='POST':
        file=request.files['filename']
        if file.filename=='':
            flash('No File Selected!', 'warning')
            return redirect('/patdash')
        else:
            secure_file=secure_filename(file.filename)
            user_id=current_user.patient_id
            new_path=f"{user_id}_{secure_file}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],new_path))
            new_report = MedicalReport(patient_id=current_user.patient_id, report_file=new_path)
            db.session.add(new_report)
            db.session.commit()
            flash('Report Uploaded successfully!', 'success')
    reports = MedicalReport.query.filter_by(patient_id=current_user.patient_id).all()
    diagnoses = DiagnosisHistory.query.filter_by(patient_id=current_user.patient_id).all()
    return render_template('patientview.html', reports=reports, diagnoses=diagnoses)
    # return render_template('patientview.html')

# to download the reports
@app.route('/download_report/<int:file_id>', methods=['GET'])
def download_report(file_id):
    report = MedicalReport.query.get(file_id)
    if not report:
        return flash("File not found", 'warning')

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report.report_file)
    return send_file(file_path, as_attachment=True)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        mail=request.form.get('useremail')
        password=request.form.get('userpass')
        user=User.query.filter_by(username=mail).first() 
        if user is not None: #checking if user already exists or not
            if bcrypt.check_password_hash(user.password,password): #matching password and username
                login_user(user)
                #directs to different dashboard based on doc or patients
                if user.user_type =='doctor':
                    flash('Logged In Successfully!', 'success')
                    return redirect('/docdash')
                else:
                    flash('Logged In Successfully!', 'success')
                    return redirect('/patdash')
            else:
                flash('Check your Password', 'danger')
                return redirect('/login')
        else:
            flash('Email is not registered', 'danger')
            return redirect('/register')
        # print(mail, password, usertype)
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('username')
        mail=request.form.get('useremail')
        password=request.form.get('userpass')
        usertype=request.form.get('user_type')
        hashpass=bcrypt.generate_password_hash(password).decode('utf-8') #converts the password into a hash string
        #checks if the same username exists in the table User
        if User.query.filter_by(username=mail).first() is not None:
            flash('Email is already registered', 'danger')
            return redirect('/register')
        #checks if user_type is selected or not
        if usertype=='--Choose an option--':
            flash('Select a category', 'danger')
            return redirect('/register')
        # creating a doctor id and a patient id as foreign key
        if usertype=='doctor':
            candidate=Doctor()
            db.session.add(candidate)
            db.session.commit()
            #using email as username in the database
            data=User(name=name,username=mail,password=hashpass,user_type=usertype,doctor_id=candidate.id)
        else:
            candidate=Patient()
            db.session.add(candidate)
            db.session.commit()
            # adds the key for medical reports of the patient 
            pat=MedicalReport(patient_id=candidate.id)
            db.session.add(pat)
            db.session.commit
            data=User(name=name,username=mail,password=hashpass,user_type=usertype,patient_id=candidate.id)
        db.session.add(data)
        db.session.commit()
        flash('Registration Successful! You can now login.', 'success')
        return redirect('/login')
        # return make_response("OK", 200)
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/account')
@login_required
def account():
    return render_template('account.html')