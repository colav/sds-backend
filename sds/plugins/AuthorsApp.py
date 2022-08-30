from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from pickle import load
from math import log
from datetime import date
import json


class AuthorsApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)

    def get_info(self,idx,institutions=[],groups=[],start_year=None,end_year=None):
        initial_year=9999
        final_year = 0

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


        author = self.colav_db['person'].find_one({"_id":ObjectId(idx)})
        if author:
            entry={
                "id":author["_id"],
                "name":author["full_name"],
                "citations":author["citations_count"],
                "affiliation":{"institution":{"name":"","id":""},"group":{"name":"","id":""}},
                "external_urls":[],
                "policies":{},
                "logo":"",
                "sds":author["sds"] if "sds" in author.keys() else False
            }
            index_list=[]
            if "policies" in author.keys():
                for policy in author["policies"]:
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

            if "affiliations" in author.keys():
                if len(author["affiliations"]):
                    for aff in author["affiliations"]:
                        for typ in aff["types"]:
                            if typ["type"]=="group":
                                entry["affiliation"]["group"]={
                                    "name":aff["name"],
                                    "id":aff["id"]
                                }
                            else:   
                                entry["affiliation"]["institution"]["name"]=aff["name"]
                                entry["affiliation"]["institution"]["id"]  =aff["id"]
        
            if entry["affiliation"]["institution"]["id"] != "":
                    inst_db=self.colav_db["affiliations"].find_one({"_id":ObjectId(entry["affiliation"]["institution"]["id"])})
                    if inst_db:
                        for ext in inst_db["external_urls"]:
                            if ext["source"]=="logo":
                                entry["logo"]=ext["url"]

            sources=[]
            for ext in author["external_ids"]:

                if ext["source"]=="researchid" and not "researcherid" in sources:
                    sources.append("researcherid")
                    entry["external_urls"].append({
                        "source":"researcherid",
                        "url":"https://publons.com/researcher/"+ext["id"]})
                if ext["source"]=="scopus" and not "scopus" in sources:
                    sources.append("scopus")
                    entry["external_urls"].append({
                        "source":"scopus",
                        "url":"https://www.scopus.com/authid/detail.uri?authorId="+ext["id"]})
                if ext["source"]=="scholar" and not "scholar" in sources:
                    sources.append("scholar")
                    entry["external_urls"].append({
                        "source":"scholar",
                        "url":"https://scholar.google.com.co/citations?user="+ext["id"]})
                if ext["source"]=="orcid" and not "orcid" in sources:
                    sources.append("orcid")
                    entry["external_urls"].append({
                        "source":"orcid",
                        "url":"https://orcid.org/"+ext["id"]})
                if ext["source"]=="linkedin" and not "linkedin" in sources:
                    sources.append("linkedin")
                    entry["external_urls"].append({
                        "source":"linkedin",
                        "url":"https://www.linkedin.com/in/"+ext["id"]})
                if ext["source"]=="minciencias" and not "minciencias" in sources:
                    sources.append("minciencias")
                    entry["external_urls"].append({
                        "source":"minciencias",
                        "url":"https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh="+ext["id"]})

            filters={"years":{}}
            for reg in self.colav_db["works"].find({"authors.id":ObjectId(idx),"year_published":{"$exists":1}}).sort([("year_published",ASCENDING)]).limit(1):
                filters["years"]["start_year"]=reg["year_published"]
            for reg in self.colav_db["works"].find({"authors.id":ObjectId(idx),"year_published":{"$exists":1}}).sort([("year_published",DESCENDING)]).limit(1):
                filters["years"]["end_year"]=reg["year_published"]

            return {"data": entry, "filters": filters }
        else:
            return None

    def get_subjects(self,idx=None,start_year=None,end_year=None,limit=10):
        initial_year=0
        final_year=0

        if not limit:
            limit=10
        else:
            try:
                limit=int(limit)
            except:
                print("Could not convert limit to int")
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
        if idx:
            result=self.colav_db["person"].find_one({"_id":ObjectId(idx)})
        else:
            return None

        data=[]
        names=[]
        if "subjects_by_year" in result.keys():
            for val in result["subjects_by_year"]:
                year=val["year"]
                if start_year:
                    if start_year>year:
                        continue
                if end_year:
                    if end_year<year:
                        continue
                for sub in val["subjects"]:
                    if sub["name"] in names:
                        data[names.index(sub["name"])]["products"]+=sub["products"]
                    else:
                        data.append(sub)
                        names.append(sub["name"])
        
        sorted_data=sorted(data,key=lambda x:x["products"],reverse=True)
                
        return {"data":sorted_data[:limit],"total":len(data)}

    def get_coauthors(self,idx=None,start_year=None,end_year=None):
        geojson=json.load(open("sds/etc/world_map.json","r"))
        initial_year=0
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
        if idx:
            pipeline=[
                {"$match":{"authors.id":ObjectId(idx)}}
            ]


            if start_year and not end_year:
                pipeline=[
                    {"$match":{"year_published":{"$gte":start_year},"authors.id":ObjectId(idx)}}
                ]
            elif end_year and not start_year:
                pipeline=[
                    {"$match":{"year_published":{"$lte":end_year},"authors.id":ObjectId(idx)}}
                ]
            elif start_year and end_year:
                pipeline=[
                    {"$match":{"year_published":{"$gte":start_year,"$lte":end_year},"authors.id":ObjectId(idx)}}
                ]

        pipeline.extend([
            {"$unwind":"$authors"},
            {"$unwind":"$authors.affiliations"},
            {"$group":{"_id":"$authors.id","count":{"$sum":1}}},
            {"$sort":{"count":-1}},
            {"$lookup":{"from":"person","localField":"_id","foreignField":"_id","as":"author"}},
            {"$project":{"count":1,"author.full_name":1,"author.affiliations":1}},
            {"$unwind":"$author"}
        ])

        entry={
            "coauthors":[],
            "geo":[],
            "coauthors_network":{}
        }

        for reg in self.colav_db["works"].aggregate(pipeline):
            affiliation_id = ""
            affiliation_name = ""
            group_id=""
            group_name=""
            if str(reg["_id"])==str(idx):
                continue
            if "affiliations" in reg["author"].keys():
                for aff in reg["author"]["affiliations"]:
                    if "types" in aff.keys():
                        for typ in aff["types"]:
                            if typ["type"]=="group":
                                group_name=aff["name"]
                                group_id=aff["id"]
                            else:
                                inst_name=aff["name"]
                                inst_id=aff["id"]

            entry["coauthors"].append(
                {"id":reg["_id"],"name":reg["author"]["full_name"],
                "affiliation":{
                    "institution":{"id":affiliation_id,"name":affiliation_name} ,
                    "group":{"id":group_id,"name":group_name} ,
                    },
                "count":reg["count"]} 
            )
            entry["coauthors"]=sorted(entry["coauthors"],key=lambda x:x["count"],reverse=True)

        countries={}
        country_list=[]
        pipeline=[pipeline[0]]
        pipeline.extend([
            {"$unwind":"$authors"},
            {"$group":{"_id":"$authors.affiliations.id","count":{"$sum":1}}},
            {"$unwind":"$_id"},
            {"$lookup":{"from":"affiliations","localField":"_id","foreignField":"_id","as":"affiliation"}},
            {"$project":{"count":1,"affiliation.addresses.country_code":1,"affiliation.addresses.country":1}},
            {"$unwind":"$affiliation"},
            {"$unwind":"$affiliation.addresses"}
        ])
        for reg in self.colav_db["works"].aggregate(pipeline,allowDiskUse=True):
            if str(reg["_id"])==idx:
                continue
            if not "country_code" in reg["affiliation"]["addresses"].keys():
                continue
            if reg["affiliation"]["addresses"]["country_code"] and reg["affiliation"]["addresses"]["country"]:
                alpha2=reg["affiliation"]["addresses"]["country_code"]
                country_name=reg["affiliation"]["addresses"]["country"]
                if alpha2 in countries.keys():
                    countries[alpha2]["count"]+=reg["count"]
                else:
                    countries[alpha2]={
                        "count":reg["count"],
                        "name":country_name
                    }
        for key,val in countries.items():
            countries[key]["log_count"]=log(val["count"])
        for i,feat in enumerate(geojson["features"]):
            if feat["properties"]["country_code"] in countries.keys():
               alpha2=feat["properties"]["country_code"]
               geojson["features"][i]["properties"]["count"]=countries[alpha2]["count"]
               geojson["features"][i]["properties"]["log_count"]=countries[alpha2]["log_count"]

        entry["geo"]=geojson

        db_reg=self.colav_db["person"].find_one({"_id":ObjectId(idx)})
        if db_reg:
            if "coauthors_network" in db_reg.keys():
                entry["coauthors_network"]=db_reg["coauthors_network"]

        return {"data":entry}

    def get_venn(self,venn_query):
        venn_source={
            "scholar":0,"lens":0,"wos":0,"scopus":0,
            "scholar_lens":0,"scholar_wos":0,"scholar_scopus":0,"lens_wos":0,"lens_scopus":0,"wos_scopus":0,
            "scholar_lens_wos":0,"scholar_wos_scopus":0,"scholar_lens_scopus":0,"lens_wos_scopus":0,
            "scholar_lens_wos_scopus":0
        }
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["lens"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["wos"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scopus"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_lens"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_wos"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scholar_scopus"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["lens_wos"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["lens_scopus"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["wos_scopus"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_lens_wos"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["scholar_wos_scopus"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scholar_lens_scopus"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["lens_wos_scopus"]=self.colav_db["works"].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["scholar_lens_wos_scopus"]=self.colav_db["works"].count_documents(venn_query)

        return venn_source

    def get_production(self,idx=None,max_results=100,institutions=None,groups=None,page=1,start_year=None,end_year=None,sort=None,direction="descending"):
        papers=[]
        total=0
        open_access=[]
        
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
                

        search_dict={}
        venn_query={}
        oa_query={}

        if idx:
            search_dict={"authors.id":ObjectId(idx)}
            venn_query={"authors.id":ObjectId(idx)}
            oa_query={"authors.id":ObjectId(idx)}
                
        if start_year or end_year:
            search_dict["year_published"]={}
            venn_query["year_published"]={}
            oa_query["year_published"]={}
        if start_year:
            search_dict["year_published"]["$gte"]=start_year
            venn_query["year_published"]["$gte"]=start_year
            oa_query["year_published"]["$gte"]=start_year
        if end_year:
            search_dict["year_published"]["$lte"]=end_year
            venn_query["year_published"]["$lte"]=end_year
            oa_query["year_published"]["$lte"]=end_year
        
        cursor=self.colav_db["works"].find(search_dict)
        total=cursor.count()

        for oa in ["green","gold","bronze","closed","hybrid"]:
            oa_query["bibliographic_info.open_access_status"]=oa
            val=self.colav_db["works"].count_documents(oa_query)
            if val!=0:
                open_access.append({"type":oa ,"value":val})
        
        types = self.colav_db['works'].distinct("types",{"authors.id":ObjectId(idx)})
        tipos=[]
        for tipo in types:
            if tipo["source"]=="minciencias":
                if not tipo["type"] in tipos:
                    tipos.append(tipo["type"])

        return {
            "open_access":open_access,
            "venn_source":self.get_venn(venn_query),
            "types":tipos
            }

    def get_production_by_type(self,idx=None,max_results=100,page=1,
            groups=None,institutions=None,start_year=None,end_year=None,sort="year",direction="descending",tipo=None):
        total = 0

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

        search_dict={"types.type":tipo}

        if idx:
            search_dict["authors.id"]=ObjectId(idx)
                
        if start_year or end_year:
            search_dict["year_published"]={}
        if start_year:
            search_dict["year_published"]["$gte"]=start_year
        if end_year:
            search_dict["year_published"]["$lte"]=end_year
        
        cursor=self.colav_db["works"].find(search_dict)
        total=cursor.count()

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
        
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="year" and direction=="ascending":
            cursor.sort([("year_published",ASCENDING)])
        if sort=="year" and direction=="descending":
            cursor.sort([("year_published",DESCENDING)])

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)

        if cursor:
            paper_list=[]
            for paper in cursor:
                entry={
                    "id":paper["_id"],
                    "title":paper["titles"][0]["title"],
                    "authors":[],
                    "source":"",
                    "open_access_status":paper["bibliographic_info"]["open_access_status"] if "open_access_status" in paper["bibliographic_info"] else "",
                    "year_published":paper["year_published"],
                    "citations_count":paper["citations_count"] if "citations_count" in paper.keys() else 0,
                    "subjects":[]
                }

                for subs in paper["subjects"]:
                    if subs["source"]=="openalex":
                        for sub in subs["subjects"]:
                            name=sub["names"][0]["name"]
                            for n in sub["names"]:
                                if n["lang"]=="es":
                                    name=n["name"]
                                    break
                                if n["lang"]=="en":
                                    name=n["name"]
                            entry["subjects"].append({"name":name,"id":sub["id"]})
                        break

                if "source" in paper.keys():
                    source=self.colav_db["sources"].find_one({"_id":paper["source"]["id"]})
                    if source:
                        entry["source"]={"name":source["title"],"id":source["_id"]}
                
                authors=[]
                for author in paper["authors"]:
                    author_entry={
                        "id":author["id"],
                        "full_name":author["full_name"],
                        "affiliation": {
                            "institution":{"name":"","id":""}
                        }
                    }
                    if "affiliations" in author.keys():
                        if len(author["affiliations"])>0:
                            for aff in author["affiliations"]:
                                if "types" in aff.keys():
                                    for typ in aff["types"]:
                                        if typ["type"]=="group":
                                            if groups:
                                                if aff["id"] in aff_list:
                                                    author_entry["affiliation"]["group"]={
                                                        "name":aff["name"],
                                                        "id":aff["id"]
                                                    }
                                            else:
                                                author_entry["affiliation"]["group"]={
                                                    "name":aff["name"],
                                                    "id":aff["id"]
                                                }
                                        else:
                                            if institutions:
                                                if aff["id"] in aff_list:
                                                    author_entry["affiliation"]["institution"]["name"]=aff["name"]
                                                    author_entry["affiliation"]["institution"]["id"]  =aff["id"]
                                            else:    
                                                author_entry["affiliation"]["institution"]["name"]=aff["name"]
                                                author_entry["affiliation"]["institution"]["id"]  =aff["id"]
                    authors.append(author_entry)

                entry["authors"]=authors

                paper_list.append(entry)

            return {"data":paper_list,
                    "count":len(paper_list),
                    "page":page,
                    "total_results":total
                }
        else:
            return None
    

    @endpoint('/app/authors', methods=['GET'])
    def app_authors(self):
       
        data = self.request.args.get('data')

        if data=="info":
            idx = self.request.args.get('id')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            info = self.get_info(idx,start_year=start_year,end_year=end_year)
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
        elif data=="production":
            idx = self.request.args.get('id')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            sort=self.request.args.get('sort')
            tipo = self.request.args.get('type')

            if tipo == None: 
                production=self.get_production(idx=idx,
                    max_results=max_results,
                    page=page,
                    start_year=start_year,
                    end_year=end_year,
                    sort=sort)
            else:
                production=self.get_production_by_type(idx=idx,
                    max_results=max_results,
                    page=page,
                    start_year=start_year,
                    end_year=end_year,
                    sort=sort,tipo=tipo)

            if production:
                response = self.app.response_class(
                response=self.json.dumps(production),
                status=200,
                mimetype='application/json'
                )
            else:
                response = self.app.response_class(
                response=self.json.dumps({"status":"Request returned empty"}),
                status=204,
                mimetype='application/json'
                )
        elif data=="coauthors":
            idx = self.request.args.get('id')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            coauthors=self.get_coauthors(idx,start_year,end_year)
            if coauthors:
                response = self.app.response_class(
                response=self.json.dumps(coauthors),
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
            idx = self.request.args.get('id')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            limit=self.request.args.get('limit')
            subjects=self.get_subjects(idx,start_year,end_year,limit)
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
