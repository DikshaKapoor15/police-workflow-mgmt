from app import app
from app.forms import *
from app.models import *
from flask import render_template, url_for, redirect,request, jsonify, session, flash, current_app
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import create_engine
from flask_mail import Message,Mail
from app.email import *
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash
from functools import wraps
import pandas as pd
import datetime
import os
from dateutil.relativedelta import relativedelta
Bootstrap(app)

engine = create_engine('postgres://xmxtulwzfymycv:325459c809306339560bbad8dcae00e37b80ec1492f0360c5f495f25980817ec@ec2-18-207-95-219.compute-1.amazonaws.com:5432/dnh5em2ovkoou')
connection = engine.raw_connection()
mycursor = connection.cursor()
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://xmxtulwzfymycv:325459c809306339560bbad8dcae00e37b80ec1492f0360c5f495f25980817ec@ec2-18-207-95-219.compute-1.amazonaws.com:5432/dnh5em2ovkoou"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if ( (current_user.urole != role) and (role != "ANY")):
                return login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# session = db.session()
# cursor = session.execute(sql).cursor




##mail section to be checked
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'developmentsoftware305@gmail.com'
app.config['MAIL_PASSWORD'] = 'tempmail1@'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

data = [
        ("2020-01-01",79.2),
        ("2020-02-01", 59.6),
        ("2020-03-01", 64),
        ("2020-04-01", 51.6),
        ("2020-05-01", 56),
    ]
labels2 = [row[0]  for row in data ]
values2 = [row[1] for row in data]

@login_manager.user_loader
def load_user(id):
    return Credentials.query.get(int(id))

@app.route('/', methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        login_form = LoginForm()
        if login_form.validate_on_submit():
            user_object = Credentials.query.filter_by(email=login_form.email.data).first()
            login_user(user_object)
            if user_object.urole == 'POLICE_STATION':
                return redirect(url_for('home', userdata = user_object.username))
            if user_object.urole == 'SSP':
                return redirect(url_for('mark'))
        return render_template("login.html", form=login_form)
    else:
        flash("You are already logged in. Please logout to access login page")
        user = Credentials.query.filter_by(email=current_user.email).first()
        return redirect(url_for('home', userdata = user.username))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('login', flashmsg = "Please logout to change your password"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Credentials.query.filter_by(email=form.email.data).first()
        if user:
            print("user found")
            send_password_reset_email(user)
        #flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login', flashmsg = 'Mail sent'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    idRec = Credentials.verify_reset_password_token(token)
    print("heyyyyyyappplication""", idRec)
    # if not user:
    #     return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = Credentials.query.filter_by(email=idRec).first()
        print("heyy after reset password", user.id)
        print("heyy before reset password", user.password)
        user.password=generate_password_hash(form.password.data)

        mycursor.execute("UPDATE credentials SET password = '{password}' WHERE email = '{mail}' ".format(password = str(user.password), mail =  str(idRec)))
        connection.commit()
        # user1 = Credentials.query.filter_by(mail_id=idRec).first()
        print("heyy after reset password in database", user.password)
        #flash('Your password has been reset.')
        return redirect(url_for('login', flashmsg = 'Password reset successful'))
    return render_template('reset_password.html', form=form)


@app.route("/home", methods=['GET', 'POST'])
@login_required(role = "POLICE_STATION")
def home():
    userdata = request.args.get('userdata',None)
    d = datetime.datetime.today()
    d = d + relativedelta(months=-1)
    sixdates=[]          # list to store last six months in '%Y-%m' format
    sixdatesb=[]         # list to store last six months dates in '%b-%Y' format to use them as labels

    wdate = d
    sixdates.append(wdate.strftime('%Y-%m'))
    sixdatesb.append(wdate.strftime('%b-%Y'))
    for i in range(5):
         wdate = wdate + relativedelta(months=-1)
         sixdates.append(wdate.strftime('%Y-%m'))
         sixdatesb.append(wdate.strftime('%b-%Y'))


    sixvaluesps1 = []        # list to store challan data over 6 mnths
    for i in range(6):
         mycursor.execute("SELECT * FROM challans WHERE ps_Name='{0}' and to_char(date, 'YYYY-MM')='{1}' ".format(str(current_user.username),sixdates[i]))
         onevalue = mycursor.fetchall()
         if onevalue:
             sixvaluesps1.extend(onevalue)
         else:
             sixvaluesps1.append((0, 0, 0, 0, 0, 0, 0, 0, 0))



    valueChallanMonth = [ sum(x[1:7]) for x in sixvaluesps1]


    valueChallanAttr = [0,0,0,0,0,0]

    for j in range(len(sixvaluesps1)):
        valueChallanAttr[0] += sixvaluesps1[j][1]
        valueChallanAttr[1] += sixvaluesps1[j][2]
        valueChallanAttr[2] += sixvaluesps1[j][3]
        valueChallanAttr[3] += sixvaluesps1[j][4]
        valueChallanAttr[4] += sixvaluesps1[j][5]
        valueChallanAttr[5] += sixvaluesps1[j][6]
    colors = [
        "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
        "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
        "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]



    labels1 = ['overload_tripper_and_truck', 'drunken_driving', 'over_speed', 'without_mask', 'without_helmet_seatbelt',
               'other']



    labels3=['ui_over_12_months','ui_over_six_months','ui_over_three_months','ui_over_lt_three_months']
    values3=[]
    values4 = []
    mycursor.execute("SELECT * FROM investigation WHERE name_ps='{0}' AND category='under_ipc' and to_char(date,'YYYY-MM')='{1}'".format(str(current_user.username),sixdates[1])) ## d.strftime('%Y-%m')
    data = mycursor.fetchall()
    if data:
        data=data
    else:
        data=[(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)]

    values3.append(data[0][12])
    values3.append(data[0][10])
    values3.append(data[0][8])
    values3.append(data[0][14])
    values4.append(data[0][13])
    values4.append(data[0][11])
    values4.append(data[0][9])
    values4.append(data[0][15])

    values5 = []
    values6 = []
    mycursor.execute("SELECT * FROM investigation WHERE name_ps='{0}' AND category='under_local' and to_char(date,'YYYY-MM')='{1}'".format(str(current_user.username),sixdates[1]))  ##should change city name
    data = mycursor.fetchall()
    if data:
        data=data
    else:
        data=[(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)]

    values5.append(data[0][12])
    values5.append(data[0][10])
    values5.append(data[0][8])
    values5.append(data[0][14])
    values6.append(data[0][13])
    values6.append(data[0][11])
    values6.append(data[0][9])
    values6.append(data[0][15])

    values_all = []
    for x in sixdates:
        mycursor.execute("SELECT * from marks where ps_name='{0}' and to_char(date,'YYYY-MM')='{1}'".format(str(current_user.username),x))
        data= mycursor.fetchall()
        if data:
            values_all.extend(data)
        else:
            values_all.append((0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))

    final_score = []

    for j in range(len(values_all)):
        result = (values_all[j][2] * 0.1) + (values_all[j][3] * 2) + (values_all[j][4] * 0.1) + (
                values_all[j][5] * 0.4) + (values_all[j][6] * 2) + (values_all[j][7] * 1) + (
                         values_all[j][8] * 0.2) + (values_all[j][9] * 0.2) + (values_all[j][10] * 0.1) + (
                         values_all[j][11] * 0.1) + (values_all[j][12] * 2) + (values_all[j][13] * 0.4) + (
                     values_all[j][14]) + (values_all[j][15]) + (values_all[j][16])
        final_score.append(result)


    return render_template("home.html", final_score=final_score[::-1] ,colors=colors, labels1 = labels1, labels2=labels2, values2=values2, values3=values3, values4=values4,values5=values5,values6=values6,labels3=labels3, userdata = userdata,
                           valueChallanMonth=valueChallanMonth[::-1],valueChallanAttr=valueChallanAttr,sixdatesb=sixdatesb[::-1])

@app.route('/challan', methods=['POST', 'GET'])
@login_required(role="POLICE_STATION")
def challan():
    challan_form = challanForm()
    if challan_form.validate_on_submit():
        date = challan_form.date.data
        d = datetime.date.today()
        m = d.strftime("%m")
        m1 = date.strftime('%b')
        y = d.strftime("%Y")
        mnth = date.strftime("%m")
        yr = date.strftime("%Y")
        attribute = 'Challan'
        mycursor.execute(
            "select * from challans where extract(year from date)='{yr}' and extract(month from date)='{mnth}' and ps_name='{ps}' "
            .format(yr=yr, mnth=mnth, ps=str(current_user.username)))
        data = mycursor.fetchall()
        if len(data) != 0 and m == mnth and yr == y:
            oltt = challan_form.overload_truck.data
            os = challan_form.over_speed.data
            dd = challan_form.drunken_drive.data
            wm = challan_form.without_mask.data
            whs = challan_form.without_helmet_seatbelt.data
            oc = challan_form.other_challan.data
            id = data[0][0]
            mycursor.execute(
                "update challans set  overload_tripper_and_truck='{oltt}',over_speed='{os}', drunken_driving='{dd}',without_mask='{wm}',without_helmet_seatbelt='{whs}',other='{oc}' where id={id}"
                    .format(id=id, oltt=oltt, os=os, dd=dd, wm=wm, whs=whs, oc=oc))
            connection.commit()
            mycursor.execute(
                "UPDATE credentials SET date_challan='{d}' where username='{u}'; ".format(d=d,
                                                                                          u=str(current_user.username)))
            connection.commit()
            newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1, yr=yr,
                                       ud=d)
            db.session.add(newupdate)
            db.session.commit()
            flash("Data updated Successfully", category='success')
            return redirect(url_for('challan'))
        elif len(data) != 0:
            flash("no duplicates allowed", category='warning')
            return redirect(url_for('challan'))
        else:
            newchallan = challans(overload_tripper_and_truck=challan_form.overload_truck.data,
                                  drunken_driving=challan_form.drunken_drive.data,
                                  over_speed=challan_form.over_speed.data, without_mask=challan_form.without_mask.data,
                                  without_helmet_seatbelt=challan_form.without_helmet_seatbelt.data,
                                  other=challan_form.other_challan.data, date=challan_form.date.data,
                                  ps_name=current_user.username)
            db.session.add(newchallan)
            db.session.commit()

            mycursor.execute("UPDATE credentials SET date_challan='{d}' where username='{u}'; ".format(d=d, u=str(
                current_user.username)))
            connection.commit()

            newupdate = updation_track(nps=current_user.username, un=current_user.username, a='Challan', md=m1, yr=yr,
                                       ud=d)
            db.session.add(newupdate)
            db.session.commit()
            flash("Data uploaded Successfully", category='success')
            return redirect(url_for('challan'))
    return render_template("challan.html",form = challan_form)



@app.route('/recovery', methods=['POST', 'GET'])
@login_required(role = "POLICE_STATION")

def recovery():
    recovery_form = recoveryForm()

    if recovery_form.validate_on_submit():
        date = recovery_form.date.data
        d = datetime.date.today()
        m = d.strftime("%m")
        y = d.strftime("%Y")
        mnth = date.strftime("%m")
        yr = date.strftime("%Y")
        m1 = date.strftime('%b')
        attribute = 'Recovery'
        mycursor.execute(
            "select * from recoveries where extract(year from date)='{yr}' and extract(month from date)='{mnth}' and ps_name='{ps}' "
            .format(yr=yr, mnth=mnth, ps=str(current_user.username)))
        data = mycursor.fetchall()
        if len(data) != 0 and m == mnth and yr == y:
            id = data[0][0]
            il= recovery_form.illicit.data
            li = recovery_form.licit.data
            la = recovery_form.lahan.data
            op = recovery_form.opium.data
            po = recovery_form.poppy.data
            he = recovery_form.heroine.data
            ch = recovery_form.charas.data
            ga = recovery_form.ganja.data
            inj = recovery_form.injections.data
            ta = recovery_form.tablets.data
            ot = recovery_form.other_recovery.data
            mycursor.execute(
                "update recoveries set  illicit='{il}',licit='{li}', lahan='{la}',opium='{op}', poppy ='{po}',heroine='{he}' , charas = '{ch}',ganja= '{ga}',injections= '{inj}',tablets= '{ta}',other_recovery= '{ot}' where id={id}"
                .format(id=id, il = il, li = li, la = la, op = op, po = po, he = he, ch = ch, ga = ga, inj = inj, ta = ta , ot = ot))
            connection.commit()
            mycursor.execute(
                "UPDATE credentials SET date_recovery='{d}' where username='{u}'; ".format(d=recovery_form.date.data,
                                                                                          u=str(current_user.username)))
            connection.commit()
            newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1, yr=yr,
                                       ud=d)
            db.session.add(newupdate)
            db.session.commit()
            flash("Data updated Successfully", category='success')
            return redirect(url_for('recovery'))
        elif len(data) != 0:
            flash("no duplicates allowed", category='warning')
            redirect(url_for('recovery'))
        else:
            new_recovery = recoveries(illicit = recovery_form.illicit.data, licit=recovery_form.licit.data, lahan=recovery_form.lahan.data,opium=recovery_form.opium.data, poppy=recovery_form.poppy.data, heroine=recovery_form.heroine.data,charas=recovery_form.charas.data, ganja=recovery_form.ganja.data, injections=recovery_form.injections.data, tablets=recovery_form.tablets.data, other_recovery =recovery_form.other_recovery.data, date=recovery_form.date.data,ps_name=current_user.username)
            db.session.add(new_recovery)
            db.session.commit()
            mycursor.execute(
                "UPDATE credentials SET date_recovery='{d}' where username='{u}'; ".format(d=recovery_form.date.data,
                                                                                           u=str(current_user.username)))
            connection.commit()
            newupdate = updation_track(nps=current_user.username, un=current_user.username, a='Recovery', md=m1, yr=yr,
                                       ud=d)
            db.session.add(newupdate)
            db.session.commit()
            flash("Data uploaded Successfully", category='success')
            return redirect(url_for('recovery'))
    return render_template('recovery.html', form=recovery_form)

@app.route("/investigations", methods=['GET','POST'])
@login_required(role = "POLICE_STATION")

def investigations():

    iform = investigationForm()

    if iform.validate_on_submit():
        date = iform.date.data
        d = datetime.date.today()
        m = d.strftime("%m")
        y = d.strftime("%Y")
        m1 = date.strftime('%b')
        attribute = 'Investigation'
        mnth = date.strftime("%m")
        yr = date.strftime("%Y")
        cate = iform.category.data
        mycursor.execute(
            "select * from investigation where category='{c}' and extract(year from date)='{yr}' and extract(month from date)='{mnth}' and name_ps='{ps}' "
            .format(yr=yr, c=cate, mnth=mnth, ps=str(current_user.username)))
        data = mycursor.fetchall()
        pending_ui = iform.pending_3_ui.data + iform.pending_6_ui.data + iform.pending_12_ui.data + iform.pending_lt3_ui.data
        disposed_ui = iform.dispose_3_ui.data + iform.dispose_6_ui.data + iform.dispose_12_ui.data + iform.dispose_lt3_ui.data


        if len(data) != 0 and m == mnth and y == yr:
            id = data[0][0]
            pui = pending_ui
            dui = disposed_ui
            put = iform.pending_ut.data
            dut = iform.dispose_ut.data
            plt3 = iform.dispose_lt3_ui.data
            dlt3 = iform.pending_lt3_ui.data
            p3 = iform.pending_3_ui.data
            d3 = iform.dispose_3_ui.data
            p6 = iform.pending_6_ui.data
            d6 = iform.dispose_6_ui.data
            p12 = iform.pending_12_ui.data
            d12 = iform.dispose_12_ui.data
            mycursor.execute(
                "update investigation set date='{d1}',pending_ui ='{pui}', dispose_ui ='{dui}', pending_ut ='{put}', dispose_ut ='{dut}', _3_pending_ui ='{p3}', _3_dispose_ui ='{d3}', _6_pending_ui ='{p6}', _6_dispose_ui ='{d6}', _12_pending_ui ='{p12}', _12_dispose_ui ='{d12}', _lt3_pending_ui ='{plt3}', _lt3_dispose_ui ='{dlt3}' where id={id}"
                .format(id=id, d1=date, pui=pui, dui=dui, put=put, dut=dut, plt3=plt3, dlt3=dlt3, p3=p3, d3=d3, p6=p6,
                        d6=d6,
                        p12=p12, d12=d12))
            connection.commit()
            mycursor.execute(
                "UPDATE credentials SET date_investigation='{d}' where username='{u}'; ".format(d=iform.date.data,
                                                                                          u=str(current_user.username)))
            connection.commit()
            newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1, yr=yr,
                                       ud=d)
            db.session.add(newupdate)
            db.session.commit()
            flash("Data updated Successfully", category='success')
            return redirect(url_for('investigations'))
        elif len(data) != 0:
            flash("no duplicates allowed", category='warning')
            redirect(url_for('investigations'))
        else:
            newinvestigation = investigation(d=iform.date.data, nps=current_user.username, pui=pending_ui,
                                             dui=disposed_ui,
                                             put=iform.pending_ut.data, dut=iform.dispose_ut.data,
                                             lttd=iform.dispose_lt3_ui.data, lttp=iform.pending_lt3_ui.data,
                                             cate=iform.category.data, tpui=iform.pending_3_ui.data,
                                             tdui=iform.dispose_3_ui.data,
                                             spui=iform.pending_6_ui.data, sdui=iform.dispose_6_ui.data,
                                             twpui=iform.pending_12_ui.data, twdui=iform.dispose_12_ui.data)
            db.session.add(newinvestigation)
            db.session.commit()
            mycursor.execute(
            "UPDATE credentials SET date_investigation='{d}' where username='{u}'; ".format(d=iform.date.data, u=str(
               current_user.username)))
            connection.commit()
            newupdate = updation_track(nps=current_user.username, un=current_user.username, a='Investigation', md=m1, yr=yr,
                                       ud=d)
            db.session.add(newupdate)
            db.session.commit()
            flash("Data uploaded Successfully", category='success')
            return redirect(url_for('investigations'))
    return render_template('investigations.html',form=iform)

@app.route('/uploading', methods=['POST', 'GET'])
@login_required(role="POLICE_STATION")
def uploading():
    eform = excelForm()
    if request.method == 'POST':
        file = request.files['uploadFile']
        cdata = pd.read_excel(file, sheet_name='Challan')
        if set(cdata.columns.ravel()) == {'overloaded truck', 'druken drive', 'over speed', 'without mask',
                                          'without helmet/seatbelt', 'others', 'date'}:
            for i, r in cdata.iterrows():
                date = datetime.datetime.strptime(r['date'], "%Y-%m")
                d = datetime.date.today()
                m = d.strftime("%m")
                m1 = date.strftime('%b')
                y = d.strftime("%Y")
                mnth = date.strftime("%m")
                yr = date.strftime("%Y")
                attribute = 'Challan'
                mycursor.execute(
                    "select * from challans where extract(year from date)='{yr}' and extract(month from date)='{mnth}' and ps_name='{ps}' ".format(
                        yr=yr, mnth=mnth, ps=str(current_user.username)))
                data = mycursor.fetchall()
                oltt = r['overloaded truck']
                os = r['over speed']
                dd = r['druken drive']
                wm = r['without mask']
                whs = r['without helmet/seatbelt']
                oc = r['others']
                if len(data) != 0 and m == mnth and yr == y:
                    id = data[0][0]
                    mycursor.execute(
                        "update challans set  overload_tripper_and_truck='{oltt}',over_speed='{os}', drunken_driving='{dd}',without_mask='{wm}',without_helmet_seatbelt='{whs}',other='{oc}' where id={id}".format(
                            id=id, oltt=oltt, os=os, dd=dd, wm=wm, whs=whs, oc=oc))
                    connection.commit()
                    mycursor.execute("UPDATE credentials SET date_challan='{d}' where username='{u}'; ".format(d=d,
                                                                                                               u=str(
                                                                                                                   current_user.username)))
                    connection.commit()
                    newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=d)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("done 1")
                elif len(data) != 0:
                    print("no duplications")
                else:
                    newchallan = challans(overload_tripper_and_truck=int(oltt),
                                          drunken_driving=int(dd),
                                          over_speed=int(os),
                                          without_mask=int(wm),
                                          without_helmet_seatbelt=int(whs),
                                          other=int(oc), date=date,
                                          ps_name=current_user.username)
                    db.session.add(newchallan)
                    db.session.commit()

                    mycursor.execute(
                        "UPDATE credentials SET date_challan='{d}' where username='{u}'; ".format(d=d, u=str(
                            current_user.username)))
                    connection.commit()

                    newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=d)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("done 2")

        ipcdata = pd.read_excel(file, sheet_name='Investigation Under IPC', header=[0, 1])
        for i, r in ipcdata.iterrows():
            if set(ipcdata.columns.ravel()) == {('UNDER INVESTIGATION', 'PENDING'), ('UNDER INVESTIGATION', 'DISPOSED'),
                                                ('CANCELLATION/UNTRACED', 'PENDING'),
                                                ('CANCELLATION/UNTRACED', 'DISPOSED (GIVEN IN COURT)'),
                                                ('UNDER INVESTIGATION   OVER ONE YEAR', 'PENDING'),
                                                ('UNDER INVESTIGATION   OVER ONE YEAR', 'DISPOSED'),
                                                ('UNDER INVESTIGATION   OVER SIX MONTH', 'PENDING'),
                                                ('UNDER INVESTIGATION   OVER SIX MONTH', 'DISPOSED'),
                                                ('UNDER INVESTIGATION   OVER THREE MONTH', 'PENDING'),
                                                ('UNDER INVESTIGATION   OVER THREE MONTH', 'DISPOSED'),
                                                ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'PENDING'),
                                                ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'DISPOSED'),
                                                ('DATE', 'DATE')}:

                date = datetime.datetime.strptime(ipcdata.loc[i, ('DATE', 'DATE')], '%Y-%m')
                dtoday = datetime.date.today()
                mtoday = dtoday.strftime("%m")
                ytoday = dtoday.strftime("%Y")
                m1 = date.strftime('%b')
                mnth = date.strftime("%m")
                yr = date.strftime("%Y")
                cate = 'under_ipc'
                attribute = 'investigation ' + cate
                mycursor.execute(
                    "select * from investigation where category='{c}' and extract(year from date)='{yr}' and extract(month from date)='{mnth}' and name_ps='{ps}' "
                    .format(yr=yr, c=cate, mnth=mnth, ps=str(current_user.username)))
                data = mycursor.fetchall()

                put = int(ipcdata.loc[i, ('CANCELLATION/UNTRACED', 'PENDING')])
                dut = int(ipcdata.loc[i, ('CANCELLATION/UNTRACED', 'DISPOSED (GIVEN IN COURT)')])
                plt3 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'PENDING')])
                dlt3 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'DISPOSED')])
                p3 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER THREE MONTH', 'PENDING')])
                d3 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER THREE MONTH', 'DISPOSED')])
                p6 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER SIX MONTH', 'PENDING')])
                d6 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER SIX MONTH', 'DISPOSED')])
                p12 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER ONE YEAR', 'PENDING')])
                d12 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER ONE YEAR', 'DISPOSED')])

                pending_ui = p3 + p6 + p12 + plt3
                disposed_ui = d3 + d6 + d12 + dlt3

                pui = pending_ui
                dui = disposed_ui

                if len(data) != 0 and mtoday == mnth and ytoday == yr:
                    id = data[0][0]
                    mycursor.execute(
                        "update investigation set date='{d1}',pending_ui ='{pui}', dispose_ui ='{dui}', pending_ut ='{put}', dispose_ut ='{dut}', _3_pending_ui ='{p3}', _3_dispose_ui ='{d3}', _6_pending_ui ='{p6}', _6_dispose_ui ='{d6}', _12_pending_ui ='{p12}', _12_dispose_ui ='{d12}', _lt3_pending_ui ='{plt3}', _lt3_dispose_ui ='{dlt3}' where id={id}"
                            .format(id=id, d1=date, pui=pui, dui=dui, put=put, dut=dut, plt3=plt3, dlt3=dlt3, p3=p3,
                                    d3=d3,
                                    p6=p6,
                                    d6=d6, p12=p12, d12=d12))
                    connection.commit()
                    newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    mycursor.execute(
                       "UPDATE credentials SET date_investigation='{d}' where username='{u}'; ".format(d=dtoday, u=str(
                            current_user.username)))
                    connection.commit()
                    print("under ipc 1")
                elif len(data) != 0:
                    print("under ipc no duplications")
                else:
                    newinvestigation = investigation(d=date, nps=current_user.username, pui=pending_ui,
                                                     dui=disposed_ui,
                                                     put=put, dut=dut,
                                                     lttd=dlt3, lttp=plt3,
                                                     cate=cate, tpui=p3,
                                                     tdui=d3,
                                                     spui=p6, sdui=d6,
                                                     twpui=p12, twdui=d12)
                    db.session.add(newinvestigation)
                    db.session.commit()
                    mycursor.execute(
                        "UPDATE credentials SET date_investigation='{d}' where username='{u}'; ".format(d=dtoday, u=str(
                            current_user.username)))
                    connection.commit()
                    newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("under ipc 2")

        localdata = pd.read_excel(file, sheet_name='Investigation Under Local & Special Law', header=[0, 1])
        for i, r in localdata.iterrows():
            if set(localdata.columns.ravel()) == {('UNDER INVESTIGATION', 'PENDING'),
                                                  ('UNDER INVESTIGATION', 'DISPOSED'),
                                                  ('CANCELLATION/UNTRACED', 'PENDING'),
                                                  ('CANCELLATION/UNTRACED', 'DISPOSED (GIVEN IN COURT)'),
                                                  ('UNDER INVESTIGATION   OVER ONE YEAR', 'PENDING'),
                                                  ('UNDER INVESTIGATION   OVER ONE YEAR', 'DISPOSED'),
                                                  ('UNDER INVESTIGATION   OVER SIX MONTH', 'PENDING'),
                                                  ('UNDER INVESTIGATION   OVER SIX MONTH', 'DISPOSED'),
                                                  ('UNDER INVESTIGATION   OVER THREE MONTH', 'PENDING'),
                                                  ('UNDER INVESTIGATION   OVER THREE MONTH', 'DISPOSED'),
                                                  ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'PENDING'),
                                                  ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'DISPOSED'),
                                                  ('DATE', 'DATE')}:

                date = datetime.datetime.strptime(localdata.loc[i, ('DATE', 'DATE')], '%Y-%m')
                dtoday = datetime.date.today()
                mtoday = dtoday.strftime("%m")
                ytoday = dtoday.strftime("%Y")
                m1 = date.strftime('%b')
                mnth = date.strftime("%m")
                yr = date.strftime("%Y")
                cate = 'under_local'
                attribute = 'investigation ' + cate
                mycursor.execute(
                    "select * from investigation where category='{c}' and extract(year from date)='{yr}' and extract(month from date)='{mnth}' and name_ps='{ps}' "
                    .format(yr=yr, c=cate, mnth=mnth, ps=str(current_user.username)))
                data = mycursor.fetchall()

                put = int(localdata.loc[i, ('CANCELLATION/UNTRACED', 'PENDING')])
                dut = int(localdata.loc[i, ('CANCELLATION/UNTRACED', 'DISPOSED (GIVEN IN COURT)')])
                plt3 = int(localdata.loc[i, ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'PENDING')])
                dlt3 = int(localdata.loc[i, ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'DISPOSED')])
                p3 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER THREE MONTH', 'PENDING')])
                d3 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER THREE MONTH', 'DISPOSED')])
                p6 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER SIX MONTH', 'PENDING')])
                d6 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER SIX MONTH', 'DISPOSED')])
                p12 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER ONE YEAR', 'PENDING')])
                d12 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER ONE YEAR', 'DISPOSED')])

                pending_ui = p3 + p6 + p12 + plt3
                disposed_ui = d3 + d6 + d12 + dlt3

                pui = pending_ui
                dui = disposed_ui

                if len(data) != 0 and mtoday == mnth and ytoday == yr:
                    id = data[0][0]
                    mycursor.execute(
                        "update investigation set date='{d1}',pending_ui ='{pui}', dispose_ui ='{dui}', pending_ut ='{put}', dispose_ut ='{dut}', _3_pending_ui ='{p3}', _3_dispose_ui ='{d3}', _6_pending_ui ='{p6}', _6_dispose_ui ='{d6}', _12_pending_ui ='{p12}', _12_dispose_ui ='{d12}', _lt3_pending_ui ='{plt3}', _lt3_dispose_ui ='{dlt3}' where id={id}"
                            .format(id=id, d1=date, pui=pui, dui=dui, put=put, dut=dut, plt3=plt3, dlt3=dlt3, p3=p3,
                                    d3=d3,
                                    p6=p6,
                                    d6=d6, p12=p12, d12=d12))
                    connection.commit()
                    newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    mycursor.execute(
                       "UPDATE credentials SET date_investigation='{d}' where username='{u}'; ".format(d=dtoday, u=str(
                            current_user.username)))
                    connection.commit()

                    print("under local 1")
                elif len(data) != 0:
                    print("under local no duplications")
                else:
                    newinvestigation = investigation(d=date, nps=current_user.username, pui=pending_ui,
                                                     dui=disposed_ui,
                                                     put=put, dut=dut,
                                                     lttd=dlt3, lttp=plt3,
                                                     cate=cate, tpui=p3,
                                                     tdui=d3,
                                                     spui=p6, sdui=d6,
                                                     twpui=p12, twdui=d12)
                    db.session.add(newinvestigation)
                    db.session.commit()
                    mycursor.execute(
                        "UPDATE credentials SET date_investigation='{d}' where username='{u}'; ".format(d=dtoday, u=str(
                            current_user.username)))
                    connection.commit()
                    newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("under local 2")

        rdata =  pd.read_excel(file, sheet_name='Recovery')
        for i,r  in rdata.iterrows():
            if set(rdata.columns.ravel()) == {'ILLICIT LIQUOR', 'LICIT LIQUOR', 'LAHAN', 'OPIUM', 'POPPY HUSK',
                                              'HEROIN', 'CHARAS ', 'GANJA', 'TABLETS', 'INJECTION  ', 'OTHERS', 'DATE'}:
                date = datetime.datetime.strptime(r['DATE'],'%Y-%m')
                dtoday = datetime.date.today()
                mtoday = dtoday.strftime("%m")
                ytoday = dtoday.strftime("%Y")
                m1=date.strftime('%b')
                mnth = date.strftime("%m")
                yr = date.strftime("%Y")
                attribute='Recovery'
                mycursor.execute(
                    "select * from recoveries where extract(year from date)='{yr}' and extract(month from date)='{mnth}' and ps_name='{ps}' "
                    .format(yr=yr, mnth=mnth, ps=str(current_user.username)))
                data = mycursor.fetchall()
                il = r['ILLICIT LIQUOR']
                li = r['LICIT LIQUOR']
                la = r['LAHAN']
                op = r['OPIUM']
                po = r['POPPY HUSK']
                he = r['HEROIN']
                ch = r['CHARAS ']
                ga = r['GANJA']
                inj = r['INJECTION  ']
                ta = r['TABLETS']
                ot = r['OTHERS']
                if len(data) != 0 and mtoday == mnth and yr == ytoday:
                    id = data[0][0]
                    mycursor.execute(
                        "update recoveries set  illicit='{il}',licit='{li}', lahan='{la}',opium='{op}', poppy ='{po}',heroine='{he}' , charas = '{ch}',ganja= '{ga}',injections= '{inj}',tablets= '{ta}',other_recovery= '{ot}' where id={id}"
                            .format(id=id, il=il, li=li, la=la, op=op, po=po, he=he, ch=ch, ga=ga, inj=inj, ta=ta,
                                    ot=ot))

                    connection.commit()
                    mycursor.execute(
                        "UPDATE credentials SET date_recovery='{d}' where username='{u}'; ".format(
                            d=dtoday,
                            u=str(current_user.username)))
                    connection.commit()
                    newupdate = updation_track(nps= str(current_user.username), un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    print( "recovery Data Updated Successfully")
                elif len(data) != 0:
                    print("recovery Duplicate Submissions are not allowed")

                else:
                    new_recovery = recoveries(illicit=il, licit=li,
                                              lahan=la, opium=op,
                                              poppy=po, heroine=he,
                                              charas=ch, ganja=ga,
                                              injections=inj,
                                              tablets=ta,
                                              other_recovery=ot,
                                              date=date, ps_name=current_user.username)

                    db.session.add(new_recovery)
                    db.session.commit()
                    newupdate = updation_track(nps=current_user.username, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    mycursor.execute(
                        "UPDATE credentials SET date_recovery='{d}' where username='{u}'; ".format(
                            d=dtoday,
                            u=str(current_user.username)))
                    connection.commit()
                    print( "recovery submited successfully")

        flash("Data uploaded Successfully", category='success')
        return redirect(url_for('uploading'))
    return render_template("uploading.html", form=eform)




@app.route('/SSPuploading', methods=['POST', 'GET'])
@login_required(role="SSP")
def SSPuploading():
    eform = excelForm()
    if request.method == 'POST':
        file = request.files['uploadFile']
        rdata = pd.read_excel(file, sheet_name='Recovery')
        for i, r in rdata.iterrows():
            if set(rdata.columns.ravel()) == {'ILLICIT LIQUOR', 'LICIT LIQUOR', 'LAHAN', 'OPIUM', 'POPPY HUSK',
                                              'HEROIN', 'CHARAS ', 'GANJA', 'TABLETS', 'INJECTION  ', 'OTHERS', 'DATE','ps_name'}:
                date = datetime.datetime.strptime(r['DATE'], '%Y-%m')
                dtoday = datetime.date.today()
                ps = r['ps_name']
                m1 = date.strftime('%b')
                mnth = date.strftime("%m")
                yr = date.strftime("%Y")
                attribute = 'Recovery'
                mycursor.execute(
                    "select * from recoveries where extract(year from date)='{yr}' and extract(month from date)='{mnth}' and ps_name='{ps}' "
                        .format(yr=yr, mnth=mnth, ps=ps))
                data = mycursor.fetchall()
                il = r['ILLICIT LIQUOR']
                li = r['LICIT LIQUOR']
                la = r['LAHAN']
                op = r['OPIUM']
                po = r['POPPY HUSK']
                he = r['HEROIN']
                ch = r['CHARAS ']
                ga = r['GANJA']
                inj = r['INJECTION  ']
                ta = r['TABLETS']
                ot = r['OTHERS']
                if len(data) != 0 :
                    id = data[0][0]
                    mycursor.execute(
                        "update recoveries set  illicit='{il}',licit='{li}', lahan='{la}',opium='{op}', poppy ='{po}',heroine='{he}' , charas = '{ch}',ganja= '{ga}',injections= '{inj}',tablets= '{ta}',other_recovery= '{ot}' where id={id}"
                            .format(id=id, il=il, li=li, la=la, op=op, po=po, he=he, ch=ch, ga=ga, inj=inj, ta=ta,
                                    ot=ot))
                    connection.commit()

                    newupdate = updation_track(nps=ps, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("ssp recovery Data Updated Successfully")

                else:
                    new_recovery = recoveries(illicit=il, licit=li,
                                              lahan=la, opium=op,
                                              poppy=po, heroine=he,
                                              charas=ch, ganja=ga,
                                              injections=inj,
                                              tablets=ta,
                                              other_recovery=ot,
                                              date=date, ps_name=ps)

                    db.session.add(new_recovery)
                    db.session.commit()
                    newupdate = updation_track(nps=ps, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()

                    print(" SSP recovery submited successfully")

        cdata = pd.read_excel(file, sheet_name='Challan')
        if set(cdata.columns.ravel()) == {'overloaded truck', 'druken drive', 'over speed', 'without mask',
                                          'without helmet/seatbelt', 'others', 'date','ps_name'}:
            for i, r in cdata.iterrows():
                date = datetime.datetime.strptime(r['date'], "%Y-%m")
                d = datetime.date.today()
                m = d.strftime("%m")
                m1 = date.strftime('%b')
                y = d.strftime("%Y")
                mnth = date.strftime("%m")
                yr = date.strftime("%Y")
                attribute = 'Challan'
                ps = r['ps_name']
                mycursor.execute("select * from challans where extract(year from date)='{yr}' and extract(month from date)='{mnth}' and ps_name='{ps}' ".format( yr=yr, mnth=mnth, ps=ps))
                data = mycursor.fetchall()
                oltt = r['overloaded truck']
                os = r['over speed']
                dd = r['druken drive']
                wm = r['without mask']
                whs = r['without helmet/seatbelt']
                oc = r['others']
                if len(data) != 0 :
                    id = data[0][0]
                    mycursor.execute(
                        "update challans set  overload_tripper_and_truck='{oltt}',over_speed='{os}', drunken_driving='{dd}',without_mask='{wm}',without_helmet_seatbelt='{whs}',other='{oc}' where id={id}".format(
                            id=id, oltt=oltt, os=os, dd=dd, wm=wm, whs=whs, oc=oc))
                    connection.commit()

                    newupdate = updation_track(nps=ps, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=d)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("ssp done 1")

                else:
                    newchallan = challans(overload_tripper_and_truck=int(oltt),
                                          drunken_driving=int(dd),
                                          over_speed=int(os),
                                          without_mask=int(wm),
                                          without_helmet_seatbelt=int(whs),
                                          other=int(oc), date=date,
                                          ps_name=ps)
                    db.session.add(newchallan)
                    db.session.commit()


                    newupdate = updation_track(nps=ps, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=d)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("ssp done 2")

        mdata = pd.read_excel(file, sheet_name='Marks', header=[0, 1])

        if set(mdata.columns.ravel()) == {('Name of PS', 'Unnamed: 0_level_1'),
                                          ('1 Point for 10 %caes submitted in court', 'Unnamed: 1_level_1'),
                                          ('Number', 'Unnamed: 2_level_1'), (
                                          'Undetected cases traced of Henius Crime -\n 2 points on tracing 1 case',
                                          'Unnamed: 3_level_1'), ('Number', 'Unnamed: 4_level_1'), (
                                          'Unraced cases of crime against  property -\n 1 points on tracing 10% of  cases',
                                          'Unnamed: 5_level_1'), ('Number', 'Unnamed: 6_level_1'), (
                                          'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                                          'NDPS \n '), (
                                          'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                                          'COMMERCIAL RECOVERY '), (
                                          'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                                          'ARM ACT '), (
                                          'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                                          'EXCISE ACT \n'), (
                                          'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                                          'GAMBLING ACT \n'), ('Number', 'Unnamed: 12_level_1'),
                                          ('1 point on 10% of Disposal of complaints', 'Unnamed: 13_level_1'),
                                          ('Number', 'Unnamed: 14_level_1'),
                                          ('1 point on 10 property disposal', 'Unnamed: 15_level_1'),
                                          ('Number', 'Unnamed: 16_level_1'),
                                          ('2 point on arrest of 1 P.O.', 'Unnamed: 17_level_1'),
                                          ('Number', 'Unnamed: 18_level_1'),
                                          ('2 points on 5  untrace cases put in court', 'Unnamed: 19_level_1'),
                                          ('Number', 'Unnamed: 20_level_1'), (
                                          'Negligence in duty/public dealing/ image in public and feedback\nfor +ve = 5\nFor -ve = -5',
                                          'Unnamed: 21_level_1'),
                                          ('Cleaniness of Police Staion ', 'Unnamed: 22_level_1'),
                                          ('Handling of Law & order Situation +5', 'Unnamed: 23_level_1'),
                                          ('Marks obtained ', 'Unnamed: 24_level_1'),
                                          ('Ranking', 'Unnamed: 25_level_1'), ('DATE', 'DATE')}:
            for i, r in mdata.iterrows():

                date = datetime.datetime.strptime(mdata.loc[i, ('DATE', 'DATE')], '%Y-%m')
                date1 = date.strftime('%Y-%m')
                date2 = date.strftime('%Y-%m-%d')
                print(date1)
                ps = mdata.loc[i, ('Name of PS', 'Unnamed: 0_level_1')]

                attribute = 'Marks'
                m1 = date.strftime('%b')
                yr = date.strftime('%Y')
                dtoday = datetime.datetime.today()
                mycursor.execute(
                    "select id from marks where ps_name='{ps}' and to_char(date ,'YYYY-MM')='{d}'".format(ps=ps,
                                                                                                          d=date1))
                data = mycursor.fetchall()
               # print(data)
                # print(type(mdata.loc[i,('1 Point for 10 %caes submitted in court', 'Unnamed: 1_level_1')]))
                pocsic = int(mdata.loc[i, ('1 Point for 10 %caes submitted in court', 'Unnamed: 1_level_1')] * 100)
                cohc = int(mdata.loc[i, (
                'Undetected cases traced of Henius Crime -\n 2 points on tracing 1 case', 'Unnamed: 3_level_1')])
                cap = int(mdata.loc[i, (
                'Unraced cases of crime against  property -\n 1 points on tracing 10% of  cases',
                'Unnamed: 5_level_1')] * 100)
                n = int(mdata.loc[i, (
                'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                'NDPS \n ')])
                cr = int(mdata.loc[i, (
                'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                'COMMERCIAL RECOVERY ')])
                ac = int(mdata.loc[i, (
                'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                'ARM ACT ')])
                ea = int(mdata.loc[i, (
                'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                'EXCISE ACT \n')])
                ga = int(mdata.loc[i, (
                'Cases registerd under Detection work \n(Total Points - 10)\n5 cases of NDPS - 2 Point\n(2 extra points on every Commercial recoery) \nArms Act -  1 point on 1 case \nExcise Act - 1 point on 5 cases\nGambling Act  - 1 point on 5 cases  \n',
                'GAMBLING ACT \n')])
                podoc = int(mdata.loc[i, ('1 point on 10% of Disposal of complaints', 'Unnamed: 13_level_1')] * 100)
                popd = int(mdata.loc[i, ('1 point on 10 property disposal', 'Unnamed: 15_level_1')])
                aop = int(mdata.loc[i, ('2 point on arrest of 1 P.O.', 'Unnamed: 17_level_1')])
                ucpic = int(mdata.loc[i, ('2 points on 5  untrace cases put in court', 'Unnamed: 19_level_1')])
                ne = int(mdata.loc[i, (
                'Negligence in duty/public dealing/ image in public and feedback\nfor +ve = 5\nFor -ve = -5',
                'Unnamed: 21_level_1')])
                c = int(mdata.loc[i, ('Cleaniness of Police Staion ', 'Unnamed: 22_level_1')])
                hol = int(mdata.loc[i, ('Handling of Law & order Situation +5', 'Unnamed: 23_level_1')])

                if len(data) != 0:
                    id = data[0][0]
                #    print(id)
                    #  print(pocsic,cohc,cap,n,cr,ac)
                    mycursor.execute(
                        "update marks set percent_of_cases_submitted_in_court= '{pocsic}', cases_of_henius_crime='{cohc}',crime_against_property='{cap}',ndps='{n}',commercial_recovery='{cr}',"
                        "arm_act='{ac}',excise_act='{ea}',gambling_act='{ga}',percent_of_disposal_of_complaints='{podoc}',percent_of_property_disposal='{popd}',arrest_of_po='{aop}',untrace_cases_put_in_court='{ucpic}',"
                        "negligence='{ne}',cleanliness='{c}',handling_of_law='{hol}' where id='{id}'"
                        .format(id=id, pocsic=pocsic, cohc=cohc, cap=cap, n=n, cr=cr, ac=ac, ea=ea, ga=ga, podoc=podoc,
                                popd=popd, aop=aop, ucpic=ucpic, ne=ne, c=c, hol=hol))
                    connection.commit()
                    newupdate = updation_track(nps=ps, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("updated data")

                else:
                    newmarks = marks(ps_name=ps,
                         percent_of_cases_submitted_in_court=pocsic,
                         cases_of_henius_crime=cohc,
                         crime_against_property=cap, ndps=n,
                         commercial_recovery=cr,
                         arm_act=ac, excise_act=ea,
                         gambling_act=ga,
                         percent_of_disposal_of_complaints=podoc,
                         percent_of_property_disposal=popd,
                         arrest_of_po=aop,
                         untrace_cases_put_in_court=ucpic,
                         negligence=ne,
                         date=date2,
                         cleanliness=c, handling_of_law=hol
                         )
                    db.session.add(newmarks)
                    db.session.commit()
                    newupdate = updation_track(nps=ps, un=current_user.username, a=attribute, md=m1,
                                               yr=yr, ud=dtoday)
                    db.session.add(newupdate)
                    db.session.commit()
                    print("inserted marks")

          #  print(pd.ExcelFile(file).sheet_names)
            ipcdata = pd.read_excel(file, sheet_name='Investigation Under IPC', header=[0, 1])
            for i, r in ipcdata.iterrows():
              #  print(ipcdata.loc[i,('PS_NAME','PS_NAME')])
                if set(ipcdata.columns.ravel()) == {('PS_NAME','PS_NAME'),('UNDER INVESTIGATION', 'PENDING'),
                                                    ('UNDER INVESTIGATION', 'DISPOSED'),
                                                    ('CANCELLATION/UNTRACED', 'PENDING'),
                                                    ('CANCELLATION/UNTRACED', 'DISPOSED (GIVEN IN COURT)'),
                                                    ('UNDER INVESTIGATION   OVER ONE YEAR', 'PENDING'),
                                                    ('UNDER INVESTIGATION   OVER ONE YEAR', 'DISPOSED'),
                                                    ('UNDER INVESTIGATION   OVER SIX MONTH', 'PENDING'),
                                                    ('UNDER INVESTIGATION   OVER SIX MONTH', 'DISPOSED'),
                                                    ('UNDER INVESTIGATION   OVER THREE MONTH', 'PENDING'),
                                                    ('UNDER INVESTIGATION   OVER THREE MONTH', 'DISPOSED'),
                                                    ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'PENDING'),
                                                    ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'DISPOSED'),
                                                    ('DATE', 'DATE')}:
                    # print(ipcdata.loc[i,('DATE','DATE')])
                    ps=ipcdata.loc[i,('PS_NAME','PS_NAME')]
                    date = datetime.datetime.strptime(ipcdata.loc[i, ('DATE', 'DATE')], '%Y-%m')
                    dtoday = datetime.date.today()
                    mtoday = dtoday.strftime("%m")
                    ytoday = dtoday.strftime("%Y")
                    m1 = date.strftime('%b')
                    mnth = date.strftime("%m")
                    yr = date.strftime("%Y")
                    cate = 'under_ipc'
                    attribute = 'investigation ' + cate
                    mycursor.execute(
                        "select * from investigation where category='{c}' and extract(year from date)='{yr}' and extract(month from date)='{mnth}' and name_ps='{ps}' "
                            .format(yr=yr, c=cate, mnth=mnth, ps=ps))
                    data = mycursor.fetchall()

                    put = int(ipcdata.loc[i, ('CANCELLATION/UNTRACED', 'PENDING')])
                    dut = int(ipcdata.loc[i, ('CANCELLATION/UNTRACED', 'DISPOSED (GIVEN IN COURT)')])
                    plt3 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'PENDING')])
                    dlt3 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'DISPOSED')])
                    p3 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER THREE MONTH', 'PENDING')])
                    d3 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER THREE MONTH', 'DISPOSED')])
                    p6 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER SIX MONTH', 'PENDING')])
                    d6 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER SIX MONTH', 'DISPOSED')])
                    p12 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER ONE YEAR', 'PENDING')])
                    d12 = int(ipcdata.loc[i, ('UNDER INVESTIGATION   OVER ONE YEAR', 'DISPOSED')])

                    pending_ui = p3 + p6 + p12 + plt3
                    disposed_ui = d3 + d6 + d12 + dlt3

                    pui = pending_ui
                    dui = disposed_ui

                    if len(data) != 0 :
                        id = data[0][0]
                        mycursor.execute(
                            "update investigation set date='{d1}',pending_ui ='{pui}', dispose_ui ='{dui}', pending_ut ='{put}', dispose_ut ='{dut}', _3_pending_ui ='{p3}', _3_dispose_ui ='{d3}', _6_pending_ui ='{p6}', _6_dispose_ui ='{d6}', _12_pending_ui ='{p12}', _12_dispose_ui ='{d12}', _lt3_pending_ui ='{plt3}', _lt3_dispose_ui ='{dlt3}' where id={id}"
                                .format(id=id, d1=date, pui=pui, dui=dui, put=put, dut=dut, plt3=plt3, dlt3=dlt3, p3=p3,
                                        d3=d3,
                                        p6=p6,
                                        d6=d6, p12=p12, d12=d12))
                        connection.commit()
                        newupdate = updation_track(nps=ps, un=current_user.username, a=attribute,
                                                   md=m1,
                                                   yr=yr, ud=dtoday)
                        db.session.add(newupdate)
                        db.session.commit()
                        mycursor.execute(
                            "UPDATE notification SET investigation_date='{d}' where name_ps='{u}'; ".format(d=dtoday,
                                                                                                            u=ps))
                        connection.commit()
                        print("ssp under ipc 1")

                    else:
                        newinvestigation = investigation(d=date, nps=ps, pui=pending_ui,
                                                         dui=disposed_ui,
                                                         put=put, dut=dut,
                                                         lttd=dlt3, lttp=plt3,
                                                         cate=cate, tpui=p3,
                                                         tdui=d3,
                                                         spui=p6, sdui=d6,
                                                         twpui=p12, twdui=d12)
                        db.session.add(newinvestigation)
                        db.session.commit()
                        mycursor.execute(
                            "UPDATE notification SET investigation_date='{d}' where name_ps='{u}'; ".format(d=dtoday,
                                                                                                            u=ps))
                        connection.commit()
                        newupdate = updation_track(nps=ps, un=current_user.username, a=attribute,
                                                   md=m1,
                                                   yr=yr, ud=dtoday)
                        db.session.add(newupdate)
                        db.session.commit()
                        print("ssp under ipc 2")

            localdata = pd.read_excel(file, sheet_name='Investigation Under Local & Special Law', header=[0, 1])
            for i, r in localdata.iterrows():
              #  print(localdata.loc[i,('PS_NAME','PS_NAME')])
                if set(localdata.columns.ravel()) == {('PS_NAME','PS_NAME'),('UNDER INVESTIGATION', 'PENDING'),
                                                      ('UNDER INVESTIGATION', 'DISPOSED'),
                                                      ('CANCELLATION/UNTRACED', 'PENDING'),
                                                      ('CANCELLATION/UNTRACED', 'DISPOSED (GIVEN IN COURT)'),
                                                      ('UNDER INVESTIGATION   OVER ONE YEAR', 'PENDING'),
                                                      ('UNDER INVESTIGATION   OVER ONE YEAR', 'DISPOSED'),
                                                      ('UNDER INVESTIGATION   OVER SIX MONTH', 'PENDING'),
                                                      ('UNDER INVESTIGATION   OVER SIX MONTH', 'DISPOSED'),
                                                      ('UNDER INVESTIGATION   OVER THREE MONTH', 'PENDING'),
                                                      ('UNDER INVESTIGATION   OVER THREE MONTH', 'DISPOSED'),
                                                      ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'PENDING'),
                                                      ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'DISPOSED'),
                                                      ('DATE', 'DATE')}:
                    # print(localdata.loc[i,('DATE','DATE')])
                    ps=localdata.loc[i,('PS_NAME','PS_NAME')]
                    date = datetime.datetime.strptime(localdata.loc[i, ('DATE', 'DATE')], '%Y-%m')
                    dtoday = datetime.date.today()
                    mtoday = dtoday.strftime("%m")
                    ytoday = dtoday.strftime("%Y")
                    m1 = date.strftime('%b')
                    mnth = date.strftime("%m")
                    yr = date.strftime("%Y")
                    cate = 'under_local'
                    attribute = 'investigation ' + cate
                    mycursor.execute(
                        "select * from investigation where category='{c}' and extract(year from date)='{yr}' and extract(month from date)='{mnth}' and name_ps='{ps}' "
                            .format(yr=yr, c=cate, mnth=mnth, ps=ps))
                    data = mycursor.fetchall()

                    put = int(localdata.loc[i, ('CANCELLATION/UNTRACED', 'PENDING')])
                    dut = int(localdata.loc[i, ('CANCELLATION/UNTRACED', 'DISPOSED (GIVEN IN COURT)')])
                    plt3 = int(localdata.loc[i, ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'PENDING')])
                    dlt3 = int(localdata.loc[i, ('UNDER INVESTIGATION   LESS THAN THREE MONTH', 'DISPOSED')])
                    p3 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER THREE MONTH', 'PENDING')])
                    d3 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER THREE MONTH', 'DISPOSED')])
                    p6 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER SIX MONTH', 'PENDING')])
                    d6 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER SIX MONTH', 'DISPOSED')])
                    p12 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER ONE YEAR', 'PENDING')])
                    d12 = int(localdata.loc[i, ('UNDER INVESTIGATION   OVER ONE YEAR', 'DISPOSED')])

                    pending_ui = p3 + p6 + p12 + plt3
                    disposed_ui = d3 + d6 + d12 + dlt3

                    pui = pending_ui
                    dui = disposed_ui

                    if len(data) != 0 :
                        id = data[0][0]
                        mycursor.execute(
                            "update investigation set date='{d1}',pending_ui ='{pui}', dispose_ui ='{dui}', pending_ut ='{put}', dispose_ut ='{dut}', _3_pending_ui ='{p3}', _3_dispose_ui ='{d3}', _6_pending_ui ='{p6}', _6_dispose_ui ='{d6}', _12_pending_ui ='{p12}', _12_dispose_ui ='{d12}', _lt3_pending_ui ='{plt3}', _lt3_dispose_ui ='{dlt3}' where id={id}"
                                .format(id=id, d1=date, pui=pui, dui=dui, put=put, dut=dut, plt3=plt3, dlt3=dlt3, p3=p3,
                                        d3=d3,
                                        p6=p6,
                                        d6=d6, p12=p12, d12=d12))
                        connection.commit()
                        newupdate = updation_track(nps=ps, un=current_user.username, a=attribute,
                                                   md=m1,
                                                   yr=yr, ud=dtoday)
                        db.session.add(newupdate)
                        db.session.commit()
                        mycursor.execute(
                            "UPDATE notification SET investigation_date='{d}' where name_ps='{u}'; ".format(d=dtoday,
                                                                                                            u=ps))
                        connection.commit()
                        print("ssp under local 1")

                    else:
                        newinvestigation = investigation(d=date, nps=ps, pui=pending_ui,
                                                         dui=disposed_ui,
                                                         put=put, dut=dut,
                                                         lttd=dlt3, lttp=plt3,
                                                         cate=cate, tpui=p3,
                                                         tdui=d3,
                                                         spui=p6, sdui=d6,
                                                         twpui=p12, twdui=d12)
                        db.session.add(newinvestigation)
                        db.session.commit()
                        mycursor.execute(
                            "UPDATE notification SET investigation_date='{d}' where name_ps='{u}'; ".format(d=dtoday,
                                                                                                            u=ps))
                        connection.commit()
                        newupdate = updation_track(nps=ps, un=current_user.username, a=attribute,
                                                   md=m1,
                                                   yr=yr, ud=dtoday)
                        db.session.add(newupdate)
                        db.session.commit()
                        print("ssp under local 2")



            flash("Data uploaded Successfully", category='success')
            return redirect(url_for('SSPuploading'))
    psLabels = ["ps1",'ps2','ps3','ps4','ps5','ps6','ps7','ps8','ps9','ps10']
    recent_update = []
    for x in psLabels:
        mycursor.execute("SELECT * from credentials where username='{0}' ".format(x))
        data = mycursor.fetchall()
        maximum = max(data[0][4], data[0][5], data[0][6])

        lst = [x, maximum.strftime('%d-%b-%Y')]
        recent_update.append(lst)
    return render_template("uploadingSSP.html", form=eform,lst = recent_update)


@app.route("/marksCriteria",methods=['GET',"POST"])
@login_required(role = "SSP")

def marksCriteria():
    return render_template('marksCriteria.html')


@app.route('/tablesSSP',methods=['GET',"POST"])
@login_required(role = "SSP")
def tablesSSP():
    d = datetime.datetime.today()
    # d = d + relativedelta(months=-1)
    d = d.strftime('%Y-%m')
    psLabels = ['ps1', 'ps2', 'ps3', 'ps4', 'ps5', 'ps6', 'ps7', 'ps8', 'ps9', 'ps10']
    values_all = []
    for x in psLabels:
        mycursor.execute("SELECT * from marks where ps_name='{0}' and to_char(date,'YYYY-MM')='{1}'".format(x, d))
        data = mycursor.fetchall()
        if data:
            values_all.extend(data)
        else:
            values_all.append((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    final_score = []
    final_mapping = []
    result = 0
    for j in range(len(values_all)):
        print(j, '  j')
        result = (values_all[j][2] * 0.1) + (values_all[j][3] * 2) + (values_all[j][4] * 0.1) + (
                values_all[j][5] * 0.4) + (values_all[j][6] * 2) + (values_all[j][7] * 1) + (
                         values_all[j][8] * 0.2) + (values_all[j][9] * 0.2) + (values_all[j][10] * 0.1) + (
                         values_all[j][11] * 0.1) + (values_all[j][12] * 2) + (values_all[j][13] * 0.4) + (
                     values_all[j][14]) + (values_all[j][15]) + (values_all[j][16])
        temp1 = values_all[j][1]
        tuple = (temp1, round(result, 2))
        combo = list(tuple)
        final_mapping.append(combo)

    final_mapping.sort(key=lambda x: x[1], reverse=True)
    for j in range(len(final_mapping)):
        final_mapping[j].append(j + 1)
    print(final_mapping)

    psLabels1 = [x[0] for x in final_mapping]
    psMarks = [x[1] for x in final_mapping]
    return render_template('tablesSSP.html',form=table(),psLabels1=psLabels1,psMarks=psMarks,values=final_mapping)


@app.route('/tables',methods=['GET',"POST"])
@login_required(role = "SSP")
def tables():
    if request.method=='GET':
        return jsonify({"htmlresponse": render_template('marksCriteria.html' )})

    elif request.method=='POST':
        ps=request.form['ps_name']
        date1 =request.form['from_date']
        date2  = request.form['to_date']

        if request.form['attribute']=='Marks':
            if date1 and date2:
                mycursor.execute("select * from marks where ps_name ='{ps}' and (to_char(date,'YYYY-MM') between '{d1}' and '{d2}')"
                                 .format(ps=ps, d1=date1, d2=date2))
                data = mycursor.fetchall()
            else:
                mycursor.execute("select * from marks where ps_name ='{ps}'".format(ps=ps))
                data = mycursor.fetchall()
            return jsonify({"htmlresponse": render_template('marksTable.html', data=data)})


        elif request.form['attribute']=='Challan':
            if date1 and date2:
                mycursor.execute("select * from challans where ps_name ='{ps}' and (to_char(date,'YYYY-MM') between '{d1}' and '{d2}')"
                                  .format(ps=ps,d1=date1,d2=date2))
                data = mycursor.fetchall()
            else:
                mycursor.execute("select * from challans where ps_name ='{ps}'".format(ps=ps))
                data = mycursor.fetchall()
            return jsonify({"htmlresponse": render_template('challanTable.html', data=data)})


        elif request.form['attribute'] == 'Recovery':
            if date1 and date2:
                mycursor.execute("select * from recoveries where ps_name ='{ps}' and (to_char(date,'YYYY-MM') between '{d1}' and '{d2}')"
                                 .format(ps=ps, d1=date1, d2=date2))
                data = mycursor.fetchall()
            else:
                mycursor.execute("select * from recoveries where ps_name ='{ps}'".format(ps=ps))
                data = mycursor.fetchall()
            return jsonify({"htmlresponse": render_template('recoveryTable.html', data=data)})


        elif request.form['attribute'] == 'Investigation under IPC':
            session["type"] ="IPC"
            if date1 and date2:
                mycursor.execute("select * from investigation where category='under_ipc' and name_ps ='{ps}' and (to_char(date,'YYYY-MM') between '{d1}' and '{d2}')"
                                 .format(ps=ps, d1=date1, d2=date2))
                data = mycursor.fetchall()
            else:
                mycursor.execute("select * from investigation where category='under_ipc' and name_ps ='{ps}'".format(ps=ps))
                data = mycursor.fetchall()
            return jsonify({"htmlresponse": render_template('investigationTable.html', data=data)})


        elif request.form['attribute'] == 'Investigation under Local & Special Law':
            session["type"] = "Local & Special Law"
            if date1 and date2:
                mycursor.execute("select * from investigation where category='under_local' and name_ps ='{ps}' and (to_char(date,'YYYY-MM') between '{d1}' and '{d2}')"
                    .format(ps=ps, d1=date1, d2=date2))
                data=mycursor.fetchall()
            else:
                mycursor.execute( "select * from investigation where category='under_local' and name_ps ='{ps}'".format(ps=ps))
                data = mycursor.fetchall()
            return jsonify({"htmlresponse": render_template('investigationTable.html',data=data)})

    return jsonify({"error": "re-try"})

@app.route('/edit_challan/<string:id>',methods=['GET','POST'])
@login_required(role = "SSP")
def edit_challan(id):

    mycursor.execute("select * from challans where id={0}".format(id))
    data =mycursor.fetchall()
    cform=challanForm()

    if request.method=='POST':
       # print('1111')
       # print(request.form)
        oltt = request.form.get('overload_truck')
        os   = request.form.get('over_speed')
        dd   = request.form.get('drunken_drive')
        wm   = request.form.get('without_mask')
        whs  = request.form.get('without_helmet_seatbelt')
        oc   = request.form.get('other_challan')

        #print(oltt,os,dd,wm,whs,oc,sep=" ")

        mycursor.execute("update challans set  overload_tripper_and_truck='{oltt}',over_speed='{os}', drunken_driving='{dd}',without_mask='{wm}',without_helmet_seatbelt='{whs}',other='{oc}' where id={id}"
                         .format(id=id,oltt=oltt,os=os,dd=dd,wm=wm,whs=whs,oc=oc))
        connection.commit()
        return redirect(url_for('tablesSSP'))
    return render_template('edit_challan.html',form=cform,data=data)


@app.route('/edit_recovery/<string:id>',methods=['GET','POST'])
@login_required(role = "SSP")
def edit_recovery(id):

    mycursor.execute("select * from recoveries where id={0}".format(id))
    data =mycursor.fetchall()
    rform=recoveryForm()

    if request.method=='POST':
      #  print(request.form)
        il = request.form.get('illicit')
        li   = request.form.get('licit')
        la   = request.form.get('lahan')
        op   = request.form.get('opium')
        po  = request.form.get('poppy')
        he   = request.form.get('heroine')
        ch  =  request.form.get('charas')
        ga  =   request.form.get('ganja')
        ta  =   request.form.get('tablets')
        inj =   request.form.get('injections')
        other =  request.form.get('other_recovery')

        #print(il,li,la,op,po,he,ch,ga,ta,inj,other,sep=" ")

        mycursor.execute("update recoveries set  illicit='{il}',licit='{li}',lahan='{la}',opium='{op}',poppy='{po}',heroine='{he}',charas='{ch}',ganja='{ga}',injections='{inj}',tablets='{ta}',other_recovery='{o}' where id={id}"
                         .format(id=id,il=il,li=li,la=la,op=op,po=po,he=he,ch=ch,ga=ga,ta=ta,inj=inj,o=other))
        connection.commit()
        return redirect(url_for('tablesSSP'))
    return render_template('edit_recovery.html',form=rform,data=data)


@app.route('/edit_investigation/<string:id>',methods=['GET','POST'])
@login_required(role = "SSP")
def edit_investigation(id):

    mycursor.execute("select * from investigation where id={0}".format(id))
    data =mycursor.fetchall()
    iform=investigationForm()

    if request.method=='POST':


        put  = request.form.get('pending_ut')
        dut  = request.form.get('dispose_ut')
        plt3 = request.form.get('pending_lt3_ui')
        dlt3 = request.form.get('dispose_lt3_ui')
        p3   = request.form.get('pending_3_ui')
        d3   = request.form.get('dispose_3_ui')
        p6   = request.form.get('pending_6_ui')
        d6   = request.form.get('dispose_6_ui')
        p12  = request.form.get('pending_12_ui')
        d12  = request.form.get('dispose_6_ui')

        pui =  int(plt3) + int(p3) + int(p6) + int(p12)
        dui = int(dlt3) + int(d3) + int(d6) + int(d12)



        mycursor.execute("update investigation set pending_ui ='{pui}', dispose_ui ='{dui}', pending_ut ='{put}', dispose_ut ='{dut}', _3_pending_ui ='{p3}', _3_dispose_ui ='{d3}', _6_pending_ui ='{p6}', _6_dispose_ui ='{d6}', _12_pending_ui ='{p12}', _12_dispose_ui ='{d12}', _lt3_pending_ui ='{plt3}', _lt3_dispose_ui ='{dlt3}' where id={id}"
            .format(id=id,pui=pui,dui=dui,put=put,dut=dut,plt3=plt3,dlt3=dlt3,p3=p3,d3=d3,p6=p6,d6=d6,p12=p12,d12=d12 ))
        connection.commit()
        return redirect(url_for('tablesSSP'))

    return render_template('edit_investigation.html',form=iform,data=data)

@app.route('/edit_marks/<string:id>',methods=['GET','POST'])
@login_required(role = "SSP")
def edit_marks(id):

    mycursor.execute("select * from marks where id={0}".format(id))
    data =mycursor.fetchall()
    mform=marksForm()

    if request.method=='POST':


        pcsc  = request.form.get('percent_of_cases_submitted_in_court')
        hc  = request.form.get('cases_of_henius_crime')
        cap  = request.form.get('crime_against_property')
        ndps  = request.form.get('ndps')
        cr = request.form.get('commercial_recovery')
        aa = request.form.get('arm_act')
        ea   = request.form.get('excise_act')
        ga   = request.form.get('gambling_act')
        pdc   = request.form.get('percent_of_disposal_of_complaints')
        ppd  = request.form.get('percent_of_property_disposal')
        apo  = request.form.get('arrest_of_po')
        ucc  = request.form.get('untrace_cases_put_in_court')
        ne = request.form.get('negligence')
        cl = request.form.get('cleanliness')
        hol = request.form.get('handling_of_law')


        mycursor.execute("update marks set  percent_of_cases_submitted_in_court ='{pcsc}', cases_of_henius_crime ='{hc}', crime_against_property ='{cap}', ndps ='{ndps}', commercial_recovery ='{cr}', arm_act='{aa}', excise_act ='{ea}', gambling_act ='{ga}', percent_of_disposal_of_complaints ='{pdc}', percent_of_property_disposal ='{ppd}', arrest_of_po ='{apo}', untrace_cases_put_in_court ='{ucc}', negligence ='{ne}', cleanliness ='{cl}', handling_of_law ='{hol}' where id={id}"
            .format(id=id,pcsc=pcsc,hc=hc,cap=cap,ndps=ndps,cr=cr,aa=aa,ea=ea,ga=ga,pdc=pdc,ppd=ppd,apo=apo,ucc=ucc,ne=ne,cl=cl,hol=hol ))
        connection.commit()
        return redirect(url_for('tablesSSP'))

    return render_template('edit_marks.html',form=mform,data=data)



@app.route('/test', methods=['GET', 'POST'])
def test():
    output = "hello "
    if request.method == 'POST':
        #  user1=request.form['ps_name1']
        mycursor.execute("SELECT * FROM challans WHERE ps_Name='user1' ORDER BY date ")
        data = mycursor.fetchall()
        values = [0, 0, 0, 0, 0, 0]
        for j in range(len(data)):
            values[0] += data[j][1]
            values[5] += data[j][6]
            values[1] += data[j][2]
            values[2] += data[j][3]
            values[3] += data[j][4]
            values[4] += data[j][5]
        labels = ['overloadedTruck', 'drunkenDrive', 'overSpeed', 'withoutMask', 'without_helmet_seatbelt',
                  'others']
    return jsonify({'htmlresponse': render_template('new.html', values=values, labels=labels)})

@app.route('/output',methods=['GET','POST'])
def output():
    x=request.args.get('ps1')
    y=request.args.get('ps2')
    z=request.args.get('attributef')
    if z == 'challan':
        mycursor.execute("SELECT * FROM challans WHERE ps_Name='{0}' ORDER BY date ".format(str(x)))
        ssp_data = mycursor.fetchall()
        values3=[0,0,0,0,0,0]
        for j in range(len(ssp_data)):
            values3[0]+=ssp_data[j][0]
            values3[1] += ssp_data[j][0]
            values3[1] += ssp_data[j][1]
            values3[2] += ssp_data[j][2]
            values3[3] += ssp_data[j][3]
            values3[4] += ssp_data[j][4]
        mycursor.execute("SELECT * FROM challans WHERE ps_Name='{0}' ORDER BY date ".format(str(y)))
        ssp_data = mycursor.fetchall()
        values4 = [0, 0, 0, 0, 0, 0]
        for j in range(len(ssp_data)):
            values4[0] += ssp_data[j][0]
            values4[1] += ssp_data[j][0]
            values4[1] += ssp_data[j][1]
            values4[2] += ssp_data[j][2]
            values4[3] += ssp_data[j][3]
            values4[4] += ssp_data[j][4]
        labels2 = ['overloadedTruck','drunkenDrive','overSpeed','withoutMask','without_helmet_seatbelt','others']
    return render_template('output.html',ps1=request.args.get('ps1'),ps2=request.args.get('ps2'),attributef=request.args.get('attributef'),
                           values=values3, values1=values4,labels=labels2,x=x,y=y)


@app.route('/mark', methods=['GET', 'POST'])
@login_required(role = "SSP")
def mark():
    d = datetime.datetime.today()
   # d = d + relativedelta(months=-1)
    d=d.strftime('%Y-%m')
    psLabels=['ps1','ps2','ps3','ps4','ps5','ps6','ps7','ps8','ps9','ps10']
    values_all=[]
    for x in psLabels:
        mycursor.execute("SELECT * from marks where ps_name='{0}' and to_char(date,'YYYY-MM')='{1}'".format(x,d))
        data= mycursor.fetchall()
        if data:
            values_all.extend(data)
        else:
            values_all.append((0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))

    final_score = []
    final_mapping = []
    result = 0
    for j in range(len(values_all)):
        print(j,'  j')
        result = (values_all[j][2] * 0.1) + (values_all[j][3] * 2) + (values_all[j][4] * 0.1) + (
                values_all[j][5] * 0.4) + (values_all[j][6] * 2) + (values_all[j][7] * 1) + (
                         values_all[j][8] * 0.2) + (values_all[j][9] * 0.2) + (values_all[j][10] * 0.1) + (
                         values_all[j][11] * 0.1) + (values_all[j][12] * 2) + (values_all[j][13] * 0.4) + (
                     values_all[j][14]) + (values_all[j][15]) + (values_all[j][16])
        temp1 = values_all[j][1]
        tuple = (temp1, round(result, 2))
        combo = list(tuple)
        final_mapping.append(combo)


    final_mapping.sort(key=lambda x: x[1], reverse=True)
    for j in range(len(final_mapping)):
        final_mapping[j].append(j + 1)
    print(final_mapping)

    psLabels1 = [x[0] for x in final_mapping]
    psMarks  = [x[1] for x in final_mapping]

    ##for graphs 1
    labels1 = ['ps1', 'ps2', 'ps3', 'ps4', 'ps5', 'ps6', 'ps7', 'ps8', 'ps9', 'ps10']
    values1 = []
    values2 = []
    values3 = []
    values4 = []
    values100 = []  ###values[5] initially

    data=[]
    for x in psLabels:
        mycursor.execute("SELECT * from marks where ps_name='{0}' and to_char(date,'YYYY-MM')='{1}'".format(x, d))
        val = mycursor.fetchall()
        if val:
            data.extend(val)
        else:
            data.append((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))


    print(psLabels)
    for j in range(0, 10):
        a = data[j][3] * 2
        values1.append(a)
    for j in range(0, 10):
        a = ((data[j][5] / 5) * 2) + (data[j][6] * 2) + (data[j][7]) + (data[j][8] / 5) + (data[j][9] / 5)
        a = round(a, 2)
        values2.append(a)
    for j in range(0, 10):
        a = (data[j][11] / 10)
        values3.append(a)
    for j in range(0, 10):
        a = data[j][12] * 2
        values4.append(a)
    for j in range(0, 10):
        a = (data[j][13] / 5) * 2
        values100.append(a)  ## to be seen
    # return render_template("marks.html", values1=values1, values2=values2, values3=values3, values4=values4,
    #                        values100=values100, labels1=labels1)   ##here five values are there check it

    # for graph 2
    labelsG2 = ['ps1', 'ps2', 'ps3', 'ps4', 'ps5', 'ps6', 'ps7', 'ps8', 'ps9', 'ps10']
    valuesG2_1 = []
    valuesG2_2 = []
    valuesG2_3 = []
    valuesG2_4 = []
    valuesG2_5 = []
   # mycursor.execute("SELECT * FROM marks where to_char(date,'YYYY-MM')='{0}'".format(d))
   # data = mycursor.fetchall()
    # print(data)
    for j in range(0, 10):
        valuesG2_1.append(data[j][5])
    for j in range(0, 10):
        valuesG2_2.append(data[j][6])
    for j in range(0, 10):
        valuesG2_3.append(data[j][7])
    for j in range(0, 10):
        valuesG2_4.append(data[j][8])
    for j in range(0, 10):
        valuesG2_5.append(data[j][9])

    ###### doughnut graphs##################################################
   # mycursor.execute("select  * from marks where to_char(date,'YYYY-MM')='{0}'".format(d))
   # data = mycursor.fetchall()
    data_negligence = [x[14] for x in data]
    data_cleanliness = [x[15] for x in data]
    data_handling_law = [x[16] for x in data]
   # labels = [x[3] for x in data]
    # print(data_cleanliness,data_handling_law,data_handling_law,sep="\n")
    # return render_template("index.html", data_handling_law=data_handling_law, data_cleanliness=data_cleanliness,
    #                        data_negligence=data_negligence, labels=labels)

    valuesb1 = []  # percent of cases submitted in the court
    valuesb2 = []  # percent of disposal complaints
    valuesb3 = []  # percent of   property disposal
    for j in range(0, 10):
        valuesb1.append(data[j][2])
    for j in range(0, 10):
        valuesb2.append(data[j][10])
    for j in range(0, 10):
        valuesb3.append(data[j][11])

    return render_template("marks.html", valuesb1=valuesb1,valuesb2=valuesb2,valuesb3=valuesb3,values1=values1, values2=values2, values3=values3, values4=values4,
                           values100=values100, labels1=psLabels,
                           valuesG2_1=valuesG2_1, valuesG2_2=valuesG2_2, valuesG2_3=valuesG2_3, valuesG2_4=valuesG2_4,
                           valuesG2_5=valuesG2_5, labelsG2=psLabels,
                           values=final_mapping,psLabels1=psLabels1,psMarks=psMarks,
                           data_handling_law=data_handling_law, data_cleanliness=data_cleanliness,
                           data_negligence=data_negligence, labels=psLabels,
                            labelsB1=psLabels
                           )

@app.route('/ssportal',methods = ['GET','POST'])
@login_required(role = "SSP")
def ssportal():
    d = datetime.datetime.today()
    # d = d + relativedelta(months=-1)
    d = d.strftime('%Y-%m')
    psLabels = ['ps1','ps2','ps3','ps4','ps5','ps6','ps7','ps8','ps9','ps10']
    values_all = []
    for x in psLabels:
        mycursor.execute("SELECT * from marks where ps_name='{0}' and to_char(date,'YYYY-MM')='{1}'".format(x, d))
        data = mycursor.fetchall()
        if data:
            values_all.extend(data)
        else:
            values_all.append((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    final_score = []
    final_mapping = []
    result = 0
    for j in range(len(values_all)):
        print(j, '  j')
        result = (values_all[j][2] * 0.1) + (values_all[j][3] * 2) + (values_all[j][4] * 0.1) + (
                values_all[j][5] * 0.4) + (values_all[j][6] * 2) + (values_all[j][7] * 1) + (
                         values_all[j][8] * 0.2) + (values_all[j][9] * 0.2) + (values_all[j][10] * 0.1) + (
                         values_all[j][11] * 0.1) + (values_all[j][12] * 2) + (values_all[j][13] * 0.4) + (
                     values_all[j][14]) + (values_all[j][15]) + (values_all[j][16])
        temp1 = values_all[j][1]
        tuple = (temp1, round(result, 2))
        combo = list(tuple)
        final_mapping.append(combo)

    final_mapping.sort(key=lambda x: x[1], reverse=True)
    for j in range(len(final_mapping)):
        final_mapping[j].append(j + 1)
    print(final_mapping)

    psLabels1 = [x[0] for x in final_mapping]
    psMarks = [x[1] for x in final_mapping]
    return render_template('sspcomp.html', form = adminForm(),psLabels1=psLabels1,psMarks=psMarks,values=final_mapping)

@app.route('/test1',methods = ['GET','POST'])
@login_required(role = "SSP")
def test1():
    if request.method == 'POST':
        x = request.form['ps_name1']
        y = request.form['ps_name2']
        z = request.form['attribute']
        w = request.form['date']

        # stri = "-01"
        # w = w+stri
        print(x)
        print(y)
        print(z)
        print(w)
        if z == 'Marks':
            mycursor.execute("SELECT * FROM marks WHERE ps_name ='{0}' and to_char(date, 'YYYY-MM') = '{1}' ".format(str(x), w))
            data1 = mycursor.fetchall()
            print(data1)
            print(len(data1[0]))
            if data1:
                data1=data1
            else:
                data1=[(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)]

            ## data for 3 graphs on ps1
            data_d1 = [data1[0][i] for i in range(5, 10)]
            data_b1 = [data1[0][3], data1[0][11], data1[0][12], data1[0][13]]
            data_r1 = [data1[0][2], data1[0][4], data1[0][10]]

            ## data for 3 graphs on ps2
            mycursor.execute("SELECT * FROM marks WHERE ps_Name='{0}' and to_char(date, 'YYYY-MM') = '{1}' ".format(str(y), w))
            data2 = mycursor.fetchall()

            if data2:
                data2 = data2
            else:
                data2 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]

            data_d2 = [data2[0][i] for i in range(5, 10)]
            data_b2 = [data2[0][3], data2[0][11] / 5, data2[0][12], data2[0][13] / 5]
            data_r2 = [data2[0][2], data2[0][4], data2[0][10]]


            labels1 = ['ndps', 'commercial_recovery', 'arm act', 'excise act', 'gambling act']
            labels2 = ['henius crime cases', 'property disposal', 'Arrest of PO', "untrace cases put in court"]
            labels3 = ['cases submitted in court', 'crime aganist property', 'disposal of complaints']

            return jsonify({'htmlresponse': render_template('responsemarks.html', data_r1=data_r1, data_r2=data_r2,
                                                            labels3=labels3, data_d1=data_d1, data_d2=data_d2,
                                                            data_b1=data_b1, data_b2=data_b2, labels1=labels1,
                                                            labels2=labels2,x=x,y=y)})
        elif z == 'Challan':
            '''values3 -------->ps1  6 months data sum of each attribute for 6 months ps1
               values1 -------->ps1  sum of all attributes of each month ps1
               values4 -------->ps2  6 months data sum of each attribute for 6 months ps2
               values2 -------->ps2  sum of all attributes of each month ps2
               labels2 --------> attributes of challan
               dates   --------> 6 months data
               valuesps1 ------> selected month data of ps1
               valuesps2 ------> selected month data of ps2
            '''
            values3 = [0, 0, 0, 0, 0, 0]
            sixdates =[]
            sixdatesb = []
            sixdates.append(w)
            wdate = datetime.datetime.strptime(w,'%Y-%m')
            sixdatesb.append(wdate.strftime('%b-%Y'))
            for i in range(5):
                wdate = wdate + relativedelta(months=-1)
                sixdates.append(wdate.strftime('%Y-%m'))
                sixdatesb.append(wdate.strftime('%b-%Y'))

            sixvaluesps1 = []
            sixvaluesps2 = []
            for i in range(6):
                mycursor.execute("SELECT * FROM challans WHERE ps_Name='{0}' and to_char(date, 'YYYY-MM')='{1}' ".format(str(x),sixdates[i]))
                onevalue = mycursor.fetchall()
                if onevalue:
                    sixvaluesps1.extend(onevalue)
                else :
                    sixvaluesps1.append((0,0,0,0,0,0,0,0,0))

                mycursor.execute("SELECT * FROM challans WHERE ps_Name='{0}' and to_char(date, 'YYYY-MM')='{1}' ".format(str(y),sixdates[i]))
                onevalue = mycursor.fetchall()
                if onevalue:
                    sixvaluesps2.extend(onevalue)
                else :
                    sixvaluesps2.append((0,0,0,0,0,0,0,0,0))


            for j in range(len(sixvaluesps1)):
                values3[0] += sixvaluesps1[j][1]
                values3[1] += sixvaluesps1[j][2]
                values3[2] += sixvaluesps1[j][3]
                values3[3] += sixvaluesps1[j][4]
                values3[4] += sixvaluesps1[j][5]
                values3[5] += sixvaluesps1[j][6]
            values1 = [sum(x[1:7]) for x in sixvaluesps1]

            values4 = [0, 0, 0, 0, 0, 0]

            for j in range(len(sixvaluesps2)):
                values4[0] += sixvaluesps2[j][1]
                values4[1] += sixvaluesps2[j][2]
                values4[2] += sixvaluesps2[j][3]
                values4[3] += sixvaluesps2[j][4]
                values4[4] += sixvaluesps2[j][5]
                values4[5] += sixvaluesps2[j][6]
            values2 = [sum(x[1:7]) for x in sixvaluesps2]
            labels2 = ['overloadedTruck', 'drunkenDrive', 'overSpeed', 'withoutMask', 'without_helmet_seatbelt',
                       'others']
            valuesps1= list(sixvaluesps1[0][1:7])
            valuesps2 = list(sixvaluesps2[0][1:7])
            return jsonify({'htmlresponse': render_template('responsechallan.html',values3=values3, values4=values4,labels2=labels2,dates=sixdatesb,values1=values1,values2=values2,valuesps1=valuesps1,valuesps2=valuesps2,x=x,y=y)})

        elif z=='Investigation under IPC':

            '''investigation under ipc/local:
            values1 ----> selected month data of ps1 of lables1
            values2 ----> selected month data of ps2 of labels1
            values3 ----> selected month data of ps1 of lables
            values4 ----> selected month data of ps2 of lables
            '''
            labels1 = [
                      'pending over 3 months', 'disposed over 3 months',
                      'pending over 6 months', 'disposed 6 months',
                       'pending over 1 year', 'disposed  over 1 year',
                      'pending less than 3 months','disposed less than 3 months']
            session['type'] = 'IPC'

            mycursor.execute("SELECT * FROM investigation WHERE category='under_ipc' and name_ps='{0}' and to_char(date,'YYYY-MM')='{1}'".format(str(x),w))
            data1 = mycursor.fetchall()
            mycursor.execute("SELECT * FROM investigation WHERE category='under_ipc' and name_ps='{0}' and to_char(date,'YYYY-MM')='{1}'".format(y, w))
            data2 = mycursor.fetchall()

            if data1:
                values1=list(data1[0][8:])
            else :
                data1=[(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)]
                values1 = list(data1[0][8:])

            if data2:
                values2=list(data2[0][8:])
            else :
                data2=[(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)]
                values2 = list(data2[0][8:])

            labels = ['pending under investigation','disposed under investigation','cancellation/untraced pending','cancellation/untraced disposed']
            values3 = list(data1[0][4:8])
            values4 = list(data2[0][4:8])
            w = datetime.datetime.strptime(w,'%Y-%m')

            return jsonify(
                {'htmlresponse': render_template('responseinvestigation.html',values3= values3, values4= values4, labels1= labels1, values1 =values1, values2= values2,
                 labels= labels,x=x,y=y,w=w.strftime('%b-%Y'))})


        elif z=='Investigation under LOCAL & SPECIAL LAW':
            labels1 = [
                      'pending over 3 months', 'disposed over 3 months',
                      'pending over 6 months', 'disposed 6 months',
                       'pending over 1 year', 'disposed  over 1 year',
                      'pending less than 3 months','disposed less than 3 months']
            session['type'] = 'LOCAL & SPECIAL LAW'

            mycursor.execute("SELECT * FROM investigation WHERE category='under_local' and name_ps='{0}' and to_char(date,'YYYY-MM')='{1}'".format(str(x),w))
            data1 = mycursor.fetchall()
            mycursor.execute("SELECT * FROM investigation WHERE category='under_local' and name_ps='{0}' and to_char(date,'YYYY-MM')='{1}'".format(y, w))
            data2 = mycursor.fetchall()


            if data1:
                values1=list(data1[0][8:])
            else :
                data1=[(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)]
                values1 = list(data1[0][8:])

            if data2:
                values2=list(data2[0][8:])
            else :
                data2=[(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)]
                values2 = list(data2[0][8:])

            labels = ['pending under investigation','disposed under investigation','cancellation/untraced pending','cancellation/untraced disposed']

            values3 = list(data1[0][4:8])
            values4 = list(data2[0][4:8])
            w = datetime.datetime.strptime(w,'%Y-%m')

            return jsonify(
                {'htmlresponse': render_template('responseinvestigation.html',values3= values3, values4= values4, labels1= labels1, values1 =values1, values2= values2,
                 labels= labels,x=x,y=y,w=w.strftime('%b-%Y'))})

@app.route("/marksform", methods=['GET','POST'])
@login_required(role = "SSP")
def marksform():
    iform = marksForm()
    d = datetime.datetime.today()
    # d = d + relativedelta(months=-1)
    d = d.strftime('%Y-%m')
    psLabels = ['ps1', 'ps2', 'ps3', 'ps4', 'ps5', 'ps6', 'ps7', 'ps8', 'ps9', 'ps10']
    values_all = []
    for x in psLabels:
        mycursor.execute("SELECT * from marks where ps_name='{0}' and to_char(date,'YYYY-MM')='{1}'".format(x, d))
        data = mycursor.fetchall()
        if data:
            values_all.extend(data)
        else:
            values_all.append((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    final_score = []
    final_mapping = []
    result = 0
    for j in range(len(values_all)):
        print(j, '  j')
        result = (values_all[j][2] * 0.1) + (values_all[j][3] * 2) + (values_all[j][4] * 0.1) + (
                values_all[j][5] * 0.4) + (values_all[j][6] * 2) + (values_all[j][7] * 1) + (
                         values_all[j][8] * 0.2) + (values_all[j][9] * 0.2) + (values_all[j][10] * 0.1) + (
                         values_all[j][11] * 0.1) + (values_all[j][12] * 2) + (values_all[j][13] * 0.4) + (
                     values_all[j][14]) + (values_all[j][15]) + (values_all[j][16])
        temp1 = values_all[j][1]
        tuple = (temp1, round(result, 2))
        combo = list(tuple)
        final_mapping.append(combo)

    final_mapping.sort(key=lambda x: x[1], reverse=True)
    for j in range(len(final_mapping)):
        final_mapping[j].append(j + 1)
    print(final_mapping)

    psLabels1 = [x[0] for x in final_mapping]
    psMarks = [x[1] for x in final_mapping]

    if iform.validate_on_submit():
        date =  iform.date.data
        date1 = date.strftime('%Y-%m')

        ps = iform.ps_name.data

        attribute = 'Marks'
        m1 = date.strftime('%b')
        yr = date.strftime('%Y')
        dtoday = datetime.datetime.today()
        mycursor.execute(
            "select id from marks where ps_name='{ps}' and to_char(date ,'YYYY-MM')='{d}'".format(ps=ps,
                                                                                                  d=date1))
        data = mycursor.fetchall()

        pocsic = iform.percent_of_cases_submitted_in_court.data
        cohc = iform.cases_of_henius_crime.data
        cap =  iform.crime_against_property.data
        n = iform.ndps.data
        cr = iform.commercial_recovery.data
        ac = iform.arm_act.data
        ea = iform.excise_act.data
        ga = iform.gambling_act.data
        podoc = iform.percent_of_disposal_of_complaints.data
        popd = iform.percent_of_property_disposal.data
        aop = iform.arrest_of_po.data
        ucpic = iform.untrace_cases_put_in_court.data
        ne =  iform.negligence.data
        c = iform.cleanliness.data
        hol = iform.handling_of_law.data

        if len(data) != 0:
            id = data[0][0]

            mycursor.execute(
                "update marks set percent_of_cases_submitted_in_court= '{pocsic}', cases_of_henius_crime='{cohc}',crime_against_property='{cap}',ndps='{n}',commercial_recovery='{cr}',"
                "arm_act='{ac}',excise_act='{ea}',gambling_act='{ga}',percent_of_disposal_of_complaints='{podoc}',percent_of_property_disposal='{popd}',arrest_of_po='{aop}',untrace_cases_put_in_court='{ucpic}',"
                "negligence='{ne}',cleanliness='{c}',handling_of_law='{hol}' where id='{id}'"
                    .format(id=id, pocsic=pocsic, cohc=cohc, cap=cap, n=n, cr=cr, ac=ac, ea=ea, ga=ga, podoc=podoc,
                            popd=popd, aop=aop, ucpic=ucpic, ne=ne, c=c, hol=hol))
            connection.commit()
            newupdate = updation_track(nps=ps, un=current_user.username, a=attribute, md=m1,
                                       yr=yr, ud=dtoday)
            db.session.add(newupdate)
            db.session.commit()
            flash("Data updated Successfully", category='success')
            return redirect(url_for('marksform'))
        else:
            newmarks = marks(ps_name=ps,
                             percent_of_cases_submitted_in_court=pocsic,
                             cases_of_henius_crime=cohc,
                             crime_against_property=cap, ndps=n,
                             commercial_recovery=cr,
                             arm_act=ac, excise_act=ea,
                             gambling_act=ga,
                             percent_of_disposal_of_complaints=podoc,
                             percent_of_property_disposal=popd,
                             arrest_of_po=aop,
                             untrace_cases_put_in_court=ucpic,
                             negligence=ne,
                             date=date,
                             cleanliness=c, handling_of_law=hol
                             )
            db.session.add(newmarks)
            db.session.commit()
            newupdate = updation_track(nps=ps, un=current_user.username, a=attribute, md=m1,
                                       yr=yr, ud=dtoday)
            db.session.add(newupdate)
            db.session.commit()
            flash("Data uploaded Successfully", category='success')
            return redirect(url_for('marksform'))
    return render_template('marksform.html',form=iform,psLabels1=psLabels1,psMarks=psMarks,values=final_mapping)

@app.route("/logout")
@login_required(role = "ANY")
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)

