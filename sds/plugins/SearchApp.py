from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING

class SearchApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)

    def search_subjects(self,keywords='',max_results=100,page=1,sort="products",direction="descending"):
        if keywords:
            cursor=self.colav_db["subjects"].find({"$text":{"$search":keywords}})
        else:
            cursor=self.colav_db["subjects"].find()

        if sort=="citations":
            cursor.sort([("citations_count",DESCENDING)])
        else:
            cursor.sort([("products_count",DESCENDING)])

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

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)

        if cursor:
            subjects_list=[]
            for subject in cursor:
                name=""
                for n in subject["names"]:
                    if n["lang"]=="es":
                        name=n["name"]
                        break
                    elif n["lang"]=="en":
                        name=n["name"]
                entry={
                    "name":name,
                    "id":subject["_id"],
                    "products_count":subject["products_count"],
                    "citations_count":subject["citations_count"]
                }
                subjects_list.append(entry)

            return {
                    "total_results":total,
                    "count":len(subjects_list),
                    "page":page,
                    "filters":{},
                    "data":subjects_list
                }

        else:
            return None

    def search_subjects_pbi(self):
        
        cursor=self.colav_db["subjects"].find({},{"names":1,"products_count":1,"citations_count":1})

        if cursor:
            subjects_list=[]
            for subject in cursor:
                name=""
                for n in subject["names"]:
                    if n["lang"]=="es":
                        name=n["name"]
                        break
                    elif n["lang"]=="en":
                        name=n["name"]
                entry={
                    "name":name,
                    "id":subject["_id"],
                    "products_count":subject["products_count"],
                    "citations_count":subject["citations_count"]
                }
                subjects_list.append(entry) 

            return subjects_list
        else:
            return None

    def search_author(self,keywords="",institutions="",groups="",country="",max_results=100,page=1,sort="citations"):
        search_dict={"external_ids":{"$ne":[]}}
        aff_list=[]
        if institutions:
            aff_list.extend([ObjectId(inst) for inst in institutions.split()])
        if groups:
            aff_list.extend([ObjectId(grp) for grp in groups.split()])
        if len(aff_list)!=0:
            search_dict["affiliations.id"]={"$in":aff_list}

        if keywords:
            search_dict["$text"]={"$search":keywords}
            filter_cursor=self.colav_db['person'].find({"$text":{"$search":keywords},"external_ids":{"$ne":[]}},{ "score": { "$meta": "textScore" } }).sort([("score", { "$meta": "textScore" } )])
        else:
            filter_cursor=self.colav_db['person'].find({"external_ids":{"$ne":[]}})

        cursor=self.colav_db['person'].find(search_dict,{"score":{"$meta":"textScore"}})

        institution_filters = []
        group_filters=[]
        institution_ids=[]
        groups_ids=[]

        for author in filter_cursor:
            if "affiliations" in author.keys():
                if len(author["affiliations"])>0:
                    for aff in author["affiliations"]:
                        if "types" in aff.keys():
                            for typ in aff["types"]: 
                                if typ["type"]=="group":
                                    groups_ids.append(aff["id"])
                                    group_filters.append({
                                        "id":str(aff["id"]),
                                        "name":aff["name"]
                                    })
                                else:
                                    institution_ids.append(str(aff["id"]))
                                    entry = {"id":str(aff["id"]),"name":aff["name"]}
                                    institution_filters.append(entry)


        if sort=="citations":
            cursor.sort([("citations_count",DESCENDING)])
        elif sort=="products":
            cursor.sort([("products_count",DESCENDING)])
        else:
            cursor.sort([("score", { "$meta": "textScore" } )])


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

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)

        if cursor:
            author_list=[]
            keywords=[]
            group_name = ""
            group_id = ""
            for author in cursor:
                entry={
                    "id":author["_id"],
                    "name":author["full_name"],
                    "products_count":author["products_count"],
                    "citations_count":author["citations_count"],
                    "affiliation":{"institution":{"name":"","id":""}}
                }
                if "affiliations" in author.keys():
                    if len(author["affiliations"])>0:
                        for aff in author["affiliations"]:
                            if "types" in aff.keys():
                                for typ in aff["types"]:
                                    if typ["type"]=="group":
                                        if groups:
                                            if aff["id"] in aff_list:
                                                entry["affiliation"]["group"]={
                                                    "name":aff["name"],
                                                    "id":aff["id"]
                                                }
                                        else:
                                            entry["affiliation"]["group"]={
                                                "name":aff["name"],
                                                "id":aff["id"]
                                            }
                                    else:
                                        if institutions:
                                            if aff["id"] in aff_list:
                                                entry["affiliation"]["institution"]["name"]=aff["name"]
                                                entry["affiliation"]["institution"]["id"]  =aff["id"]
                                        else:    
                                            entry["affiliation"]["institution"]["name"]=aff["name"]
                                            entry["affiliation"]["institution"]["id"]  =aff["id"]

                author_list.append(entry)
    
            return {
                    "total_results":total,
                    "count":len(author_list),
                    "page":page,
                    "filters":{"institutions":institution_filters,"groups":group_filters},
                    "data":author_list
                }
        else:
            return None

    def search_groups(self,keywords="",institutions=None,max_results=100,page=1,sort="citations"):
        search_dict={"types.type":"group","external_ids":{"$ne":[]}}
        aff_list=[]
        if institutions:
            aff_list.extend([ObjectId(inst) for inst in institutions.split()])
        if len(aff_list)!=0:
            search_dict["relations.id"]={"$in":aff_list}

        if keywords:
            search_dict["$text"]={"$search":keywords}

        cursor=self.colav_db['affiliations'].find(search_dict,{"score":{"$meta":"textScore"}})
        relations = cursor.distinct("relations")
            
        tmp = []
        
        for r in relations:
            if "types" in r.keys():
                for typ in r["types"]:
                    if typ["type"]=="group":
                        continue
            entry = {"id":str(r["id"]),"name":r["name"]}
            tmp.append(entry)

        #eliminamos duplicados en la lista de instituciones:
        institution_filters = []
        for e in tmp:
            if e not in institution_filters:
                institution_filters.append(e)


        if sort=="citations":
            cursor.sort([("citations_count",DESCENDING)])
        elif sort=="products":
                cursor.sort([("products_count",DESCENDING)])
        else:
            cursor.sort([("score", { "$meta": "textScore" } )])

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

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)
        
        entity_list=[]
        if cursor:
            for entity in cursor:
                entry={
                    "name":entity["names"][0]["name"],
                    "id":str(entity["_id"]),
                    "products_count":entity["products_count"],
                    "citations_count":entity["citations_count"],
                    "affiliation":{"institution":{"name":"","id":""}}

                }
                
                for relation in entity["relations"]:
                    if "types" in relation.keys():
                        for typ in relation["types"]:
                            if typ["type"]!="group":
                                if institutions:
                                    if relation["id"] in aff_list:
                                        entry["affiliation"]["institution"]["name"]=relation["name"]
                                        entry["affiliation"]["institution"]["id"]  =relation["id"]
                                else:    
                                    entry["affiliation"]["institution"]["name"]=relation["name"]
                                    entry["affiliation"]["institution"]["id"]  =relation["id"]

                entity_list.append(entry)
                        
            return {
                    "total_results":total,
                    "count":len(entity_list),
                    "page":page,
                    "filters":{"institutions":institution_filters},
                    "data":entity_list
                }
        else:
            return None

    def search_institution(self,keywords="",max_results=100,page=1,sort='citations'):
        search_dict={"types.type":{"$ne":"group"},"external_ids":{"$ne":[]}}

        if keywords:
            search_dict["$text"]={"$search":keywords}

        cursor=self.colav_db['affiliations'].find(search_dict,{"score":{"$meta":"textScore"}})
        
        if sort=="citations":
            cursor.sort([("citations_count",DESCENDING)])
        elif sort=="products":
            cursor.sort([("products_count",DESCENDING)])
        else:
            cursor.sort([("score", { "$meta": "textScore" } )])

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

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)
        if cursor:
            institution_list=[]
            for institution in cursor:
                name=institution["names"][0]["name"]
                for n in institution["names"]:
                    if n["lang"]=="es":
                        name=n["name"]
                        break
                    if n["lang"]=="en":
                        name=n["name"]

                logo=""
                for ext in institution["external_urls"]:
                    if ext["source"]=="logo":
                        logo=ext["url"]
                entry={
                    "id":institution["_id"],
                    "name":name,
                    "products_count":institution["products_count"],
                    "citations_count":institution["citations_count"],
                    "logo":logo
                }
                institution_list.append(entry)
    
            return {
                    "total_results":total,
                    "count":len(institution_list),
                    "page":page,
                    "data":institution_list

                }
        else:
            return None

    def search_info(self,keywords=""):

        initial_year=0
        final_year = 0

        if keywords: 
            result=self.colav_db['works'].find({"$text":{"$search":keywords}},{"year_published":1}).sort([("year_published",ASCENDING)]).limit(1)
            if result:
                result=list(result)
                if len(result)>0:
                    initial_year=result[0]["year_published"]
            result=self.colav_db['works'].find({"$text":{"$search":keywords}},{"year_published":1}).sort([("year_published",DESCENDING)]).limit(1)
            if result:
                result=list(result)
                if len(result)>0:
                    final_year=result[0]["year_published"]
                

            filters={
                "start_year":initial_year if initial_year!=0 else "",
                "end_year":final_year if final_year!=0 else ""
            }

            return {"filters": filters}
        else:
            return None

    def search_documents(self,keywords="",start_year=None,end_year=None,institutions=None,groups=None):
        open_access=[]
        entry={}

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

        if keywords: 
            cursor=self.colav_db['works'].find({"$text":{"$search":keywords}},{"year_published":1})
            result = cursor.sort([("year_published",ASCENDING)]).limit(1)
            if result:
                result=list(result)
                
                if len(result)>0:
                    initial_year=result[0]["year_published"]
            result=self.colav_db['works'].find({"$text":{"$search":keywords}},{"year_published":1}).sort([("year_published",DESCENDING)]).limit(1)
            if result:
                result=list(result)
                
                if len(result)>0:
                    final_year=result[0]["year_published"]
        else:
            cursor=self.colav_db['works'].find({},{"year_published":1})
            result = cursor.sort([("year_published",ASCENDING)]).limit(1)
            if result:
                result=list(result)
                
                if len(result)>0:
                    initial_year=result[0]["year_published"]
            result=self.colav_db['works'].find({},{"year_published":1}).sort([("year_published",DESCENDING)]).limit(1)
            if result:
                result=list(result)
                
                if len(result)>0:
                    final_year=result[0]["year_published"]

        years={
                "start_year":initial_year if initial_year!=0 else "",
                "end_year":final_year if final_year!=0 else ""
            }

        institution_filters = []
        group_filters=[]

        cursor = self.colav_db["works"].find()
        for reg in cursor:
            for author in reg["authors"]:
                for aff in author["affiliations"]:
                    if "types" in aff.keys():
                        for typ in aff["types"]:
                            if typ["type"]=="group":
                                entry={
                                    "name":aff["name"],
                                    "id":aff["id"]
                                }
                                if not entry in group_filters:
                                    group_filters.append(entry)
                            else:    
                                entry={
                                    "name":aff["name"],
                                    "id":aff["id"]
                                    }
                                if not entry in institution_filters:
                                    institution_filters.append(entry)

        venn_query={}
        oa_query={}
        types_query={}
        if keywords:
            venn_query={"$text":{"$search":keywords}}
            oa_query={"$text":{"$search":keywords}}
            types_query={"$text":{"$search":keywords}}

        if start_year or end_year:
            venn_query["year_published"]={}
            oa_query["year_published"]={}
            types_query["year_published"]={}
        if start_year:
            venn_query["year_published"]["$gte"]=start_year
            oa_query["year_published"]["$gte"]=start_year
            types_query["year_published"]["$gte"]=start_year
        if end_year:
            venn_query["year_published"]["$lte"]=end_year
            oa_query["year_published"]["$lte"]=end_year
            types_query["year_published"]["$lte"]=end_year
        in_list=[]
        if groups:
            in_list.extend(groups.split())
        if institutions:
            in_list.extend(institutions.split())
        if len(in_list)>0:
            def_list=[]
            for iid in in_list:
                def_list.append(ObjectId(iid))
            venn_query["authors.affiliations.id"]={"$in":def_list}
            oa_query["authors.affiliations.id"]={"$in":def_list}
            types_query["authors.affiliations.id"]={"$in":def_list}

        for oa in ["green","gold","bronze","closed","hybrid"]:
            oa_query["bibliographic_info.open_access_status"]=oa
            val=self.colav_db["works"].count_documents(oa_query)
            if val!=0:
                open_access.append({"type":oa ,"value":val})

        types = self.colav_db['works'].distinct("types",types_query)
        tipos=[]
        for tipo in types:
            if tipo["source"]=="minciencias":
                if not tipo["type"] in tipos:
                    tipos.append(tipo["type"])

        return {
            "open_access":open_access,
            "venn_source":self.get_venn(venn_query),
            "types":tipos,
            "filters":{"years":years,"institutions":institution_filters,"groups":group_filters}
        }
                    
    def search_documents_by_type(self,keywords="",max_results=100,page=1,start_year=None,end_year=None,
        sort="citations",direction="descending",tipo="article",institutions=None,
        groups=None):

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
        if start_year or end_year:
            search_dict["year_published"]={}
        if start_year:
            search_dict["year_published"]["$gte"]=start_year
        if end_year:
            search_dict["year_published"]["$lte"]=end_year
        
        aff_list=[]
        if institutions:
            aff_list.extend([ObjectId(inst) for inst in institutions.split()])
        if groups:
            aff_list.extend([ObjectId(grp) for grp in groups.split()])
        if len(aff_list)!=0:
            search_dict["authors.affiliations.id"]={"$in":aff_list}
        if keywords:
            search_dict["$text"]={"$search":keywords}

        cursor=self.colav_db['works'].find(search_dict)

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
        elif sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        elif sort=="year" and direction=="ascending":
            cursor.sort([("year_published",ASCENDING)])
        elif sort=="year" and direction=="descending":
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
                    "subjects":[{"name":reg["name"],"id":reg["id"]}for reg in paper["subjects"]] if "subjects" in paper.keys() else  []
                }

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

    def search_documents_pbi(self):
        open_access=[]

        val=self.colav_db['works'].count_documents({"bibliographic_info.open_access_status":"green" })
        if val!=0:
            open_access.append({"type":"green" ,"value":val})
        val=self.colav_db['works'].count_documents({"bibliographic_info.open_access_status":"gold" })
        if val!=0:
            open_access.append({"type":"gold" ,"value":val})
        val=self.colav_db['works'].count_documents({"bibliographic_info.open_access_status":"bronze" })
        if val!=0:
            open_access.append({"type":"bronze" ,"value":val})
        val=self.colav_db['works'].count_documents({"bibliographic_info.open_access_status":"closed" })
        if val!=0:
            open_access.append({"type":"closed" ,"value":val})
        val=self.colav_db['works'].count_documents({"bibliographic_info.open_access_status":"hybrid" })
        if val!=0:
            open_access.append({"type":"hybrid" ,"value":val})

        cursor=self.colav_db['works'].find()
        
        products={}
        if cursor:
            for paper in cursor:
                if "types" in paper.keys():
                    for typ in paper["types"]:
                        if typ["type"]:
                            if typ["type"] in products.keys():
                                if paper["year_published"] in products[typ["type"]].keys():
                                    products[typ["type"]][paper["year_published"]]["products"]+=1
                                    products[typ["type"]][paper["year_published"]]["citations"]+=paper["citations_count"] if "citations_count" in paper.keys() else 0
                                else:
                                    products[typ["type"]][paper["year_published"]]={
                                        "products":1,
                                        "citations":paper["citations_count"] if "citations_count" in paper.keys() else 0
                                    }
                            else:
                                if paper["year_published"]:
                                    products[typ["type"]]={
                                            paper["year_published"]:{
                                                "products":1,
                                                "citations":paper["citations_count"] if "citations_count" in paper.keys() else 0
                                            }
                                        }
            table=[]
            for typ,years in products.items():
                for year,counts in years.items():
                    entry={
                        "year":year,
                        "products":counts["products"],
                        "type":typ,
                        "citations":counts["citations"]
                    }
                    table.append(entry)

            return {
                "open_access":open_access,
                "products":table
                }
        else:
            return None


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

    @endpoint('/app/search', methods=['GET'])
    def app_search(self):
        """
        """
        data = self.request.args.get('data')
        tipo = self.request.args.get('type')

        if data=="info":
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            result = self.search_info(keywords=keywords)

        elif data=="groups":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            sort = self.request.args.get('sort') if "sort" in self.request.args else "citations"
            institutions = self.request.args.get('institutions') if "institutions" in self.request.args else ""
            result=self.search_groups(keywords=keywords,institutions=institutions,max_results=max_results,page=page,sort=sort)
        elif data=="authors":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            sort = self.request.args.get('sort') if "sort" in self.request.args else "citations"
            groups = self.request.args.get('groups') if "groups" in self.request.args else None
            institutions = self.request.args.get('institutions') if "institutions" in self.request.args else None
            result=self.search_author(keywords=keywords,max_results=max_results,page=page,sort=sort,
                groups=groups,institutions=institutions)
        elif data=="institutions":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            sort = self.request.args.get('sort') if "sort" in self.request.args else "citations"
            result=self.search_institution(keywords=keywords,max_results=max_results,page=page,sort=sort)
        elif data=="literature":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            sort=self.request.args.get('sort')
            institutions=self.request.args.get('institutions')
            groups=self.request.args.get('groups')
            if tipo == None:
                result=self.search_documents(keywords=keywords,
                        start_year=start_year,end_year=end_year,
                        institutions=institutions,groups=groups)
            else:
                result=self.search_documents_by_type(keywords=keywords,max_results=max_results,
                    page=page,start_year=start_year,end_year=end_year,sort=sort,
                    direction="descending",tipo=tipo,institutions=institutions,
                    groups=groups)
        elif data=="subjects":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            sort=self.request.args.get('sort')
            result=self.search_subjects(keywords=keywords,max_results=max_results,
                page=page,sort=sort,direction="descending")
        elif data=="subjects_pbi":
            result=self.search_subjects_pbi()
        elif data=="literature_pbi":
            result=self.search_documents_pbi()

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