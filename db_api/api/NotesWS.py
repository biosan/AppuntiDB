from db_api.extensions   import websocket
from db_api.common.utils import IDTools

class WS():
    def __init__(self, DB):
        self.DB = DB

    #@websocket.route('/notes/ws')
    def WSPageHandler(self, ws):
        page = 0
        nid  = ''
        message = ws.receive()
        if not self.DB.IDTools.note_exist(message):
            ws.send('Error: Note does not exist')
        nid = message
        max_pages = self.DB.get_note(nid)['pages']

        while not ws.closed:
            message = ws.receive()
            new_page = page
            update = True
            if message == 'up':
                new_page += 1
            elif message == 'down':
                new_page -= 1
            elif message.isdigit():
                new_page = int(message)
                if new_page == page:
                    'No change'
                    update = False
            else:
                ws.send('Error: Wrong command')
                update = False

            if max_pages == None and update:
                ws.send(self.DB.get_note_file(nid, page=None))
            elif 0 < new_page < max_pages and update:
                page == new_page
                ws.send(self.DB.get_note_file(nid, page))  ### Maybe something more performant (some caching)

"""
class NotesWS(Namespace):
    def on_connect(self):
        self.send('New connection, send the NID of the required note')
        sid_nid_table[request.sid] = None
        return request.sid

    def on_disconnect(self):
        return sid_nid_table.pop(request.sid)

    def on_event(self, data):
        if data == 'up':
            sid_nid_table[request.sid] += 1
        elif data == 'down':
            sid_nid_table[request.sid] -= 1
        else:
            self.send('No change!')
        self.send(sid_nid_table[request.sid])


    def on_event(self, data):
        if IDTools.is_valid_id(data, with_identificator=True):
            if IDTools.note_exist(data[3:]):
                sid_nid_table[request.sid] = data[3:]
            else:
                self.send('Error: NID inexistent')
        elif data.isdigit():
            page = int(data)
            self.send(db.get_page(sid_nid_table[request.sid], page))
        elif data == 'up':
            sid_nid_page_table
        else:
            self.send('Error: Wrong message')

        emit('my_response', data)
"""

