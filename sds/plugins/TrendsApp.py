from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from datetime import date

class TrendsApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)

    def get_info(self):
        subject=self.colav_db["subjects"].find_one({"names.name":{"$regex":".*covid.*","$options":"i"}},{"_id":1})
        covid_data={
            "id":subject["_id"] if subject else "",
            "products":self.colav_db["works"].count_documents({"subjects.name":{"$regex":".*covid.*","$options":"i"}}),
            "authors":self.colav_db["person"].count_documents({"subjects.name":{"$regex":".*covid.*","$options":"i"}}),
            "institutions":self.colav_db["affiliations"].count_documents({"types.type":{"$ne":"group"},"subjects.name":{"$regex":".*covid.*","$options":"i"}}),
            "groups":self.colav_db["affiliations"].count_documents({"types.type":"group","subjects.name":{"$regex":".*covid.*","$options":"i"}})
        }

        ods_data=[]
        for policy in self.colav_db["policies"].find({"abbreviations":"ODS"}):
            name=""
            for n in policy["names"]:
                if n["lang"]=="es":
                    name=n["name"]
                    break
                elif n["lang"]=="en":
                    name=n["name"]
            entry={
                "id":policy["_id"],
                "name":name,
                "index":"",
                "products":self.colav_db["works"].count_documents({"policies.id":policy["_id"]}),
                "authors":self.colav_db["person"].count_documents({"policies.id":policy["_id"]}),
                "institutions":self.colav_db["affiliations"].count_documents({"types.type":{"$ne":"group"},"policies.id":policy["_id"]}),
                "groups":self.colav_db["affiliations"].count_documents({"types.type":"group","policies.id":policy["_id"]})
            }
            if len(policy["index"])>0:
                for index in policy["index"]:
                    entry["index"]+=str(int(index["index"]))+"."
                entry["index"]=entry["index"][:-1]
            ods_data.append(entry)

        pdd_reg=self.colav_db["policies"].find_one({"abbreviations":"PDD"})
        pdd_data={
            "id":pdd_reg["_id"],
            "products":self.colav_db["works"].count_documents({"policies.id":pdd_reg["_id"]}),
            "authors":self.colav_db["person"].count_documents({"policies.id":pdd_reg["_id"]}),
            "institutions":self.colav_db["affiliations"].count_documents({"types.type":{"$ne":"group"},"policies.id":pdd_reg["_id"]}),
            "groups":self.colav_db["affiliations"].count_documents({"types.type":"group","policies.id":pdd_reg["_id"]})
        }

        pts_reg=self.colav_db["policies"].find_one({"abbreviations":"PTS"})
        pts_data={
            "id":pts_reg["_id"],
            "documents":self.colav_db["works"].count_documents({"policies.id":pts_reg["_id"]}),
            "authors":self.colav_db["person"].count_documents({"policies.id":pts_reg["_id"]}),
            "institutions":self.colav_db["affiliations"].count_documents({"types.type":{"$ne":"group"},"policies.id":pts_reg["_id"]}),
            "groups":self.colav_db["affiliations"].count_documents({"types.type":"group","policies.id":pts_reg["_id"]})
        }

        return {
            "covid":covid_data,
            "ODS":ods_data,
            "PDD":pdd_data,
            "PTS":pts_data
        }


    @endpoint('/app/trends', methods=['GET'])
    def app_trends(self):

        trends=self.get_info()
        if trends:    
            response = self.app.response_class(
            response=self.json.dumps(trends),
            status=200,
            mimetype='application/json'
            )
        else:
            response = self.app.response_class(
            response=self.json.dumps({"status":"Request returned empty"}),
            status=204,
            )

        response.headers.add("Access-Control-Allow-Origin", "*")
        return response