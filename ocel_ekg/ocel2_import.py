from zipfile import ZipFile
import json

import pandas as pd
import csv,os

from neo4j import Driver
from ocel2_import_queries import OcelImportQueryLibrary as ql


class OcelImport:
    def __init__(self, driver: Driver):
        self.driver = driver

    ocelData = dict()
    dataset_baseName = str()

    csv_objects : str
    csv_events : str
    csv_object_attributes : str
    csv_relations_e2o : str

    K_OBJECT_TYPES = "objectTypes"
    K_EVENT_TYPES = "eventTypes"
    K_OBJECTS = "objects"
    K_EVENTS = "events"

    K_ATTRIBUTES = "attributes"
    K_RELATIONSHIPS = "relationships"

    def readJsonOcel(self, dataset:str):
        # dataset is a file with 'jsconocel.zip' extension
        self.dataset_baseName = dataset[:-len(".jsonocel.zip")]

        # read zip
        with ZipFile(dataset, 'r') as zip:
            for jsonOcelFile in zip.namelist():
                print(f"Reading {jsonOcelFile}.")
                # get JSON file from ZIP
                with zip.open(jsonOcelFile) as jsonOcel:
                    # read JSON
                    data = jsonOcel.read()  
                    d = json.loads(data.decode("utf-8"))    
                    if isinstance(d, dict):
                        self.ocelData = d

    def import_object_types(self):
        for ot in self.ocelData[OcelImport.K_OBJECT_TYPES]:
            result = self.connection.exec_query(ql.q_import_object_type_node, **{"object_type_node":ot})
            print(f"Import {result} nodes.")

    def prepare_objects(self):
        o = self.ocelData[OcelImport.K_OBJECTS]

        # generate table for all objects: id and type
        data_o = pd.json_normalize(o)
        data_o = data_o[["id","type"]] 

        # generate table for all object attributes: id, attribute name, value, timestmap
        o_attr = [d for d in o if OcelImport.K_ATTRIBUTES in d.keys()] # first drop all records without attributes
        data_o_attr = pd.json_normalize(o_attr, OcelImport.K_ATTRIBUTES, ["id"])
        data_o_attr = data_o_attr[["id", "name", "value", "time"]]

        self.csv_objects = self.dataset_baseName+".ocel."+OcelImport.K_OBJECTS+".csv"
        print("Writing "+self.csv_objects)
        data_o.to_csv(self.csv_objects, index=False)

        self.csv_object_attributes = self.dataset_baseName+".ocel."+OcelImport.K_OBJECTS+"."+OcelImport.K_ATTRIBUTES+".csv"
        print("Writing "+self.csv_object_attributes)
        data_o_attr.to_csv(self.csv_object_attributes, index=False)

    def prepare_events(self):
        e = self.ocelData[OcelImport.K_EVENTS]

        # normalize evnts and build relationship table
        relationships = list()
        e_normalized = list()
        for ev in e:
            # the OCEL event stores attributes as a list of [ { "name":<attributeName>, "value":<actualValue>} ]
            # transalte into normalized event that stores attribute directly as key/value pair  
            ev_normalized = dict()
            ev_normalized["id"] = ev["id"]
            ev_normalized["type"] = ev["type"]
            ev_normalized["time"] = ev["time"]

            # translate [ { "name":<attributeName>, "value":<actualValue>} ] into <attributeName>:<actualValue>
            for attr in ev[OcelImport.K_ATTRIBUTES]:
                ev_normalized[attr["name"]] = attr["value"]
            # store each normalized event in a list for later serialization as table
            e_normalized.append(ev_normalized)

            # translate each relationship reference at the event into an actual triple
            # (eventId, objectId, qualifier)
            for rel in ev[OcelImport.K_RELATIONSHIPS]:
                rel_normalized = dict()
                rel_normalized["eventId"] = ev["id"]
                rel_normalized["objectId"] = rel["objectId"]
                rel_normalized["qualifier"] = rel["qualifier"]
                # store in list for later serialization as table
                relationships.append(rel_normalized)

        # generate table for all events: id, type, time, and its attributes
        data_e = pd.json_normalize(e_normalized)
        #print(data_e)

        # generate table for all relationships
        data_r = pd.json_normalize(relationships)
        #print(data_r)

        self.csv_events = self.dataset_baseName+".ocel."+OcelImport.K_EVENTS+".csv"
        print("Writing "+self.csv_events)
        data_e.to_csv(self.csv_events, index=False)

        self.csv_relations_e2o = self.dataset_baseName+".ocel."+OcelImport.K_RELATIONSHIPS+"."+OcelImport.K_EVENTS+"-"+OcelImport.K_OBJECTS+".csv"
        print("Writing "+self.csv_relations_e2o)
        data_r.to_csv(self.csv_relations_e2o, index=False)

    # execute a query
    def run_query(self, query: str):
        with self.driver.session() as session:
            result = session.run(query).single()
            if result != None: 
                return result.value()
            else:
                return None

    # load csv header (attribute names) from import file
    @staticmethod
    def get_csv_header(fileName):
        with open(fileName) as f:
            reader = csv.reader(f)
            logHeader = list(next(reader))
            f.close()
        return logHeader

    # create index on nodes with label 'node_label', for a specific attribute 'id'
    def create_index(self, nodel_label, id):
        index_query = ql.q_create_index(nodel_label, id)
        self.run_query(index_query)

    # import records from 'csv' file as nodes with label 'node_label'
    def import_nodes(self, csv, node_label):
        print("Import "+node_label+" from "+csv)
        
        # need full path to csv file for correct import query for neo4j
        full_path = os.path.realpath(csv)
        # need csv header to generate load query
        header = OcelImport.get_csv_header(csv)
        # generate query for loading nodes
        load_query = ql.q_load_csv_as_nodes(full_path, header, node_label)
        # run the query
        self.run_query(load_query)

    # import ocel2 events from prepared event table csv
    def ocel2_import_events(self):
        self.create_index("Event", "id")
        self.import_nodes(self.csv_events, "Event")

    # import ocel2 objects from prepared object table csv
    def ocel2_import_objects(self):
        self.create_index("Entity", "id")
        self.import_nodes(self.csv_objects, "Entity")

    # import ocel2 object attributes from prepared attribute table csv
    def ocel2_import_object_attributes(self):
        # import attribute nodes        
        self.import_nodes(self.csv_object_attributes, "EntityAttribute")
        # link attribute nodes to object nodes
        link_query = ql.q_link_node_to_node("Entity", "id", "HAS_ATTRIBUTE", "EntityAttribute", "id")
        self.run_query(link_query)

    # import ocel2 event-object relation from relation tabel csv
    def ocel2_import_e2o_relation(self):

        print("Import relation from "+self.csv_relations_e2o)

        # need full path to csv file for correct import query for neo4j
        full_path = os.path.realpath(self.csv_relations_e2o)
        # load the event-object relation csv as relation
        ### resolve 'eventId' to an 'Event' node with matching 'id'
        ### create CORR relation with type 'qualifier'
        ### resolve 'objectId' to an 'Entity' node with matching 'id' 
        load_query = ql.q_load_csv_as_relation(full_path, "eventId", "Event", "id", "qualifier", "CORR", "objectId", "Entity", "id")
        self.run_query(load_query)

    # ocel2 allows storing multiple values per object attribute
    # materialze last object state by translating the latest attribute values in node properties of the object node
    def ocel2_materialize_last_object_state(self):
        set_query = ql.q_ocel2_materialize_last_object_state()
        self.run_query(set_query)