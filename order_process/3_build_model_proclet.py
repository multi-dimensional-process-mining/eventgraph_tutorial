# Build event knowledge graph for Order Process example

from neo4j import GraphDatabase

# connection to Neo4J database
# the queries in this file make use of the APOC library, make sure to have the APOC plugin installed for this DB instance
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# function to run the given query on the connected Neo4J database
def runQuery(driver, query):
    print('\n'+query)
    with driver.session() as session:
        result = session.run(query).single()
        if result != None: 
            return result.value()
        else:
            return None


qCleanDatabase_allClassNodes = f'''
MATCH (c:Class) DETACH DELETE c'''''

runQuery(driver, qCleanDatabase_allClassNodes) # delete all class nodes and attached relationships


### Build Proclet Model
### Step 1) Aggregate Events to Classes based on their Activity and EntityType, and count the frequency of each class

def q_aggregate_events_to_classes(tx):
    qEventToClass = f'''
        MATCH (e:Event)-[:CORR]->(n:Entity) WITH distinct e.Activity as actName,n.EntityType as EType
        MERGE ( c : Class {{ ID: actName+"_"+EType, Name:actName, EventType:actName, EntityType:EType, Type:"Activity,EntityType"}})
    '''
    print(qEventToClass)
    tx.run(qEventToClass)

def q_link_events_to_classes(tx):
    qObserve = f'''
        MATCH ( c : Class ) WHERE c.Type = "Activity,EntityType"
        MATCH (e:Event)-[:CORR]->(n:Entity) WHERE c.EventType = e.Activity AND c.EntityType=n.EntityType
        CREATE ( e ) -[:OBSERVED]-> ( c )'''
    print(qObserve)
    tx.run(qObserve)

def q_count_class_frequency(tx):
    qCountFrequency = f'''
        MATCH ( e : Event )-[:OBSERVED]->( c : Class ) 
        WITH c, count(e) AS freq 
        SET c.frequency = freq'''
    print(qCountFrequency)
    tx.run(qCountFrequency)


with driver.session() as session:
    session.execute_write(q_aggregate_events_to_classes)
    session.execute_write(q_link_events_to_classes)
    session.execute_write(q_count_class_frequency)

### Step 2) Aggregate Directly-Follows Relations from Events to Classes, i.e. create DF relations between classes if there are DF relations between the events that are observed by these classes.

def q_aggregate_directly_follows(tx):
    qAggregateDF = f'''
        MATCH ( c1 : Class ) <-[:OBSERVED]- ( e1 : Event ) -[df:DF]-> ( e2 : Event ) -[:OBSERVED]-> ( c2 : Class )
        MATCH (e1) -[:CORR] -> (n) <-[:CORR]- (e2)
        WHERE c1.Type = c2.Type AND n.EntityType = df.EntityType AND c1.EntityType=n.EntityType AND c2.EntityType=n.EntityType
        WITH n.EntityType as EType, c1, count(df) AS df_freq, c2
        MERGE ( c1 ) -[df_agg:DF_C {{EntityType:EType}}]-> ( c2 ) 
        ON CREATE SET df_agg.frequency=df_freq'''
    
    print(qAggregateDF)
    tx.run(qAggregateDF)

def q_count_start_frequqency(tx):
    qCountStartFrequency = f'''
        MATCH ( c : Class ) <-[:OBSERVED]- ( e : Event ) 
        WHERE NOT ( ()-[:DF {{EntityType:c.EntityType}}]->(e) )
        WITH c, count(e) AS start_freq
        SET c.StartCount = start_freq'''
    
    print(qCountStartFrequency)
    tx.run(qCountStartFrequency)

def q_count_end_frequqency(tx):
    qCountEndFrequency = f'''
        MATCH ( c : Class ) <-[:OBSERVED]- ( e : Event ) 
        WHERE NOT ( (e)-[:DF {{EntityType:c.EntityType}}]->() )
        WITH c, count(e) AS end_freq
        SET c.EndCount = end_freq'''
    
    print(qCountEndFrequency)
    tx.run(qCountEndFrequency)

with driver.session() as session:
    session.execute_write(q_aggregate_directly_follows)
    session.execute_write(q_count_start_frequqency)
    session.execute_write(q_count_end_frequqency)

### Step 3) Add Synchronization Edges between Class nodes of the same EventType for different EntityTypes

def q_add_synchronization_edges(tx):
    qAddSync = f'''
        MATCH ( c1 : Class ) , ( c2 : Class ) 
        WHERE c1.EventType = c2.EventType AND c1.EntityType <> c2.EntityType
        MERGE ( c1 ) -[:SYNC]-> ( c2 )'''
    
    print(qAddSync)
    tx.run(qAddSync)


with driver.session() as session:
    session.execute_write(q_add_synchronization_edges)