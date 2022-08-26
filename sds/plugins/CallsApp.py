from sds.sdsBase import sdsPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime as dt
from dateutil import parser
import html_to_json


class CallsApp(sdsPluginBase):
    def __init__(self, sds):
        super().__init__(sds)

    def search_nih(self,max_results=100,page=1):
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

        skip = (page - 1)*max_results

        url='https://search.grants.nih.gov/guide/api/data?perpage=%d&sort=expdate:desc&from=%d&type=active,activenosis&parentic=all&primaryic=all&activitycodes=all&doctype=all&parentfoa=all&daterange=01021991-12132021&clinicaltrials=all&fields=all&spons=true&query='%(max_results,skip)

        
        response = requests.get(url)
        results = json.loads(response.text)

        calls = []
        total = results["data"]["hits"]["total"]

        for item in results["data"]["hits"]["hits"]:

            title=item.get("_source")["title"]
            if "Notice" in title:
                url = "https://grants.nih.gov/grants/guide/notice-files/"+item.get("_source")["docnum"]+".html"
            else:
                url = "https://grants.nih.gov/grants/guide/pa-files/"+item.get("_source")["docnum"]+".html"

            org=item.get("_source")["organization"]["primary"]
            exp_date = parser.parse(item.get("_source")["expdate"]).strftime("%Y-%m-%d")
            rel_date = parser.parse(item.get("_source")["reldate"]).strftime("%Y-%m-%d")
            


            entry = {
                "title":title,
                "organization":org,
                "expiration_date":exp_date,
                "release_date":rel_date,
                "url":url}

            calls.append(entry)

        return {"total":total,"page":page,"data":calls}
    
    def search_min(self,page=0):

        numbers=[]

        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://minciencias.gov.co/convocatorias-asctei?order=body&sort=asc',
            'Accept-Language': 'es-419,es;q=0.9',
            'If-None-Match': '"1639931969-0"',
        }
        

        #getting aditional calls for each page without parsing them
        repeated=0
        calls=[]
        for p in range(5):
            params = (
                ('order', 'field_fecha_de_apertura'),
                ('sort', 'asc'),
                ('page', str(p)),
            )
            response = requests.get('https://minciencias.gov.co/convocatorias-asctei?order=field_fecha_de_apertura&sort=asc', headers=headers, params=params,verify=False)
            soup = BeautifulSoup(response.text,'html.parser')
            box = soup.find_all('tr',class_='odd')
            calls_odd = []
            for e in box:
                if e.find('span',class_="file"):
                    continue
                number_field=e.find('td',class_='views-field-field-numero')
                number=number_field.get_text().replace("\n","").strip()
                if number in numbers:
                    repeated+=1
                else:
                    numbers.append(number)
                    entry={}

                    title=e.find('td',class_='views-field-title')
                    cuantia = e.find('td',class_='views-field-field-cuantia-xl')
                    apertura=e.find('td',class_='views-field-field-fecha-de-apertura')
                    fecha=apertura.find('span',class_='date-display-single')

                    url = "https://minciencias.gov.co/"+title.find('a')['href']

                    entry['title']=title.get_text().replace("\n","").strip()
                    entry['release_date']=fecha["content"].split("T")[0] if fecha else ""
                    entry['amount']=cuantia.get_text().replace("\n","").strip()
                    entry['url']=url
                    calls_odd.append(entry)

            box = soup.find_all('tr',class_='even')
            calls_even = []
            for e in box:
                number_field=e.find('td',class_='views-field-field-numero')
                number=number_field.get_text().replace("\n","").strip()
                if number in numbers:
                    repeated+=1
                else:
                    numbers.append(number)
                    entry={}

                    title=e.find('td',class_='views-field-title')
                    cuantia = e.find('td',class_='views-field-field-cuantia-xl')
                    apertura=e.find('td',class_='views-field-field-fecha-de-apertura')
                    fecha=apertura.find('span',class_='date-display-single')

                    url = "https://minciencias.gov.co/"+title.find('a')['href']

                    entry['title']=title.get_text().replace("\n","").strip()
                    entry['release_date']=fecha["content"].split("T")[0]  if fecha else ""
                    entry['amount']=cuantia.get_text().replace("\n","").strip()
                    entry['url']=url
                    calls_even.append(entry)
            if repeated>=5:
                break

            for i in range(max([len(calls_odd),len(calls_even)])):
                if i<len(calls_odd):
                    calls.append(calls_odd[i])
                if i<len(calls_even):
                    calls.append(calls_even[i])

        return {"data":calls,"total":len(calls),"page":0}

    def search_pfizer(self):
        url="https://www.pfizer.com/about/programs-policies/grants/competitive-grants?viewsreference%5Bdata%5D%5Bargument%5D=&viewsreference%5Bdata%5D%5Blimit%5D=&viewsreference%5Bdata%5D%5Boffset%5D=&viewsreference%5Bdata%5D%5Bpager%5D=&viewsreference%5Bdata%5D%5Btitle%5D=0&viewsreference%5Benabled_settings%5D%5Bpager%5D=pager&viewsreference%5Benabled_settings%5D%5Bargument%5D=argument&viewsreference%5Benabled_settings%5D%5Blimit%5D=limit&viewsreference%5Benabled_settings%5D%5Boffset%5D=offset&viewsreference%5Benabled_settings%5D%5Btitle%5D=title&items_per_page=12&search_api_fulltext=&order=field_rfp_loi_due_date&sort=desc"
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'html.parser')
        table = soup.find_all('td',class_='views-field')
        data=[]
        column_index=0
        entry={
            "title":"",
            "release_date":"",
            "due_date":"",
            "review_process":"",
            "grant_type":"",
            "focus_area":"",
            "country":"",
            "url":"",
        }
        for idx,cell in enumerate(table):
            if column_index==0:
                for item in cell.find_all("div",class_="compound-name"):
                    entry["title"]=item.get_text().strip()
                idate=""
                for jdx,item in enumerate(cell.find_all("span",class_="data")):
                    if jdx==0:
                        idate=dt.strptime(item.get_text(),"%B %d, %Y")
                    else:
                        entry["review_process"]=item.get_text().strip()
                if idate:
                    entry["release_date"]=idate.strftime("%Y-%m-%d")
                for item in cell.find_all("a",class_="clinical-link",href=True):
                    entry["url"]=item["href"]
                column_index+=1
            elif column_index==1:
                #print(idx,column_index,cell.get_text())
                entry["grant_type"]=cell.get_text().strip()
                column_index+=1
            elif column_index==2:
                #print(idx,column_index,cell.get_text())
                entry["focus_area"]=cell.get_text().strip()
                column_index+=1
            elif column_index==3:
                #print(idx,column_index,cell.get_text())
                entry["country"]=cell.get_text().strip()
                column_index+=1
            elif column_index==4:
                #print(idx,column_index,cell.get_text())
                date=dt.strptime(cell.get_text(),"%B %d, %Y")
                entry["due_date"]=date.strftime("%Y-%m-%d")
                data.append(entry)
                column_index=0
                entry={
                    "title":"",
                    "release_date":"",
                    "due_date":"",
                    "review_process":"",
                    "grant_type":"",
                    "focus_area":"",
                    "country":"",
                    "url":"",
                }
        return data
    
    def search_ukri(self,page=1):
        url="https://www.ukri.org/opportunity/page/"+str(page)+"/?filter_status%5B0%5D=open&filter_status%5B1%5D=upcoming&filter_submitted=true&filter_order=closing_date"
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'html.parser')
        opportunities = soup.find_all('div',class_='opportunity')
        data=[]
        for idx,op in enumerate(opportunities):
            entry={
                "title":"",
                "url":"",
                "description":"",
                "publication_date":"",
                "type":"",
                "opening_date":"",
                "closing_date":"",
                "total_fund":"",
                "funders":"",
                "funders_url":"",
                "status":""
            }
            for h in op.find_all("div",class_="entry-header"):
                entry["title"]=h.get_text().strip()
                for a in h.find_all("a",href=True):
                    entry["url"]=a["href"]
            for c in op.find_all("div",class_="entry-content"):
                entry["description"]=c.get_text().strip()
            for m in op.find_all("div",class_="entry-meta"):
                for s in m.find_all("span",class_="opportunity-status__flag"):
                    entry["status"]=s.get_text().strip()
                for a in m.find_all("a",class_="ukri-funder__link",href=True):
                    entry["funders"]=a.get_text().strip()
                    entry["funders_url"]=a["href"]
                for odx,o in enumerate(m.find_all("dd",class_="opportunity-cells")):
                    if odx==2:
                        entry["type"]=o.get_text().strip()
                    elif odx==3:
                        entry["total_fund"]=o.get_text().strip()
                    elif odx==4:
                        entry["publication_date"]=o.get_text().strip()
                    elif odx==5:
                        entry["opening_date"]=o.get_text().strip()
                    elif odx==6:
                        entry["closing_date"]=o.get_text().strip()
            data.append(entry)
        return data
    
    @endpoint('/app/calls', methods=['GET'])
    def calls_search(self):
        """

        """
        data = self.request.args.get('data')

        if data=="nih":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 10
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            result = self.search_nih(max_results=max_results,page=page)
        elif data=="min":
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            result = self.search_min(page=page)
        elif data=="pfizer":
            result=self.search_pfizer()
        elif data=="ukri":
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            result=self.search_ukri(page)
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