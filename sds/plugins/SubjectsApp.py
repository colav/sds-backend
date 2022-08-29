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
        name=result["names"][0]["name"]
        for n in result["names"]:
            if n["lang"]=="es":
                name=n["name"]
                break
            if n["lang"]=="en":
                name=n["name"]
        tree={
            "title":name,
            "level":result["level"],
            "key":"0",
            "children":[]
        }
        count=0
        parent={}
        if result["relations"]:
            for sub in result["relations"]:
                name=sub["names"][0]["name"]
                for n in sub["names"]:
                    if n["lang"]=="es":
                        name=n["name"]
                        break
                    if n["lang"]=="en":
                        name=n["name"]
                if sub["level"]<result["level"]:
                    if sub["level"]==result["level"]-1:
                        parent={
                            "title":name,
                            "id":sub["id"] if "id" in sub.keys() else "",
                            "level":sub["level"]
                        }
                else:

                    entry={
                        "title":name,
                        "id":sub["id"] if "id" in sub.keys() else "",
                        "level":sub["level"],
                        "key":"0-"+str(count)
                    }
                    tree["children"].append(entry)
                    count+=1

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
            search_dict={"subjects.subjects.id":ObjectId(idx)}
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
            search_dict={"subjects.subjects.id":ObjectId(idx)}
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

        return {"data":{"tree":tree,"parent":parent,"citations":result["citations_count"],"products":result["products_count"]},"filters":filters}

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
        venn_source["scholar"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["lens"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["wos"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_lens"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_wos"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scholar_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["lens_wos"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["lens_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["wos_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":{"$ne":"scopus"}}]
        venn_source["scholar_lens_wos"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":{"$ne":"lens"}},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["scholar_wos_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":{"$ne":"wos"}},
                {"updated.source":"scopus"}]
        venn_source["scholar_lens_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":{"$ne":"scholar"}},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["lens_wos_scopus"]=self.colav_db['documents'].count_documents(venn_query)
        venn_query["$and"]=[{"updated.source":"scholar"},
                {"updated.source":"lens"},
                {"updated.source":"wos"},
                {"updated.source":"scopus"}]
        venn_source["scholar_lens_wos_scopus"]=self.colav_db['documents'].count_documents(venn_query)

        return venn_source

    def get_production(self,idx=None,max_results=100,page=1,groups=None,institutions=None,start_year=None,end_year=None,sort=None,direction=None):
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
            search_dict={"subjects.subjects.id":ObjectId(idx)}
            venn_query={"subjects.subjects.id":ObjectId(idx)}
            oa_query={"subjects.subjects.id":ObjectId(idx)}
                
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
            venn_query["_id"]={"$in":def_list}
            oa_query["_id"]={"$in":def_list}
        
        cursor=self.colav_db["works"].find(search_dict)
        total=cursor.count()

        for oa in ["green","gold","bronze","closed","hybrid"]:
            oa_query["bibliographic_info.open_access_status"]=oa
            val=self.colav_db["works"].count_documents(oa_query)
            if val!=0:
                open_access.append({"type":oa ,"value":val})
        
        types = self.colav_db['works'].distinct("types",{"subjects.subjects.id":ObjectId(idx)})
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
    
    def get_production_by_type(self,idx=None,max_results=100,page=1,groups=None,institutions=None,start_year=None,end_year=None,sort="descending",direction=None,tipo=None):
        total = 0
        search_dict={}

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
            search_dict["subjects.subjects.id"]=ObjectId(idx)
                
        if start_year or end_year:
            search_dict["year_published"]={}
        if start_year:
            search_dict["year_published"]["$gte"]=start_year
        if end_year:
            search_dict["year_published"]["$lte"]=end_year

        in_list=[]
        if groups:
            in_list.extend(groups.split())
        if institutions:
            in_list.extend(institutions.split())
        if len(in_list)>0:
            def_list=[]
            for iid in in_list:
                def_list.append(ObjectId(iid))
            search_dict["authors.affiliations.id"]={"$in":def_list}
        
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

    def get_institutions(self,idx=None,start_year=None,end_year=None,page=1,max_results=100,sort="citations",direction="descending"):

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

        search_dict={"types.type":{"$ne":"group"},"subjects.subjects.id":ObjectId(idx)}
        var_dict={"names":1,"products_count":1,"citations_count":1,"products_by_year":1,"subjects":1}
        total=self.colav_db["affiliations"].count_documents(search_dict)

        cursor=self.colav_db["affiliations"].find(search_dict,var_dict)

        skip = (max_results*(page-1))

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
            name=reg["names"][0]["name"]
            for n in reg["names"]:
                if n["lang"]=="es":
                    name=n["name"]
                    break
                if n["lang"]=="en":
                    name=n["name"]
            entry={
                "name":name,
                "id":reg["_id"],
                "plot":[],
                "citations_count":reg["citations_count"] if "citations_count" in reg.keys() else 0,
                "products_count":reg["products_count"],
                "word_cloud":[]
            }

            for subs in reg["subjects"]:
                if subs["source"]=="openalex":
                    for s in subs["subjects"]:
                        name=s["name"]
                        entry["word_cloud"].append({
                            "id":s["id"],
                            "name":name,
                            "products":s["products"],
                            "citations":s["citations"]
                        })
            
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
                    "products":prod["value"]
                })
                year_index[prod["year"]]=i
                i+=1
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])

            data.append(entry)

        return {"total":total,"page":page,"count":len(data),"data":data}
    
    def get_groups(self,idx=None,page=1,max_results=100,start_year=None,end_year=None,institutions="",sort="citations",direction="descending"):
        search_dict={"types.type":"group","subjects.subjects.id":ObjectId(idx)}
        if institutions:
            institutions_list=[ObjectId(inst) for inst in institutions.split()]
            search_dict["relations.id"]={"$in":institutions_list}
        total_results = self.colav_db["affiliations"].count_documents(search_dict)

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
            name=reg["names"][0]["name"]
            for n in reg["names"]:
                if n["lang"]=="es":
                    name=n["name"]
                    break
                if n["lang"]=="en":
                    name=n["name"]
            entry={
                "name":name,
                "id":reg["_id"],
                "institution":{},
                "plot":[],
                "citations_count":reg["citations_count"] if "citations_count" in reg.keys() else 0,
                "products_count":reg["products_count"],
                "word_cloud":[]
            }
            if "relations" in reg.keys():
                for relation in reg["relations"]:
                    for typ in relation["types"]:
                        if typ["type"]!="group":
                            entry["institution"]={
                                "name":reg["relations"][0]["name"],
                                "id":reg["relations"][0]["id"]
                            }

            for subs in reg["subjects"]:
                if subs["source"]=="openalex":
                    for s in subs["subjects"]:
                        name=s["name"]
                        entry["word_cloud"].append({
                            "id":s["id"],
                            "name":name,
                            "products":s["products"],
                            "citations":s["citations"]
                        })
            
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
                    "products":prod["value"]
                })
                year_index[prod["year"]]=i
                i+=1
            
            entry["plot"]=sorted(entry["plot"],key=lambda x:x["year"])

            data.append(entry)

        return {"total":total_results,"page":page,"count":len(data),"data":data}

    def get_authors(self,idx=None,page=1,max_results=100,start_year=None,end_year=None,groups=[],institutions=[],sort="citations",direction="descending"):
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

        aff_list=[]
        if institutions:
            aff_list.extend([ObjectId(inst) for inst in institutions.split()])
        if groups:
            aff_list.extend([ObjectId(grp) for grp in groups.split()])

        if idx:
            sorting_var="citations_count"
            if sort=="production":
                sorting_var="products_count"
            pipeline=[
                {"$match":{"subjects.subjects.id":ObjectId(idx)}}
            ]

            pipeline.extend([{"$unwind":"$authors"}])
            if aff_list:
                pipeline.append({"$match":{"authors.affiliations.id":{"$in":aff_list}}})
            if start_year:
                pipeline.append({"$match":{"year_published":{"$gte":start_year}}})
            if end_year:
                pipeline.append({"$match":{"year_published":{"$lte":end_year}}})
            pipeline.extend([
                {"$project":{"authors":1,"citations_count":1,"subjects":1}},
                {"$group":{"_id":"$authors.id","products_count":{"$sum":1},"citations_count":{"$sum":"$citations_count"},"author":{"$first":"$authors"},"subjects":{"$last":"$subjects"}}},
                {"$sort":{sorting_var:-1}},
                {"$project":{"author.id":1,"author.full_name":1,"author.affiliations":1,
                    "products_count":1,"citations_count":1,"subjects":1}}
            ])

            total_results = self.colav_db["person"].count_documents({"subjects.id":ObjectId(idx)})

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

            pipeline.extend([{"$skip":skip},{"$limit":max_results}])

            result= self.colav_db["works"].aggregate(pipeline,allowDiskUse=True)
        
            data = []

            for reg in result:
                group_name = ""
                group_id = ""
                inst_name=""
                inst_id=""
                if "author" in reg.keys():
                    if "affiliations" in reg["author"].keys():
                        if len(reg["author"]["affiliations"])>0:
                            for aff in reg["author"]["affiliations"]:
                                if "types" in aff.keys():
                                    for typ in aff["types"]:
                                        if typ["type"]=="group":
                                            if groups:
                                                if aff["id"] in aff_list:
                                                    group_name=aff["name"],
                                                    group_id=aff["id"]
                                            else:
                                                group_name=aff["name"],
                                                group_id=aff["id"]
                                        else:
                                            if institutions:
                                                if aff["id"] in aff_list:
                                                    inst_name=aff["name"]
                                                    inst_id=aff["id"]
                                            else:    
                                                inst_name=aff["name"]
                                                inst_id=aff["id"]  

                            entry={
                                "id":reg["_id"],
                                "name":reg["author"]["full_name"],
                                "subjects":[],
                                "products_count":reg["products_count"],
                                "citations_count":reg["citations_count"],
                                "affiliation":{"institution":{"name":inst_name, 
                                                    "id":inst_id},
                                            "group":{"name":group_name, "id":group_id}}
                            }
                            for subs in reg["subjects"]:
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
                            data.append(entry)
            
        return {"total":total_results,"page":page,"count":len(data),"data":data}



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
            institutions=self.request.args.get('institutions')
            groups=self.request.args.get('groups')

            if tipo == None: 
                production=self.get_production(idx=idx,
                    max_results=max_results,
                    page=page,
                    start_year=start_year,
                    end_year=end_year,
                    groups=groups,
                    institutions=institutions,
                    sort=sort)
            else:
                production=self.get_production_by_type(idx=idx,
                    max_results=max_results,
                    page=page,
                    start_year=start_year,
                    end_year=end_year,
                    groups=groups,
                    institutions=institutions,
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
            res=self.get_institutions(idx,page=page,max_results=max_results)
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
        else:
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=400,
                mimetype='application/json'
            )

        response.headers.add("Access-Control-Allow-Origin", "*")
        return response