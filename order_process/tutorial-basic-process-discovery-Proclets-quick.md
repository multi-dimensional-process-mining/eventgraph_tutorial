# Tutorial 3: Discovering Proclet Models in Event Knowledge Graphs with Neo4j and Cypher (the quick version)

This is the quick version of the 2nd tutorial on process discovery in event graphs. It skips over all explanations and cuts straight to the essential code and queries. The full tutorial is still to be published.

This tutorial provides queries to discover proclet models from event knowledge graphs. A proclet model provides one distcint behavioral model (e.g., one DFG) per entity type. The nodes and edges in each proclet describe the life-cycle of all entities of this type. If two different entities synchronize in an event, then the model represents this by synchronization edges between the activities nodes of the different life-cycle models.

## Prerequisites

  * You complete the [1st tutorial on building event knowledge graphs](./tutorial-your-first-event-knowledge-graph.md)
     * You have a running instance of Neo4j
     * You have imported events and constructed an event knowledge graph
  * You followed the [2nd tutorial on discovering DFGs in event knowledge graphs](./tutorial-basic-process-discovery-DFG-quick.md)

## 1 Constructing DFGs for different event classifiers

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

## 2 Lifting D