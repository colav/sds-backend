from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
import hashlib
import os

class UpdateApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)

    def backup_db(self):
        response=os.system("rm -rf dump/")
        response=os.system("mongodump $MONGODB_IP -d sds")
        return {"response":response}

    def restore_db(self):
        if os.path.exists("dump"):
            response=os.system("mongorestore $MONGODB_IP -d sds dump/sds")
        else:
            response=-1
        return {"response":response}
    
    def delete_db(self):
        self.dbclient.drop_database("sds")

    def update_db(self,url="http://colav.co/snapshots/"):
        print("Attempting snapshot download")
        response=os.system("wget "+url+"sds.tgz")
        print("Decompressing")
        response=os.system("tar -zxvf sds.tgz")
        print("Attempting restoreing")
        response=os.system("mongorestore -h $MONGODB_IP -d sds dump/sds")
        
        return {"response":response}

    def pull(self):
        response=os.system("git pull")
        return {"response":response}
    
    def reset(self,commit):
        response=os.system("git reset --hard "+commit)
        return {"response":response}

    @endpoint('/app/updatedb', methods=['GET'])
    def updatedb(self):
        data = self.request.args.get('data')
        apikey=self.request.args.get('apikey')
        if apikey:
            if hashlib.md5(apikey.encode("utf-8")).hexdigest()!="c84894700bf94c6dad06ef7f22670e52":
                response = self.app.response_class(
                    response=self.json.dumps({}),
                    status=401,
                    mimetype='application/json'
                )
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
        else:
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=401,
                mimetype='application/json'
            )
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        if data=="update":
            url = self.request.args.get('url')
            if url:
                result=self.update_db(url=url)
            else:
                result=self.update_db()
        elif data=="backup":
            result=self.backup_db()
        elif data=="restore":
            result=self.restore_db()
        elif data=="delete":
            result=self.delete_db()
        elif data=="pull":
            result=self.pull()
        elif data=="reset":
            commit = self.request.args.get('commit')
            if commit:
                result=self.reset(url=url)
            else:
                result=self.update_db()
        else:
            result=None

        if result:
            response = self.app.response_class(
            response=self.json.dumps(result),
            status=200,
            mimetype='application/json'
            )
        else:
            response = self.app.response_class(
            response=self.json.dumps({}),
            status=204,
            mimetype='application/json'
            )
        
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response