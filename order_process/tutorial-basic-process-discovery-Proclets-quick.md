# Tutorial 3: Discovering Proclet Models in Event Knowledge Graphs with Neo4j and Cypher (the quick version)

This is the quick version of the 2nd tutorial on process discovery in event graphs. It skips over all explanations and cuts straight to the essential code and queries. The full tutorial is still to be published.

This tutorial provides queries to discover proclet models from event knowledge graphs. A proclet model provides one distcint behavioral model (e.g., one DFG) per entity type. The nodes and edges in each proclet describe the life-cycle of all entities of this type. If two different entities synchronize in an event, then the model represents this by synchronization edges between the activities nodes of the different life-cycle models.

## Prerequisites

  * You complete the [1st tutorial on building event knowledge graphs](./tutorial-your-first-event-knowledge-graph.md)
     * You have a running instance of Neo4j
     * You have imported events and constructed an event knowledge graph
  * You followed the [2nd tutorial on discovering DFGs in event knowledge graphs](./tutorial-basic-process-discovery-DFG-quick.md)

## 1 Constructing Event Classes per Activity and Entity Type

The [tutorial on discovering DFGs](./tutorial-basic-process-discovery-DFG-quick.md) only aggregated events by their *Activity* property. Below is a different classifier that distinguishes in which *EntityType* an event occurs.
```
MATCH (e:Event)-[:CORR]->(n:Entity) WITH distinct e.Activity as actName,n.EntityType as EType
MERGE ( c : Class { ID: actName+"_"+EType, Name:actName, EntityType:EType, Type:"Activity,EntityType"})
```
Again, we link `:Class` nodes to the event nodes from which they are generated:
```
MATCH ( c : Class ) WHERE c.Type = "Activity,EntityType"
MATCH (e:Event)-[:CORR]->(n:Entity) WHERE c.Name = e.Activity AND c.EntityType=e.EntityType
CREATE ( e ) -[:OBSERVED]-> ( c )
```

## 2 Lifting Directly-Follows Relationships

We adapt the query for DFG discovery to aggregate `:DF` relationships between events to classes - but only if the classes match the entitytype of the `:DF` relationships to aggregate:
```
MATCH ( c1 : Class ) <-[:OBSERVED]- ( e1 : Event ) -[df:DF]-> ( e2 : Event ) -[:OBSERVED]-> ( c2 : Class )
MATCH (e1) -[:CORR] -> (n) <-[:CORR]- (e2)
WHERE c1.Type = c2.Type AND n.EntityType = df.EntityType AND c1.EntityType=n.EntityType AND c2.EntityType=n.EntityType
WITH n.EntityType as EType,c1,count(df) AS df_freq,c2
MERGE ( c1 ) -[rel2:DF_C {EntityType:EType}]-> ( c2 ) ON CREATE SET rel2.count=df_freq
```

# 3 Adding synchronization edges between event classes

We now add synchronized edges between event classes of the same activity in different entity types:
```
MATCH ( c1 : Class ), ( c2 : Class) WHERE c1.Name=c2.Name AND c1.EntityType <> c2.EntityType
MERGE (c1)-[:SYNC]->(c2)
```
Note that this query constructs a full join (cartesian product) between `:Class` nodes. This is only unproblematic if the number of distinct `:Class` nodes is small.

# 4 Retrieving the Proclet Model

We can retrieve the proclet model with the following query:
```
MATCH (c1:Class) WHERE c1.Type = "Activity,EntityType"
OPTIONAL MATCH (c1)-[df:DF_C]->(c2) WHERE c1.Type = c2.Type
OPTIONAL MATCH (c1)-[sync:SYNC]->(c3) WHERE c1.Type = c3.Type
RETURN c1,df,c2,sync,c3
```
