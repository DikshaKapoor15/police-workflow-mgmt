from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField, SelectField, FileField
from wtforms.validators import InputRequired, ValidationError, DataRequired, EqualTo
from app.models import Credentials
import datetime
from werkzeug.security import generate_password_hash,check_password_hash

def invalid_credentials(form,field):
    email_entered = form.email.data
    password_entered = field.data
    user_object = Credentials.query.filter_by(email = email_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif not check_password_hash(user_object.password,password_entered):
        raise ValidationError("Username or password is incorrect")


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(message = "Email required")])
    password = PasswordField('Password', validators=[InputRequired(message = "Password required"),invalid_credentials])
    submit_button = SubmitField('Login')

class challanForm(FlaskForm):
    date = DateField(format = '%Y-%m')
    ps_name = StringField()
    overload_truck = IntegerField("overload truck",default=0)
    drunken_drive = IntegerField("drunken drive",default=0)
    over_speed = IntegerField("over speed",default=0)
    without_mask = IntegerField("without mask",default=0)
    without_helmet_seatbelt = IntegerField("without helmet/seatbelt",default=0)
    other_challan = IntegerField("other challan",default=0)


class recoveryForm(FlaskForm):
    date = DateField(format='%Y-%m')
    ps_name = StringField()
    illicit = StringField(label='illicit',default=0)
    licit   = StringField(label='licit',default=0)
    lahan  = StringField(label='lahan' , default=0)
    opium  = StringField(label='opium',default=0)
    poppy =  StringField(label='poppy',default=0)
    heroine = StringField(label='heroine',default=0)
    charas = StringField(label='charas',default=0)
    ganja   = StringField(label='ganja',default=0)
    tablets = StringField(label='tablets',default=0)
    injections = StringField(label='injections',default=0)
    other_recovery = StringField(label='other_recovery',default='nil')



class investigationForm(FlaskForm):
    date = DateField(format='%Y-%m')
    name_ps = StringField()
    category = SelectField(label='category', choices=[('ipc', 'IPC'), ('lsl', 'LOCAL AND SPECIAL LAW')])
    pending_ut = IntegerField(label='pending_ut', default=0)
    dispose_ut = IntegerField(label='dispose_ut', default=0)
    pending_lt3_ui = IntegerField(label='pending_lt3_ui', default=0)
    dispose_lt3_ui = IntegerField(label='dispose_lt3_ui', default=0)
    pending_3_ui = IntegerField(label='pending_3_ui', default=0)
    dispose_3_ui = IntegerField(label='dispose_3_ui', default=0)
    pending_6_ui = IntegerField(label=' pending_6_ui', default=0)
    dispose_6_ui = IntegerField(label=' dispose_6_ui', default=0)
    pending_12_ui = IntegerField(label='pending_12_ui', default=0)
    dispose_12_ui = IntegerField(label=' dispose_12_ui', default=0)



class adminForm(FlaskForm):
    ps_name1 = SelectField(label = 'ps_name1',choices=[('Nangal','Nangal'),('Anandpur','Anandpur'),('Rupnagar','Rupnagar')])
    ps_name2 = SelectField(label = 'ps_name2',choices=[('Nangal','Nangal'),('Anandpur','Anandpur'),('Rupnagar','Rupnagar')])
    attribute_field = SelectField(label='attribute_field',choices=[('Investigation under LOCAL & SPECIAL LAW','Investigation Under LOCAL & SPECIAL LAW'),('Investigation under IPC','Investigation Under IPC'),('Marks',"MARKS"),('Challan',"CHALLAN")])
    date = DateField(format = '%Y-%m')

class marksForm(FlaskForm):
    date = DateField(format='%Y-%m')
    ps_name = StringField()
    percent_of_cases_submitted_in_court = IntegerField(label='percent_of_cases_submitted_in_court',default=0)
    cases_of_henius_crime= IntegerField(label='cases_of_henius_crime',default=0)
    crime_against_property = IntegerField(label='crime_against_property' , default=0)
    ndps= IntegerField(label='ndps',default=0)
    commercial_recovery=  IntegerField(label='commercial_recovery',default=0)
    arm_act = IntegerField(label='arm_act',default=0)
    excise_act= IntegerField(label='excise_act',default=0)
    gambling_act= IntegerField(label='gambling_act',default=0)
    percent_of_disposal_of_complaints= IntegerField(label='percent_of_disposal_of_complaints',default=0)
    percent_of_property_disposal= IntegerField(label='percent_of_property_disposal',default=0)
    arrest_of_po = StringField(label='arrest_of_po',default=0)
    untrace_cases_put_in_court = IntegerField(label='untrace_cases_put_in_court', default=0)
    negligence = StringField(label='negligence', default=0)
    cleanliness = IntegerField(label='cleanliness', default=0)
    handling_of_law= StringField(label='handling_of_law', default=0)


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class table(FlaskForm):
    ps_name =  StringField(label = 'Police Station',validators=[InputRequired()])
    attribute = SelectField(label='Attribute',choices=[('Marks','Marks'),('Challan','Challan'),
            ('Investigation under IPC','Investigation under IPC'),('Recovery','Recovery'),
                    ('Investigation under Local & Special Law','Investigation under Local & Special Law')])
    from_date = DateField(label='From Date')
    to_date  = DateField(label='To Date')

class excelForm(FlaskForm):
    uploadFile = FileField("upload")