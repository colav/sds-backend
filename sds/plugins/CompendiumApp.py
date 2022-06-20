from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from datetime import date
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from math import log
from flask import redirect




class CompendiumApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)

    def get_info(self,institutions=[],groups=[],start_year=None,end_year=None):
        initial_year=9999
        final_year=0
        if start_year:
            try:
                start_year=int(start_year)
            except:
                print("Could not convert start year to int")
                return None
        if end_year:
            try:
                end_year=int(end_year)
            except:
                print("Could not convert end year to int")
                return None

        institutions_list=institutions.split() if institutions else []
        groups_list=groups.split() if groups else []

        groups_filter=[]
        institutions_filter=[]
        if len(groups_list)!=0:
            for group in groups_list:
                res=self.colav_db["affiliations"].find_one({"_id":ObjectId(group),"types.type":"group"})
                if res:
                    name=""
                    for n in res["names"]:
                        if n["lang"]=="es":
                            name=n["name"]
                            break
                        elif n["lang"]=="en":
                            name=n["name"]
                    groups_filter.append({"name":name,"id":group})
                    for pby in res["products_by_year"]:
                        if pby["year"]<initial_year:
                            initial_year=pby["year"]
                        if pby["year"]>final_year:
                            final_year=pby["year"]
        if len(institutions_list)!=0:
            for inst in institutions_list:
                res=self.colav_db["affiliations"].find_one({"_id":ObjectId(inst)})
                if res:
                    name=""
                    for n in res["names"]:
                        if n["lang"]=="es":
                            name=n["name"]
                            break
                        elif n["lang"]=="en":
                            name=n["name"]
                    institutions_filter.append({"name":name,"id":inst})
                    if initial_year==9999:
                        for pby in res["products_by_year"]:
                            if pby["year"]<initial_year:
                                initial_year=pby["year"]
                    if final_year==0:
                        for pby in res["products_by_year"]:
                            if pby["year"]>final_year:
                                final_year=pby["year"]

        if len(groups_filter)==0:
            search_dict={}
            in_list=[]
            if institutions :
                in_list.extend(institutions_list)
            if len(in_list)>0:
                def_list=[]
                for iid in in_list:
                    def_list.append(ObjectId(iid))
                search_dict["relations.id"]={"$in":def_list}
            if start_year or end_year:
                search_dict["products_by_year.year"]={}
            if start_year:
                search_dict["products_by_year.year"]["$gte"]=start_year
            if end_year:
                search_dict["products_by_year.year"]["$lte"]=end_year
            for reg in self.colav_db["affiliations"].find(search_dict,{"names":1,"relations":1,"types":1,"products_by_year":1}):
                for typ in reg["types"]: 
                    if typ["type"]=="group":
                        name=reg["names"][0]["name"]
                        for n in reg["names"]:
                            if n["lang"]=="es":
                                name=n["name"]
                                break
                            if n["lang"]=="en":
                                name=n["name"]
                        groups_filter.append({"name":name,"id":reg["_id"]})
                        for pby in reg["products_by_year"]:
                            if pby["year"]<initial_year:
                                initial_year=pby["year"]
                            if pby["year"]>final_year:
                                final_year=pby["year"]

        if len(institutions_filter)==0:
            search_dict={}
            in_list=[]
            if groups:
                in_list.extend(groups_list)
            elif len(groups_list)>0:
                for gr in groups_list:
                    in_list.append(str(gr["id"]))
            if len(in_list)>0:
                def_list=[]
                for iid in in_list:
                    def_list.append(ObjectId(iid))
                search_dict["relations.id"]={"$in":def_list}
            if start_year or end_year:
                search_dict["products_by_year.year"]={}
            if start_year:
                search_dict["products_by_year.year"]["$gte"]=start_year
            if end_year:
                search_dict["products_by_year.year"]["$lte"]=end_year
            for reg in self.colav_db["affiliations"].find(search_dict,{"names":1,"relations":1,"types":1}):
                for typ in reg["types"]: 
                    if typ["type"]!="group":
                        name=reg["names"][0]["name"]
                        for n in reg["names"]:
                            if n["lang"]=="es":
                                name=n["name"]
                                break
                            if n["lang"]=="en":
                                name=n["name"]
                        institutions_filter.append({"name":name,"id":reg["_id"]})

        if start_year:
            initial_year=start_year
        if end_year:
            final_year=end_year

        filters={
            "years":{
            "start_year":initial_year if initial_year!=9999 else "",
            "end_year":final_year if final_year!=0 else ""},
            "groups":groups_filter,
            "institutions":institutions_filter
        }

        return {"filters":filters}

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
        var_dict={"names":1,"products_count":1,
                "citations_count":1,"products_by_year":1,
                "affiliations":1,"authors":1,"counts_by_year":1
                }
        total=self.colav_db["subjects"].count_documents(search_dict)
        cursor=self.colav_db["subjects"].find(search_dict,var_dict)
        
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="products" and direction=="ascending":
            cursor.sort([("products_count",ASCENDING)])
        if sort=="products" and direction=="descending":
            cursor.sort([("products_count",DESCENDING)])

        skip = (max_results*(page-1))

        cursor=cursor.skip(skip).limit(max_results)

        data=[]
        index=max_results*(page-1)
        for subject in cursor:
            index+=1
            name=subject["names"][0]["name"]
            for n in subject["names"]:
                if n["lang"]=="es":
                    name=n["name"]
                    break
                if n["lang"]=="en":
                    name=n["name"]
            entry={
                "index":index,
                "name":name,
                "products_count":subject["products_count"],
                "citations_count":subject["citations_count"],
                "id":subject["_id"],
                "institutions":[], 
                "authors":[], 
                "groups":[], 
                "plot":[] #citations and products per year
            }
            if "affiliations" in subject.keys():
                for aff in subject["affiliations"]:
                    name=aff["names"][0]["name"]
                    for n in aff["names"]:
                        if n["lang"]=="es":
                            name=n["name"]
                            break
                        if n["lang"]=="en":
                            name=n["name"]
                    if "types" in aff.keys():
                        for typ in aff["types"]:
                            if typ["type"]=="group":
                                entry["groups"].append({"name":name,"id":aff["id"]})
                            else:
                                entry["institutions"].append({"name":name,"id":aff["id"]})
                    if len(entry["groups"])>=5 and len(entry["institutions"])>=5:
                        break
            entry["groups"]=entry["groups"][:5]
            entry["institutions"]=entry["institutions"][:5]
                        
            if "authors" in subject.keys():
                entry["authors"]=[{"name":au["name"],"id":au["id"]} for au in subject["authors"]][:5]
            
            entry["plot"]=[{"year":sub["year"],"products":sub["products_count"],"citations":sub["citations_count"]} for sub in subject["counts_by_year"] if sub["year"]<start_year or sub["year"]>end_year]
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])
            
            data.append(entry)

        return {"data":data,"page":page,"count":max_results,"total":total}


    def get_groups(self,page=1,max_results=10,groups="",institutions="",start_year=None,end_year=None,sort="citations",direction="descending"):
        filters={}
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

        if start_year:
            try:
                start_year=int(start_year)
            except:
                print("Could not convert start year to int")
                return None
        if end_year:
            try:
                end_year=int(end_year)
            except:
                print("Could not convert end year to int")
                return None

        search_dict={"types.type":"group"}

        ins_list=[]
        grp_list=[]
        if groups:
            grp_list.extend(groups.split())
        if institutions:
            ins_list.extend(institutions.split())
        if len(ins_list)>0:
            def_ins_list=[]
            for iid in ins_list:
                def_ins_list.append(ObjectId(iid))
            search_dict["relations.id"]={"$in":def_ins_list}
        if len(grp_list)>0:
            def_grp_list=[]
            for iid in grp_list:
                def_grp_list.append(ObjectId(iid))
            search_dict["_id"]={"$in":def_grp_list}
        var_dict={
            "names":1,"relations":1,
            "products_count":1,"citations_count":1,
            "products_by_year":1,"subjects":1
        }
        total=self.colav_db["affiliations"].count_documents(search_dict)
        cursor=self.colav_db["affiliations"].find(search_dict,var_dict)
        
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="products" and direction=="ascending":
            cursor.sort([("products_count",ASCENDING)])
        if sort=="products" and direction=="descending":
            cursor.sort([("products_count",DESCENDING)])

        skip = (max_results*(page-1))

        cursor=cursor.skip(skip).limit(max_results)

        data=[]
        index=max_results*(page-1)
        for reg in cursor:
            index+=1
            name=reg["names"][0]["name"]
            for n in reg["names"]:
                if n["lang"]=="es":
                    name=n["name"]
                    break
                if n["lang"]=="en":
                    name=n["name"]
            entry={
                "index":index,
                "id":reg["_id"],
                "name":name,
                "products_count":reg["products_count"],
                "citations_count":reg["citations_count"],
                "affiliations":{
                    "institution":{
                        "name":reg["relations"][0]["name"],
                        "id":reg["relations"][0]["id"]
                    }
                },
                "plot":[],
                "subjects":[]
            }

            for inst in reg["relations"]:
                if str(inst["id"]) in ins_list:
                    entry["affiliations"]["institution"]={
                        "name":inst["name"],
                        "id":inst["id"]
                    }

            for subs in reg["subjects"]:
                if subs["source"]=="openalex":
                    entry["subjects"]=subs["subjects"]
                    break
            if entry["subjects"]:
                entry["subjects"]=entry["subjects"][:10] if len(entry["subjects"])>=10 else entry["subjects"]

            year_index={}

            i=0
            for prod in reg["products_by_year"]:
                if start_year:
                    if prod["year"]<start_year:
                        continue
                if end_year:
                    if prod["year"]>end_year:
                        continue
                entry["plot"].append({
                    "year":prod["year"],
                    "products":prod["value"],
                    "citations":0
                })
                year_index[prod["year"]]=i
                i+=1

            if "citations_by_year" in reg.keys():
                for cit in reg["citations_by_year"]:
                    if start_year:
                        if cit["year"]<start_year:
                            continue
                    if end_year:
                        if cit["year"]>end_year:
                            continue
                    if cit["year"] in year_index.keys():
                        i=year_index[cit["year"]]
                        entry["plot"][i]["citations"]=cit["value"]
                    else:
                        entry["plot"].append({
                            "year":cit["year"],
                            "products":0,
                            "citations":cit["value"]
                        })
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])
                
            data.append(entry)

        return {"data":data,"page":page,"count":max_results,"total":total}


    def get_authors(self):
        data={
            "sex":[
                {"type":"Femenino","value":self.colav_db["person"].count_documents({"sex":"f"})},
                {"type":"Masculino","value":self.colav_db["person"].count_documents({"sex":"m"})}
            ],#pie
            "age":[],#pie
            "scholarity":[],#bars
            "rank":[]#pie
        }

        adolescent_search={
            "birthdate":{"$lte":int((dt.now()-relativedelta(years=12)).timestamp())},
            "birthdate":{"$gte":int((dt.now()-relativedelta(years=18)).timestamp())}
            }
        young_search={
            "birthdate":{"$lte":int((dt.now()-relativedelta(years=19)).timestamp())},
            "birthdate":{"$gte":int((dt.now()-relativedelta(years=26)).timestamp())}
            }
        adult_search={
            "birthdate":{"$lte":int((dt.now()-relativedelta(years=27)).timestamp())},
            "birthdate":{"$gte":int((dt.now()-relativedelta(years=59)).timestamp())}
            }
        old_search={
            "birthdate":{"$lte":int((dt.now()-relativedelta(years=60)).timestamp())},
            }
        data["age"]=[
            {"type":"Adolescencia","value":self.colav_db["person"].count_documents(adolescent_search)},
            {"type":"Juventud","value":self.colav_db["person"].count_documents(young_search)},
            {"type":"Adultez","value":self.colav_db["person"].count_documents(adult_search)},
            {"type":"Persona mayor","value":self.colav_db["person"].count_documents(old_search)}
        ]

        pregrado=0
        esp=0
        esp_medica=0
        maestria=0
        doctorado=0
        posdoctorado=0

        junior=0
        asociado=0
        senior=0
        emerito=0

        for author in self.colav_db["person"].find():
            max_time=0
            max_degree=""
            for deg in author["degrees"]:
                if deg["date"]>max_time:
                    max_time=deg["date"]
                    max_degree=deg["degree"]

            if max_degree=='Pregrado/Universitario':
                pregrado+=1
            elif max_degree=='Especialización':
                esp+=1
            elif max_degree=='Especialidad Médica':
                esp_medica+=1
            elif max_degree=='Maestría/Magister':
                maestria+=1
            elif max_degree=='Doctorado':
                doctorado+=1
            elif max_degree=='Postdoctorado' or max_degree=='Postdoctorado/Estancia postdoctoral':
                posdoctorado+=1
            max_time=0
            max_rank=""
            for rank in author["ranking"]:
                if rank["date"]>max_time:
                    max_time=rank["date"]
                    max_rank=rank["rank"]
            if max_rank=='Investigador Junior':
                junior+=1
            elif max_rank=='Investigador Asociado':
                asociado+=1
            elif max_rank=='Investigador Sénior':
                senior+=1
            elif max_rank=='Investigador Emérito':
                emerito+=1

        data["scholarity"]=[
            {"type":"Pregrado","value":pregrado},
            {"type":"Especialización","value":esp},
            {"type":"Especialidad médica","value":esp_medica},
            {"type":"Maestría","value":maestria},
            {"type":"Doctorado","value":doctorado},
            {"type":"Postdoctorado","value":posdoctorado}
        ]

        data["rank"]=[
            {"type":"Junior","value":junior},
            {"type":"Asociado","value":asociado},
            {"type":"Sénior","value":senior},
            {"type":"Emérito","value":emerito}
        ]

        return {"data":data}


    def get_institutions(self,page=1,max_results=10,groups="",institutions="",start_year=None,end_year=None,sort="citations",direction="descending"):

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
        
        if start_year:
            try:
                start_year=int(start_year)
            except:
                print("Could not convert start year to int")
                return None
        if end_year:
            try:
                end_year=int(end_year)
            except:
                print("Could not convert end year to int")
                return None

        search_dict={"types.type":{"$ne":"group"}}
        ins_list=[]
        grp_list=[]
        if groups:
            grp_list.extend(groups.split())
        if institutions:
            ins_list.extend(institutions.split())
        if len(ins_list)>0:
            def_list=[]
            for iid in ins_list:
                def_ins_list.append(ObjectId(iid))
            search_dict["_id"]={"$in":def_ins_list}
        if len(grp_list)>0:
            def_grp_list=[]
            for iid in grp_list:
                def_grp_list.append(ObjectId(iid))
            search_dict["relations.id"]={"$in":def_grp_list}
        var_dict={"names":1,"products_count":1,"citations_count":1,"products_by_year":1,"subjects":1}
        total=self.colav_db["affiliations"].count_documents(search_dict)
        cursor=self.colav_db["affiliations"].find(search_dict,)
        
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="products" and direction=="ascending":
            cursor.sort([("products_count",ASCENDING)])
        if sort=="products" and direction=="descending":
            cursor.sort([("products_count",DESCENDING)])
        
        skip = (max_results*(page-1))

        cursor=cursor.skip(skip).limit(max_results)

        data=[]
        index=max_results*(page-1)
        for reg in cursor:
            index+=1
            name=reg["names"][0]["name"]
            for n in reg["names"]:
                if n["lang"]=="es":
                    name=n["name"]
                    break
                if n["lang"]=="en":
                    name=n["name"]
            entry={
                "index":index,
                "id":reg["_id"],
                "name":name,
                "products_count":reg["products_count"],
                "citations_count":reg["citations_count"],
                "plot":[],
                "subjects":[]
            }
            for subs in reg["subjects"]:
                if subs["source"]=="openalex":
                    entry["subjects"]=subs["subjects"]
                    break
            if entry["subjects"]:
                entry["subjects"]=entry["subjects"][:10] if len(entry["subjects"])>=10 else entry["subjects"]
            year_index={}
            i=0
            for prod in reg["products_by_year"]:
                if start_year:
                    if prod["year"]<start_year:
                        continue
                if end_year:
                    if prod["year"]>end_year:
                        continue
                entry["plot"].append({
                    "year":prod["year"],
                    "products":prod["value"],
                    "citations":0
                })
                year_index[prod["year"]]=i
                i+=1
            if "citations_by_year" in reg.keys():
                for cit in reg["citations_by_year"]:
                    if start_year:
                        if cit["year"]<start_year:
                            continue
                    if end_year:
                        if cit["year"]>end_year:
                            continue
                    if cit["year"] in year_index.keys():
                        i=year_index[cit["year"]]
                        entry["plot"][i]["citations"]=cit["value"]
                    else:
                        entry["plot"].append({
                            "year":cit["year"],
                            "products":0,
                            "citations":cit["value"]
                        })
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])
            
            data.append(entry)

        return {"data":data,"page":page,"count":max_results,"total":total}
            

    @endpoint('/app/compendium', methods=['GET'])
    def app_compendium(self):
        """
        """
        data = self.request.args.get('data')
        
        if data=="info":
            institutions=self.request.args.get('institutions')
            groups=self.request.args.get('groups')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            info=self.get_info(institutions=institutions,groups=groups,start_year=start_year,end_year=end_year)
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
        elif data=="groups":
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            sort=self.request.args.get('sort')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            inst=self.request.args.get('institutions')
            grps=self.request.args.get('groups')
            groups=self.get_groups(
                page=page,max_results=max_results,sort=sort,
                start_year=start_year,end_year=end_year,
                groups=grps,institutions=inst)
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
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            inst=self.request.args.get('institutions')
            grps=self.request.args.get('groups')
            institutions=self.get_institutions(
                page=page,max_results=max_results,sort=sort,
                start_year=start_year,end_year=end_year,
                groups=grps,institutions=inst)
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
        elif data=="authors":
            authors=self.get_authors()
            if authors:    
                response = self.app.response_class(
                response=self.json.dumps(authors),
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