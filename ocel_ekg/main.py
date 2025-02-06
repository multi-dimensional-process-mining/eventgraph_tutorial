# Import OCEL2 logs in .csv format into EKG#

import os

# path where input file is located
#
# IMPORTANT: by default Neo4j does not allow importing data from arbitrary local URLs, e.g., this directoy
# to allow Neo4j importing a file from this directoy:
#
# 1. Find the neo4j.conf file for your Neo4j installation. See https://neo4j.com/docs/operations-manual/current/configuration/file-locations/
#    If you are using Neo4j Desktop, this is located under <yourGraph> > Manage > Settings (you have to stop the DB instance first)
# 2. Comment out this line (by adding # at the start of the line):
#         server.directories.import=import
# 3. Uncomment this line to allow CSV import from file URL:
#         #dbms.security.allow_csv_import_from_file_urls=true
# 4. Restart Neo4j
#
inputPath = './data/'
inputFile = '1_running-example.jsonocel.zip'

from neo4j import GraphDatabase

# connection to Neo4J database
# the queries in this file make use of the APOC library, make sure to have the APOC plugin installed for this DB instance
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12341234"))

from ocel2_import import OcelImport

oi = OcelImport(driver)
oi.readJsonOcel(inputPath+inputFile)
oi.prepare_objects()
oi.prepare_events()

oi.import_objects()
oi.import_object_attributes()
oi.import_events()
oi.import_e2o_relation()
oi.materialize_last_object_state()