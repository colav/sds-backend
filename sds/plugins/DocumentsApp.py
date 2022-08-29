from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from pickle import load

class DocumentsApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)

    def get_info(self,idx):
        document = self.colav_db['works'].find_one({"_id":ObjectId(idx)})
        if document:
            entry={"id":document["_id"],
                "title":document["titles"][0]["title"],
                "abstract":document["abstract"],
                "source":{},
                "year_published":document["year_published"],
                "language":"",
                "volume":"",
                "issue": "",
                "authors":[],
                "policies":{},
                "open_access_status": "",
                "citations_count":document["citations_count"] if "citations_count" in document.keys() else "",
                "external_ids":[],
                "external_urls":document["external_urls"]
            }
            if "language" in document.keys():
                entry["language"]=document["languages"][0] if len(document["languages"])>0 else ""
            if "bibliographic_info" in document.keys():
                if "volume" in document["bibliographic_info"].keys():
                    entry["volume"]=document["bibliographic_info"]["volume"]
                if "issue" in document["bibliographic_info"].keys():
                    entry["issue"]=document["bibliographic_info"]["issue"]
                if "open_access_status" in document["bibliographic_info"].keys():
                    entry["open_access_status"]=document["bibliographic_info"]["open_access_status"]
            index_list=[]
            if "policies" in document.keys():
                for policy in document["policies"]:
                    policy_reg=self.colav_db["policies"].find_one({"_id":policy["id"]})
                    policy_entry={
                        "id":policy["id"],
                        "index":"",
                        "name":policy["name"]
                    }
                    if len(policy_reg["index"])>0:
                        indexes=[]
                        for index in policy_reg["index"]:
                            indexes.append(index["index"])
                            policy_entry["index"]+=str(int(index["index"]))+"."
                        index_list.append(indexes)
                        policy_entry["index"]=policy_entry["index"][:-1]
                    if policy_reg["abbreviations"][0] in entry["policies"].keys():
                        entry["policies"][policy_reg["abbreviations"][0]].append(policy_entry)
                    else:
                        entry["policies"][policy_reg["abbreviations"][0]]=[policy_entry]
            if "ODS" in entry["policies"].keys():
                sorted_ods=sorted(entry["policies"]["ODS"],key=lambda x:index_list[entry["policies"]["ODS"].index(x)])
                entry["policies"]["ODS"]=sorted_ods

            if "source" in document.keys():
                source=self.colav_db["sources"].find_one({"_id":document["source"]["id"]})
                entry_source={
                    "name":source["title"],
                    "serials":{}
                }
                for serial in source["serials"]:
                    if not serial["type"] in entry_source.keys():
                        entry_source["serials"][serial["type"]]=serial["value"]
                entry["source"]=entry_source

            for author in document["authors"]:
                author_entry={}
                if len(document["authors"])==1:
                    author_entry["corresponding"]=True
                else:
                    for typ in author["types"]:
                        if typ["type"]=="corresponding":
                            author_entry["corresponding"]=True
                author_entry["name"]=author["full_name"]
                author_entry["id"]=author["id"]
                author_entry["affiliation"]={}
                group_name = ""
                group_id = ""
                inst_name=""
                inst_id=""
                if "affiliations" in author.keys():
                    if len(author["affiliations"])>0:
                        for aff in author["affiliations"]:
                            if "types" in aff.keys():
                                for typ in aff["types"]:
                                    if typ["type"]=="group":
                                        group_name=aff["name"]
                                        group_id=aff["id"]
                                    else:   
                                        inst_name=aff["name"]
                                        inst_id=aff["id"]  
                author_entry["affiliation"]={"institution":{"name":inst_name,"id":inst_id},
                                              "group":{"name":group_name,"id":group_id}}  

                entry["authors"].append(author_entry)
            
            for ext in document["external_ids"]:
                if ext["source"]=="doi":
                    entry["external_ids"].append({
                        "id":ext["id"],
                        "source":"doi",
                        "url":"https://doi.org/"+ext["id"]
                        
                    })
                if ext["source"]=="lens":
                    entry["external_ids"].append({
                        "id":ext["id"],
                        "source":"lens",
                        "url":"https://www.lens.org/lens/scholar/article/"+ext["id"]
                    })
                if ext["source"]=="scholar":
                    entry["external_ids"].append({
                        "id":ext["id"],
                        "source":"scholar",
                        "url":"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=info%3A"+ext["id"]+
                            "%3Ascholar.google.com"
                    })
                if ext["source"]=="minciencias":
                    entry["external_ids"].append({
                        "id":ext["id"],
                        "source":"minciencias",
                        "url":""
                    })   
            
            return {"data":entry,"filters":{}}
        else:
            return None

    def get_networks(self,idx=None,max_results=100,page=1,start_year=None,end_year=None,sort=None,direction=None):
        entry={
            "citations_network":{"nodes":load(open("./nodes.p","rb")),"edges":load(open("./edges.p","rb"))},
            "citations":[{}]
        }

        return {"data":entry,"filters":{}}

    @endpoint('/app/documents', methods=['GET'])
    def app_document(self):
        data = self.request.args.get('data')

        if data=="info":
            idx = self.request.args.get('id')
            info = self.get_info(idx)
            if info:    
                response = self.app.response_class(
                response=self.json.dumps(info),
                status=200,
                mimetype='application/json'
                )
            else:
                response = self.app.response_class(
                response=self.json.dumps({"status":"Request returned empty"}),
                status=204,
                mimetype='application/json'
            )
        elif data=="networks":
            idx = self.request.args.get('id')
            network=self.get_networks(idx)
            if network:
                response = self.app.response_class(
                response=self.json.dumps(network),
                status=200,
                mimetype='application/json'
                )
            else:
                response = self.app.response_class(
                response=self.json.dumps({"status":"Request returned empty"}),
                status=204,
                mimetype='application/json'
                )
        else:
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=400,
                mimetype='application/json'
            )

        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

