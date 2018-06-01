import requests, base64, hashlib

### TODO
### Support error codes and automatically get new token and url

class B2():
    _ACCOUNT_ID      = ''
    _APPLICATION_KEY = ''
    _BUCKET_ID       = ''
    _BUCKET_NAME     = ''
    _API_URL         = ''
    _DOWNLOAD_URL    = ''
    _UPLOAD_URL      = ''
    _TOKEN           = ''
    _UPLOAD_TOKEN    = ''
    _AUTH_HEADER     = ''   #{'Authorization':self._TOKEN}
    _MID_URL         = '/b2api/v1/'


    def __init__(self, account_id, application_key, bucket_id, bucket_name):
        self._ACCOUNT_ID = account_id
        self._APPLICATION_KEY = application_key
        self._BUCKET_ID = bucket_id
        self._BUCKET_NAME = bucket_name
        self.__authorize()

    def __authorize(self):
        auth_string = self._ACCOUNT_ID + ':' + self._APPLICATION_KEY
        auth_string = base64.b64encode(bytes(auth_string, 'utf-8'))
        auth_string = 'Basic ' + str(auth_string)[2:-1]
        #auth_string = 'Basic {}'.format(base64.b64encode(bytes('{}:{}'.format(self._ACCOUNT_ID, self._APPLICATION_KEY), 'utf-8')))
        r = requests.get('https://api.backblazeb2.com/b2api/v1/b2_authorize_account', headers={'Authorization':auth_string})
        data = r.json()
        self._API_URL      = data['apiUrl']
        self._TOKEN        = data['authorizationToken']
        self._DOWNLOAD_URL = data['downloadUrl']
        self._AUTH_HEADER  = {'Authorization':self._TOKEN}

    def __get_upload_url(self):
        r = requests.post(self._API_URL + self._MID_URL + '/b2_get_upload_url',
                         json = {'bucketId':self._BUCKET_ID},
                         headers = self._AUTH_HEADER)
        json = r.json()
        self._UPLOAD_URL = json['uploadUrl']
        self._UPLOAD_TOKEN = json['authorizationToken']
        return json['uploadUrl']

    def __get_path(self, nid, hash, part=None):
        if part == None:
            part = 0
        if type(part) is int:
            path = '{}.{}.{}'.format(nid, hash, part)
        print(path)
        return path

    def get_path(self, nid, hash, part=None):
        return self.__get_path(nid, hash, part=part)

    def upload(self, file, nid, hash, part=None):
        up_url = self.__get_upload_url()
        sha1digest = hashlib.sha1(file).hexdigest()
        headers = {'Authorization'     : self._UPLOAD_TOKEN,
                   'X-Bz-File-Name'    : self.__get_path(nid, hash, part),
                   'Content-Type'      : 'b2/x-auto',
                   'Content-Length'    : str(len(file)),
                   'X-Bz-Content-Sha1' : sha1digest}
        r = requests.post(self._UPLOAD_URL, headers=headers, data=file)
        return r.status_code, r.json()

    def download(self, nid, hash, part=None):
        full_path = '{}/file/{}/{}'.format(self._DOWNLOAD_URL, self._BUCKET_NAME, self.__get_path(nid, hash, part))
        print(full_path)
        return requests.get(full_path, headers=self._AUTH_HEADER).content

    def refresh(self):
        __authorize()
        __get_upload_url()
