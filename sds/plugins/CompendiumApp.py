from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from datetime import date
from math import log
from flask import redirect




class CompendiumApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)


    def get_subjects(self,page=1,max_results=10,institutions=[],groups=[],sort="citations",direction="descending"):
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
        var_dict={"name":1,"products_count":1,
                "citations_count":1,"products_by_year":1,
                "affiliations":1,"authors":1,"counts_by_year":1}
        total=self.colav_db["subjects"].count_documents(search_dict)
        cursor=self.colav_db["subjects"].find(search_dict,var_dict)
        
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
        index=max_results*(page-1)
        for subject in cursor:
            index+=1
            entry={
                "index":index,
                "name":subject["name"],
                "id":subject["_id"],
                "institutions":[], 
                "authors":[], 
                "groups":[], 
                "plot":[] #citations and products per year
            }
            if "affiliations" in subject.keys():
                entry["institutions"]=[{"name":aff["name"],"id":aff["id"]} for aff in subject["affiliations"] if not "type" in subject.keys()][:5]
                entry["groups"]=[{"name":aff["name"],"id":aff["id"]} for aff in subject["affiliations"] if "type" in subject.keys()][:5]
            if "authors" in subject.keys():
                entry["authors"]=[{"name":au["name"],"id":au["id"]} for au in subject["authors"]][:5]
            
            entry["plot"]=[{"year":sub["year"],"products":sub["works_count"],"citations":sub["cited_by_count"]} for sub in subject["counts_by_year"]]
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])
            
            data.append(entry)

        return {"data":data,"page":page,"count":max_results,"total":total}


    def get_groups(self,page=1,max_results=10,groups="",institutions="",sort="citations",direction="descending"):
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
        in_list=[]
        if groups:
            in_list.extend(groups.split())
        if institutions:
            in_list.extend(institutions.split())
        if len(in_list)>0:
            def_list=[]
            for iid in in_list:
                def_list.append(ObjectId(iid))
            search_dict["_id"]={"$in":def_list}
        var_dict={"name":1,"relations":1,"products_count":1,"citations_count":1,"products_by_year":1,"subjects":1}
        total=self.colav_db["affiliations"].count_documents(search_dict)
        cursor=self.colav_db["affiliations"].find(search_dict,var_dict)
        
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
        index=max_results*(page-1)
        for reg in cursor:
            index+=1
            entry={
                "index":index,
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


    def get_institutions(self,page=1,max_results=10,groups="",institutions="",sort="citations",direction="descending"):
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
        in_list=[]
        if groups:
            in_list.extend(groups.split())
        if institutions:
            in_list.extend(institutions.split())
        if len(in_list)>0:
            def_list=[]
            for iid in in_list:
                def_list.append(ObjectId(iid))
            search_dict["_id"]={"$in":def_list}
        var_dict={"name":1,"products_count":1,"citations_count":1,"products_by_year":1,"subjects":1}
        total=self.colav_db["affiliations"].count_documents(search_dict)
        cursor=self.colav_db["affiliations"].find(search_dict,)
        
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
        index=max_results*(page-1)
        for reg in cursor:
            index+=1
            entry={
                "index":index,
                "id":reg["_id"],
                "name":reg["name"],
                "products_count":reg["products_count"],
                "citations_count":reg["citations_count"],
                "plot":[],
                "subjects":[]
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
        elif data=="subjects":
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            sort=self.request.args.get('sort')
            subjects=self.get_subjects(page=page,max_results=max_results,sort=sort)
            if subjects:    
                response = self.app.response_class(
                response=self.json.dumps(subjects),
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