# Build event knowledge graph for Order Process example

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


qCleanDatabase_allEntityNodes = f'''
MATCH (n:Entity) DETACH DELETE n'''

qCleanDatabase_allRelationsFromEvents = f'''
MATCH (:Event) -[r]-> () DELETE r'''

qCleanDatabase_allRelationsToEvents = f'''
MATCH () -[r]-> (:Event) DELETE r'''

runQuery(driver, qCleanDatabase_allEntityNodes) # delete all entity nodes and attached relationships
runQuery(driver, qCleanDatabase_allRelationsFromEvents) # delete all relations from/to events
runQuery(driver, qCleanDatabase_allRelationsToEvents) # delete all relations from/to events


### Build Event Knowledge Graph:
### Step 1) Infer Entitiy Nodes and Correlate Events to Entities

# specification of how the entity types are stored in the data, array has 3 fields
# 1 - name of Entity Type 
# 2 - attribute of Event nodes holding the entity identifiers (values)
# 3- an optional WHERE clause to only infert entity types from specifc events, left empty here
model_entities_from_attributes = [
            ["Order", "Order", ""],
            ["Supplier Order", "SupplierOrder", ""],
            ["Item", "Item", ""],
            ["Invoice", "Invoice", ""],
            ["Payment", "Payment", ""]
        ]  

def q_create_entity(tx, entity_type, attribute_holding_id, WHERE_event_property):
    qCreateEntity = f'''
            MATCH (e:Event) {WHERE_event_property}
            UNWIND e.{attribute_holding_id} AS id
            MERGE (en:Entity {{ID:id, uID:("{entity_type}"+toString(id)), EntityType:"{entity_type}" }})'''
    print(qCreateEntity)
    tx.run(qCreateEntity)

def q_correlate_events_to_entity(tx, entity_type, attribute_holding_id, WHERE_event_property):
    qCorrelate = f'''
            MATCH (e:Event) {WHERE_event_property}
            UNWIND e.{attribute_holding_id} AS id
            MATCH (n:Entity {{EntityType: "{entity_type}" }}) WHERE n.ID = id
            CREATE (e)-[:CORR]->(n)'''
    print(qCorrelate)
    tx.run(qCorrelate)


with driver.session() as session:
    for ent in model_entities_from_attributes:
        session.execute_write(q_create_entity,ent[0],ent[1],ent[2])
        session.execute_write(q_correlate_events_to_entity,ent[0],ent[1],ent[2])

### Build Event Knowledge Graph:
### Step 2) Infer Directly-Follows Relation between correlated evente

def q_create_directly_follows(tx):
    qCreateDF = f'''
        MATCH (n:Entity)
        MATCH (n)<-[:CORR]-(e)
        WITH n, e AS nodes ORDER BY e.timestamp, ID(e)
        WITH n, collect(nodes) AS event_node_list
        UNWIND range(0, size(event_node_list)-2) AS i
        WITH n, event_node_list[i] AS e1, event_node_list[i+1] AS e2
        
        MERGE (e1)-[df:DF {{EntityType:n.EntityType, ID:n.ID}}]->(e2)'''
    
    print(qCreateDF)
    tx.run(qCreateDF)


def q_create_directly_follows_typed(tx, entity_type):

    entity_type_safe_str = entity_type.replace(' ','_')

    qCreateDF = f'''
        MATCH ( n : Entity ) WHERE n.EntityType="{entity_type}"
        MATCH ( n ) <-[:CORR]- ( e )
        
        WITH n , e as nodes ORDER BY e.timestamp,ID(e)
        WITH n , collect ( nodes ) as nodeList
        UNWIND range(0,size(nodeList)-2) AS i
        WITH n , nodeList[i] as first, nodeList[i+1] as second

        MERGE ( first ) -[df:DF_{entity_type_safe_str} {{ ID:n.ID }}]->( second )'''

    print(qCreateDF)
    tx.run(qCreateDF)

option_df_typed = False

with driver.session() as session:
    
    if option_df_typed == False: # for generic DF relations
        session.execute_write(q_create_directly_follows)
    else:
        for ent in model_entities_from_attributes:
            session.execute_write(q_create_directly_follows_typed,ent[0])

