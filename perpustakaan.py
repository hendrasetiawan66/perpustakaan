import falcon
import json
import MySQLdb
from datetime import datetime, timedelta
import uuid
import sys


class Login:
        def on_post(self, req, resp):
            db = MySQLdb.connect(host='localhost', user='root',
                             passwd='Aks4ra', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            raw_json = req.stream.read()

            param = json.loads(raw_json, encoding='utf-8')

            usr = param.get('username')

            pwd = param.get('password')

            if usr is not None and usr != "" and pwd is not None and pwd != "":
                 sqlCek = """
                    SELECT * FROM `user` WHERE username=%s AND password=%s
                 """

                 cursor.execute(sqlCek, (usr, pwd))

                 ada = cursor.fetchone()

                 if ada != "" and ada is not None:
                     genToken = str(uuid.uuid4())

                     if genToken != "" and genToken is not None:
                         db = MySQLdb.connect(host='localhost', user='root',
                                          passwd='Aks4ra', db='perpustakaan')
                         cursor = db.cursor(MySQLdb.cursors.DictCursor)

                         sqlUpdateToken = """
                            UPDATE `user` SET `token`=%s,`exp`=%s WHERE id=%s
                         """

                         expDate = datetime.now() + timedelta(days=1)

                         cursor.execute(sqlUpdateToken, (genToken, expDate, ada['id']))

                         db.commit()

                     ret = {"confirm": "login is succesfull", "data": genToken}

                 else:
                     ret = {"confirm": "Try again!"}

                 resp.body = json.dumps(ret)

                 print usr, pwd


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

aplikasi.add_route("/perpustakaan/login", Login())
aplikasi.add_route("/perpustakaan/buku", Buku())
aplikasi.add_route("/perpustakaan/insertbuku", InsertBuku())
aplikasi.add_route("/perpustakaan/updatebuku", UpdateBuku())
aplikasi.add_route("/perpustakaan/deletebuku", DeleteBuku())
aplikasi.add_route("/perpustakaan/pinjambuku", PinjamBuku())
aplikasi.add_route("/perpustakaan/listpeminjaman", ListPeminjaman())
aplikasi.add_route("/perpustakaan/pengembalianbuku", PengembalianBuku())
