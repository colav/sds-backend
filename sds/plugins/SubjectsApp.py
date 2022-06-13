from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from pickle import load
from math import log
from datetime import date


class SubjectsApp(sdsPluginBase):
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

        if idx:
            result=self.colav_db["subjects"].find_one({"_id":ObjectId(idx)})
        else:
            return None
        tree={
            "title":result["name"],
            "level":result["level"],
            "key":"0",
            "children":[]
        }
        count=0
        if result["related_concepts"]:
            for sub in result["related_concepts"]:
                if sub["level"]-1!=result["level"]:
                    continue
                entry={
                    "title":sub["display_name"],
                    "id":sub["id"] if "id" in sub.keys() else "",
                    "level":sub["level"],
                    "key":"0-"+str(count)
                }
                tree["children"].append(entry)
                count+=1
        parent={}
        if result["ancestors"]:
            for ancestor in result["ancestors"]:
                if ancestor["level"]!=result["level"]-1:
                    continue
                else:
                    parent={
                        "title":ancestor["display_name"],
                        "id":ancestor["id"] if "id" in ancestor.keys() else "",
                        "level":ancestor["level"]
                    }
                    break

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
            search_dict={"policies.id":ObjectId(idx)}
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
            search_dict={"policies.id":ObjectId(idx)}
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

        return {"data":{"tree":tree,"parent":parent,"citations":result["cited_by_count"],"products":result["works_count"]},"filters":filters}

    def get_venn(self,venn_query):
        venn_source={
            "scholar":0,"lens":0,"wos":0,"scopus":0,
            "scholar_lens":0,"scholar_wos":0,"scholar_scopus":0,"lens_wos":0,"lens_scopus":0,"wos_scopus":0,
            "scholar_lens_wos":0,"scholar_wos_scopus":0,"scholar_lens_scopus":0,"lens_wos_scopus":0,
            "scholar_lens_wos_scopus":0
        }
        venn_query["$and"]=[{"source_checked.source":"scholar"},
                {"source_checked.source":{"$ne":"lens"}},
                {"source_checked.source":{"$ne":"wos"}},
                {"source_checked.source":{"$ne":"scopus"}}]
        venn_source["scholar"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":{"$ne":"scholar"}},
                {"source_checked.source":"lens"},
                {"source_checked.source":{"$ne":"wos"}},
                {"source_checked.source":{"$ne":"scopus"}}]
        venn_source["lens"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":{"$ne":"scholar"}},
                {"source_checked.source":{"$ne":"lens"}},
                {"source_checked.source":"wos"},
                {"source_checked.source":{"$ne":"scopus"}}]
        venn_source["wos"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":{"$ne":"scholar"}},
                {"source_checked.source":{"$ne":"lens"}},
                {"source_checked.source":{"$ne":"wos"}},
                {"source_checked.source":"scopus"}]
        venn_source["scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":"scholar"},
                {"source_checked.source":"lens"},
                {"source_checked.source":{"$ne":"wos"}},
                {"source_checked.source":{"$ne":"scopus"}}]
        venn_source["scholar_lens"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":"scholar"},
                {"source_checked.source":{"$ne":"lens"}},
                {"source_checked.source":"wos"},
                {"source_checked.source":{"$ne":"scopus"}}]
        venn_source["scholar_wos"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":"scholar"},
                {"source_checked.source":{"$ne":"lens"}},
                {"source_checked.source":{"$ne":"wos"}},
                {"source_checked.source":"scopus"}]
        venn_source["scholar_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":{"$ne":"scholar"}},
                {"source_checked.source":"lens"},
                {"source_checked.source":"wos"},
                {"source_checked.source":{"$ne":"scopus"}}]
        venn_source["lens_wos"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":{"$ne":"scholar"}},
                {"source_checked.source":"lens"},
                {"source_checked.source":{"$ne":"wos"}},
                {"source_checked.source":"scopus"}]
        venn_source["lens_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":{"$ne":"scholar"}},
                {"source_checked.source":{"$ne":"lens"}},
                {"source_checked.source":"wos"},
                {"source_checked.source":"scopus"}]
        venn_source["wos_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":"scholar"},
                {"source_checked.source":"lens"},
                {"source_checked.source":"wos"},
                {"source_checked.source":{"$ne":"scopus"}}]
        venn_source["scholar_lens_wos"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":"scholar"},
                {"source_checked.source":{"$ne":"lens"}},
                {"source_checked.source":"wos"},
                {"source_checked.source":"scopus"}]
        venn_source["scholar_wos_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":"scholar"},
                {"source_checked.source":"lens"},
                {"source_checked.source":{"$ne":"wos"}},
                {"source_checked.source":"scopus"}]
        venn_source["scholar_lens_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":{"$ne":"scholar"}},
                {"source_checked.source":"lens"},
                {"source_checked.source":"wos"},
                {"source_checked.source":"scopus"}]
        venn_source["lens_wos_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"source_checked.source":"scholar"},
                {"source_checked.source":"lens"},
                {"source_checked.source":"wos"},
                {"source_checked.source":"scopus"}]
        venn_source["scholar_lens_wos_scopus"]=self.colav_db['documents'].count_documents(venn_query)

        return venn_source

    def get_production(self,idx=None,max_results=100,page=1,start_year=None,end_year=None,sort=None,direction=None):
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
        
        if idx:
            if start_year and not end_year:
                cursor=self.colav_db['documents'].find({"year_published":{"$gte":start_year},"subjects.id":ObjectId(idx)})
                venn_query={"year_published":{"$gte":start_year},"subjects.id":ObjectId(idx)}
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$gte":start_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$gte":start_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$gte":start_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"bronze","value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$gte":start_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"closed","value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$gte":start_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"hybrid","value":val})
            elif end_year and not start_year:
                cursor=self.colav_db['documents'].find({"year_published":{"$lte":end_year},"subjects.id":ObjectId(idx)})
                venn_query={"year_published":{"$lte":end_year},"subjects.id":ObjectId(idx)}
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"gold"  ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"bronze","value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"closed","value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"hybrid","value":val})
                
            elif start_year and end_year:
                cursor=self.colav_db['documents'].find({"year_published":{"$gte":start_year,"$lte":end_year},"subjects.id":ObjectId(idx)})
                venn_query={"year_published":{"$gte":start_year,"$lte":end_year},"subjects.id":ObjectId(idx)}
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$gte":start_year,"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$gte":start_year,"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"gold"  ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$gte":start_year,"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"bronze","value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$gte":start_year,"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"closed","value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$gte":start_year,"$lte":end_year},"subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"hybrid","value":val})
                
            else:
                cursor=self.colav_db['documents'].find({"subjects.id":ObjectId(idx)})
                venn_query={"subjects.id":ObjectId(idx)}
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"gold"  ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"bronze","value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"closed","value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","subjects.id":ObjectId(idx)})
                if val!=0:
                    open_access.append({"type":"hybrid","value":val})
                
        else:
            cursor=self.colav_db['documents'].find() 
            venn_query={}
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

        for paper in cursor:
            entry={
                "id":paper["_id"],
                "title":paper["titles"][0]["title"],
                "citations_count":paper["citations_count"],
                "year_published":paper["year_published"],
                "open_access_status":paper["open_access_status"]
            }

            source=self.colav_db["sources"].find_one({"_id":paper["source"]["id"]})
            if source:
                entry["source"]={"name":source["title"],"id":str(source["_id"])}
            authors=[]
            for author in paper["authors"]:
                au_entry={"full_name":author["full_name"]
                            ,"id":author["id"],
                            "affiliation":{"institution": {},"group":{}}}
                
                for aff in author["affiliations"]:
                    if "type" in aff.keys():
                        if aff["type"]=="group":
                            au_entry["affiliation"]["group"]={"name":aff["name"],"id":aff["id"]}
                    else:
                        au_entry["affiliation"]["institution"]={"name":aff["name"],"id":aff["id"]}
                    
    
                authors.append(au_entry)
            entry["authors"]=authors
            papers.append(entry)

        tipos = self.colav_db['documents'].distinct("publication_type.type",{"subjects.id":ObjectId(idx)})

        return {
            "open_access":open_access,
            "venn_source":self.get_venn(venn_query),
            "types":tipos
            }
    
    def get_production_by_type(self,idx=None,max_results=100,page=1,start_year=None,end_year=None,sort="descending",direction=None,tipo=None):
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

        if idx:

            if start_year and not end_year:
                cursor=self.colav_db['documents'].find({"year_published":{"$gte":start_year},"subjects.id":ObjectId(idx),
                    "publication_type.type":tipo})

            elif end_year and not start_year:
                cursor=self.colav_db['documents'].find({"year_published":{"$lte":end_year},"subjects.id":ObjectId(idx),
                    "publication_type.type":tipo})

            elif start_year and end_year:
                cursor=self.colav_db['documents'].find({"year_published":{"$gte":start_year,"$lte":end_year},
                    "subjects.id":ObjectId(idx), "publication_type.type":tipo})

            else:
                cursor=self.colav_db['documents'].find({"subjects.id":ObjectId(idx),"publication_type.type":tipo})
        
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

        entry=[]

        for doc in cursor:
            authors=[]
            for author in doc["authors"]:
                au_entry={}
                author_db=self.colav_db["authors"].find_one({"_id":author["id"]})
                if author_db:
                    au_entry={"full_name":author_db["full_name"],"id":author_db["_id"]}
                affiliation={}
                for aff in author["affiliations"]:
                    aff_entry={}
                    aff_db=self.colav_db["affiliations"].find_one({"_id":aff["id"]})
                    if aff_db:
                        aff_entry={"name":aff_db["name"],"id":aff_db["_id"]}
                    
                    affiliation["institution"]=aff_entry
                au_entry["affiliation"]=affiliation
                authors.append(au_entry)

            try:
                if doc["publication_type"]["source"]=="lens":

                    source=self.colav_db["sources"].find_one({"_id":doc["source"]["id"]})

                    entry.append({
                    "id":doc["_id"],
                    "title":doc["titles"][0]["title"],
                    "citations_count":doc["citations_count"],
                    "year_published":doc["year_published"],
                    "open_access_status":doc["open_access_status"],
                    "source":{"name":source["title"],"id":str(source["_id"])},
                    "authors":authors,
                    "subjects":[{"name":reg["name"],"id":reg["id"]}for reg in doc["subjects"] if str(reg["id"])!=idx] if "subjects" in doc.keys() else  []
                    })

            except:
                continue
        return {"total":total,"page":page,"count":len(entry),"data":entry}

    def get_institutions(self,idx=None,institutions="",page=1,max_results=100,sort="citations",direction="descending"):
        search_dict={"types.type":{"$ne":"group"},"subjects.id":ObjectId(idx)}
        if institutions:
            institutions_list=[ObjectId(inst) for inst in institutions.split()]
            search_dict["_id"]={"$in":institutions_list}
        total_results = self.colav_db["affiliations"].count_documents(search_dict)

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

        cursor=self.colav_db["affiliations"].find(search_dict)

        #SORTING here is wrong, it should sort from citations and production in the subject
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="products" and direction=="ascending":
            cursor.sort([("products_count",ASCENDING)])
        if sort=="products" and direction=="descending":
            cursor.sort([("products_count",DESCENDING)])

        cursor=cursor.skip(skip).limit(max_results)

        data = []
        for reg in cursor:
            entry={
                "name":reg["name"],
                "id":reg["_id"],
                "plot":[],
                "citations":0,
                "products":0,
                "subjects":[sub for sub in reg["subjects"] if str(sub["id"])!=idx][:5]
            }
            if "subjects" in reg.keys():
                for sub in reg["subjects"]:
                    if str(sub["id"])==idx:
                        entry["citations"]=sub["citations"]
                        entry["products"]=sub["products"]
                        break
            for year_sub in reg["subjects_by_year"]:
                for sub in year_sub["subjects"]:
                    if str(sub["id"])==idx:
                        entry["plot"].append({
                            "year":year_sub["year"],
                            "products":sub["products"],
                            "citations":sub["citations"]
                        })
            
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])
            data.append(entry)

        return {"total":total_results,"page":page,"count":len(data),"data":data}
    
    def get_groups(self,idx=None,page=1,max_results=100,institutions="",sort="citations",direction="descending"):
        search_dict={"types":"group","subjects.id":ObjectId(idx)}
        if institutions:
            institutions_list=[ObjectId(inst) for inst in institutions.split()]
            search_dict["relations.id"]={"$in":institutions_list}
        total_results = self.colav_db["affiliations"].count_documents(search_dict)

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

        cursor=self.colav_db["affiliations"].find(search_dict)

        #SORTING here is wrong, it should sort from citations and production in the subject
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="products" and direction=="ascending":
            cursor.sort([("products_count",ASCENDING)])
        if sort=="products" and direction=="descending":
            cursor.sort([("products_count",DESCENDING)])

        cursor=cursor.skip(skip).limit(max_results)

        data = []
        for reg in cursor:
            entry={
                "name":reg["name"],
                "id":reg["_id"],
                "institution":{},
                "plot":[],
                "citations":0,
                "products":0,
                "subjects":[sub for sub in reg["subjects"] if str(sub["id"])!=idx][:5]
            }
            if "relations" in reg.keys():
                if len(reg["relations"])>0:
                    entry["institution"]={
                        "name":reg["relations"][0]["name"],
                        "id":reg["relations"][0]["id"]
                    }
            if "subjects" in reg.keys():
                for sub in reg["subjects"]:
                    if str(sub["id"])==idx:
                        entry["citations"]=sub["citations"]
                        entry["products"]=sub["products"]
                        break
            for year_sub in reg["subjects_by_year"]:
                for sub in year_sub["subjects"]:
                    if str(sub["id"])==idx:
                        entry["plot"].append({
                            "year":year_sub["year"],
                            "products":sub["products"],
                            "citations":sub["citations"]
                        })
            
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])
            data.append(entry)

        return {"total":total_results,"page":page,"count":len(data),"data":data}

    def get_authors(self,idx=None,page=1,max_results=100,start_year=None,end_year=None,groups=[],institutions=[],sort="citations",direction="descending"):
        query={}
        filter_list=[]

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
        if idx:
            query={"subjects.id":ObjectId(idx)}
                
            if institutions:
                filter_list=[]
                for institution in institutions.split(" "):
                    filter_list.append({"affiliations.id":ObjectId(institution)})
            if groups:
                for group in groups.split(" "):
                    filter_list.append({"affiliations.id":ObjectId(group)})
            if start_year:
                query["subjects_by_year.year"]={"$gte":start_year}
            if end_year:
                if "subjects_by_year" in query.keys():
                    query["subjects_by_year.year"]["$lte"]=end_year
                else:
                    query["subjects_by_year.year"]={"$lte":end_year}

            if len(filter_list)>0:
                query["$or"]=filter_list

            cursor=self.colav_db["authors"].find(query)
            cursor_citations=self.colav_db["authors"].find(query)
            cursor_products=self.colav_db["authors"].find(query)

            total_results = self.colav_db["authors"].count_documents(query)

            skip = (max_results*(page-1))
        
            entry = {
                "authors":[],#id,name,affiliations,subjects with id
                "authors_citations_count":[],
                "authors_production_count":[]
            } 

            if sort=="citations" and direction=="ascending":
                cursor.sort([("citations_count",ASCENDING)])
            if sort=="citations" and direction=="descending":
                cursor.sort([("citations_count",DESCENDING)])
            if sort=="products" and direction=="ascending":
                cursor.sort([("products_count",ASCENDING)])
            if sort=="products" and direction=="descending":
                cursor.sort([("products_count",DESCENDING)])

            cursor=cursor.skip(skip).limit(max_results)

            for reg in cursor:
                group_name = ""
                group_id = ""
                institution={}
                if "affiliations" in reg.keys():
                    for aff in reg["affiliations"]:
                        if "type" in aff.keys():
                            if aff["type"]=="group":
                                group_name=aff["name"]
                                group_id=str(aff["id"])
                        else:
                            institution={
                            "name":aff["name"], 
                            "id":aff["id"]
                            }
    

                entry["authors"].append({
                    "id":reg["_id"],
                    "name":reg["full_name"],
                    "products_count":reg["products_count"],
                    "citations_count":reg["citations_count"],
                    "affiliation":{"institution":institution,
                                "group":{"name":group_name, "id":group_id}}
                })
            
            
            cursor_citations.sort([("citations_count",DESCENDING)])
            cursor_citations=cursor_citations.limit(max_results)
            for reg in cursor_citations:
                entry["authors_citations_count"].append({"name":reg["full_name"],"citations":reg["citations_count"]})

            cursor_products.sort([("products_count",DESCENDING)])
            cursor_products=cursor_products.limit(max_results)
            for reg in cursor_products:
                entry["authors_production_count"].append({"name":reg["full_name"],"production":reg["products_count"]})
            
        return {"total":total_results,"page":page,"count":len(entry),"data":entry}



    @endpoint('/app/subjects', methods=['GET'])
    def app_subjects(self):
       
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
        elif data=="production":
            idx = self.request.args.get('id')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            sort=self.request.args.get('sort')
            tipo = self.request.args.get('type')

            if tipo == None: 
                production=self.get_production(idx,max_results,page,start_year,end_year,sort,"descending")
            else:
                production=self.get_production_by_type(idx,max_results,page,start_year,end_year,sort,"descending",tipo)

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
            institutions=self.request.args.get('institutions')
            groups=self.request.args.get('groups')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            authors=self.get_authors(idx,page,max_results,start_year,end_year,groups,institutions,sort,"descending")
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
        elif data=="groups":
            idx = self.request.args.get('id')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            institutions=self.request.args.get('institutions')
            res=self.get_groups(idx,page=page,max_results=max_results,institutions=institutions)
            if res:
                response = self.app.response_class(
                response=self.json.dumps(res),
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
            idx = self.request.args.get('id')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            institutions=self.request.args.get('institutions')
            res=self.get_institutions(idx,page=page,max_results=max_results,institutions=institutions)
            if res:
                response = self.app.response_class(
                response=self.json.dumps(res),
                status=200,
                mimetype='application/json'
                )
            else:
                response = self.app.response_class(
                response=self.json.dumps({"status":"Request returned empty"}),
                status=204,
                mimetype='application/json'
                )
        elif data=="csv":
            idx = self.request.args.get('id')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            sort=self.request.args.get('sort')
            production_csv=self.get_csv(idx,start_year,end_year,sort,"descending")
            if production_csv:
                response = self.app.response_class(
                response=production_csv,
                status=200,
                mimetype='text/csv',
                headers={"Content-disposition":
                 "attachment; filename=authors.csv"}
                )
            else:
                response = self.app.response_class(
                response=self.json.dumps({"status":"Request returned empty"}),
                status=204,
                mimetype='application/json'
                )
        elif data=="json":
            idx = self.request.args.get('id')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            sort=self.request.args.get('sort')
            production_json=self.get_json(idx,start_year,end_year,sort,"descending")
            if production_json:
                response = self.app.response_class(
                response=production_json,
                status=200,
                mimetype='text/plain',
                headers={"Content-disposition":
                 "attachment; filename=authors.json"}
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