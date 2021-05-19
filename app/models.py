from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import jwt
from time import time
from app import app

db = SQLAlchemy()

class Credentials(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(25), unique = True, nullable = False)
    password = db.Column(db.String(), nullable= False)
    email = db.Column(db.String(50))
    urole = db.Column(db.String(80))
    def get_reset_password_token(self, expires_in=6000):
        return jwt.encode(
            {'reset_password': self.mail_id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        print("heyymodels",id)
        return id


class challans(db.Model):
    _tablename_ = "challan"
    id             = db.Column(db.Integer, primary_key=True)
    overload_tripper_and_truck = db.Column(db.Integer,nullable=False)
    drunken_driving  = db.Column(db.Integer,nullable=False)
    over_speed     = db.Column(db.Integer,nullable=False)
    without_mask = db.Column(db.Integer, nullable=False)
    without_helmet_seatbelt = db.Column(db.Integer,nullable=False)
    other = db.Column(db.Integer,nullable=False)
    date = db.Column(db.DateTime(timezone=False), nullable = False)
    ps_name = db.Column(db.String(15),nullable = False)

    def _init_(self, ovt, dd, os, wohsb, wom, oc,d,ps):
        self.overload_truck = ovt
        self.drunken_drive = dd
        self.over_speed = os
        self.without_helmet_seatbelt = wohsb
        self.without_mask = wom
        self.other_challan = oc
        self.date =d
        self.ps_name = ps

class recoveries(db.Model):
    tablename = "recoveries"

    id = db.Column(db.Integer, primary_key=True)
    illicit = db.Column(db.String(),nullable=False)
    licit   = db.Column(db.String(),nullable=False)
    lahan  = db.Column(db.String(),nullable=False)
    opium = db.Column(db.String(),nullable=False)
    poppy = db.Column(db.String(),nullable=False)
    heroine = db.Column(db.String(),nullable=False)
    charas = db.Column(db.String(),nullable=False)
    ganja = db.Column(db.String(),nullable=False)
    tablets = db.Column(db.String(),nullable=False)
    injections= db.Column(db.String(),nullable=False)
    other_recovery = db.Column(db.String(),nullable=False)
    date       =db.Column(db.DateTime(timezone=False),nullable=False)
    ps_name    = db.Column(db.String(15),nullable=False)


    def _init_(self,illicit,licit,lahan,opium,poppy,heroine,charas,ganja,tablets,injections,other_recovery,date,ps_name):
        self.illicit = illicit
        self.licit   = licit
        self.lahan   = lahan
        self.opium  = opium
        self.poppy  = poppy
        self.heroine = heroine
        self.charas = charas
        self.ganja =ganja
        self.tablets = tablets
        self.injections = injections
        self.other_recovery =other_recovery
        self.date=date
        self.ps_name =ps_name

class investigation(db.Model):
    tablename = "investigation"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=False), nullable=False)
    name_ps = db.Column(db.String(25), nullable=False)
    category  = db.Column(db.String(30),nullable=False)
    pending_ui = db.Column(db.Integer,nullable=False)
    dispose_ui = db.Column(db.Integer,nullable=False)
    pending_ut = db.Column(db.Integer,nullable=False)
    dispose_ut = db.Column(db.Integer,nullable=False)
    _lt3_pending_ui = db.Column(db.Integer,nullable=False)
    _lt3_dispose_ui = db.Column(db.Integer,nullable=False)
    _3_pending_ui = db.Column(db.Integer,nullable=False)
    _3_dispose_ui = db.Column(db.Integer,nullable=False)
    _6_pending_ui = db.Column(db.Integer,nullable=False)
    _6_dispose_ui = db.Column(db.Integer,nullable=False)
    _12_pending_ui = db.Column(db.Integer,nullable=False)
    _12_dispose_ui = db.Column(db.Integer,nullable=False)

    def __init__(self,d,nps,cate,pui,dui,put,dut,lttp,lttd,tpui,tdui,spui,sdui,twpui,twdui):
        self.date = d
        self.name_ps =nps
        self.category =cate
        self.pending_ui =pui
        self.dispose_ui =dui
        self.pending_ut =put
        self.dispose_ut =dut
        self._lt3_pending_ui =lttp
        self._lt3_dispose_ui = lttd
        self._3_pending_ui = tpui
        self._3_dispose_ui = tdui
        self._6_pending_ui = spui
        self._6_dispose_ui = sdui
        self._12_pending_ui = twpui
        self._12_dispose_ui = twdui

class marks(db.Model):
    tablename = "marks"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=False), nullable=False)
    ps_name = db.Column(db.String(25), nullable=False)
    percent_of_cases_submitted_in_court = db.Column(db.Integer, nullable=False)
    cases_of_henius_crime = db.Column(db.Integer, nullable=False)
    crime_against_property = db.Column(db.Integer, nullable=False)
    ndps = db.Column(db.Integer, nullable=False)
    commercial_recovery = db.Column(db.Integer, nullable=False)
    arm_act = db.Column(db.Integer, nullable=False)
    excise_act =db.Column(db.Integer, nullable=False)
    gambling_act = db.Column(db.Integer, nullable=False)
    percent_of_disposal_of_complaints = db.Column(db.Integer, nullable=False)
    percent_of_property_disposal =db.Column(db.Integer, nullable=False)
    arrest_of_po =db.Column(db.Integer, nullable=False)
    untrace_cases_put_in_court = db.Column(db.Integer, nullable=False)
    negligence = db.Column(db.Integer, nullable=False)
    cleanliness = db.Column(db.Integer, nullable=False)
    handling_of_law = db.Column(db.Integer, nullable=False)

    def __inti__(self,d,nps,pocsic,cohc,cap,n,cr,ac,ea,ga,podoc,popd,aop,ucpic,ne,c,hol):
        self.date = d
        self.ps_name = nps
        self.percent_of_cases_submitted_in_court = pocsic
        self.cases_of_henius_crime = cohc
        self.crime_against_property = cap
        self.ndps = n
        self.commercial_recovery = cr
        self.arm_act = ac
        self.excise_act = ea
        self.gambling_act = ga
        self.percent_of_disposal_of_complaints = podoc
        self.percent_of_property_disposal = popd
        self.arrest_of_po = aop
        self.untrace_cases_put_in_court = ucpic
        self.negligence = ne
        self.cleanliness = c
        self.handling_of_law = hol

class updation_track(db.Model) :
    id= db.Column(db.Integer, primary_key=True)
    name_ps = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), nullable=False)
    attribute = db.Column(db.String(), nullable=False)
    month_data = db.Column(db.String(), nullable=False)
    year =  db.Column(db.Integer, nullable=False)
    uploaded_date = db.Column(db.DateTime(timezone=False), nullable=False)

    def __init__(self,nps,un,a,md,yr,ud):
        self.name_ps =nps
        self.username = un
        self.attribute =a
        self.month_data =md
        self.year=yr
        self.uploaded_date =ud