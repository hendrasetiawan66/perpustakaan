import falcon
import json
import MySQLdb
from datetime import datetime
import sys
import traceback


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

                print user_id

                sql_count = """
                    SELECT COUNT(*) as total
                    FROM messages
                    WHERE recipient_id=%s
                    GROUP BY sender_id
                    ORDER BY id DESC
                """
                cursor.execute(sql_count, (user_id,))
                total_data = cursor.fetchone()
                if total_data is not None and total_data!="":
                    total_message = int(total_data['total'])

                else:
                    return return_json(resp, 404, "message is not found")

                if total_message > 0:
                    message_sql = """
                        SELECT *
                        FROM messages
                        LEFT JOIN users ON messages.sender_id = users.id
                        WHERE sender_id=%s OR recipient_id=%s
                        ORDER BY modified DESC
                    """
                    cursor.execute(message_sql, (user_id, user_id))
                    all_messages = cursor.fetchall()

                    if all_messages is not None and all_messages != "":
                        output = {
                            "meta": {
                                "code": 200,
                                "confirm": "success"
                            },
                            "data": {}
                        }

                        for dc_mess in all_messages:
                            print dc_mess
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

                            output['data'].update(data_dict)
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
