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
            cursor.sort([("works_count",DESCENDING)])

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
                entry={
                    "name":subject["name"],
                    "id":subject["_id"],
                    "products_count":subject["works_count"],
                }
                if "international" in subject.keys():
                    if "display_name" in subject["international"].keys():
                        if "es" in subject["international"]["display_name"].keys():
                            entry["name"]=subject["international"]["display_name"]["es"]
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

    def search_author(self,keywords="",affiliation="",country="",max_results=100,page=1,
        group_id=None,institution_id=None,sort="citations"):
        search_dict={}
        if keywords:
            cursor=self.colav_db['authors'].find({"$text":{"$search":keywords},"external_ids":{"$ne":[]}},{ "score": { "$meta": "textScore" } }).sort([("score", { "$meta": "textScore" } )])
            filter_cursor=self.colav_db['authors'].find({"$text":{"$search":keywords},"external_ids":{"$ne":[]}},{ "score": { "$meta": "textScore" } }).sort([("score", { "$meta": "textScore" } )])
            pipeline=[{"$match":{"$text":{"$search":keywords},"external_ids":{"$ne":[]}}}]
            aff_pipeline=[
                {"$match":{"$text":{"$search":keywords},"external_ids":{"$ne":[]}}},
                {"$unwind":"$affiliations"},{"$project":{"affiliations":1,"products_count":1, "citations_count":1}},
                {"$group":{"_id":"$id","affiliation":{"$last":"$affiliations"}}},
                {"$group":{"_id":"$affiliation"}}
            ]
        else:
            cursor=self.colav_db['authors'].find({"external_ids":{"$ne":[]}})
            filter_cursor=self.colav_db['authors'].find({"external_ids":{"$ne":[]}})
            pipeline=[{"$match":{"external_ids":{"$ne":[]}}}]
            aff_pipeline=[
                {"$match":{"external_ids":{"$ne":[]}}},
                {"$unwind":"$affiliations"},{"$project":{"affiliations":1,"products_count":1, "citations_count":1}},
                {"$group":{"_id":"$id","affiliation":{"$last":"$affiliations"}}},
                {"$group":{"_id":"$affiliation"}}
            ]

        institution_filters = []
        group_filters=[]
        institution_ids=[]
        groups_ids=[]

        for author in filter_cursor:
            if "affiliations" in author.keys():
                if len(author["affiliations"])>0:
                    for aff in author["affiliations"]:
                        if "type" in aff.keys():
                            if aff["type"]=="group":
                                if not aff["id"] in groups_ids:
                                    groups_ids.append(aff["id"])
                                    group_filters.append({
                                        "id":str(aff["id"]),
                                        "name":aff["name"]
                                    })
                        else:
                            if not str(aff["id"]) in institution_ids:    
                                institution_ids.append(str(aff["id"]))
                                entry = {"id":str(aff["id"]),"name":aff["name"]}
                                institution_filters.append(entry)

        def_list=[]
        if keywords and group_id:
            for group in group_id.split():
                def_list.append(ObjectId(group))
            search_dict["affiliations.id"]={"$in":def_list}
            search_dict["$text"]={"$search":keywords}
            search_dict["external_ids"]={"$ne":[]}
            cursor=self.colav_db['authors'].find(search_dict,{ "score": { "$meta": "textScore" } }).sort([("score", { "$meta": "textScore" } )])
            pipeline=[{"$match":{"$text":{"$search":keywords},"external_ids":{"$ne":[]}}}]
            aff_pipeline=[
                {"$match":{"$text":{"$search":keywords},"external_ids":{"$ne":[]}}},
                {"$unwind":"$affiliations"},{"$project":{"affiliations":1,"products_count":1, "citations_count":1}},
                {"$group":{"_id":"$id","affiliation":{"$last":"$affiliations"}}},
                {"$group":{"_id":"$affiliation"}}
            ]
        
        if keywords and institution_id:
            for inst in institution_id.split():
                def_list.append(ObjectId(inst))
            search_dict["affiliations.id"]={"$in":def_list}
            search_dict["$text"]={"$search":keywords}
            search_dict["external_ids"]={"$ne":[]}
            cursor=self.colav_db['authors'].find(search_dict,{ "score": { "$meta": "textScore" } }).sort([("score", { "$meta": "textScore" } )])
            pipeline=[{"$match":{"$text":{"$search":keywords},"external_ids":{"$ne":[]}}}]
            aff_pipeline=[
                {"$match":{"$text":{"$search":keywords},"external_ids":{"$ne":[]}}},
                {"$unwind":"$affiliations"},{"$project":{"affiliations":1,"products_count":1, "citations_count":1}},
                {"$group":{"_id":"$id","affiliation":{"$last":"$affiliations"}}},
                {"$group":{"_id":"$affiliation"}}
            ]

        if keywords=="" and institution_id:
            for inst in institution_id.split():
                def_list.append(ObjectId(inst))
            search_dict["affiliations.id"]={"$in":def_list}
            search_dict["external_ids"]={"$ne":[]}
            cursor=self.colav_db['authors'].find(search_dict)
            pipeline=[{"$match":{"external_ids":{"$ne":[]}}}]
            aff_pipeline=[
                {"$match":{"external_ids":{"$ne":[]}}},
                {"$unwind":"$affiliations"},{"$project":{"affiliations":1,"products_count":1, "citations_count":1}},
                {"$group":{"_id":"$id","affiliation":{"$last":"$affiliations"}}},
                {"$group":{"_id":"$affiliation"}}
            ]

        if keywords=="" and group_id:
            for group in group_id.split():
                def_list.append(ObjectId(group))
            search_dict["affiliations.id"]={"$in":def_list}
            search_dict["external_ids"]={"$ne":[]}
            cursor=self.colav_db['authors'].find(search_dict)
            pipeline=[{"$match":{"external_ids":{"$ne":[]}}}]
            aff_pipeline=[
                {"$match":{"external_ids":{"$ne":[]}}},
                {"$unwind":"$affiliations"},{"$project":{"affiliations":1,"products_count":1, "citations_count":1}},
                {"$group":{"_id":"$id","affiliation":{"$last":"$affiliations"}}},
                {"$group":{"_id":"$affiliation"}}
            ]


        if sort=="citations":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="products":
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
            author_list=[]
            keywords=[]
            group_name = ""
            group_id = ""
            for author in cursor:
                entry={
                    "id":author["_id"],
                    "name":author["full_name"],
                    "papers_count"   :author["products_count"],
                    "citations_count":author["citations_count"],
                    "affiliation":{"institution":{"name":"","id":""}}
                }
                if "affiliations" in author.keys():
                    if len(author["affiliations"])>0:
                        for aff in author["affiliations"]:
                            if "type" in aff.keys():
                                entry["affiliation"]["group"]={
                                    "name":aff["name"],
                                    "id":aff["id"]
                                }
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

    def search_groups(self,keywords="",institution_id=None,max_results=100,page=1,sort="citations"):
        if keywords:
            cursor=self.colav_db['affiliations'].find({"$text":{"$search":keywords},"types":"group"})        
            relations = cursor.distinct("relations")
        else:
            cursor=self.colav_db['affiliations'].find({"types":"group"})
            relations = cursor.distinct("relations")
            

        if keywords:
            if institution_id:
                cursor=self.colav_db['affiliations'].find({"$text":{"$search":keywords},"types":"group","relations.id":ObjectId(institution_id)})

            else:
                cursor=self.colav_db['affiliations'].find({"$text":{"$search":keywords},"types":"group"})
        
            
            pipeline=[{"$match":{"$text":{"$search":keywords},"types":"group"}}]
            aff_pipeline=[
                {"$match":{"$text":{"$search":keywords},"types":"group"}},
                {"$project":{"relations":1}},
                {"$unwind":"$relations"},
                {"$group":{"_id":{"name":"$relations.name","id":"$relations.id"}}}
                

            ] 
        else:
            if institution_id:
                cursor=self.colav_db['affiliations'].find({"types":"group","relations.id":ObjectId(institution_id)})

            else:
                cursor=self.colav_db['affiliations'].find({"types":"group"})

            pipeline=[]
            aff_pipeline=[
                {"$project":{"relations":1}},
                {"$unwind":"$relations"},
                {"$group":{"_id":{"name":"$relations.name","id":"$relations.id"}}}
            ]
            
        tmp = []

        entry={"id":"","name":""}
        for r in relations:
            if 'university' in r["type"]:
                entry = {"id":str(r["id"]),"name":r["name"]}
                tmp.append(entry)

        #eliminamos duplicados en la lista de instituciones:
        institution_filters = []
        for e in tmp:
            if e not in institution_filters:
                institution_filters.append(e)


        if sort=="citations":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="products":
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

        pipeline.append({"$group":{"_id":{"country_code":"$addresses.country_code","country":"$addresses.country"}}})
        countries=[]
        for res in self.colav_db["affiliations"].aggregate(pipeline):
            reg=res["_id"]
            if reg["country_code"] and reg["country"]:
                country={"country_code":reg["country_code"][0],"country":reg["country"][0]}
                if not country in countries:
                    countries.append(country)

        if cursor:
            entity_list=[]
            for entity in cursor:
                entry={
                    "name":entity["name"],
                    "id":str(entity["_id"]),
                    "papers_count":entity["products_count"],
                    "citations_count":entity["citations_count"],
                    "affiliation":{"institution":{"name":"","id":""}}

                }
                
                for relation in entity["relations"]:
                    if "university" in relation["type"]:
                        entry["affiliation"]["institution"]["name"]=relation["name"]
                        entry["affiliation"]["institution"]["id"]=relation["id"]

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

    def search_institution(self,keywords="",country="",max_results=100,page=1,sort='citations'):
        if keywords:
            if country:
                cursor=self.colav_db['affiliations'].find({"$text":{"$search":keywords},"types":{"$ne":"group"},"addresses.country_code":country,"external_ids":{"$ne":[]}})
            else:
                cursor=self.colav_db['affiliations'].find({"$text":{"$search":keywords},"types":{"$ne":"group"},"external_ids":{"$ne":[]}})
                
            country_pipeline=[{"$match":{"$text":{"$search":keywords},"types":{"$ne":"group"},"external_ids":{"$ne":[]}}}]
        else:
            if country:
                cursor=self.colav_db['affiliations'].find({"addresses.country_code":country,"types":{"$ne":"group"},"external_ids":{"$ne":[]}})
                
            else:
                cursor=self.colav_db['affiliations'].find({"external_ids":{"$ne":[]},"types":{"$ne":"group"}})
                
            country_pipeline=[{"$match":{"types":{"$ne":"group"}}}]
        
        if sort=="citations":
            cursor.sort([("citations_count",DESCENDING)])
        if sort=="products":
            cursor.sort([("products_count",DESCENDING)])

        country_pipeline.append(
            {
                "$group":{
                    "_id":{"country_code":"$addresses.country_code","country":"$addresses.country"}
                    }
                }
        )
        countries=[]
        for res in self.colav_db["affiliations"].aggregate(country_pipeline):
            reg=res["_id"]
            if reg["country_code"] and reg["country"]:
                country={"country_code":reg["country_code"][0],"country":reg["country"][0]}
                if not country in countries:
                    countries.append(country)

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
                entry={
                    "id":institution["_id"],
                    "name":institution["name"],
                    "papers_count":institution["products_count"],
                    "citations_count":institution["citations_count"],
                    "logo":institution["logo_url"]
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
            result=self.colav_db['documents'].find({"$text":{"$search":keywords}},{"year_published":1}).sort([("year_published",ASCENDING)]).limit(1)
            if result:
                result=list(result)
                if len(result)>0:
                    initial_year=result[0]["year_published"]
            result=self.colav_db['documents'].find({"$text":{"$search":keywords}},{"year_published":1}).sort([("year_published",DESCENDING)]).limit(1)
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

    def search_documents(self,keywords="",start_year=None,end_year=None):
        open_access=[]
        entry={}

        initial_year=0
        final_year = 0

        if keywords: 
            cursor=self.colav_db['documents'].find({"$text":{"$search":keywords}},{"year_published":1})
            result = cursor.sort([("year_published",ASCENDING)]).limit(1)
            if result:
                result=list(result)
                
                if len(result)>0:
                    initial_year=result[0]["year_published"]
            result=self.colav_db['documents'].find({"$text":{"$search":keywords}},{"year_published":1}).sort([("year_published",DESCENDING)]).limit(1)
            if result:
                result=list(result)
                
                if len(result)>0:
                    final_year=result[0]["year_published"]
        else:
            cursor=self.colav_db['documents'].find({},{"year_published":1})
            result = cursor.sort([("year_published",ASCENDING)]).limit(1)
            if result:
                result=list(result)
                
                if len(result)>0:
                    initial_year=result[0]["year_published"]
            result=self.colav_db['documents'].find({},{"year_published":1}).sort([("year_published",DESCENDING)]).limit(1)
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

        if keywords:
            aff_pipeline =[
                {"$match":{"$text":{"$search":keywords}}},
                {"$project":{"authors.affiliations":1}},
                {"$unwind":"$authors"},
                {"$group":{"_id":{"$arrayElemAt":["$authors.affiliations.id",0]},"name":{"$first":"$authors.affiliations.name"}}},
                {"$unwind":"$name"}
            ]
            cursor = self.colav_db["documents"].aggregate(aff_pipeline,allowDiskUse=True)
            for institution in cursor:
                entry = {"id":institution["_id"],"name":institution["name"]}

            institution_filters.append(entry)

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

            if start_year and not end_year:
                venn_query={"year_published":{"$gte":start_year},"$text":{"$search":keywords}}
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$gte":start_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$gte":start_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$gte":start_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"bronze" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$gte":start_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"closed" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$gte":start_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"hybrid" ,"value":val})
                
            elif end_year and not start_year:
                venn_query={"year_published":{"$lte":end_year},"$text":{"$search":keywords}}
                
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$lte":end_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val={"type":"gold"  ,"value": self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$lte":end_year},"$text":{"$search":keywords}})  },
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$lte":end_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"bronze" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$lte":end_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"closed" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$lte":end_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"hybrid" ,"value":val})
                
            elif start_year and end_year:
                venn_query={"year_published":{"$gte":start_year,"$lte":end_year},"$text":{"$search":keywords}}
                
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$gte":start_year,"$lte":end_year},"$text":{"$search":keywords} })
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$gte":start_year,"$lte":end_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$gte":start_year,"$lte":end_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"bronze" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$gte":start_year,"$lte":end_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"closed" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$gte":start_year,"$lte":end_year},"$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"hybrid" ,"value":val})
                
            else:
                venn_query={"$text":{"$search":keywords}}
    
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"bronze" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"closed" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","$text":{"$search":keywords}})
                if val!=0:
                    open_access.append({"type":"hybrid" ,"value":val})
                


            tipos = self.colav_db['documents'].distinct("publication_type.type",{"$text":{"$search":keywords}})

        else:
            if start_year and not end_year:
                venn_query={"year_published":{"$gte":start_year}}
                
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$gte":start_year} })
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$gte":start_year} })
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$gte":start_year} })
                if val!=0:
                    open_access.append({"type":"bronze" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$gte":start_year} })
                if val!=0:
                    open_access.append({"type":"closed" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$gte":start_year} })
                if val!=0:
                    open_access.append({"type":"hybrid" ,"value":val})
            
            elif end_year and not start_year:
                venn_query={"year_published":{"$lte":end_year} }
                
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"bronze" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"closed" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"hybrid" ,"value":val})
                
            elif start_year and end_year:
                venn_query={"year_published":{"$gte":start_year,"$lte":end_year} }
                
                val=self.colav_db['documents'].count_documents({"open_access_status":"green","year_published":{"$gte":start_year,"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold","year_published":{"$gte":start_year,"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze","year_published":{"$gte":start_year,"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"bronze" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed","year_published":{"$gte":start_year,"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"closed" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid","year_published":{"$gte":start_year,"$lte":end_year} })
                if val!=0:
                    open_access.append({"type":"hybrid" ,"value":val})
            
            else:
                venn_query={}
                
                val=self.colav_db['documents'].count_documents({"open_access_status":"green" })
                if val!=0:
                    open_access.append({"type":"green" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"gold" })
                if val!=0:
                    open_access.append({"type":"gold" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"bronze" })
                if val!=0:
                    open_access.append({"type":"bronze" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"closed" })
                if val!=0:
                    open_access.append({"type":"closed" ,"value":val})
                val=self.colav_db['documents'].count_documents({"open_access_status":"hybrid" })
                if val!=0:
                    open_access.append({"type":"hybrid" ,"value":val})
                


            tipos = self.colav_db['documents'].distinct("publication_type.type")

        return {
            "open_access":open_access,
            "venn_source":self.get_venn(venn_query),
            "types":tipos,
            "filters":{"years":years,"institutions":institution_filters}
        }
                    
    def search_documents_by_type(self,keywords="",max_results=100,page=1,start_year=None,end_year=None,
        sort="citations",direction="descending",tipo="article",institution_id=None,
        group_id=None):


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

        if start_year and end_year:
            if keywords:
                if institution_id:
                    cursor=self.colav_db['documents'].find({"$text":{"$search":keywords},
                        "publication_type.type":tipo,"authors.affiliations.id":ObjectId(institution_id),
                        "year_published":{"$gte":start_year,"$lte":end_year}})
                    aff_pipeline=[
                    {"$match":{"$text":{"$search":keywords}}}
                    ]
                else:
                    cursor=self.colav_db['documents'].find({"$text":{"$search":keywords},
                    "publication_type.type":tipo,"year_published":{"$gte":start_year,"$lte":end_year}})
                    aff_pipeline=[
                    {"$match":{"$text":{"$search":keywords}}}
                    ]
            else:
                if institution_id:
                    cursor=self.colav_db['documents'].find({"publication_type.type":tipo,
                        "authors.affiliations.id":ObjectId(institution_id),
                        "year_published":{"$gte":start_year,"$lte":end_year}})
                    aff_pipeline=[]
                else:
                    cursor=self.colav_db['documents'].find({"publication_type.type":tipo,
                        "year_published":{"$gte":start_year,"$lte":end_year}})
                    aff_pipeline=[]
        elif start_year and not end_year:
            if keywords:
                if institution_id:
                    cursor=self.colav_db['documents'].find({"$text":{"$search":keywords},
                        "publication_type.type":tipo,"authors.affiliations.id":ObjectId(institution_id),
                        "year_published":{"$gte":start_year}})
                    aff_pipeline=[
                    {"$match":{"$text":{"$search":keywords}}}
                    ]
                else:
                    cursor=self.colav_db['documents'].find({"$text":{"$search":keywords},"publication_type.type":tipo,"year_published":{"$gte":start_year}})
                    aff_pipeline=[
                    {"$match":{"$text":{"$search":keywords}}}
                    ]
            else:
                if institution_id:
                    cursor=self.colav_db['documents'].find({"publication_type.type":tipo,
                        "authors.affiliations.id":ObjectId(institution_id),
                        "year_published":{"$gte":start_year}})
                    aff_pipeline=[]
                else:
                    cursor=self.colav_db['documents'].find({"publication_type.type":tipo,
                        "year_published":{"$gte":start_year}})
                    aff_pipeline=[]
        if not start_year and end_year:
            if keywords:
                if institution_id:
                    cursor=self.colav_db['documents'].find({"$text":{"$search":keywords},
                        "publication_type.type":tipo,"authors.affiliations.id":ObjectId(institution_id),
                        "year_published":{"$lte":end_year}})
                    aff_pipeline=[
                    {"$match":{"$text":{"$search":keywords}}}
                    ]
                else:
                    cursor=self.colav_db['documents'].find({"$text":{"$search":keywords},
                    "publication_type.type":tipo,"year_published":{"$lte":end_year}})
                    aff_pipeline=[
                    {"$match":{"$text":{"$search":keywords}}}
                    ]
            else:
                if institution_id:
                    cursor=self.colav_db['documents'].find({"publication_type.type":tipo,
                        "authors.affiliations.id":ObjectId(institution_id),
                        "year_published":{"$lte":end_year}})
                    aff_pipeline=[]
                else:
                    cursor=self.colav_db['documents'].find({"publication_type.type":tipo,
                        "year_published":{"$lte":end_year}})
                    aff_pipeline=[]
        else:
            if keywords:
                if institution_id:
                    cursor=self.colav_db['documents'].find({"$text":{"$search":keywords},
                    "publication_type.type":tipo,"authors.affiliations.id":ObjectId(institution_id)})
                    aff_pipeline=[
                        {"$match":{"$text":{"$search":keywords}}}
                    ]
                else:
                    cursor=self.colav_db['documents'].find({"$text":{"$search":keywords},
                        "publication_type.type":tipo})
                aff_pipeline=[]
            else:
                if institution_id:
                    cursor=self.colav_db['documents'].find({"publication_type.type":tipo,
                        "authors.affiliations.id":ObjectId(institution_id)})
                    aff_pipeline=[]
                else:
                    cursor=self.colav_db['documents'].find({"publication_type.type":tipo})
                    aff_pipeline=[]

        #¿ESTO PA' QUÉ?
        '''aff_pipeline.extend([
                {"$unwind":"$affiliations"},{"$project":{"affiliations":1}},
                {"$group":{"_id":"$_id","affiliation":{"$last":"$affiliations"}}},
                {"$group":{"_id":"$affiliation"}}
            ])'''
        #affiliations=[reg["_id"] for reg in self.colav_db["authors"].aggregate(aff_pipeline)]


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
                    "open_access_status":paper["open_access_status"],
                    "year_published":paper["year_published"],
                    "citations_count":paper["citations_count"],
                    "subjects":[{"name":reg["name"],"id":reg["id"]}for reg in paper["subjects"]] if "subjects" in paper.keys() else  []
                }

                source=self.colav_db["sources"].find_one({"_id":paper["source"]["id"]})
                if source:
                    entry["source"]={"name":source["title"],"id":source["_id"]}
                
                authors=[]
                for author in paper["authors"]:
                    reg_au=self.colav_db["authors"].find_one({"_id":author["id"]})
                    reg_aff=""
                    if author["affiliations"]:
                        reg_aff=self.colav_db["affiliations"].find_one({"_id":author["affiliations"][0]["id"]})
                    
                    
                    author_entry={
                        "id":reg_au["_id"],
                        "full_name":reg_au["full_name"],
                        "affiliation": {
                            "institution":{"name":"","id":""}
                        }
                    }
                    if reg_aff:
                        author_entry["affiliation"]["institution"]["name"] = reg_aff["name"]
                        author_entry["affiliation"]["institution"]["id"]   = reg_aff["_id"]
                    

                        
                  

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
            idx = self.request.args.get('institution') if "institution" in self.request.args else ""
            result=self.search_groups(keywords=keywords,institution_id=idx,max_results=max_results,page=page,sort=sort)
        elif data=="authors":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            sort = self.request.args.get('sort') if "sort" in self.request.args else "citations"
            group_id = self.request.args.get('group') if "group" in self.request.args else None
            institution_id = self.request.args.get('institution') if "institution" in self.request.args else None
            result=self.search_author(keywords=keywords,max_results=max_results,page=page,sort=sort,
                group_id=group_id,institution_id=institution_id)
        elif data=="institutions":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            sort = self.request.args.get('sort') if "sort" in self.request.args else "citations"
            country = self.request.args.get('country') if "country" in self.request.args else ""
            result=self.search_institution(keywords=keywords,country=country,max_results=max_results,page=page,sort=sort)
        elif data=="literature":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            country = self.request.args.get('country') if "country" in self.request.args else ""
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            sort=self.request.args.get('sort')
            institution_id=self.request.args.get('institution')
            group_id=self.request.args.get('group')
            if tipo == None:
                result=self.search_documents(keywords=keywords,start_year=start_year,end_year=end_year)
            else:
                result=self.search_documents_by_type(keywords=keywords,max_results=max_results,
                    page=page,start_year=start_year,end_year=end_year,sort=sort,
                    direction="descending",tipo=tipo,institution_id=institution_id,
                    group_id=group_id)
        elif data=="subjects":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            sort=self.request.args.get('sort')
            result=self.search_subjects(keywords=keywords,max_results=max_results,
                page=page,sort=sort,direction="descending")

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