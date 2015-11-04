import falcon
import json
import MySQLdb
from datetime import datetime
import sys
import traceback
import pprint


class Index:
    def on_get(self, req, resp):
        try:
            # setting konfigurasi database
            db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            # variable yang dibutuhkan
            token = req.get_param('access_token')

            if token is None or token == "":
                return return_json(resp, 401, "Unauthorized access_token")

            sql_get_token = """
                SELECT * FROM oauth_access_tokens WHERE oauth_token=%s
            """
            cursor.execute(sql_get_token, (token,))
            rows = cursor.fetchone()

            if rows is not None and rows != "":
                user_id = int(rows['user_id'])

                sql_count = """
                    SELECT COUNT(*) as total
                    FROM messages
                    WHERE (sender_id=%s OR recipient_id=%s) AND messages.status=1
                    GROUP BY sender_id, recipient_id
                    ORDER BY id DESC
                """
                cursor.execute(sql_count, (user_id, user_id))
                total_data = cursor.fetchone()
                print total_data
                if total_data is not None and total_data!="":
                    total_message = int(total_data['total'])

                else:
                    return return_json(resp, 404, "message is not found")

                if total_message > 0:
                    message_sql = """
                        SELECT *
                        FROM messages
                        JOIN users send ON messages.sender_id = send.id
                        JOIN users rec ON messages.sender_id = rec.id
                        WHERE (sender_id=%s OR recipient_id=%s) AND messages.status=1
                        GROUP BY sender_id, recipient_id
                        ORDER BY modified DESC
                    """
                    cursor.execute(message_sql, (user_id, user_id))
                    all_messages = cursor.fetchall()
                    pprint.pprint(all_messages)
                    if all_messages is not None and all_messages != "":
                        output = {
                            "meta": {
                                "code": 200,
                                "confirm": "success"
                            },
                            "data": {}
                        }
                        output['data'] = []
                        for dc_mess in all_messages:
                            data_recipient = int(dc_mess['recipient_id'])
                            data_created = str(dc_mess['created']).split('.')[0]
                            data_modified = str(dc_mess['modified']).split('.')[0]

                            data_dict = {
                                "Message": {
                                    "id": int(dc_mess['id']),
                                    "parent_id": int(dc_mess['parent_id']),
                                    "sender_id": int(dc_mess['sender_id']),
                                    "recipient_id": int(dc_mess['recipient_id']),
                                    "message": str(dc_mess['message']),
                                    "is_read": int(dc_mess['is_read']),
                                    "created": data_created,
                                    "modified": data_modified
                                },
                                "Sender": {
                                    "id": int(dc_mess['sender_id']),
                                    "name": str(dc_mess['username']),
                                    "username": str(dc_mess['username'])
                                }
                            }

                            output['data'].append(data_dict)
                            cursor.close()

                            try:
                                data_resp = json.dumps(output, ensure_ascii=False).encode('utf-8')
                            except:
                                data_resp = json.dumps(output)

                            resp.status = falcon.HTTP_200
                            resp.body = data_resp
                else:
                    return return_json(resp, 404, "message is not found")

            else:
                return return_json(resp, 401, "token is not found")

        except Exception as e:
            if IS_DEV:
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                return return_json(resp, 500, str(e))
            else:
                return return_json(resp, 500, "Server sedang dalam proses maintenance. Maaf atas ketidaknyamanannya")


class Send:
    def on_post(self, req, resp):
        try:
            # konfigurasi database
            db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            raw_json = req.stream.read()
            param = json.loads(raw_json, encoding='utf-8')
            # daftar variable yang dibutuhkan dan respon jika variable-nya kosong
            list_parameter = [
                                {'index': 'access_token', 'message': 'Unauthorized access_token'},
                                {'index': 'message', 'message': 'message is required'},
                                {'index': 'recipient_id', 'message': 'recipient id is required'}
                             ]
            # inisialisasi variable penyimpan parameter
            data = {}

            for daftar in list_parameter:
                if daftar['index'] in param:
                    if param[daftar['index']] == "":
                        return return_json(resp, 401, daftar['message'])
                    else:
                        data[daftar['index']] = str(param[daftar['index']])
                else:
                    return return_json(resp, 401, daftar['message'])

            sql_get_user_id = """
                SELECT * FROM oauth_access_tokens WHERE oauth_token=%s
            """
            cursor.execute(sql_get_user_id, (data['access_token'],))
            rows = cursor.fetchone()

            if rows is not None and rows != "":
                user_id = int(rows['user_id'])

                waktu = datetime.now()
                sql_insert = "INSERT INTO `messages`(`sender_id`, `recipient_id`, `message`, `is_read`, `created`, `modified`) VALUES (%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql_insert, (user_id, data['recipient_id'], data['message'], 0, waktu, waktu))
                db.commit()
                # mengambil message_id terakhir/yang baru diinsertkan
                message_id = cursor.lastrowid

                sql = """ SELECT messages.*,
                send.id as send_id,send.username as send_name, send.username as send_username,
                rec.id as rec_id,rec.username as rec_name, rec.username as rec_username
                FROM messages
                left join users as send on send.id=sender_id
                left join users as rec on rec.id=recipient_id
                where messages.id=%s """
                cursor.execute(sql, (message_id, ))
                message_data = cursor.fetchone()

                query_notif = """
                    INSERT INTO `notifications`(`action_type`, `sender_type`,
                    `sender_key`, `recipient_type`, `recipient_key`, `object_type`,
                    `object_key`, `message`, `is_read`, `is_read_lightnotif`,
                    `created`, `modified`)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                cursor.execute(query_notif, ("DM", "User", user_id,
                                    "User", data['recipient_id'],
                                    "Message", message_id, SOCIAL_MESSAGES['DM'], 0, 0,
                                    waktu, waktu))
                db.commit()

                output = {
                    "meta": {
                        "code": 200,
                        "confirm": "Pesan berhasil dikirim"
                    },
                    "data": {
                        "Message": {
                                "id": message_data['id'],
                                "parent_id":message_data['parent_id'],
                                "sender_id": message_data['sender_id'],
                                "recipient_id": message_data['recipient_id'],
                                "message": message_data['message'],
                                "is_read": message_data['is_read'],
                                "created": str(message_data['created']).split(".")[0],
                                "modified": str(message_data['modified']).split(".")[0]
                        },
                        "Sender": {
                            "User": {
                                "id": message_data['send_id'],
                                "name": message_data['send_name'],
                                "username": message_data['send_username']
                            }
                        },
                        "Recipient": {
                            "User": {
                                "id": message_data['rec_id'],
                                "name": message_data['rec_name'],
                                "username": message_data['rec_username']
                            }
                        }
                    }
                }

                data_resp = json.dumps(output, encoding='utf-8', ensure_ascii=False)
                resp.status = falcon.HTTP_200
                resp.body = data_resp

            else:
                return return_json(resp, 401, "token is not found")

        except Exception as e:
            if IS_DEV:
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                return return_json(resp, 500, str(e))
            else:
                return return_json(resp, 500, "Server sedang dalam proses maintenance. Mohon maaf atas ketidaknyamanannya.")


class Delete:
    def on_post(self, req, resp):
        try:
            # konfigurasi database
            db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            raw_json = req.stream.read()
            param = json.loads(raw_json, encoding='utf-8')
            # daftar variable yang dibutuhkan dan respon jika variable-nya kosong
            list_parameter = [
                                {'index': 'access_token', 'message': 'Unauthorized access_token'},
                                {'index': 'message_ids', 'message': 'message index is required'}
                            ]
            # inisialisasi variable penyimpan parameter
            data = {}

            for daftar in list_parameter:
                if daftar['index'] in param:
                    if param[daftar['index']] == "":
                        return return_json(resp, 401, daftar['message'])
                    else:
                        data[daftar['index']] = param.get(daftar['index'])
                else:
                    return return_json(resp, 401, daftar['message'])

            sql_get_user_id = """
                SELECT * FROM oauth_access_tokens WHERE oauth_token=%s
            """
            cursor.execute(sql_get_user_id, (data['access_token'],))
            rows = cursor.fetchone()

            if rows is not None and rows != "":
                user_id = int(rows['user_id'])

            for message_id in data['message_ids']:
                sql_count = """
                    SELECT count(*) as jml FROM `messages` WHERE (`sender_id`=%s OR `recipient_id`=%s) AND `id`=%s
                    """

                cursor.execute(sql_count, (user_id, user_id, message_id))
                row_count = cursor.fetchone()
                print row_count
                if row_count is None:
                    return return_json(resp, 404, "Data tidak ditemukan")
                else:
                    total_data = int(row_count['jml'])

                    if total_data > 0:
                        q = """
                            UPDATE `messages`
                            SET `modified`=%s,
                                `status`=0 WHERE `id`=%s
                        """
                        try:
                            waktu = datetime.now()
                            cursor.execute(q, (waktu, message_id))
                            db.commit()

                        except Exception as e:
                            db.rollback()
                            return return_json(resp, 500, "Gagal menghapus pesan")
                    else:
                        return return_json(resp, 404, "Data tidak ditemukan")

            cursor.close()

            output = {
                "meta": {
                    "code": 200,
                    "confirm": "success"
                },
                "data": {'message': "Pesan berhasil dihapus"}
            }

            data_resp = json.dumps(output, ensure_ascii=False).encode('utf-8')
            resp.status = falcon.HTTP_200  # This is the default status
            resp.body = data_resp
        except Exception as e:
            if IS_DEV:
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                return return_json(resp, 500, str(e))
            else:
                return return_json(resp, 500, "Server sedang dalam proses maintenance. Mohon maaf atas ketidaknyamanannya.")


class Detail:
    def on_get(self, req, resp):
      try:
        # konfigurasi database
        db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='perpustakaan')
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        # daftar variable yang dibutuhkan dan respon jika variable-nya kosong
        list_parameter = [
            {"index": "access_token", "message": "Unauthorized access_token"},
            {"index": "sender_id", "message": "Sender_id is required"}
        ]
        data = {}

        for par in list_parameter:
            if req.get_param(par['index']) is None or req.get_param(par['index']) == "":
                return return_json(resp, 401, req.get_param(par['message']))
            else:
                data[req.get_param(par['index'])] = str(req.get_param(par['index']))

        sql_get_user_id = """
            SELECT * FROM oauth_access_tokens WHERE oauth_token=%s
        """
        cursor.execute(sql_get_user_id, (req.get_param('access_token'),))
        rows = cursor.fetchone()

        if rows is not None and rows != "":
            user_id = int(rows['user_id'])
        else:
            return return_json(resp, 401, "token is not found")

        sql_count = """
                SELECT count(*) as total
                FROM messages
                where (sender_id=%s and recipient_id=%s) or (sender_id=%s and recipient_id=%s)
                order by id DESC;
            """ %  (req.get_param('sender_id'), user_id, user_id, req.get_param('sender_id'))

        cursor.execute(sql_count)
        row_count = cursor.fetchone()
        total_data = int(row_count['total'])

        #print row_count[0][0]
        if total_data > 0:
            output = {
                "meta": {
                    "code": 200,
                    "confirm": "success"
                },
                "data": {}
            }
        else:
           return return_json(resp, 404, "Pesan tidak ditemukan")

        query_m = """
                 SELECT messages.*,
                 send.id as send_id,send.username as sender_name, send.username as send_username,
                 rec.id as rec_id,rec.username as rec_name, rec.username as rec_username
                 FROM messages
                 left join users as send on send.id=sender_id
                 left join users as rec on rec.id=recipient_id
                 where (sender_id=%s and recipient_id=%s) or (sender_id=%s and recipient_id=%s) order by id DESC;
            """ %  (req.get_param('sender_id'), user_id, user_id, req.get_param('sender_id'))

        cursor.execute(query_m)
        rows = cursor.fetchall()

        output["data"] = []

        rows = list(rows)

        rows.reverse()

        pprint.pprint(rows)

        for data_tt in rows:
            data_dict = None
            data_recipient = int(data_tt['rec_id'])

            data_created = str(data_tt['created'])
            data_modified = str(data_tt['modified'])

            waktu = data_tt['created']
            data_dict = {"Message": {
                    "id": str(data_tt['id']),
                    "parent_id":data_tt['parent_id'],
                    "sender_id": str(data_tt['send_id']),
                    "recipient_id": str(data_tt['rec_id']),
                    "message": data_tt['message'],
                    "is_read": str(data_tt['is_read']),
                    "created": data_created,
                    "modified": data_modified
                },
                "Sender": {
                    "id": str(data_tt['send_id']),
                    "name": data_tt['sender_name'],
                    "username": str(data_tt['send_username'])
                },
                "Recipient": {
                    "id": str(data_tt['rec_id']),
                    "name": data_tt['rec_name'],
                    "username": str(data_tt['rec_username'])
                },

            }

            output["data"].append(data_dict)

        cursor.close()
        try:
            data_resp = json.dumps(output, ensure_ascii=False).encode('utf-8')
        except:
            data_resp = json.dumps(output)

        resp.status = falcon.HTTP_200
        resp.body = data_resp

      except Exception as e:
        if IS_DEV:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            return return_json(resp, 500, str(e))
        else:
            return return_json(resp, 500, "Server sedang dalam proses maintenance. Mohon maaf atas ketidaknyamanannya.")


class MarkRead:
    def on_post(self, req, resp):
        try:
            # konfigurasi database
            db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='perpustakaan')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)

            raw_json = req.stream.read()
            param = json.loads(raw_json, encoding='utf-8')
            # daftar variable yang dibutuhkan dan respon jika variable-nya kosong
            list_parameter = [
                                {'index': 'access_token', 'message': 'Unauthorized access_token'},
                                {'index': 'message_ids', 'message': 'message index is required'}
                            ]

            data = {}

            for daftar in list_parameter:
                if daftar['index'] in param:
                    if param[daftar['index']] == "":
                        return return_json(resp, 401, daftar['message'])
                    else:
                        data[daftar['index']] = param.get(daftar['index'])
                else:
                    return return_json(resp, 401, daftar['message'])

            sql_get_user_id = """
                SELECT * FROM oauth_access_tokens WHERE oauth_token=%s
            """
            cursor.execute(sql_get_user_id, (param['access_token'],))
            rows = cursor.fetchone()

            if rows is not None and rows != "":
                user_id = int(rows['user_id'])
            else:
                return return_json(resp, 401, "token is not found")

            waktu = datetime.now()

            if isinstance(data['message_ids'], str) or isinstance(data['message_ids'], unicode):
                arrMessageIds = json.loads(data['message_ids'], encoding='utf-8')
            else:
                arrMessageIds = data['message_ids']

            for MessageId in arrMessageIds:
                sql_update = "UPDATE `messages` SET `is_read`=%s, `modified`=%s WHERE `id`=%s"
                cursor.execute(sql_update, (1, waktu, MessageId))

            db.commit()

            output = {
                "meta": {
                    "code": 200,
                    "confirm": "success"
                },
                "data": "mark read success"
            }

            data_resp = json.dumps(output, encoding='utf-8', ensure_ascii=False)
            resp.status = falcon.HTTP_200
            resp.body = data_resp

        except Exception as e:
            if IS_DEV:
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                return return_json(resp, 500, str(e))
            else:
                return return_json(resp, 500, "Server sedang dalam proses maintenance. Mohon maaf atas ketidaknyamanannya.")


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

SOCIAL_MESSAGES = {
                    "DM": "mengirimkan pesan untuk anda",
                    "NEW_BADGE": "mempunyai tanda pengenal baru di aplikasi",
                    "JOIN": "baru saja bergabung",
                    "ADD": "baru saja menambahkan sebuah buku baru",
                    "RELEASE": "baru saja merilis sebuah buku baru",
                    "NEW_BOOK": "ada buku baru di aplikasi",
                    "ADD_COLLECTION": "baru saja menambahkan sebuah buku baru",
                    "RECOMMEND": "baru saja merekomendasikan sebuah buku untuk anda",
                    "NEW_FOLLOWER": "mulai mengikuti anda",
                    "REVIEW": "baru saja mengulas sebuah buku",
                    "COMMENT_REVIEW": "baru saja berkomentar pada sebuah ulasan",
                    "LIKE_REVIEW": "menyukai ulasan anda",
                    "LIKE_COMMENT": "menyukai komentar anda",
                    "LIKE_FEED": "menyukai berita anda",
                    "FOLLOW_USER": "baru saja mengikuti",
                    "FOLLOW_LIBRARY": "baru saja mengikuti",
                    "FOLLOW_AUTHOR": "baru saja mengikuti"
                }
