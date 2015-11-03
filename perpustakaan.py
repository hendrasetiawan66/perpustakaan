import falcon
import json
import MySQLdb
from datetime import datetime, timedelta
import uuid
import hashlib
import traceback
import sys
import os
import message


class LoginResource:
    #import MySQLdb
    def on_post(self, req, resp):
      try:
        db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='perpustakaan')
        raw_json = req.stream.read()
        result_json = json.loads(raw_json, encoding='utf-8')
        # daftar variable yang dibutuhkan
        client_id = result_json["client_id"]
        device_id = result_json["device_id"]
        secret_id = result_json["client_secret"]
        username = result_json["username"]
        password = result_json["password"]
        # validation
        if not req.client_accepts_json:
            return return_json(resp, 400, "Data wajib valid json")

        data_list = ["client_id", "client_secret", "username", "password", "device_id"]
        for nama in data_list:
            if not result_json.has_key(nama):
        	   return return_json(resp, 400, "Data %s wajib ada" % nama)

        # cek valid client id
        sekret = API_SECRET[client_id]
        if secret_id != sekret:
            return return_json(resp, 401, "Data secret_id tidak terdaftar")
        ooo = "select users.* from users where username = '%s'" % username
        cursor = db.cursor()
        cursor.execute(ooo)
        rows = cursor.fetchone()
        if not rows:
            return return_json(resp, 404, "You don't have account yet")

        padd = password
        if rows[2] != padd: #cek password apa sudah sama
            return return_json(resp, 400, "Password Not Match")

        user_id = int(rows[0])
        cursor.close()
        return proses_login(resp, user_id, device_id, client_id)
      except Exception as e:
        if IS_DEV:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
      	#di masukan ke sistem loging
        return return_json(resp, 500, str(e))


def proses_login(resp, user_id, device_id, client_id):
        db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='perpustakaan')
        cursor = db.cursor()
        new_token = hashlib.sha1(os.urandom(128)).hexdigest()
        waktu = datetime.now()
        update = waktu + timedelta(weeks=1)
        update = update.date()
        sql = """
            insert into oauth_access_tokens(oauth_token, client_id,
                user_id, expires, created, modified, expired, device_id)
            values(%s, %s, %s, 0, %s, %s, %s, "%s")
            """
        sql0 = """
             delete from oauth_access_tokens where user_id=%s;
            """ % int(user_id)
        cursor.execute(sql0)
        cursor.execute(sql, (new_token, client_id, int(user_id), waktu,
            waktu, update, device_id))
        sql2 = "update users set users.last_login=%s where users.id=%s"
        cursor.execute(sql2, (waktu, user_id))
        db.commit() #save db
        cursor.close()
        data = {
            "meta": {
                "code": 200,
                "confirm": "success"
               },
            "data": {
               "access_token": new_token,
               "created": str(waktu),
               "expired": str(update),
               "device_id": device_id,
               "os_version": None,
               "registration_id": None,
               "app_version": None
            }
        }
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data , ensure_ascii=False).encode('utf-8')


def return_json(resp, code, message):
        data = {"meta":{"code":code}}
        data["meta"]["error_message"] = message
        resp.body = json.dumps(data)
        resp.status = falcon.HTTP_200
        return resp


API_SECRET = {
        'clientidhendra' : 'secretidhendra'
}


IS_DEV = True


class Buku:
        def on_post(self, req, resp):
            raw_json = req.stream.read()
            param = json.loads(raw_json, encoding='utf-8')

            token = param.get('token')

            if token != "" and token is not None:
                cekToken = """
                    SELECT * FROM user WHERE token=%s
                """

                db = MySQLdb.connect(host='localhost', user='root',
                                 passwd='Aks4ra', db='perpustakaan')
                cursor = db.cursor(MySQLdb.cursors.DictCursor)

                cursor.execute(cekToken, (token,))

                checked = cursor.fetchone()

                # data = ""

                if checked != "" and checked is not None:

                    viewBuku = """
                        SELECT * FROM buku
                        JOIN penerbit ON (buku.penerbit_id = penerbit.id)
                        JOIN penulis ON (buku.penulis_id = penulis.id)
                    """

                    db = MySQLdb.connect(host='localhost', user='root',
                                     passwd='Aks4ra', db='perpustakaan')
                    cursor = db.cursor(MySQLdb.cursors.DictCursor)

                    cursor.execute(viewBuku)

                    listBuku = cursor.fetchallDict()

                    if listBuku != "" and listBuku is not None:
                        data = listBuku
                    else:
                        data = "Buku Kosong!!!"

                ret = {"confirm": "Books List", "data": data}
            else:

                ret = {"confirm": "Your 'token' data is not correct!"}

            resp.body = json.dumps(ret)


class InsertBuku:
    def on_post(self, req, resp):
        raw_json = req.stream.read()
        param = json.loads(raw_json, encoding='utf-8')

        token = param.get('token')
        buku = param.get('buku')
        penulis_id = param.get('penulis_id')
        penerbit_id = param.get('penerbit_id')

        if token != "" and token is not None and buku != "" and buku is not None and penulis_id != "" and penulis_id is not None and penerbit_id != "" and penerbit_id is not None:
            cekToken = """
                SELECT * FROM user WHERE token=%s
            """

            db = MySQLdb.connect(host='localhost', user='root',
                             passwd='Aks4ra', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute(cekToken, (token,))

            tokenChecked = cursor.fetchone()

            if tokenChecked != "" and tokenChecked is not None:
                cekPenulis = """
                    SELECT * FROM penulis WHERE id=%s
                """

                db = MySQLdb.connect(host='localhost', user='root',
                                 passwd='Aks4ra', db='perpustakaan')
                cursor = db.cursor(MySQLdb.cursors.DictCursor)

                cursor.execute(cekPenulis, (penulis_id,))

                penulisChecked = cursor.fetchone()

                if penulisChecked != "" and penulisChecked is not None:
                    cekPenerbit = """
                        SELECT * FROM penerbit WHERE id=%s
                    """

                    db = MySQLdb.connect(host='localhost', user='root',
                                     passwd='Aks4ra', db='perpustakaan')
                    cursor = db.cursor(MySQLdb.cursors.DictCursor)

                    cursor.execute(cekPenerbit, (penerbit_id,))

                    penerbitChecked = cursor.fetchone()

                    if penerbitChecked != "" and penerbitChecked is not None:
                        sqlInsert = """
                            INSERT INTO `buku`(`id`, `judul`, `penerbit_id`, `penulis_id`) VALUES ('',%s, %s, %s)
                        """

                        db = MySQLdb.connect(host='localhost', user='root',
                                         passwd='Aks4ra', db='perpustakaan')
                        cursor = db.cursor(MySQLdb.cursors.DictCursor)

                        cursor.execute(sqlInsert, (buku, penerbit_id, penulis_id))

                        db.commit()

                        data = {"buku": buku, "penulis_id": penulis_id, "penerbit_id": penerbit_id}

                        ret = {"confirm": "insert buku berhasil!!!", "data": data}

            else:
                ret = {"confirm": "Data Token Salah!!!"}

            resp.body = json.dumps(ret)


class UpdateBuku:
    def on_post(self, req, resp):
        raw_json = req.stream.read()
        param = json.loads(raw_json, encoding='utf-8')

        token = param.get('token')
        buku = param.get('buku')
        penulis_id = param.get('penulis_id')
        penerbit_id = param.get('penerbit_id')
        buku_id = param.get('buku_id')

        if buku_id != "" and buku_id is not None and token != "" and token is not None and buku != "" and buku is not None and penulis_id != "" and penulis_id is not None and penerbit_id != "" and penerbit_id is not None:
            cekToken = """
                SELECT * FROM user WHERE token=%s
            """

            db = MySQLdb.connect(host='localhost', user='root',
                             passwd='Aks4ra', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute(cekToken, (token,))

            tokenChecked = cursor.fetchone()

            if tokenChecked != "" and tokenChecked is not None:
                cekPenulis = """
                    SELECT * FROM penulis WHERE id=%s
                """

                db = MySQLdb.connect(host='localhost', user='root',
                                 passwd='Aks4ra', db='perpustakaan')
                cursor = db.cursor(MySQLdb.cursors.DictCursor)

                cursor.execute(cekPenulis, (penulis_id,))

                penulisChecked = cursor.fetchone()

                if penulisChecked != "" and penulisChecked is not None:
                    cekPenerbit = """
                        SELECT * FROM penerbit WHERE id=%s
                    """

                    db = MySQLdb.connect(host='localhost', user='root',
                                     passwd='Aks4ra', db='perpustakaan')
                    cursor = db.cursor(MySQLdb.cursors.DictCursor)

                    cursor.execute(cekPenerbit, (penerbit_id,))

                    penerbitChecked = cursor.fetchone()

                    if penerbitChecked != "" and penerbitChecked is not None:
                        sqlUpdate = """
                            UPDATE `buku` SET `judul`=%s,`penerbit_id`=%s,`penulis_id`=%s WHERE id=%s
                        """

                        db = MySQLdb.connect(host='localhost', user='root',
                                         passwd='Aks4ra', db='perpustakaan')
                        cursor = db.cursor(MySQLdb.cursors.DictCursor)

                        cursor.execute(sqlUpdate, (buku, penerbit_id, penulis_id, buku_id))

                        db.commit()

                        data = {"buku": buku, "penulis_id": penulis_id, "penerbit_id": penerbit_id, "id": buku_id}

                        ret = {"confirm": "update buku berhasil!!!", "data": data}

            else:
                ret = {"confirm": "Data Token Salah!!!"}

            resp.body = json.dumps(ret)


class DeleteBuku:
    def on_post(self, req, resp):
        raw_json = req.stream.read()
        param = json.loads(raw_json, encoding='utf-8')

        token = param.get('token')
        buku_id = param.get('buku_id')

        if buku_id != "" and buku_id is not None and token != "" and token is not None:
            cekToken = """
                SELECT * FROM user WHERE token=%s
            """

            db = MySQLdb.connect(host='localhost', user='root',
                             passwd='Aks4ra', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute(cekToken, (token,))

            tokenChecked = cursor.fetchone()

            if tokenChecked != "" and tokenChecked is not None:
                sqlDelete = """
                    DELETE FROM `buku` WHERE id=%s
                """

                db = MySQLdb.connect(host='localhost', user='root',
                                 passwd='Aks4ra', db='perpustakaan')
                cursor = db.cursor(MySQLdb.cursors.DictCursor)

                cursor.execute(sqlDelete, (buku_id,))

                db.commit()

                data = {"id": buku_id}

                ret = {"confirm": "delete buku berhasil!!!", "data": data}

            else:
                ret = {"confirm": "Data Token Salah!!!"}

            resp.body = json.dumps(ret)


class PinjamBuku:
    def on_post(self, req, resp):

        raw_json = req.stream.read()
        param = json.loads(raw_json, encoding='utf-8')

        token = param.get('token')
        buku_id = param.get('buku_id')
        tgl_pinjam = datetime.strptime(param.get('tgl_pinjam'), "%Y-%m-%d")
        tgl_kembali = tgl_pinjam + timedelta(days=7)

        if token == "" or token is None:
            ret = {"confirm": "inputkan token!"}
        else:
            cek_sql = """
                SELECT * FROM user WHERE token=%s
            """

            db = MySQLdb.connect(host='localhost', user='root',
                             passwd='Aks4ra', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute(cek_sql, (token,))

            tokenChecked = cursor.fetchone()

            if tokenChecked == "" or tokenChecked is None:
                ret = {"confirm": "token yang Anda inputkan tidak valid!"}
            else:
                user_id = tokenChecked["id"]

                sql_pinjam = """
                    INSERT INTO `pinjam`
                    (`tanggal_pinjam`, `tanggal_kembali`, `user_id`, `buku_id`)
                    VALUES (%s, %s, %s, %s)
                """

                db = MySQLdb.connect(host='localhost', user='root',
                                 passwd='Aks4ra', db='perpustakaan')
                cursor = db.cursor(MySQLdb.cursors.DictCursor)

                cursor.execute(sql_pinjam, (tgl_pinjam, tgl_kembali, user_id, buku_id))

                db.commit()

                ret = {"confirm": "Buku berhasil dipinjam"}

        resp.body = json.dumps(ret)


class ListPeminjaman:
    def on_post(self, req, resp):
        raw_json = req.stream.read()
        param = json.loads(raw_json, encoding='utf-8')

        token = param.get('token')

        if token == "" or token is None:
            ret = {"confirm": "inputkan token!"}
        else:
            cek_sql = """
                SELECT * FROM user WHERE token=%s
            """

            db = MySQLdb.connect(host='localhost', user='root',
                             passwd='Aks4ra', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute(cek_sql, (token,))

            tokenChecked = cursor.fetchone()

            if tokenChecked == "" or tokenChecked is None:
                ret = {"confirm": "token yang Anda inputkan tidak valid!"}
            else:
                sql_list = """
                    SELECT user.username, buku.judul
                    FROM `pinjam`
                    JOIN user ON (pinjam.user_id = user.id)
                    JOIN buku ON (pinjam.buku_id = buku.id)
                    WHERE user.token=%s
                """

                cursor.execute(sql_list, (token,))

                data = cursor.fetchallDict()

                ret = {"confirm": "Daftar buku pinjaman Sdr/i %s" % tokenChecked['username'],
                       "data": data}

        resp.body = json.dumps(ret)


class PengembalianBuku:
    def on_post(self, req, resp):
        raw_json = req.stream.read()
        param = json.loads(raw_json, encoding='utf-8')

        token = param.get('token')
        buku_id = param.get('buku_id')

        if token == "" or token is None:
            ret = {"confirm": "inputkan token!"}
        else:
            cek_sql = """
                SELECT * FROM user WHERE token=%s
            """

            db = MySQLdb.connect(host='localhost', user='root',
                             passwd='Aks4ra', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute(cek_sql, (token,))

            tokenChecked = cursor.fetchone()

            if tokenChecked == "" or tokenChecked is None:
                ret = {"confirm": "token yang Anda inputkan tidak valid!"}
            else:
                sql_list = """
                    SELECT user.username, buku.judul
                    FROM `pinjam`
                    JOIN user ON (pinjam.user_id = user.id)
                    JOIN buku ON (pinjam.buku_id = buku.id)
                    WHERE user.token=%s AND pinjam.buku_id=%s
                """

                db = MySQLdb.connect(host='localhost', user='root',
                                 passwd='Aks4ra', db='perpustakaan')
                cursor = db.cursor(MySQLdb.cursors.DictCursor)

                cursor.execute(sql_list, (token, buku_id))

                data = cursor.fetchone()

                if data == "" or data is None:
                    ret = {"confirm": "ID Buku yang Anda masukkan salah!"}
                else:
                    sql_update = """
                        UPDATE `pinjam` SET `tanggal_pengembalian`=%s WHERE `buku_id`=%s AND user_id=%s
                    """
                    db = MySQLdb.connect(host='localhost', user='root',
                                     passwd='Aks4ra', db='perpustakaan')
                    cursor = db.cursor(MySQLdb.cursors.DictCursor)

                    date_1 = datetime.now()

                    cursor.execute(sql_update, (date_1, buku_id, tokenChecked['id']))

                    db.commit()

                    ret = {"confirm": "Buku dengan judul %s telah dikembalikan" % data['judul']}

            resp.body = json.dumps(ret)


aplikasi = falcon.API()

aplikasi.add_route("/perpustakaan/login", LoginResource())
aplikasi.add_route("/perpustakaan/buku", Buku())
aplikasi.add_route("/perpustakaan/insertbuku", InsertBuku())
aplikasi.add_route("/perpustakaan/updatebuku", UpdateBuku())
aplikasi.add_route("/perpustakaan/deletebuku", DeleteBuku())
aplikasi.add_route("/perpustakaan/pinjambuku", PinjamBuku())
aplikasi.add_route("/perpustakaan/listpeminjaman", ListPeminjaman())
aplikasi.add_route("/perpustakaan/pengembalianbuku", PengembalianBuku())
aplikasi.add_route("/perpustakaan/indexpesan", message.Index())
aplikasi.add_route("/perpustakaan/sendpesan", message.Send())
aplikasi.add_route("/perpustakaan/deletepesan", message.Delete())
aplikasi.add_route("/perpustakaan/detailpesan", message.Detail())
