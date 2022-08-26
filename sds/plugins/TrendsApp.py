from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
from datetime import date
import json

class TrendsApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)
        with open('sds/etc/pddpts.json') as json_file:
            self.pddpts = json.load(json_file)

    def get_info(self):
        subject=self.colav_db["subjects"].find_one({"names.name":{"$regex":".*covid.*","$options":"i"}},{"_id":1})
        covid_data={
            "id":subject["_id"] if subject else "",
            "products":self.colav_db["works"].count_documents({"subjects.name":{"$regex":".*covid.*","$options":"i"}}),
            "authors":self.colav_db["person"].count_documents({"subjects.name":{"$regex":".*covid.*","$options":"i"}}),
            "institutions":self.colav_db["affiliations"].count_documents({"types.type":{"$ne":"group"},"subjects.name":{"$regex":".*covid.*","$options":"i"}}),
            "groups":self.colav_db["affiliations"].count_documents({"types.type":"group","subjects.name":{"$regex":".*covid.*","$options":"i"}})
        }

        ods_data=[]
        for policy in self.colav_db["policies"].find({"abbreviations":"ODS"}):
            name=""
            for n in policy["names"]:
                if n["lang"]=="es":
                    name=n["name"]
                    break
                elif n["lang"]=="en":
                    name=n["name"]
            entry={
                "id":policy["_id"],
                "name":name,
                "index":"",
                "products":self.colav_db["works"].count_documents({"policies.id":policy["_id"]}),
                "authors":self.colav_db["person"].count_documents({"policies.id":policy["_id"]}),
                "institutions":self.colav_db["affiliations"].count_documents({"types.type":{"$ne":"group"},"policies.id":policy["_id"]}),
                "groups":self.colav_db["affiliations"].count_documents({"types.type":"group","policies.id":policy["_id"]})
            }
            if len(policy["index"])>0:
                for index in policy["index"]:
                    entry["index"]+=str(int(index["index"]))+"."
                entry["index"]=entry["index"][:-1]
            ods_data.append(entry)

        pdd_reg=self.colav_db["policies"].find_one({"abbreviations":"PDD"})
        pdd_data={
            "id":pdd_reg["_id"],
            "products":self.colav_db["works"].count_documents({"policies.id":pdd_reg["_id"]}),
            "authors":self.colav_db["person"].count_documents({"policies.id":pdd_reg["_id"]}),
            "institutions":self.colav_db["affiliations"].count_documents({"types.type":{"$ne":"group"},"policies.id":pdd_reg["_id"]}),
            "groups":self.colav_db["affiliations"].count_documents({"types.type":"group","policies.id":pdd_reg["_id"]}),
            "tree":[]
        }
        pdd_subtree=[]
        prop_titles=[]
        for idprop,prop in enumerate(sorted(self.pddpts["PDD"].keys())):
            if not prop in prop_titles:
                pdd_subtree.append({"title":prop,"value":"0-0-"+str(idprop),"children":[]})
                prop_titles.append(prop)
            prog_titles=[]
            for idprog,prog in enumerate(sorted(self.pddpts["PDD"][prop].keys())):
                if not prog in prog_titles:
                    pdd_subtree[idprop]["children"].append(
                        {"title":prog,"value":"0-0-"+str(idprop)+"-"+str(idprog),"children":[]}
                    )
                    prog_titles.append(prog)
                key_titles=[]
                for idkey,keyword in enumerate(sorted(self.pddpts["PDD"][prop][prog]["es"])):
                    if not keyword in key_titles:
                        pdd_subtree[idprop]["children"][idprog]["children"].append(
                            {"title":keyword,
                            "value":"0-0-"+str(idprop)+"-"+str(idprog)+"-"+str(idkey)
                            }
                        )
                        key_titles.append(keyword)
        pdd_data["tree"]=pdd_subtree

        pts_reg=self.colav_db["policies"].find_one({"abbreviations":"PTS"})
        pts_data={
            "id":pts_reg["_id"],
            "products":self.colav_db["works"].count_documents({"policies.id":pts_reg["_id"]}),
            "authors":self.colav_db["person"].count_documents({"policies.id":pts_reg["_id"]}),
            "institutions":self.colav_db["affiliations"].count_documents({"types.type":{"$ne":"group"},"policies.id":pts_reg["_id"]}),
            "groups":self.colav_db["affiliations"].count_documents({"types.type":"group","policies.id":pts_reg["_id"]}),
            "tree":[]
        }
        pts_subtree=[]
        prop_titles=[]
        for idprop,prop in enumerate(sorted(self.pddpts["PTS"].keys())):
            if not prop in prop_titles:
                pts_subtree.append({"title":prop,"value":"0-0-"+str(idprop),"children":[]})
                prop_titles.append(prop)
            prog_titles=[]
            for idprog,prog in enumerate(sorted(self.pddpts["PTS"][prop].keys())):
                if not prog in prog_titles:
                    pts_subtree[idprop]["children"].append(
                        {"title":prog,"value":"0-0-"+str(idprop)+"-"+str(idprog),"children":[]}
                    )
                    prog_titles.append(prog)
                key_titles=[]
                for idkey,keyword in enumerate(sorted(self.pddpts["PTS"][prop][prog]["es"])):
                    if not keyword in key_titles:
                        pts_subtree[idprop]["children"][idprog]["children"].append(
                            {"title":keyword,
                            "value":"0-0-"+str(idprop)+"-"+str(idprog)+"-"+str(idkey)
                            }
                        )
                        key_titles.append(keyword)
        pts_data["tree"]=pts_subtree

        return {
            "covid":covid_data,
            "ODS":ods_data,
            "PDD":pdd_data,
            "PTS":pts_data,
        }

    def get_program(self,program):
        keywords=[]
        for key,val in self.pddpts["PDD"].items():
            if program in list(val.keys()):
                keywords.extend(val[program]["es"])
                keywords.extend(val[program]["en"])
        for key,val in self.pddpts["PTS"].items():
            if program in list(val.keys()):
                keywords.extend(val[program]["es"])
                keywords.extend(val[program]["en"])
        if len(keywords)==0:
            return None

        products_ids=[]
        authors_ids=[]
        groups_ids=[]
        affiliations_ids=[]
        subjects_ids=[]
        word_cloud=[]
        products=0
        for keyword in keywords:
            for reg in self.colav_db["works"].find({"$or":[{"titles.title":{"$regex":keyword,"$options":"i"}},{"abstract":{"$regex":keyword,"$options":"i"}}]}):
                if str(reg["_id"]) in products_ids:
                    continue
                products_ids.append(str(reg["_id"]))
                for author in reg["authors"]:
                    if not str(author["id"]) in authors_ids:
                        authors_ids.append(str(author["id"]))
                    for aff in author["affiliations"]:
                        for typ in aff["types"]:
                            if typ["type"]=="group":
                                if not str(aff["id"]) in groups_ids:
                                    groups_ids.append(str(aff["id"]))
                            else:    
                                if not str(aff["id"]) in affiliations_ids:
                                    affiliations_ids.append(str(aff["id"]))
                for s in reg["subjects"]:
                    name=s["names"][0]["name"]
                    for n in s["names"]:
                        if n["lang"]=="es":
                            name=n["name"]
                            break
                        if n["lang"]=="en":
                            name=n["name"]
                    if str(s["id"]) in subjects_ids:
                        word_cloud[subjects_ids.index(str(s["id"]))]["products"]+=1
                    else:
                        word_cloud.append({
                            "id":s["id"],
                            "name":name,
                            "products":1
                        })
                        subjects_ids.append(str(s["id"]))
        entry={
            "products":len(products_ids),#count
            "authors":len(authors_ids),#count
            "institutions":len(affiliations_ids),#count
            "groups":len(groups_ids),#count
            "word_cloud":word_cloud,#subjects with id, name
        }
        return entry
    
    def get_concept(self,concept):
        authors_ids=[]
        groups_ids=[]
        affiliations_ids=[]
        subjects_ids=[]
        word_cloud=[]
        products=0
        for reg in self.colav_db["works"].find({"$or":[{"titles.title":{"$regex":concept,"$options":"i"}},{"abstract":{"$regex":concept,"$options":"i"}}]}):
            products+=1
            for author in reg["authors"]:
                if not str(author["id"]) in authors_ids:
                    authors_ids.append(str(author["id"]))
                for aff in author["affiliations"]:
                    for typ in aff["types"]:
                        if typ["type"]=="group":
                            if not str(aff["id"]) in groups_ids:
                                groups_ids.append(str(aff["id"]))
                        else:    
                            if not str(aff["id"]) in affiliations_ids:
                                affiliations_ids.append(str(aff["id"]))
            for s in reg["subjects"]:
                name=s["names"][0]["name"]
                for n in s["names"]:
                    if n["lang"]=="es":
                        name=n["name"]
                        break
                    if n["lang"]=="en":
                        name=n["name"]
                if str(s["id"]) in subjects_ids:
                    word_cloud[subjects_ids.index(str(s["id"]))]["products"]+=1
                else:
                    word_cloud.append({
                        "id":s["id"],
                        "name":name,
                        "products":1
                    })
                    subjects_ids.append(str(s["id"]))
        entry={
            "products":products,#count
            "authors":len(authors_ids),#count
            "institutions":len(affiliations_ids),#count
            "groups":len(groups_ids),#count
            "word_cloud":word_cloud,#subjects with id, name
        }
        return entry


    @endpoint('/app/trends', methods=['GET'])
    def app_trends(self):

        
        data = self.request.args.get('data')
        if data=="info":
            trends=self.get_info()
            if trends:
                response = self.app.response_class(
                response=self.json.dumps(trends),
                status=200,
                mimetype='application/json'
                )
        elif data=="program":
            program = self.request.args.get('program')
            if program:
                result=self.get_program(program)
                if result:
                    response = self.app.response_class(
                    response=self.json.dumps(result),
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
        elif data=="concept":
            concept = self.request.args.get('concept')
            if concept:
                result=self.get_concept(concept)
                if result:
                    response = self.app.response_class(
                    response=self.json.dumps(result),
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
        else:
            response = self.app.response_class(
            response=self.json.dumps({"status":"Request returned empty"}),
            status=204,
            )

        response.headers.add("Access-Control-Allow-Origin", "*")
        return response