define({ "api": [
  {
    "type": "get",
    "url": "/apidoc/update",
    "title": "Update ApiDoc Documentation",
    "name": "ApiDoc",
    "group": "ApiDoc",
    "version": "0.0.0",
    "filename": "/home/muzgash/Projects/colav/repos/sds-backend/sds/plugins/ApiDoc.py",
    "groupTitle": "ApiDoc",
    "sampleRequest": [
      {
        "url": "http://127.0.1.1:8080/apidoc/update"
      }
    ]
  },
  {
    "type": "get",
    "url": "/app/documents",
    "title": "Document",
    "name": "app",
    "group": "CoLav_app",
    "description": "<p>Responds with information about the document</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "apikey",
            "description": "<p>Credential for authentication</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "data",
            "description": "<p>(info,networks) Whether is the general information or the production</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "id",
            "description": "<p>The mongodb id of the document requested</p>"
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Error 401": [
          {
            "group": "Error 401",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 401 Unauthorized invalid authentication apikey for the target resource.</p>"
          }
        ],
        "Error 204": [
          {
            "group": "Error 204",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 204 No Content.</p>"
          }
        ],
        "Error 200": [
          {
            "group": "Error 200",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 200 OK.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response (data=info):",
          "content": "{\n    \"id\": \"602ef785728ecc2d8e62d4ed\",\n    \"title\": \"Histology of the Reticuloendothelial System of the Spleen in Mice of Inbred Strains\",\n    \"abstract\": \"The histologic structure of the reticuloendothelial system of the spleen of mice of inbred strains was studied with a silver impregnation technique. The reticuloendothelial cells in the spleen form a general pattern common to all strains of mice examined. A central structure is formed by parallel rows of fibers and reticuloendothelial cells disposed around the follicular artery. Distributed throughout the follicle are scattered reticuloendothelial cells. At the periphery of the follicle the reticuloendothelial cells form a collar surrounding it. In the space between the collar and the red pulp is an area filled with sinusoids and a few reticuloendothelial cells. This space stains lightly with silver, appearing as a halo around the follicles. In the red pulp, the reticuloendothelial cells do not form geometric patterns as they do in the follicles. The morphological structure and arrangement of the reticuloendothelium are characteristic for each strain of inbred mice examined. The differences by which the strains are distinguished depend on the pattern of the reticuloendothelium in the splenic follicles. No quantitative difference was detected and the number of cells appeared to be roughly equivalent in all strains. Susceptibility to spontaneous tumor development could not be correlated with the structural differences found, though in strains highly susceptible to the development of leukemia the germinal centers of the splenic follicles were prominent, and their reticuloendothelial cells were abundant and large. © 1965, Oxford University Press.\",\n    \"source\": {\n        \"name\": \"Journal of the National Cancer Institute\",\n        \"serials\": {\n        \"unknown\": \"00278874\",\n        \"eissn\": \"14602105\"\n        }\n    },\n    \"year_published\": 1965,\n    \"language\": \"en\",\n    \"volume\": \"35\",\n    \"issue\": \"1\",\n    \"authors\": [\n        {\n        \"corresponding\": true,\n        \"name\": \"Oscar Duque\",\n        \"id\": \"602ef785728ecc2d8e62d4ec\",\n        \"affiliations\": [\n            {\n            \"name\": \"University of Antioquia\",\n            \"id\": \"60120afa4749273de6161883\"\n            },\n            {\n            \"name\": \"United States\",\n            \"id\": \"602ef785728ecc2d8e62d4eb\"\n            }\n        ]\n        }\n    ],\n    \"open_access_status\": \"closed\",\n    \"citations_count\": 5,\n    \"external_ids\": [\n        {\n        \"source\": \"lens\",\n        \"id\": \"146-769-885-695-441\"\n        },\n        {\n        \"source\": \"doi\",\n        \"id\": \"10.1093/jnci/35.1.15\"\n        },\n        {\n        \"source\": \"magid\",\n        \"id\": \"2142043866\"\n        },\n        {\n        \"source\": \"pmid\",\n        \"id\": \"5317934\"\n        },\n        {\n        \"source\": \"scopus\",\n        \"id\": \"2-s2.0-76549138821\"\n        },\n        {\n        \"source\": \"scholar\",\n        \"id\": \"GeY3wqc1_DgJ\"\n        }\n    ],\n    \"external_urls\": [\n        {\n        \"source\": \"scopus\",\n        \"url\": \"https://www.scopus.com/inward/record.uri?eid=2-s2.0-76549138821&doi=10.1093%2fjnci%2f35.1.15&partnerID=40&md5=fb4eec8a2f93b23a82746c827556f6d7\"\n        }\n    ]\n    }",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "/home/muzgash/Projects/colav/repos/sds-backend/sds/plugins/DocumentsApp.py",
    "groupTitle": "CoLav_app",
    "sampleRequest": [
      {
        "url": "http://127.0.1.1:8080/app/documents"
      }
    ]
  },
  {
    "type": "get",
    "url": "/app/groups",
    "title": "Groups",
    "name": "app",
    "group": "CoLav_app",
    "description": "<p>Responds with information about a group</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "apikey",
            "description": "<p>Credential for authentication</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "data",
            "description": "<p>(info,production) Whether is the general information or the production</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "id",
            "description": "<p>The mongodb id of the group requested</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "start_year",
            "description": "<p>Retrieves result starting on this year</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "end_year",
            "description": "<p>Retrieves results up to this year</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "max",
            "description": "<p>Maximum results per page</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "page",
            "description": "<p>Number of the page</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "sort",
            "description": "<p>(citations,year) Sorts the results by key in descending order</p>"
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Error 401": [
          {
            "group": "Error 401",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 401 Unauthorized invalid authentication apikey for the target resource.</p>"
          }
        ],
        "Error 204": [
          {
            "group": "Error 204",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 204 No Content.</p>"
          }
        ],
        "Error 200": [
          {
            "group": "Error 200",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 200 OK.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response (data=info):",
          "content": "HTTP/1.1 200 OK\n{\n    \"id\": \"602c50d1fd74967db0663833\",\n    \"name\": \"Facultad de ciencias exactas y naturales\",\n    \"type\": \"faculty\",\n    \"external_urls\": [\n        {\n        \"source\": \"website\",\n        \"url\": \"http://www.udea.edu.co/wps/portal/udea/web/inicio/unidades-academicas/ciencias-exactas-naturales\"\n        }\n    ],\n    \"departments\": [\n        {\n        \"id\": \"602c50f9fd74967db0663858\",\n        \"name\": \"Instituto de matemáticas\"\n        }\n    ],\n    \"groups\": [\n        {\n        \"id\": \"602c510ffd74967db06639a7\",\n        \"name\": \"Modelación con ecuaciones diferenciales\"\n        },\n        {\n        \"id\": \"602c510ffd74967db06639ad\",\n        \"name\": \"álgebra u de a\"\n        }\n    ],\n    \"authors\": [\n        {\n        \"full_name\": \"Roberto Cruz Rodes\",\n        \"id\": \"5fc5a419b246cc0887190a64\"\n        },\n        {\n        \"full_name\": \"Jairo Eloy Castellanos Ramos\",\n        \"id\": \"5fc5a4b7b246cc0887190a65\"\n        }\n    ],\n    \"institution\": [\n        {\n        \"name\": \"University of Antioquia\",\n        \"id\": \"60120afa4749273de6161883\"\n        }\n    ]\n    }",
          "type": "json"
        },
        {
          "title": "Success-Response (data=production):",
          "content": "HTTP/1.1 200 OK\n{\n    \"data\": [\n        {\n        \"_id\": \"602ef9dd728ecc2d8e62e030\",\n        \"title\": \"Comments on the Riemann conjecture and index theory on Cantorian fractal space-time\",\n        \"source\": {\n            \"name\": \"Chaos Solitons & Fractals\",\n            \"_id\": \"602ef9dd728ecc2d8e62e02d\"\n        },\n        \"authors\": [\n            {\n            \"full_name\": \"Carlos Castro\",\n            \"_id\": \"602ef9dd728ecc2d8e62e02f\",\n            \"affiliations\": [\n                {\n                \"name\": \"Center for Theoretical Studies, University of Miami\",\n                \"_id\": \"602ef9dd728ecc2d8e62e02e\",\n                \"branches\": []\n                }\n            ]\n            },\n            {\n            \"full_name\": \"Jorge Eduardo Mahecha Gomez\",\n            \"_id\": \"5fc65863b246cc0887190a9f\",\n            \"affiliations\": [\n                {\n                \"name\": \"University of Antioquia\",\n                \"_id\": \"60120afa4749273de6161883\",\n                \"branches\": [\n                    {\n                    \"name\": \"Facultad de ciencias exactas y naturales\",\n                    \"type\": \"faculty\",\n                    \"_id\": \"602c50d1fd74967db0663833\"\n                    },\n                    {\n                    \"name\": \"Instituto de física\",\n                    \"type\": \"department\",\n                    \"_id\": \"602c50f9fd74967db0663859\"\n                    },\n                    {\n                    \"name\": \"Grupo de física atómica y molecular\",\n                    \"type\": \"group\",\n                    \"_id\": \"602c510ffd74967db06638fb\"\n                    }\n                ]\n                }\n            ]\n            }\n        ]\n        }\n    ],\n    \"count\": 3,\n    \"page\": 1,\n    \"total_results\": 3,\n    \"initial_year\": 2002,\n    \"final_year\": 2014,\n    \"open_access\": {\n        \"green\": 2,\n        \"gold\": 0,\n        \"bronze\": 1,\n        \"closed\": 0,\n        \"hybrid\": 0\n    },\n    \"venn_source\": {\n        \"scholar\": 0,\n        \"lens\": 0,\n        \"oadoi\": 0,\n        \"wos\": 0,\n        \"scopus\": 0,\n        \"lens_wos_scholar_scopus\": 3\n    }\n    }",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "/home/muzgash/Projects/colav/repos/sds-backend/sds/plugins/GroupsApp.py",
    "groupTitle": "CoLav_app",
    "sampleRequest": [
      {
        "url": "http://127.0.1.1:8080/app/groups"
      }
    ]
  },
  {
    "type": "get",
    "url": "/app/institutions",
    "title": "Institutions",
    "name": "app",
    "group": "CoLav_app",
    "description": "<p>Responds with information about the institutions</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "apikey",
            "description": "<p>Credential for authentication</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "data",
            "description": "<p>(info,production) Whether is the general information or the production</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "id",
            "description": "<p>The mongodb id of the institution requested</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "start_year",
            "description": "<p>Retrieves result starting on this year</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "end_year",
            "description": "<p>Retrieves results up to this year</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "max",
            "description": "<p>Maximum results per page</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "page",
            "description": "<p>Number of the page</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "sort",
            "description": "<p>(citations,year) Sorts the results by key in descending order</p>"
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Error 401": [
          {
            "group": "Error 401",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 401 Unauthorized invalid authentication apikey for the target resource.</p>"
          }
        ],
        "Error 204": [
          {
            "group": "Error 204",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 204 No Content.</p>"
          }
        ],
        "Error 200": [
          {
            "group": "Error 200",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 200 OK.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response (data=info):",
          "content": "{\n    \"id\": \"60120afa4749273de6161883\",\n    \"name\": \"University of Antioquia\",\n    \"external_urls\": [\n        {\n        \"source\": \"wikipedia\",\n        \"url\": \"http://en.wikipedia.org/wiki/University_of_Antioquia\"\n        },\n        {\n        \"source\": \"site\",\n        \"url\": \"http://www.udea.edu.co/portal/page/portal/EnglishPortal/EnglishPortal\"\n        }\n    ],\n    \"departments\": [\n        {\n        \"name\": \"Departamento de artes visuales\",\n        \"id\": \"602c50f9fd74967db0663854\"\n        },\n        {\n        \"name\": \"Departamento de música\",\n        \"id\": \"602c50f9fd74967db0663855\"\n        },\n        {\n        \"name\": \"Departamento de teatro\",\n        \"id\": \"602c50f9fd74967db0663856\"\n        },\n        {\n        \"name\": \"Decanatura facultad de artes\",\n        \"id\": \"602c50f9fd74967db0663857\"\n        },\n        {\n        \"name\": \"Instituto de matemáticas\",\n        \"id\": \"602c50f9fd74967db0663858\"\n        },\n        {\n        \"name\": \"Instituto de física\",\n        \"id\": \"602c50f9fd74967db0663859\"\n        },\n        {\n        \"name\": \"Instituto de biología\",\n        \"id\": \"602c50f9fd74967db066385a\"\n        },\n        {\n        \"name\": \"Instituto de química\",\n        \"id\": \"602c50f9fd74967db066385b\"\n        },\n        {\n        \"name\": \"Departamento de bioquímica\",\n        \"id\": \"602c50f9fd74967db0663891\"\n        },\n        {\n        \"name\": \"Departamento de farmacología y toxicología\",\n        \"id\": \"602c50f9fd74967db0663892\"\n        },\n        {\n        \"name\": \"Departamento de patología\",\n        \"id\": \"602c50f9fd74967db0663893\"\n        },\n        {\n        \"name\": \"Departamento de microbiología y parasitología\",\n        \"id\": \"602c50f9fd74967db0663894\"\n        },\n        {\n        \"name\": \"Departamento de medicina interna\",\n        \"id\": \"602c50f9fd74967db0663895\"\n        },\n        {\n        \"name\": \"Departamento de cirugía\",\n        \"id\": \"602c50f9fd74967db0663896\"\n        }\n    ],\n    \"faculties\": [\n        {\n        \"name\": \"Facultad de artes\",\n        \"id\": \"602c50d1fd74967db0663830\"\n        },\n        {\n        \"name\": \"Facultad de ciencias agrarias\",\n        \"id\": \"602c50d1fd74967db0663831\"\n        },\n        {\n        \"name\": \"Facultad de ciencias económicas\",\n        \"id\": \"602c50d1fd74967db0663832\"\n        },\n        {\n        \"name\": \"Facultad de ciencias exactas y naturales\",\n        \"id\": \"602c50d1fd74967db0663833\"\n        },\n        {\n        \"name\": \"Facultad de ciencias farmacéuticas y alimentarias\",\n        \"id\": \"602c50d1fd74967db0663834\"\n        },\n        {\n        \"name\": \"Facultad de ciencias sociales y humanas\",\n        \"id\": \"602c50d1fd74967db0663835\"\n        },\n        {\n        \"name\": \"Facultad de comunicaciones y filología\",\n        \"id\": \"602c50d1fd74967db0663836\"\n        },\n        {\n        \"name\": \"Facultad de derecho y ciencias políticas\",\n        \"id\": \"602c50d1fd74967db0663837\"\n        },\n        {\n        \"name\": \"Facultad de educación\",\n        \"id\": \"602c50d1fd74967db0663838\"\n        },\n        {\n        \"name\": \"Facultad de enfermería\",\n        \"id\": \"602c50d1fd74967db0663839\"\n        },\n        {\n        \"name\": \"Facultad de ingeniería\",\n        \"id\": \"602c50d1fd74967db066383a\"\n        },\n        {\n        \"name\": \"Facultad de medicina\",\n        \"id\": \"602c50d1fd74967db066383b\"\n        },\n        {\n        \"name\": \"Facultad de odontología\",\n        \"id\": \"602c50d1fd74967db066383c\"\n        },\n        {\n        \"name\": \"Facultad de salud pública\",\n        \"id\": \"602c50d1fd74967db066383d\"\n        },\n        {\n        \"name\": \"Escuela de idiomas\",\n        \"id\": \"602c50d1fd74967db066383e\"\n        },\n        {\n        \"name\": \"Escuela interamericana de bibliotecología\",\n        \"id\": \"602c50d1fd74967db066383f\"\n        },\n        {\n        \"name\": \"Escuela de microbiología\",\n        \"id\": \"602c50d1fd74967db0663840\"\n        },\n        {\n        \"name\": \"Escuela de nutrición y dietética\",\n        \"id\": \"602c50d1fd74967db0663841\"\n        },\n        {\n        \"name\": \"Instituto de filosofía\",\n        \"id\": \"602c50d1fd74967db0663842\"\n        },\n        {\n        \"name\": \"Instituto universitario de educación física y deporte\",\n        \"id\": \"602c50d1fd74967db0663843\"\n        },\n        {\n        \"name\": \"Instituto de estudios políticos\",\n        \"id\": \"602c50d1fd74967db0663844\"\n        },\n        {\n        \"name\": \"Instituto de estudios regionales\",\n        \"id\": \"602c50d1fd74967db0663845\"\n        },\n        {\n        \"name\": \"Corporación académica ambiental\",\n        \"id\": \"602c50d1fd74967db0663846\"\n        },\n        {\n        \"name\": \"Corporación académica ciencias básicas biomédicas\",\n        \"id\": \"602c50d1fd74967db0663847\"\n        },\n        {\n        \"name\": \"Corporación académica para el estudio de patologías tropicales\",\n        \"id\": \"602c50d1fd74967db0663848\"\n        }\n    ],\n    \"area_groups\": [],\n    \"logo\": \"\"\n}",
          "type": "json"
        },
        {
          "title": "Success-Response (data=production):",
          "content": "{\n    \"data\": [\n        {\n        \"_id\": \"602ef788728ecc2d8e62d4f1\",\n        \"title\": \"Product and quotient of correlated beta variables\",\n        \"source\": {\n            \"name\": \"Applied Mathematics Letters\",\n            \"_id\": \"602ef788728ecc2d8e62d4ef\"\n        },\n        \"authors\": [\n            {\n            \"full_name\": \"Daya Krishna Nagar\",\n            \"_id\": \"5fc5b0a5b246cc0887190a69\",\n            \"affiliations\": [\n                {\n                \"name\": \"University of Antioquia\",\n                \"_id\": \"60120afa4749273de6161883\",\n                \"branches\": [\n                    {\n                    \"name\": \"Facultad de ciencias exactas y naturales\",\n                    \"type\": \"faculty\",\n                    \"_id\": \"602c50d1fd74967db0663833\"\n                    },\n                    {\n                    \"name\": \"Instituto de matemáticas\",\n                    \"type\": \"department\",\n                    \"_id\": \"602c50f9fd74967db0663858\"\n                    },\n                    {\n                    \"name\": \"Análisis multivariado\",\n                    \"type\": \"group\",\n                    \"_id\": \"602c510ffd74967db06638d6\"\n                    }\n                ]\n                }\n            ]\n            },\n            {\n            \"full_name\": \"Johanna Marcela Orozco Castañeda\",\n            \"_id\": \"5fc5bebab246cc0887190a70\",\n            \"affiliations\": [\n                {uest.args.get('start_year')\nend_year=self.request.args.get('end_year')\ncoauthors=self.get_\n                \"name\": \"University of Antioquia\",\n                \"_id\": \"60120afa4749273de6161883\",\n                \"branches\": [\n                    {\n                    \"name\": \"Facultad de ciencias exactas y naturales\",\n                    \"type\": \"faculty\",\n                    \"_id\": \"602c50d1fd74967db0663833\"\n                    },\n                    {\n                    \"name\": \"Instituto de matemáticas\",\n                    \"type\": \"department\",\n                    \"_id\": \"602c50f9fd74967db0663858\"\n                    }\n                ]\n                }\n            ]\n            },\n            {\n            \"full_name\": \"Daya Krishna Nagar\",\n            \"_id\": \"5fc5b0a5b246cc0887190a69\",\n            \"affiliations\": [\n                {\n                \"name\": \"Bowling Green State University\",\n                \"_id\": \"60120add4749273de616099f\",\n                \"branches\": []\n                },\n                {\n                \"name\": \"Univ Antioquia\",\n                \"_id\": \"602ef788728ecc2d8e62d4f0\",\n                \"branches\": []\n                }\n            ]\n            }\n        ]\n        }\n    ],\n    \"count\": 73,\n    \"page\": 1,\n    \"total_results\": 73,\n    \"initial_year\": 1995,\n    \"final_year\": 2017,\n    \"open_access\": {\n        \"green\": 9,\n        \"gold\": 17,\n        \"bronze\": 6,\n        \"closed\": 39,\n        \"hybrid\": 2\n    },\n    \"venn_source\": {\n        \"scholar\": 0,\n        \"lens\": 0,\n        \"oadoi\": 0,\n        \"wos\": 0,\n        \"scopus\": 0,\n        \"lens_wos_scholar_scopus\": 55,\n        \"lens_scholar\": 6,\n        \"lens_scholar_scopus\": 6,\n        \"lens_wos_scholar\": 6\n    }\n}",
          "type": "json"
        },
        {
          "title": "Success-Response (data=citations):",
          "content": "HTTP/1.1 200 OK\n{\n    \"data\": {\n        \"citations\": 1815,\n        \"H5\": 8,\n        \"yearly_citations\": {\n        \"2008\": 10,\n        \"2009\": 137,\n        \"2010\": 240,\n        \"2011\": 11,\n        \"2012\": 46,\n        \"2013\": 67,\n        \"2014\": 88,\n        \"2015\": 166,\n        \"2016\": 66,\n        \"2017\": 87,\n        \"2018\": 35,\n        \"2019\": 4,\n        \"2020\": 4\n        },\n        \"network\": {}\n    },\n    \"filters\": {\n        \"initial_year\": 1995,\n        \"final_year\": 2020\n    }\n}",
          "type": "json"
        },
        {
          "title": "Success-Response (data=apc):",
          "content": "HTTP/1.1 200 OK\n{\n    \"data\": {\n        \"yearly\": {\n        \"2006\": 25333.215809352663,\n        \"2007\": 31212.916051395667,\n        \"2008\": 55634.25857670785,\n        \"2009\": 54698.475858931975,\n        \"2010\": 47683.47371715034,\n        \"2011\": 84837.57770613344,\n        \"2012\": 87631.29377989819,\n        \"2013\": 106924.28252286707,\n        \"2014\": 171037.16532375227,\n        \"2015\": 159642.93025535543,\n        \"2016\": 220892.6144583558,\n        \"2017\": 246995.35012787356,\n        \"2018\": 301777.0124037427,\n        \"2019\": 346262.03413552087,\n        \"2020\": 154102.28675748224\n        },\n        \"faculty\": {\n        \"602c50d1fd74967db066383b\": {\n            \"name\": \"Facultad de Medicina\",\n            \"value\": 688505.4513403034\n        },\n        \"602c50d1fd74967db066383a\": {\n            \"name\": \"Facultad de Ingeniería\",\n            \"value\": 175085.68733245516\n        },\n        \"602c50d1fd74967db0663833\": {\n            \"name\": \"Facultad de Ciencias Exactas y Naturales\",\n            \"value\": 380902.37390428863\n        },\n        \"602c50d1fd74967db0663831\": {\n            \"name\": \"Facultad de Ciencias Agrarias\",\n            \"value\": 89374.5371867811\n        },\n        \"602c50d1fd74967db0663835\": {\n            \"name\": \"Facultad de Ciencias Sociales y Humanas\",\n            \"value\": 2237.28\n        }\n        },\n        \"department\": {\n        \"602c50f9fd74967db0663895\": {\n            \"name\": \"Departamento de Medicina Interna\",\n            \"value\": 69074.85558893369\n        },\n        \"602c50f9fd74967db0663883\": {\n            \"name\": \"Departamento de Ingeniería Industrial\",\n            \"value\": 2317.4396001110804\n        },\n        \"602c50f9fd74967db066385a\": {\n            \"name\": \"Instituto de Biología\",\n            \"value\": 182704.58261736613\n        },\n        \"602c50f9fd74967db0663893\": {\n            \"name\": \"Departamento de Patología\",\n            \"value\": 3711.3056\n        },\n        \"602c50f9fd74967db066389c\": {\n            \"name\": \"Departamento de Medicina Física y Rehabilitación\",\n            \"value\": 1890.3011862842297\n        },\n        \"602c50f9fd74967db066385f\": {\n            \"name\": \"Departamento de Antropología\",\n            \"value\": 300\n        }\n        },\n        \"group\": {\n        \"602c510ffd74967db0663947\": {\n            \"name\": \"Grupo Académico de Epidemiología Clínica\",\n            \"value\": 23510.433610132986\n        },\n        \"602c510ffd74967db06638d9\": {\n            \"name\": \"Centro de Investigaciones Básicas y Aplicadas en Veterinaria\",\n            \"value\": 12869.809579159686\n        },\n        \"602c510ffd74967db06639d0\": {\n            \"name\": \"Grupo de Química-Física Teórica\",\n            \"value\": 6156.785263507203\n        },\n        \"609cbe1f2ecb2ac1eee78eb1\": {\n            \"name\": \"Grupo de Entomología Médica\",\n            \"value\": 13696.310458738084\n        },\n        \"602c510ffd74967db066390a\": {\n            \"name\": \"Inmunomodulación\",\n            \"value\": 6536.5592890863645\n        },\n        \"602c510ffd74967db0663919\": {\n            \"name\": \"Grupo de Investigación en Psicologia Cognitiva\",\n            \"value\": 1937.2800000000002\n        },\n        \"602c510ffd74967db06639dd\": {\n            \"name\": \"Ecología Lótica: Islas, Costas y Estuarios\",\n            \"value\": 3586.559289086365\n        },\n        \"602c510ffd74967db06639b1\": {\n            \"name\": \"Simulación, Diseño, Control y Optimización de Procesos\",\n            \"value\": 1793.2796445431825\n        },\n        \"602c510ffd74967db06639ff\": {\n            \"name\": \"Ciencia y Tecnología del Gas y Uso Racional de la Energía\",\n            \"value\": 750\n        },\n        \"602c510ffd74967db0663956\": {\n            \"name\": \"Grupo de Investigación en Gestión y Modelación Ambiental\",\n            \"value\": 4445\n        },\n        \"602c510ffd74967db0663990\": {\n            \"name\": \"Grupo Mapeo Genético\",\n            \"value\": 376.97849989280576\n        },\n        \"602c510ffd74967db0663a16\": {\n            \"name\": \"No lo encontre\",\n            \"value\": 3100\n        },\n        \"602c510ffd74967db0663970\": {\n            \"name\": \"Patología Renal y de Trasplantes\",\n            \"value\": 2825\n        },\n        \"602c510ffd74967db06639e9\": {\n            \"name\": \"Aerospace Science and Technology ReseArch\",\n            \"value\": 2792.4396001110804\n        },\n        \"602c510ffd74967db0663917\": {\n            \"name\": \"Grupo de Investigacion en Farmacologia y Toxicologia \\\" INFARTO\\\"\",\n            \"value\": 5146.58644148918\n        },\n        \"602c510ffd74967db06638d6\": {\n            \"name\": \"Análisis Multivariado\",\n            \"value\": 975\n        },\n        \"602c510ffd74967db066398b\": {\n            \"name\": \"Genética Médica\",\n            \"value\": 2090.3011862842295\n        },\n        \"602c510ffd74967db0663948\": {\n            \"name\": \"Grupo de Coloides\",\n            \"value\": 1025\n        },\n        \"602c510ffd74967db06638f3\": {\n            \"name\": \"Grupo de Biofísica\",\n            \"value\": 3318.3070664250795\n        },\n        \"602c510ffd74967db0663909\": {\n            \"name\": \"Diagnóstico y Control de la Contaminación\",\n            \"value\": 3500\n        },\n        \"602c510ffd74967db06639fd\": {\n            \"name\": \"Grupo de Investigación y Gestión sobre Patrimonio\",\n            \"value\": 200\n        }\n        },\n        \"publisher\": {\n        \"Hindawi Limited\": 81695,\n        \"BMC\": 352120.33776623,\n        \"Asociación Colombiana de Infectología\": 7600,\n        \"MDPI AG\": 336352.0133296308,\n        \"Public Library of Science (PLoS)\": 259525,\n        \"Frontiers Media S.A.\": 235850,\n        \"Nature Publishing Group\": 90946.40866978905,\n        \"Colégio Brasileiro de Cirurgiões\": 185.4154543505559,\n        \"The Association for Research in Vision and Ophthalmology\": 31450,\n        \"Elsevier\": 203307.67999999988,\n        \"Cambridge University Press\": 25278.385141020815,\n        \"The Journal of Infection in Developing Countries\": 3102.0696,\n        \"Arán Ediciones, S. L.\": 19614.96000000001,\n        \"Fundação de Amparo à Pesquisa do Estado de SP\": 1600,\n        \"BMJ Publishing Group\": 48223.376978564826,\n        \"Wiley\": 53579,\n        \"American Chemical Society\": 1500,\n        \"F1000 Research Ltd\": 5000,\n        \"Universidad de Antioquia\": 98100,\n        \"Universidade de São Paulo\": 8457.478178310004,\n        \"Sociedade Brasileira de Química\": 4069.671679274754,\n        \"Pharmacotherapy Group, University of Benin, Benin City\": 2000,\n        \"American Society for Microbiology\": 14400,\n        \"Association of Support to Oral Health Research (APESB)\": 390,\n        \"Instituto de Investigaciones Agropecuarias, INIA\": 650,\n        \"Tehran University of Medical Sciences\": 0,\n        \"Wolters Kluwer Medknow Publications\": 500,\n        \"Oxford University Press\": 21739.34566339612,\n        \"Fundación Revista Medicina\": 0,\n        \"Iranian Medicinal Plants Society\": 215,\n        \"Universidad Autónoma de Yucatán\": 400,\n        \"Fundação Odontológica de Ribeirão Preto\": 101.97849989280574,\n        \"Facultad de Ciencias Agrarias. Universidad Nacional de Cuyo\": 300,\n        \"Exeley Inc.\": 500\n        },\n        \"openaccess\": {\n        \"gold\": 1723132.3620811182,\n        \"closed\": 67762.23068810394,\n        \"bronze\": 52978.00656463765,\n        \"green\": 34771.15632984965,\n        \"hybrid\": 48339.07216847288\n        }\n    },\n    \"filters\": {\n        \"start_year\": 1925,\n        \"end_year\": 2020\n    }\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "/home/muzgash/Projects/colav/repos/sds-backend/sds/plugins/InstitutionsApp.py",
    "groupTitle": "CoLav_app",
    "sampleRequest": [
      {
        "url": "http://127.0.1.1:8080/app/institutions"
      }
    ]
  },
  {
    "type": "get",
    "url": "/app/search",
    "title": "Search",
    "name": "app",
    "group": "CoLav_app",
    "description": "<p>Requests search of different entities in the CoLav database</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "data",
            "description": "<p>Specifies the type of entity (or list of entities) to return, namely paper, institution, faculty, department, author</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "affiliation",
            "description": "<p>The mongo if of the related affiliation of the entity to return</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "apikey",
            "description": "<p>Credential for authentication</p>"
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Error 401": [
          {
            "group": "Error 401",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 401 Unauthorized invalid authentication apikey for the target resource.</p>"
          }
        ],
        "Error 204": [
          {
            "group": "Error 204",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 204 No Content.</p>"
          }
        ],
        "Error 200": [
          {
            "group": "Error 200",
            "optional": false,
            "field": "msg",
            "description": "<p>The HTTP 200 OK.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response (data=faculties):",
          "content": "[\n    {\n        \"name\": \"Facultad de artes\",\n        \"id\": \"602c50d1fd74967db0663830\",\n        \"abbreviations\": [],\n        \"external_urls\": [\n        {\n            \"source\": \"website\",\n            \"url\": \"http://www.udea.edu.co/wps/portal/udea/web/inicio/institucional/unidades-academicas/facultades/artes\"\n        }\n        ]\n    },\n    {\n        \"name\": \"Facultad de ciencias agrarias\",\n        \"id\": \"602c50d1fd74967db0663831\",\n        \"abbreviations\": [],\n        \"external_urls\": [\n        {\n            \"source\": \"website\",\n            \"url\": \"http://www.udea.edu.co/wps/portal/udea/web/inicio/unidades-academicas/ciencias-agrarias\"\n        }\n        ]\n    },\n    {\n        \"name\": \"Facultad de ciencias económicas\",\n        \"id\": \"602c50d1fd74967db0663832\",\n        \"abbreviations\": [\n        \"FCE\"\n        ],\n        \"external_urls\": [\n        {\n            \"source\": \"website\",\n            \"url\": \"http://www.udea.edu.co/wps/portal/udea/web/inicio/institucional/unidades-academicas/facultades/ciencias-economicas\"\n        }\n        ]\n    },\n    {\n        \"name\": \"Facultad de ciencias exactas y naturales\",\n        \"id\": \"602c50d1fd74967db0663833\",\n        \"abbreviations\": [\n        \"FCEN\"\n        ],\n        \"external_urls\": [\n        {\n            \"source\": \"website\",\n            \"url\": \"http://www.udea.edu.co/wps/portal/udea/web/inicio/unidades-academicas/ciencias-exactas-naturales\"\n        }\n        ]\n    }\n]",
          "type": "json"
        },
        {
          "title": "Success-Response (data=authors):",
          "content": "{\n    \"data\": [\n        {\n        \"id\": \"5fc59becb246cc0887190a5c\",\n        \"full_name\": \"Johann Hasler Perez\",\n        \"affiliation\": {\n            \"id\": \"60120afa4749273de6161883\",\n            \"name\": \"University of Antioquia\"\n        },\n        \"keywords\": [\n            \"elliptical orbits\",\n            \"history of ideas\",\n            \"history of science\",\n            \"johannes kepler\",\n            \"music of the spheres\",\n            \"planetary music\",\n            \"speculative music\",\n            \"alchemical meditation\",\n            \"atalanta fugiens\",\n            \"early multimedia\",\n            \"emblem books\",\n            \"historical instances of performance\",\n            \"michael maier\"\n        ]\n        },\n        {\n        \"id\": \"5fc59d6bb246cc0887190a5d\",\n        \"full_name\": \"Carolina Santamaria Delgado\",\n        \"affiliation\": {\n            \"id\": \"60120afa4749273de6161883\",\n            \"name\": \"University of Antioquia\"\n        },\n        \"keywords\": [\n            \"art in the university\",\n            \"artist-professor\",\n            \"intellectual production\",\n            \"music as an academic field\",\n            \"research-creation\",\n            \"the world of art\"\n        ]\n        }\n    ],\n    \"filters\": {\n        \"affiliations\": [\n        {\n            \"id\": \"60120afa4749273de6161883\",\n            \"name\": \"University of Antioquia\"\n        }\n        ],\n        \"keywords\": [],\n        \"countries\": [\n        \"CO\"\n        ]\n    },\n    \"count\": 2,\n    \"page\": 2,\n    \"total_results\": 565\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "/home/muzgash/Projects/colav/repos/sds-backend/sds/plugins/SearchApp.py",
    "groupTitle": "CoLav_app",
    "sampleRequest": [
      {
        "url": "http://127.0.1.1:8080/app/search"
      }
    ]
  }
] });
