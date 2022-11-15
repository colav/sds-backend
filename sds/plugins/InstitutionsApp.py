from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from pickle import load
from datetime import date
from math import log,exp
from flask import redirect
import json
from numpy import quantile


class InstitutionsApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)

    def get_info(self,idx,start_year=None,end_year=None):
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

        institution = self.colav_db['affiliations'].find_one({"types.type":{"$ne":"group"},"_id":ObjectId(idx)})
        if institution:
            name=""
            for n in institution["names"]:
                if n["lang"]=="es":
                    name=n["name"]
                    break
                elif n["lang"]=="en":
                    name=n["name"]
            logo=""
            for ext in institution["external_urls"]:
                if ext["source"]=="logo":
                    logo=ext["url"]

            entry={"id":institution["_id"],
                "name":name,
                "citations":institution["citations_count"],
                "external_urls":[ext for ext in institution["external_urls"] if ext["source"]!="logo"],
                "logo":logo,
                "policies":{}
            }
            index_list=[]
            if "policies" in institution.keys():
                for policy in institution["policies"]:
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

        
            filters={"years":{}}
            for reg in self.colav_db["works"].find({"authors.affiliations.id":ObjectId(idx),"year_published":{"$exists":1}}).sort([("year_published",ASCENDING)]).limit(1):
                filters["years"]["start_year"]=reg["year_published"]
            for reg in self.colav_db["works"].find({"authors.affiliations.id":ObjectId(idx),"year_published":{"$exists":1}}).sort([("year_published",DESCENDING)]).limit(1):
                filters["years"]["end_year"]=reg["year_published"]
            
            return {"data": entry, "filters": filters }
        else:
            return None
 
    def get_coauthors(self,idx=None,start_year=None,end_year=None,page=1,max_results=100):
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
                {"$match":{"authors.affiliations.id":ObjectId(idx)}}
            ]
 
            if start_year and not end_year:
                pipeline=[
                    {"$match":{"year_published":{"$gte":start_year},"authors.affiliations.id":ObjectId(idx)}}
                ]
            elif end_year and not start_year:
                pipeline=[
                    {"$match":{"year_published":{"$lte":end_year},"authors.affiliations.id":ObjectId(idx)}}
                ]
            elif start_year and end_year:
                pipeline=[
                    {"$match":{"year_published":{"$gte":start_year,"$lte":end_year},"authors.affiliations.id":ObjectId(idx)}}
                ]
                
        pipeline.extend([
            {"$unwind":"$authors"},
            {"$group":{"_id":"$authors.id","count":{"$sum":1}}},
            {"$sort":{"count":-1}},
            {"$lookup":{"from":"person","localField":"_id","foreignField":"_id","as":"author"}},
            {"$project":{"count":1,"author.full_name":1,"author.affiliations":1}},
            {"$unwind":"$author"}
        ])

        entry={
            "coauthors":[],
            "geo":[]
        }

        affiliations_ids=[]
        for reg in self.colav_db["works"].aggregate(pipeline):
            inst_id = ""
            inst_name = ""
            group_id=""
            group_name=""
            if str(reg["_id"])==str(idx):
                continue
            if "affiliations" in reg["author"].keys():
                for aff in reg["author"]["affiliations"]:
                    if "types" in aff.keys():
                        for typ in aff["types"]:
                            if typ["type"]!="group":    
                                inst_name=aff["name"]
                                inst_id=aff["id"]

            if inst_id:
                if inst_id in affiliations_ids:
                    entry["coauthors"][affiliations_ids.index(inst_id)]["count"]+=reg["count"]
                else:
                    entry["coauthors"].append(
                        {
                            "name":inst_name,
                            "id":inst_id,
                            "count":reg["count"]
                        } 
                    )
                    affiliations_ids.append(inst_id)
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
        db_reg=self.colav_db["affiliations"].find_one({"_id":ObjectId(idx)})
        if db_reg:
            if "coauthors_network" in db_reg.keys():
                entry["coauthors_network"]=db_reg["coauthors_network"]
                        
        return {"data":entry}

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
            result=self.colav_db["affiliations"].find_one({"_id":ObjectId(idx)})
        else:
            return None

        if not "subjects_by_year" in result.keys():
            return {"data":{},"total":0}
        if not result["subjects_by_year"]:
            return {"data":{},"total":0}

        data=[]
        names=[]
        for reg in result["subjects_by_year"]:
            year=reg["year"]
            if start_year:
                if start_year>year:
                    continue
            if end_year:
                if end_year<year:
                    continue
            for sub in reg["subjects"]:
                if sub["name"] in names:
                    data[names.index(sub["name"])]["products"]+=sub["products"]
                else:
                    data.append(sub)
                    names.append(sub["name"])
        
        sorted_data=sorted(data,key=lambda x:x["products"],reverse=True)
                
        return {"data":sorted_data[:limit],"total":len(data)}

    
    def get_authors(self,idx=None,page=1,max_results=100,sort="citations",direction="descending"):
        if idx:

            total_results = self.colav_db["person"].count_documents({"affiliations.id":ObjectId(idx)})

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

            
            skip = (max_results*(page-1))

            cursor=self.colav_db["person"].find({"affiliations.id":ObjectId(idx)})

            if sort=="citations" and direction=="ascending":
                cursor.sort([("citations_count",ASCENDING)])
            if sort=="citations" and direction=="descending":
                cursor.sort([("citations_count",DESCENDING)])
            if sort=="products" and direction=="ascending":
                cursor.sort([("products_count",ASCENDING)])
            if sort=="products" and direction=="descending":
                cursor.sort([("products_count",DESCENDING)])

            cursor=cursor.skip(skip).limit(max_results)

            entry = []
            for reg in cursor:
                group_name=""
                group_id=""
                inst_name=""
                inst_id=""
                if len(reg["affiliations"])>0:
                    for aff in reg["affiliations"]:
                        if "types" in aff.keys():
                            for typ in aff["types"]:
                                if typ["type"]=="group":
                                    group_name=aff["name"]
                                    group_id=aff["id"]
                                else:
                                    if str(aff["id"])==idx:   
                                        inst_name=aff["name"]
                                        inst_id=aff["id"]
        
                entry.append({
                    "id":reg["_id"],
                    "name":reg["full_name"],
                    "products_count":reg["products_count"],
                    "citations_count":reg["citations_count"],
                    "affiliation":{"institution":{"name":inst_name, 
                                        "id":inst_id},
                                   "group":{"name":group_name, "id":group_id}}
                })
            
        return {"total":total_results,"page":page,"count":len(entry),"data":entry}

    def get_groups(self,idx=None,page=1,max_results=100,sort="citations",direction="descending"):
        if idx:

            total_results = self.colav_db["affiliations"].count_documents({"types.type":"group","relations.id":ObjectId(idx)})

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

            
            skip = (max_results*(page-1))

            cursor=self.colav_db["affiliations"].find({"types.type":"group","relations.id":ObjectId(idx)})

            if sort=="citations" and direction=="ascending":
                cursor.sort([("citations_count",ASCENDING)])
            if sort=="citations" and direction=="descending":
                cursor.sort([("citations_count",DESCENDING)])
            if sort=="products" and direction=="ascending":
                cursor.sort([("products_count",ASCENDING)])
            if sort=="products" and direction=="descending":
                cursor.sort([("products_count",DESCENDING)])

            cursor=cursor.skip(skip).limit(max_results)

            entry = []
            for reg in cursor:
                name=""
                for n in reg["names"]:
                    if n["lang"]=="es":
                        name=n["name"]
                        break
                    elif n["lang"]=="en":
                        name=n["name"]
                entry.append({
                    "id":reg["_id"],
                    "name":name,
                    "products_count":reg["products_count"],
                    "citations_count":reg["citations_count"]
                })
            
        return {"total":total_results,"page":page,"count":len(entry),"data":entry}


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
        venn_source["scholar"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["lens"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["wos"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scopus"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_lens"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_wos"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scholar_scopus"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["lens_wos"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["lens_scopus"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["wos_scopus"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_lens_wos"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["scholar_wos_scopus"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scholar_lens_scopus"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["lens_wos_scopus"]=self.colav_db['works'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["scholar_lens_wos_scopus"]=self.colav_db['works'].count_documents(venn_query)

        return venn_source

    def get_production(self,idx=None,start_year=None,end_year=None,sort=None):
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
            search_dict={"authors.affiliations.id":ObjectId(idx)}
            venn_query={"authors.affiliations.id":ObjectId(idx)}
            oa_query={"authors.affiliations.id":ObjectId(idx)}
                
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
        
        types = self.colav_db['works'].distinct("types",{"authors.affiliations.id":ObjectId(idx)})
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


    def get_production_by_type(self,idx=None,max_results=100,page=1,start_year=None,end_year=None,sort="year",direction="descending",tipo=None):
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
            search_dict["authors.affiliations.id"]=ObjectId(idx)
                
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
                        entry["source"]={"name":paper["source"]["title"],"id":paper["source"]["id"]}
                
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
                                            author_entry["affiliation"]["group"]={
                                                "name":aff["name"],
                                                "id":aff["id"]
                                            }
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
 
    @endpoint('/app/institutions', methods=['GET'])
    def app_institutions(self):
        """
        """
        data = self.request.args.get('data')
        tipo = self.request.args.get('type')

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
        elif data=="production":
            idx = self.request.args.get('id')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            sort=self.request.args.get('sort')

            if tipo == None: 
                production=self.get_production(idx=idx,
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
        elif data=="authors":
            idx = self.request.args.get('id')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            sort=self.request.args.get('sort')
            authors=self.get_authors(idx=idx,page=page,max_results=max_results,sort=sort)
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
        elif data=="coauthors":
            idx = self.request.args.get('id')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')

            coauthors=self.get_coauthors(idx,start_year,end_year,page,max_results)
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
        elif data=="groups":
            idx = self.request.args.get('id')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            sort=self.request.args.get('sort')
            groups=self.get_groups(idx=idx,page=page,max_results=max_results,sort=sort)
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

