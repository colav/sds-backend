from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from datetime import date
from math import log
from flask import redirect




class CompendiumApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)


    def get_topics(self):

        return {"data":""}


    def get_groups(self,page=1,max_results=100,sort="citations",direction="descending"):
        if not page:
            page=1
        else:
            try:
                page=int(page)
            except:
                print("Could not convert end page to int")
                return None
        if not max_results:
            max_results=100
        else:
            try:
                max_results=int(max_results)
            except:
                print("Could not convert end max to int")
                return None

        search_dict={"type":"group"}
        var_dict={"name":1,"relations":1,"products_count":1,"citations_count":1,"products_by_year":1,"subjects":1}
        total=self.colav_db["branches"].count_documents(search_dict)
        cursor=self.colav_db["branches"].find(search_dict,var_dict)
        
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="production" and direction=="ascending":
            cursor.sort([("products_count",ASCENDING)])
        if sort=="production" and direction=="descending":
            cursor.sort([("products_count",DESCENDING)])

        skip = (max_results*(page-1))

        cursor=cursor.skip(skip).limit(max_results)

        data=[]
        for reg in cursor:
            entry={
                "id":reg["_id"],
                "name":reg["name"],
                "products_count":reg["products_count"],
                "citations_count":reg["citations_count"],
                "affiliations":{
                    "institution":{
                        "name":reg["relations"][0]["name"],
                        "id":reg["relations"][0]["id"]
                    }
                },
                "plot":[],
                "subjects":reg["subjects"][:10] if len(reg["subjects"])>=10 else reg["subjects"]
            }
            year_index={}

            for i,prod in enumerate(reg["products_by_year"]):
                
                entry["plot"].append({
                    "year":prod["year"],
                    "products":prod["value"],
                    "citations":0
                })
                year_index[prod["year"]]=i
            if "citations_by_year" in reg.keys():
                for cit in reg["citations_by_year"]:
                    if cit["year"] in year_index.keys():
                        entry["plot"][i]["citations"]=cit["value"]
                    else:
                        entry["plot"].append({
                            "year":cit["year"],
                            "products":0,
                            "citations":cit["value"]
                        })
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])
            if "subjects" in reg.keys():
                entry["subjects"]=reg["subjects"][:10] if len(reg["subjects"])>=10 else reg["subjects"]
            data.append(entry)

        return {"data":data,"page":page,"count":max_results,"total":total}


    def get_authors(self):

        return {"data":""}


    def get_institutions(self,page=1,max_results=10,sort="citations",direction="descending"):
        if not page:
            page=1
        else:
            try:
                page=int(page)
            except:
                print("Could not convert end page to int")
                return None
        if not max_results:
            max_results=100
        else:
            try:
                max_results=int(max_results)
            except:
                print("Could not convert end max to int")
                return None

        search_dict={}
        var_dict={"name":1,"products_count":1,"citations_count":1,"products_by_year":1,"subjects":1}
        total=self.colav_db["institutions"].count_documents(search_dict)
        cursor=self.colav_db["institutions"].find(search_dict,)
        
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="production" and direction=="ascending":
            cursor.sort([("products_count",ASCENDING)])
        if sort=="production" and direction=="descending":
            cursor.sort([("products_count",DESCENDING)])
        
        skip = (max_results*(page-1))

        cursor=cursor.skip(skip).limit(max_results)

        data=[]
        for reg in cursor:
            entry={
                "id":reg["_id"],
                "name":reg["name"],
                "products_count":reg["products_count"],
                "citations_count":reg["citations_count"],
                "plot":[],
                "subjects":[]
            }
            year_index={}
            for i,prod in enumerate(reg["products_by_year"]):
                print(prod)
                entry["plot"].append({
                    "year":prod["year"],
                    "products":prod["value"],
                    "citations":0
                })
                year_index[prod["year"]]=i
            if "citations_by_year" in reg.keys():
                for cit in reg["citations_by_year"]:
                    if cit["year"] in year_index.keys():
                        entry["plot"][i]["citations"]=cit["value"]
                    else:
                        entry["plot"].append({
                            "year":cit["year"],
                            "products":0,
                            "citations":cit["value"]
                        })
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])
            if "subjects" in reg.keys():
                entry["subjects"]=reg["subjects"][:10] if len(reg["subjects"])>=10 else reg["subjects"]
            data.append(entry)

        return {"data":data,"page":page,"count":max_results,"total":total}
            

    @endpoint('/app/compendium', methods=['GET'])
    def app_compendium(self):
        """
        """
        
        data = self.request.args.get('data')


        if data=="groups":
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            sort=self.request.args.get('sort')
            groups=self.get_groups(page=page,max_results=max_results,sort=sort)
            if groups:    
                response = self.app.response_class(
                response=self.json.dumps(groups),
                status=200,
                mimetype='application/json'
                )
            else:
                response = self.app.response_class(
                response=self.json.dumps({"status":"Request returned empty"}),
                status=204,
                mimetype='application/json'
            )
        elif data=="institutions":
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            sort=self.request.args.get('sort')
            institutions=self.get_institutions(page=page,max_results=max_results,sort=sort)
            if institutions:    
                response = self.app.response_class(
                response=self.json.dumps(institutions),
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