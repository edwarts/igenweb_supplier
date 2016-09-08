import json
import os
import random
import time
from io import BytesIO

from app.base.common import isSession, toDict
from app.img import create_validate_code
from app.base.db import dbcnn
from app.send_mail import send_email
from app.platform import getpath
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request, redirect, render_template, url_for, \
    current_app, session, g, Blueprint
from app.models import topic_dict, db, Match, User, Country
from sqlalchemy import or_

auth = Blueprint('auth', __name__,
                 url_prefix='/auth',
                 template_folder='../templates')

IMG_TYPE = ["image/jpeg", "image/png"]
ISOTIMEFORMAT = '%Y%m%d%H%M%S'


# 重置密码
@auth.route('/reset/<token>')
def reset(token):
    if request.method == 'POST':
        pass
    return render_template('chongzhimima.html')


@auth.route('/upload/<uploadpath>', methods=['GET', 'POST'])
def upload(uploadpath):
    if request.method == 'POST':
        path = getpath(uploadpath)
        f = request.files['file']
        if not os.path.exists(path):
            os.makedirs(path)
        # 获取一个安全的文件名，且仅仅支持ascii字符；
        if f.content_type in IMG_TYPE:
            fname = f.filename
            f.save(os.path.join(path, fname))
            return "图片上传成功"
        else:
            return "图片格式不正确"


@auth.route('/upload1/<uploadpath>', methods=['GET', 'POST'])
def upload1(uploadpath):
    if request.method == 'POST':
        path = getpath(uploadpath)
        f = request.files['file']
        if not os.path.exists(path):
            os.makedirs(path)
        # 获取一个安全的文件名，且仅仅支持ascii字符；
        if f.content_type in IMG_TYPE:
            fname = f.filename
            newlfname = (str(time.strftime(ISOTIMEFORMAT)) +
                         str(random.randint(1000, 9999)) +
                         os.path.splitext(fname)[1])
            f.save(os.path.join(path, newlfname))
            return newlfname
        else:
            return "error"


@auth.route('/uploads/<uploadpath>', methods=['GET', 'POST'])
def uploads(uploadpath):
    if request.method == 'POST':
        path = getpath(uploadpath)
        os.makedirs(path)
        f = request.files
        for (k, v) in f.items():
            print(v)
            # 获取一个安全的文件名，且仅仅支持ascii字符；
            if v.content_type in IMG_TYPE:
                fname = v.filename
                v.save(os.path.join(path, fname))
        return "图片上传成功"
    return "图片格式不正确"


@auth.route('/getcontinent')
def getcontinent():
    dbcnn()
    cursor = g.cnn.cursor()
    try:
        sql = "select continentid, continentname_cn from continent_config"
        cursor.execute(sql)
        lists = cursor.fetchall()
        index = ['continentid', 'continentname_cn']
        resu = toDict(index, lists)
        data = json.dumps(resu)
    except Exception as e:
        print('-------Error on %s\r\n-------Exception:%s' %
              (request.path, format(e)))

    return data


@auth.route('/getcountry')
def getcountry():
    dbcnn()
    cursor = g.cnn.cursor()
    try:
        continentid = request.args.get('id')
        sql = "select countryid, countryname_cn from country_config where " \
              "continentid = %(continentid)s"
        data = {'continentid': continentid}
        cursor.execute(sql, data)
        lists = cursor.fetchall()
        index = ['countryid', 'countryname_cn']
        resu = toDict(index, lists)
        data = json.dumps(resu)
    except Exception as e:
        print('-------Error on %s\r\n-------Exception:%s' %
              (request.path, format(e)))
    return data


@auth.route('/getcity')
def getcity():
    dbcnn()
    cursor = g.cnn.cursor()
    try:
        countryid = request.args.get('id')
        sql = "select cityid, cityname_cn from city_config where " \
              "countryid = %s" % countryid
        cursor.execute(sql)
        lists = cursor.fetchall()
        index = ['cityid', 'cityname_cn']
        resu = toDict(index, lists)
        data = json.dumps(resu)
    except Exception as e:
        print('-------Error on %s\r\n-------Exception:%s' %
              (request.path, format(e)))
    return data


# 注册
@auth.route('/zhuce', methods=['GET', 'POST'])
def zhuce():
    if request.method == 'POST':
        topics = request.form.getlist('topic')
        email = request.form['email']
        pwd = request.form['pwd']
        phone = request.form['phone']
        licence = request.form['licence']
        newlicence = (str(time.strftime(ISOTIMEFORMAT)) +
                      str(random.randint(1000, 9999)) +
                      os.path.splitext(licence)[1])
        path = getpath("licence")
        os.rename(os.path.join(path, licence), os.path.join(path, newlicence))
        company = request.form['company']
        location = request.form['location']
        location_cn = request.form['location_cn']
        introduce = request.form['introduce']
        service = request.form.getlist('service')
        service_cn = request.form.getlist('service_cn')
        service_cnn = ''
        for ser in service_cn:
            service_cnn = (service_cnn + ser) + ','
        dbcnn()
        cursor = g.cnn.cursor()
        try:
            sql = "select email from userinfo where email = %s"
            data = (email,)
            cursor.execute(sql, data)
            result = cursor.fetchone()
            if result is not None and result[0] == email:
                msg = '邮箱已注册'
                return render_template('zhuce.html', message=msg)
            sql = "insert into userinfo (email, pwd, createtime, phone, " \
                  "licence, company, introduce, location, service) VALUES " \
                  "(%s, password(%s), now(), %s, %s, %s, %s, %s, %s)"
            data = (email, pwd, phone, newlicence, company, introduce,
                    location_cn, service_cnn[:-1])
            cursor.execute(sql, data)
            g.cnn.commit()
            sql = "select id from userinfo where email = %s"
            data = (email,)
            cursor.execute(sql, data)
            userid = cursor.fetchone()[0]
            service.append(location)
            for ser in service:
                for topic in topics:
                    db.session.add(Match(userid, int(ser), int(topic)))
            db.session.commit()
        except Exception as e:
            print('error!{}'.format(e))
            msg = "注册失败错误，错误原因%s" % e
            return render_template('zhuce.html', message=msg)
        return render_template('zhuce_success.html')
    else:
        return render_template('zhuce.html', topics=topic_dict)


# 登录
@auth.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        userpass = request.form['userpass']
        # remember = request.form.get('remember')
        if len(username) < 5 or len(userpass) < 8:
            msg = '邮箱或密码格式错误'
            return render_template('login.html', message=msg)
        dbcnn()
        cursor = g.cnn.cursor()
        try:
            sql_login = "select id from userinfo where email=%(username)s" \
                        " and pwd=password(%(password)s)"
            data = {'username': username, 'password': userpass}
            cursor.execute(sql_login, data)
            result = cursor.fetchall()
            if len(result) != 1:
                msg = '用户名或密码错误'
                return render_template('login.html', message=msg)
            else:
                session['username'] = username
                session['user_id'] = result[0][0]
                return redirect('/order')
        except Exception as e:
            print('-------Error on %s\r\n-------Exception:%s' %
                  (request.path, format(e)))
    return render_template('login.html')


# 创建路线
@auth.route('/create', methods=['GET', 'POST'])
def create():
    if isSession():
        wkid = 0
        xcdzid = 27
        if request.method == "POST":
            img = ""
            lightimg = ""
            email = session.get('username')
            title = request.form['title']
            if 'cover' in request.form:
                img = request.form['cover']
                newlicence = str(time.strftime(ISOTIMEFORMAT))+str(random.randint(1000, 9999))+os.path.splitext(img)[1]
                path = getpath("cover")
                if os.path.isfile(path+img):
                    os.rename(path+img, path+newlicence)
                newlicence = "/static/upload/cover/" + newlicence
            begin = request.form['begin']
            end = request.form['end']

            lightdes = request.form['lightdes']
            if 'light' in request.form:
                lightimg = request.form['light']
                newlightimg = str(time.strftime(ISOTIMEFORMAT))+str(random.randint(1000, 9999))+os.path.splitext(lightimg)[1]
                path = getpath("light")
                if os.path.isfile(path+lightimg):
                    os.rename(path+lightimg, path+newlightimg)
                lightimg = "/static/upload/light/" + newlightimg
            dbcnn()
            cursor = g.cnn.cursor()
            try:
                sql = "select id from userinfo where email = %s"
                data = (email, )
                cursor.execute(sql, data)
                userid = cursor.fetchone()[0]
                sql = "select count(*) from itinerary where providerid = %s and xcdzid = %s"
                data = (userid, int(xcdzid))
                cursor.execute(sql, data)
                cnt = cursor.fetchone()[0]
                if cnt == 0:
                    piece = ""
                    sql = "insert into itinerary (providerid, wkid, xcdzid, title, coverimg, piecelist, startdate, enddate) values (%s, %s, %s, %s, %s, %s, %s, %s)"
                    data = (userid, wkid, xcdzid, title, newlicence, piece, begin, end)
                    cursor.execute(sql, data)
                    sql = "select id from itinerary where providerid = %s and xcdzid = %s"
                    data = (userid, int(xcdzid))
                    cursor.execute(sql, data)
                    itineraryid = cursor.fetchone()[0]
                    sql = "insert into itinerarylight (itineraryid, lightdes, lightimg) VALUES (%s, %s, %s)"
                    data = (itineraryid, lightdes, lightimg)
                    cursor.execute(sql, data)
                else:
                    if img != "":
                        sql = "update itinerary set title = %s, coverimg = %s, startdate = %s, enddate = %s where providerid = %s and xcdzid = %s"
                        data = (title, newlicence, begin, end, userid, int(xcdzid))
                    else:
                        sql = "update itinerary set title = %s, startdate = %s, enddate = %s where providerid = %s and xcdzid = %s"
                        data = (title, begin, end, userid, int(xcdzid))
                    cursor.execute(sql, data)
                    sql = "select id from itinerary where providerid = %s and xcdzid = %s"
                    data = (userid, int(xcdzid))
                    cursor.execute(sql, data)
                    itineraryid = cursor.fetchone()[0]
                    if lightimg != "":
                        sql = "update itinerarylight set lightdes = %s, lightimg = %s where itineraryid = %s"
                        data = (lightdes, lightimg, itineraryid)
                    else:
                        sql = "update itinerarylight set lightdes = %s where itineraryid = %s"
                        data = (lightdes, itineraryid)
                    cursor.execute(sql, data)
                g.cnn.commit()
            except Exception as e:
                print('insert error!{}'.format(e))
            return redirect(url_for('auth.xingchengxinxi', id=itineraryid))

        return render_template('chuangjianluxian.html', wkid=wkid, xcdzid=xcdzid)
    return redirect(url_for('auth.login'))


# 保存路线
@auth.route('/saveitinerary', methods=['POST'])
def saveitinerary():
    if isSession():
        if request.method == "POST":
            email = session.get('username')
            days = request.form.getlist('days[]')
            id = request.form['id']
            dbcnn()
            cursor = g.cnn.cursor()
            try:
                sql = "select i.id, i.xcdzid, i.providerid from userinfo u, itinerary i where u.email = %s and u.id = i.providerid"
                data = (email, )
                cursor.execute(sql, data)
                lists = cursor.fetchall()
                count = 0
                for a in lists:
                    if int(id) == a[0]:
                        sql = "update itinerary set piecelist = %s, status = 1 where id = %s"
                        days = ":".join(days)
                        # days = json.dumps(days)
                        data = (days, int(id))
                        cursor.execute(sql, data)

                        count += 1
                        xcdzid = a[1]
                        providerid = a[2]
                        sql = "update supplierorder set status = 1 where providerid = %s and xcdzid = %s"
                        data = (providerid, xcdzid)
                        cursor.execute(sql, data)
                        g.cnn.commit()

                if count == 0:
                    return redirect(url_for('auth.itinerary'))
                data = [{"success": 1}]
                data = json.dumps(data)
            except Exception as e:
                print('select or update error!{}'.format(e))
        return data


# 获取路线
@auth.route('/getitinerary')
def getitinerary():
    if isSession():
        email = session.get('username')
        dbcnn()
        cursor = g.cnn.cursor()
        try:
            sql = "select i.id, i.providerid, i.xcdzid, i.title, i.coverimg, i.piecelist from userinfo u, itinerary i where u.email = %s and u.id = i.providerid"
            data = (email, )
            cursor.execute(sql, data)
            lists = cursor.fetchall()
            datalist = []

            for list in lists:
                da = {}
                da['id'] = list[0]
                da['providerid'] = list[1]
                da['xcdzid'] = list[2]
                da['title'] = list[3]
                da['coverimg'] = list[4]

                if list[5] != "":
                    piecelist = list[5].split(":")
                    i = 1
                    text = []
                    days = []

                    for pieceli in piecelist:
                        if pieceli == "":
                            continue
                        pieceli = pieceli.split(",")
                        j = 1
                        position = {}
                        coordinatelist = []
                        d = {}
                        for pi in pieceli:
                            coordinate = {}
                            if pi.find("my") >= 0:
                                piece = pi[2:]
                                sql = "select name_cn, lat, lng from mypiece where id = %s"
                                data = (int(piece), )
                            else:
                                sql = "select name_cn, lat, lng from frag where id = %s"
                                data = (int(pi), )
                            cursor.execute(sql, data)
                            res = cursor.fetchone()
                            if j == 1:
                                day = "D" + str(i) + " " + res[0]
                            else:
                                day = day + ">" + res[0]
                            coordinate['lat'] = res[1]
                            coordinate['lng'] = res[2]
                            coordinatelist.append(coordinate)
                            d["day"] = day
                            j += 1
                        days.append(d)
                        position['coordinate'] = coordinatelist
                        text.append(day)
                        i += 1
                    position['days'] = days
                    da['position'] = position
                datalist.append(da)
            data = json.dumps(datalist)
        except Exception as e:
            print('error!{}'.format(e))
        return data


# 获取创建路线详情(不包含碎片)
@auth.route('/getitineraryinfo/<xcdzid>')
def getitineraryinfo(xcdzid):
    if isSession():
        email = session.get('username')
        dbcnn()
        cursor = g.cnn.cursor()
        try:
            sql = "select i.id, i.providerid, i.xcdzid, i.title, i.coverimg, i.startdate, i.enddate from userinfo u, itinerary i " \
                  "where u.id = i.providerid and u.email = %s and i.xcdzid = %s"
            data = (email, xcdzid)
            cursor.execute(sql, data)
            lists = cursor.fetchall()
            index = ['id', 'providerid', 'xcdzid', 'title', 'coverimg', 'begindate', 'enddate']
            da = toDict(index, lists)
            itineraryid = da[0]['id']
            da[0]['cover'] = da[0]['coverimg'].split("/")[-1]
            sql = "select id, itineraryid, lightdes, lightimg from itinerarylight where itineraryid = %s"
            data = (itineraryid, )
            cursor.execute(sql, data)
            li = cursor.fetchone()
            light = {}
            light['id'] = li[0]
            light['itineraryid'] = li[1]
            light['lightdes'] = li[2]
            light['lightimg'] = li[3]
            light['light'] = light['lightimg'].split("/")[-1]
            da[0]['light'] = light
            data = json.dumps(da)
        except Exception as e:
            print('error!{}'.format(e))
        return data


@auth.route('/getitinerary/<id>')
def getitinerarybyid(id):
    if isSession():
        typeimg = {"0": "xc2.png", "1": "xc2.png", "2": "xc2.png", "3": "xc3.png", "4": "xc2.png"}
        email = session.get('username')
        dbcnn()
        cursor = g.cnn.cursor()
        try:
            sql = "select i.piecelist from userinfo u, itinerary i where u.email = %s and u.id = i.providerid and i.id = %s"
            data = (email, id)
            cursor.execute(sql, data)
            list = cursor.fetchone()[0]
            datalist = []
            da = {}
            piecelist = list.split(":")
            da["days"] = len(piecelist)
            i = 1
            days = []
            for pieceli in piecelist:
                day = []
                pieceli = pieceli.split(",")
                j = 1
                for piece in pieceli:
                    d = {}
                    if piece.find("my") >= 0:
                        piece = piece[2:]
                        url = "upload/pieceimg/"
                        sql = "select id, name_cn, type, price, left(ltrim(description),15), cover from mypiece where id = %s"
                        data = (int(piece), )
                    else:
                        url = ""
                        sql = "select id, name_cn, type, price, left(ltrim(description),15), cover from frag where id = %s"
                        data = (int(piece), )
                    cursor.execute(sql, data)
                    res = cursor.fetchone()
                    d["id"] = res[0]
                    d["name"] = res[1]
                    d["type"] = typeimg.get(str(res[2]))
                    d["price"] = str(res[3])
                    d["des"] = res[4]
                    d["cover"] = url+res[5]
                    j += 1
                    day.append(d)
                days.append(day)
                i += 1
            da["info"] = days
            datalist.append(da)
            data = json.dumps(datalist)
        except Exception as e:
            print('error!{}'.format(e))
        return data


@auth.route('/getmap/<itineraryid>')
@auth.route('/getmap/<itineraryid>/<day>')
def getmap(itineraryid, day=1):
    if isSession():
        email = session.get('username')
        dbcnn()
        cursor = g.cnn.cursor()
        try:
            sql = "select u.id, i.piecelist from userinfo u, itinerary i where u.email = %s and i.providerid = u.id and i.id = %s "
            data = (email, itineraryid)
            cursor.execute(sql, data)
            result = cursor.fetchone()
            res = result[1].split(":")
            days = len(res)
            res = res[int(day)-1].split(",")
            i = 1

            coordinatelist = []
            for piece in res:
                coordinate = {}
                if piece.find("my") >= 0:
                    piece = piece[2:]
                    sql = "select name_cn, lat, lng from mypiece where id = %s"
                    data = (int(piece), )
                else:
                    sql = "select name_cn, lat, lng from frag where id = %s"
                    data = (int(piece), )
                # sql = "select name_cn, lat, lng from frag where id = %s"
                # data = (piece, )
                cursor.execute(sql, data)
                dayres = cursor.fetchone()
                if i == 1:
                    daystr = "D" + str(day) + " " + dayres[0]
                else:
                    daystr = daystr + ">" + dayres[0]
                coordinate['lat'] = dayres[1]
                coordinate['lng'] = dayres[2]
                coordinatelist.append(coordinate)
                # d["day"] = day
                i += 1
            data = [{"days": days, "daystr": daystr, "coordinate": coordinatelist}]
            data = json.dumps(data)
        except Exception as e:
            print('-------Error on %s\r\n-------Exception:%s' %
                  (request.path, format(e)))
        return data


# 路线管理
@auth.route('/itinerary', methods=['GET', 'POST'])
def itinerary():
    if isSession():
        return render_template('luxianguanli.html')
    return redirect(url_for('auth.login'))


# 获取碎片
@auth.route('/getpiece')
def getpiece():
    begin = time.time()
    email = session.get('username')
    dbcnn()
    cursor = g.cnn.cursor()
    try:
        sql = "select c.cityid, b.cityname_cn from userinfo a, city_config b, service_city c where a.id = c.userid and c.cityid = b.cityid and a.email = %s"
        data = (email, )
        cursor.execute(sql, data)
        lists = cursor.fetchall()
        index = ['cityid', 'cityname_cn']
        resu = toDict(index, lists)
        sql = "select id, cityid, name_cn, price, left(ltrim(description),15), cover from frag where cityid = %s and name_cn is not null and name_cn <> '' order by id limit 12"
        data = (int(resu[0]['cityid']),)
        cursor.execute(sql, data)
        piece = cursor.fetchall()
        index = ['id', 'cityid', 'name_cn', 'price', 'description', 'cover']
        piecelist = toDict(index, piece)
        data = [{"citylist": resu, "piecelist": piecelist}]

        data = json.dumps(data)
    except Exception as e:
        print('-------Error on %s\r\n-------Exception:%s' %
              (request.path, format(e)))
    end = time.time()
    print(begin-end)
    return data


# 获取碎片
@auth.route('/getpiecebyid/<id>', methods=['GET', 'POST'])
def getpiecebyid(id):
    begin = time.time()
    # email = session.get('username')
    dbcnn()
    cursor = g.cnn.cursor()
    try:
        sql = "select id, cityid, name_cn, price, trim(description), cover, period, ticket, tel, url, address, lat, lng from frag where id = %s"
        data = (int(id),)
        cursor.execute(sql, data)
        piece = cursor.fetchall()
        index = ['id', 'cityid', 'name_cn', 'price', 'description', 'cover', 'period', 'ticket', 'tel', 'url', 'address', 'lat', 'lng']
        piecelist = toDict(index, piece)
        data = [{"piecelist": piecelist}]

        data = json.dumps(data)
    except Exception as e:
        print('-------Error on %s\r\n-------Exception:%s' %
              (request.path, format(e)))
    end = time.time()
    print(begin-end)
    return data


# 获取自建碎片
@auth.route('/getmypiece')
def getmypiece():
    id = session.get('user_id')
    dbcnn()
    cursor = g.cnn.cursor()
    try:
        sql = "select m.id, m.cityid, m.name_cn, m.price, "
        "left(ltrim(m.description),15), m.cover from frag m where "
        "m.sup_id = %s and m.providerid = u.id order by id  =  limit 12"
        data = (str(id),)
        cursor.execute(sql, data)
        piece = cursor.fetchall()
        index = ['id', 'cityid', 'name_cn', 'price', 'description', 'cover']
        piecelist = toDict(index, piece)
        data = [{"piecelist": piecelist}]

        data = json.dumps(data)
        print(data)
    except Exception as e:
        print('-------Error on %s\r\n-------Exception:%s' %
              (request.path, format(e)))
    return data


# 根据城市或类型获取碎片
@auth.route('/getcitypiece/<cityid>')
@auth.route('/getcitypiece/<cityid>/<type>')
@auth.route('/getcitypiece/<cityid>/<type>/<count>')
def getcitypiece(cityid, type=0, count=1):
    dbcnn()
    cursor = g.cnn.cursor()
    try:
        if int(type) == 0:
            sql = "select id, cityid, name_cn, price, left(ltrim(description), 15), cover from frag where cityid = %s and name_cn <> '' order by id limit %s, 12"
            data = (int(cityid), (int(count)-1)*12)
        else:
            sql = "select id, cityid, name_cn, price, left(ltrim(description), 15), cover from frag where cityid = %s and type = %s and name_cn <> '' order by id limit %s, 12"
            data = (int(cityid), int(type)-1, (int(count)-1)*12)
        cursor.execute(sql, data)
        piece = cursor.fetchall()
        index = ['id', 'cityid', 'name_cn', 'price', 'description', 'cover']
        piecelist = toDict(index, piece)

        data = json.dumps(piecelist)
    except Exception as e:
        print('-------Error on %s\r\n-------Exception:%s' %
              (request.path, format(e)))
    return data


# 碎片管理
@auth.route('/piece', methods=['GET', 'POST'])
def piece():
    if isSession():
        return render_template('suipianguanli.html')
    return redirect(url_for('auth.login'))


# 商家主页
@auth.route('/index')
def index():
    if isSession():
        email = session.get('username')
        user = db.session.query(User).filter_by(email=email).one_or_none()
        topic = db.session.query(Match).filter_by(sup_id=user.id)
        topics = []
        for top in topic:
            topics.append(topic_dict[top.topic])

        return render_template('shangjiazy_bianji.html', user=user,
                               topics=list(set(topics)), email=email)
    return render_template('login.html')


# 编辑商家
@auth.route('/editindex')
def editindex():
    if 'username' in session:
        email = session.get('username')
        user = db.session.query(User).filter_by(email=email).one_or_none()
        matchs = db.session.query(Match).filter_by(sup_id=user.id)
        countrys = db.session.query(Country).filter(
          or_(Country.countryid == v.countryid for v in matchs))
        local = db.session.query(Country).filter_by(
            countryname_cn=user.location).one()
        return render_template(
            'shangjiazy_tianxie.html',
            email=email,
            topics=topic_dict,
            local=local,
            countrys=countrys,
            matchs=matchs,
            user=user)
    return redirect(url_for('auth.login'))


# 保存编辑
@auth.route('/save', methods=['GET', 'POST'])
def save():
    if isSession():
        email = session.get('username')
        user_id = session.get('user_id')
        if request.method == 'POST':
            company = request.form['company']
            location = request.form['location']
            location_cn = request.form['location_cn']
            introduce = request.form['introduce']
            service = request.form.getlist('service')
            service_cn = request.form.getlist('service_cn')
            service_cnn = ''
            topics = request.form.getlist('topic')
            for ser in service_cn:
                service_cnn = (service_cnn + ser) + ','

            dbcnn()
            cursor = g.cnn.cursor()
            try:
                sql = "update userinfo set company=%s, location=%s, service=%s, introduce=%s where email=%s"
                data = (company, location_cn, service_cnn, introduce, email)
                cursor.execute(sql, data)
                g.cnn.commit()
                db.session.query(Match).filter_by(sup_id=user_id).delete()
                db.session.commit()
                service.append(location)
                for ser in service:
                    for topic in topics:
                        db.session.add(Match(user_id, int(ser), int(topic)))
                db.session.commit()
            except Exception as e:
                print('update error!{}'.format(e))
        return redirect(url_for('auth.index'))
    return redirect(url_for('auth.login'))


# 查看订单
@auth.route('/checkorder/<id>')
def checkorder(id):
    if isSession():
        email = session.get('username')
        try:
            dbcnn()
            cursor = g.cnn.cursor()
            sql = "select count(*) from supplierorder s, userinfo u where u.id = s.providerid and u.email = %s and s.xcdzid = %s"
            data = (email, id)
            cursor.execute(sql, data)
            cnt = cursor.fetchone()[0]
            if cnt == 0:
                return render_template('chakandingdanjiedan.html', id=id)
            else:
                return render_template('houqigoutong.html', id=id)
        except Exception as e:
            print("error{}!".format(e))
    return redirect(url_for('auth.login'))


# 接受订单
@auth.route('/applyorder/<wkid>/<xcdzid>')
def applyorder(wkid, xcdzid):
    if isSession():
        email = session.get('username')
        try:
            dbcnn()
            cursor = g.cnn.cursor()
            sql = "select id from userinfo where email = %s"
            data = (email, )
            cursor.execute(sql, data)
            userid = cursor.fetchone()[0]
            sql = "select count(*) from supplierorder where providerid = %s and xcdzid = %s"
            data = (userid, int(xcdzid))
            cursor.execute(sql, data)
            cnt = cursor.fetchone()[0]
            if cnt == 0:
                sql = "insert into supplierorder (providerid, xcdzid) values (%s, %s)"
                data = (userid, int(xcdzid))
                cursor.execute(sql, data)
            g.cnn.commit()
        except Exception as e:
            print("error{}!".format(e))
        return redirect(url_for('auth.checkorder', id=xcdzid))
    return redirect(url_for('auth.login'))


# 找回密码
@auth.route('/findpassword', methods=['GET', 'POST'])
def findpassword():
    if request.method == 'POST':
        email = request.form['email']
        validation = request.form['validation']
        if validation == session.get('validation'):
            session.pop('validation', None)
            dbcnn()
            cursor = g.cnn.cursor()
            try:
                sql = "select id from userinfo where email = %s"
                data = (email,)
                cursor.execute(sql, data)
                result = cursor.fetchone()[0]
                if result is None or result == "":
                    msg = "邮箱用户不存在"
                    return render_template('zhaohuimima.html', msg=msg)
                user = User(result, email)
                token = user.generate_confirmation_token()
                send_email(user.email, '重置密码',
                           'confirm', user=user, token=token)
                msg = "重置密码的链接已发送至您的邮箱！"
            except Exception as e:
                print('-------Error on %s\r\n-------Exception:%s' %
                      (request.path, format(e)))
                msg = "邮箱地址未注册"
                return render_template('zhaohuimima.html', msg=msg)
            return render_template('zhaohuimima_email.html', msg=msg)
        else:
            msg = "验证码错误"
            return render_template('zhaohuimima.html', msg=msg)
    return render_template('zhaohuimima.html')


# 获取验证码
@auth.route('/code/<time>', methods=['GET', 'POST'])
def get_code(time):
    # 把strs发给前端,在后台使用session保存
    code_img, strs = create_validate_code()
    session['validation'] = strs
    buf = BytesIO()
    code_img.save(buf, 'jpeg')

    buf_str = buf.getvalue()
    response = current_app.make_response(buf_str)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


# 重置密码页面
@auth.route('/chgpwd/<token>')
def changePassword(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        msg = u"链接已失效"
        return render_template('zhaohuimima_email.html', msg=msg)
    id = data.get('chgpwd')
    sql = "select id from userinfo where id = %s"
    data = (id, )
    dbcnn()
    cursor = g.cnn.cursor()
    cursor.execute(sql, data)
    result = cursor.fetchone()[0]
    if result == id:
        return render_template('chongzhimima.html', id=id)
    return redirect(url_for('auth.login'))


# 修改密码
@auth.route('/updatepwd', methods=['GET', 'POST'])
def updatepwd():
    if request.method == 'POST':
        id = request.form['id']
        pwd = request.form['pwd']
        dbcnn()
        cursor = g.cnn.cursor()
        try:
            sql = 'update userinfo set pwd=password(%s) where id=%s'
            data = (pwd, id)
            cursor.execute(sql, data)
            g.cnn.commit()
            msg = "密码修改成功"
            return render_template('zhaohuimima_email.html', msg=msg)
        except Exception as e:
            print('update error!{}'.format(e))

    return redirect(url_for('auth.login'))


# 行程信息
@auth.route('/xingchengxinxi/<id>')
def xingchengxinxi(id):
    if isSession():
        email = session.get('username')
        try:
            dbcnn()
            cursor = g.cnn.cursor()
            sql = "select i.id, i.wkid, i.xcdzid from itinerary i, userinfo u where i.id = %s and i.providerid = u.id and u.email = %s"
            data = (id, email)
            cursor.execute(sql, data)
            res = cursor.fetchone()
            id = res[0]
            wkid = res[1]
            xcdzid = res[2]
        except Exception as e:
            print("error {}!".format(e))
        return render_template('xingchengxinxi.html', id=id, wkid=wkid, xcdzid=xcdzid)
    return redirect(url_for('auth.login'))


# 后期沟通
@auth.route('/houqigoutong')
def houqigoutong():
    if isSession():
        return render_template('houqigoutong.html')
    return redirect(url_for('auth.login'))


# 新建碎片
@auth.route('/createsuipian', methods=['GET', 'POST'])
def createsuipian():
    if isSession():
        if request.method == 'POST':
            id = session.get('user_id')
            name_cn = request.form['name_cn']
            name_en = request.form['name_en']
            typename = request.form['suipiantype']
            # continent = request.form['continent']
            # country = request.form['country']
            city = request.form['city']
            price = request.form['price']
            description = request.form['description']
            lat = '1'
            lng = '1'
            imglist = request.files.getlist("suipianimg")
            dbcnn()
            cursor = g.cnn.cursor()
            try:
                typedict = {"不限": 5, "景点": 0, "活动": 1, "餐馆": 2,
                            "酒店": 3, "购物": 4}
                typeid = typedict.get(typename)
                sql = "select cityid from city_config where " \
                      "cityname_cn = %s or cityname_en = %s"
                data = (city, city)
                cursor.execute(sql, data)
                cityid = cursor.fetchone()[0]
                sql = "insert into frag (sup_id, cityid, name_cn, " \
                      "name_en, price, description, lat, lng, type, cover) " \
                      "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data = (id, cityid, name_cn, name_en,
                        price, description, lat, lng, typeid, 'none')
                cursor.execute(sql, data)
                g.cnn.commit()

                sql = "select max(id) from frag where sup_id = %s"
                data = (id, )
                cursor.execute(sql, data)
                pieceid = cursor.fetchone()[0]
                path = getpath("pieceimg")
                i = 0
                for v in imglist:
                    newlfname = (str(time.strftime(ISOTIMEFORMAT)) +
                                 str(random.randint(1000, 9999)) +
                                 os.path.splitext(v.filename)[1])
                    if os.path.exists(path+v.filename):
                        os.rename(path+v.filename, path+newlfname)
                    if i == 0:
                        sql = "update frag set cover = %s where " \
                              "sup_id = %s and id = %s"
                        data = (newlfname, id, pieceid)
                        cursor.execute(sql, data)
                    # sql = "insert into mypiece_imgurl " \
                    #      "(pieceid, providerid, imgurl) values (%s, %s, %s)"
                    # data = (pieceid, providerid, newlfname)
                    # cursor.execute(sql, data)
                    i += 1
                g.cnn.commit()
            except Exception as e:
                print('error!{}'.format(e))
        return render_template('xinjiansuipian.html')
    return redirect(url_for('auth.login'))


# 预览
@auth.route('/yulan/<id>')
def yulan(id):
    if isSession():
        return render_template('yulan_biaozhun.html', id=id)
    return redirect(url_for('auth.login'))


# 日历预览
@auth.route('/yulanbyrili')
def yulanbyrili():
    if isSession():
        return render_template('yulan_rili.html')
    return redirect(url_for('auth.login'))


# 退出
@auth.route('/logout')
def logout():
    if isSession():
        session.pop('username', None)
        session.pop('user_id', None)
    return redirect(url_for('auth.login'))


# 添加费用
@auth.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    if isSession():
        if request.method == "POST":
            email = session.get("username")
            itineraryid = request.form['itineraryid']
            name = request.form['name']
            price = request.form['price']
            currency = request.form['currency']
            cnt = request.form['cnt']
            try:
                dbcnn()
                cursor = g.cnn.cursor()
                sql = "insert into expense (itineraryid, ex_name, ex_price, currency, ex_cnt) VALUES (%s, %s, %s, %s, %s)"
                data = (itineraryid, name, int(price), currency, int(cnt))
                cursor.execute(sql, data)
                g.cnn.commit()
                sql = "select itineraryid, ex_name, ex_price, currency, ex_cnt, ex_price*ex_cnt from expense where itineraryid = %s "
                data = (itineraryid, )
                cursor.execute(sql, data)
                lists = cursor.fetchall()
                index = ['itineraryid', 'name', 'price', 'currency', 'cnt', 'total']
                data = toDict(index, lists)
                data = json.dumps(data)
            except Exception as e:
                print("error{}!".format(e))
            return data


# 获取费用列表
@auth.route('/getexpense/<id>')
def getexpense(id):
    try:
        dbcnn()
        cursor = g.cnn.cursor()

        sql = "select itineraryid, ex_name, ex_price, currency, ex_cnt, ex_price*ex_cnt from expense where itineraryid = %s "
        data = (id, )
        cursor.execute(sql, data)
        lists = cursor.fetchall()
        index = ['itineraryid', 'name', 'price', 'currency', 'cnt', 'total']
        data = toDict(index, lists)
        data = json.dumps(data)
    except Exception as e:
        print("error{}!".format(e))
    return data


# 按照景点名称搜索
@auth.route('/search/<word>')
def search(word):
    try:
        dbcnn()
        cursor = g.cnn.cursor()
        sql = "select id, cityid, name_cn, price, left(ltrim(description),15), cover from frag where name_cn like '%" + word + "%' or name_en like '%" + word + "%'"
        print(sql)
        # data = (word, word)
        cursor.execute(sql)
        lists = cursor.fetchall()
        index = ['id', 'cityid', 'name_cn', 'price', 'description', 'cover']
        res = toDict(index, lists)
        data = json.dumps(res)
    except Exception as e:
        print("error{}!".format(e))
    return data
