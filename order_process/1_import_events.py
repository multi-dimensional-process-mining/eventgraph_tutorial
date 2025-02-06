# Import events
#
# The script is generic for reading events from any table stored in a CSV file
# that has a 'timeestamp' column.
# The script is configured for the order_process example log file.

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
inputPath = './prepared_logs/'
inputFile = 'order_process_event_table_orderhandling_prepared.csv'
os_inputPath = os.path.realpath(inputPath+inputFile).replace('\\','/')

# Generic part for event import to Neo4j starts below

import csv, time
import pandas as pd
from neo4j import GraphDatabase

# connection to Neo4J database
# the queries in this file make use of the APOC library, make sure to have the APOC plugin installed for this DB instance
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12341234"))

# function to run the given query on the connected Neo4J database
def runQuery(driver, query):
    print('\n'+query)
    with driver.session() as session:
        result = session.run(query).single()
        if result != None: 
            return result.value()
        else:
            return None

# load log header (attribute names) from import file
def getLogHeader(fileName):
    with open(fileName) as f:
        reader = csv.reader(f)
        logHeader = list(next(reader))
        f.close()
    return logHeader


# Use Neo4j's bulk import from CSV to create on :event node per record in CSV file
# - 'fileName' is the system file path to the CSV file from which Neo4j will load
# - 'logHeader' the list of attribute names of the CSV file
# - an optional `LogID` to distinguish events coming from different event logs
def CreateEventQuery(fileName, logHeader, LogID = ""):
 
    # import each row of the CSV one by one, as variable 'line' 
    query = f'CALL {{LOAD CSV WITH HEADERS FROM \"file:///{fileName}\" as line'
    # per line create an :Event node
    query = query + f' CREATE (e:Event {{ '
    # subsequent lines specify how the attribute of event e are set (from "line')

    # if a LogID is given, set it as property of the event
    if LogID != "":
        query = query + f'Log: "{LogID}",'

    # for each colum in the header, set attribute 'column' of event e to the value line.column
    for col in logHeader:
        # allow type conversion by Neo4j during import
        if col in ['timestamp','start','end']:
            # tell Neo4j to typecast timestamp attributes to dateTime during import
            colValue = f'datetime(line.{col})'
        else:
            # every other attribute is just the value stored in the column in that line
            colValue = 'line.'+col

        # distinguish final event to close the CREATE query properly
        if (logHeader.index(col) < len(logHeader)-1):
            query = query + f' {col}: {colValue},'
        else:
            query = query + f' {col}: {colValue} }})'

    query = query + f'}} IN TRANSACTIONS'
    return query

####################################################
#### Step 1: delete existing DB contents and re-import from scratch, comment out the runQuery(...) commands if you want to keep the current DB
####################################################

#### Step 1.a) delete the existing database and ...
qCleanDatabase_allRelations = f'''
MATCH ()-[r]->() DELETE r''' 

qCleanDatabase_allNodes = f'''
MATCH (n) DELETE n'''

runQuery(driver, qCleanDatabase_allRelations) # delete all relationships, comment out if you want to keep them
runQuery(driver, qCleanDatabase_allNodes)     # delete all nodes, comment out if you want to keep them

#### Step 1.b) ... and re-import all events from scratch
print('\nImport events from CSV')
# load log header for import and post-processing
logHeader = getLogHeader(os_inputPath)
# create import query to convert each record in the input file into an event node (with all record attributes as event node properties)
qCreateEvents = CreateEventQuery(os_inputPath, logHeader, 'order_process')
runQuery(driver, qCreateEvents) # create event nodes, comment out if the DB already contains event nodes and you don't want to new ones/duplicates

#### Step 1.c) example of querying for the number of event nodes in the DB
q_countImportedEvents = "MATCH (e:Event) RETURN count(e)"
result = runQuery(driver, q_countImportedEvents) 
print (result)

#### Step 1.d) convert all values being strings of comma-separated values into actual lists of values

# retrieve the property keys of all event nodes in the graph and return them in a list
def qGetAllEventProperties(tx):
    q_getAllProperties = '''
        MATCH(e:Event) WITH DISTINCT keys(e) AS props
        UNWIND props AS prop WITH DISTINCT prop AS p
        RETURN p'''
    print(q_getAllProperties)

    # execute the query and obtain result as a structured record
    result = tx.run(q_getAllProperties)
    allProperties = []
    # iterate over retrieved record
    for result in result:
        p = result['p'] # retrieve the actual value of 'p'
        print(p)  
        allProperties.append(p)
    return allProperties

# for any :Event node where property 'prop' has a comma-separate string as value, replace the string by the list of values
def qSplitPropertyStringsToList(tx, allProperties):
    for prop in allProperties:
        q_splitValue = f'''
            MATCH (e:Event) WHERE e.{prop} <> "null" AND e.{prop} CONTAINS ',' WITH e,split(e.{prop}, ',') AS vals
            SET e.{prop}=vals'''
        print(q_splitValue)
        tx.run(q_splitValue)


# execute both queries above: for each property key in the database, split the values (except for timestamps)
with driver.session() as session:
    allProperties = session.execute_read(qGetAllEventProperties)
    allProperties.remove("timestamp") # do not process the timestamp attribute
    session.execute_write(qSplitPropertyStringsToList, allProperties)