# Tutorial 2: Basic Process Discovery in Event Knowledge Graphs with Neo4j and Cypher (the quick version)

This is the quick version of the 2nd tutorial on process discovery in event graphs. It skips over all explanations and cuts straight to the essential code and queries. The full tutorial is still to be published.

This tutorial provides queries to aggregate event knowledge graphs into the most basic form of process models: (filtered) directly-follows graphs (DFGs) from event knowledge graphs. However, there is a twist to the DFGs: each edge in the DFG is defined for one specific entity type, aggregating only behavioral information of the entities of this type.

## Prerequisites

  * You complete the [the 1st tutorial on building event knowledge graphs](./tutorial-your-first-event-knowledge-graph.md)
     * You have a running instance of Neo4j
     * You have imported events and constructed an event knowledge graph

## 1 Aggregating Events to Event Classes

An **event class** is a set of events that all share the same characteristic. 

*The* standard event classifer in process mining is the **activity name**: all events with the same activity name belong to the same event class. When discovering a process model, then we create an "activity" node for each activity name in the data. The following query does this:
```
MATCH ( e : Event ) WITH distinct e.Activity AS actName
MERGE ( c : Class { Name:actName, Type:"Activity", ID: actName})
```
Note that we introduce a new label `:Class` to model event classes. The **type** property indicates which type of property (classifier) was used to create the event class. To model which events belong to a `:Class`, we add a relationships from each `:Event` node to its `:Class` node with the following query:
```
MATCH ( c : Class ) WHERE c.Type = "Activity"
MATCH ( e : Event ) WHERE c.Name = e.Activity
CREATE ( e ) -[:OBSERVED]-> ( c )'''
```
Below we show an example of a different event classifier. For now we continue with *Activity* classes.

## 2 Lifting Directly-Follows Relationships

The following query lifts `:DF` relationships between events (correlated to the same entity *n* to event classes.
```
MATCH ( c1 : Class ) <-[:OBSERVED]- ( e1 : Event ) -[df:DF]-> ( e2 : Event ) -[:OBSERVED]-> ( c2 : Class )
MATCH (e1) -[:CORR] -> (n) <-[:CORR]- (e2)
WHERE c1.Type = c2.Type AND n.EntityType = df.EntityType
WITH n.EntityType as EType,c1,count(df) AS df_freq,c2
MERGE ( c1 ) -[rel2:DF_C {EntityType:EType}]-> ( c2 ) ON CREATE SET rel2.count=df_freq
```
Note that the relationship `(c1) -[rel2:DF_C]-> (c2)` is defined for the type of the entity *n*. That means, each aggregated `:DF_C` edge is specific for one entity type. The query also records how many `:DF` relationships were aggregated in property **count**. We here chose to use a new label `:DF_C` for the relations between event classes, to easier differentiate between directly-follows at event level (`:DF`) and at class level (`:DF_C`).

Note that the above query is entirely generic for *any* type of `:Class` nodes - it will only aggregate `:DF` relationships between `:Class` nodes of the same type.

## 3 Retrieving the Directly-Follows Graph

The following query retrieves all `:Class` nodes of type *Activity* and all adjacent `:DF_C` edges.
```
MATCH (c1:Class) WHERE c1.Type = "Activity"
OPTIONAL MATCH (c1)-[df:DF_C]->(c2) WHERE c1.Type = c2.Type
RETURN c1,df,c2
```

## 4 Removing Directly-Follows Graphs from the Event Knowledge Graph
```
# delete DF_C relationships
MATCH (c1)-[df:DF_C]->(c2) DELETE df
# delete OBSERVES relationships
MATCH (e)-[obs:OBSERVES]->(c) DELETE obs
# delete CLASS nodes
MATCH (c:Class) DELETE c
```
Any of the above queries can be refined with `WHERE` clauses to only delete specific relationships or nodes.

## 5 Constructing a filtered Directly-Follows Graph

We can construct a directly-follows graph only containing edges that satisfy a specific property, e.g., only edges with a minimum *count*:
```
MATCH ( c1 : Class ) <-[:OBSERVED]- ( e1 : Event ) -[df:DF]-> ( e2 : Event ) -[:OBSERVED]-> ( c2 : Class )
MATCH (e1) -[:CORR] -> (n) <-[:CORR]- (e2)
WHERE c1.Type = c2.Type AND n.EntityType = df.EntityType
WITH n.EntityType as EType,c1,count(df) AS df_freq,c2 WHERE df_freq > 1
MERGE ( c1 ) -[rel2:DF_C {EntityType:EType}]-> ( c2 ) ON CREATE SET rel2.count=df_freq
```

The query can also be adapted to only aggregate df relationships with a minimum/maximum time difference between `e1.time` and `e2.time`.

## 6 Constructing DFGs for different event classifiers

The above queries are generic once `:Class` nodes have been modeled in the graph. So far we only aggregated events by their *Activity* property. The following tutorials show how to do discovery for different event classifiers:
*  (discovering Proclet models in event knowledge graphs)[./tutorial-basic-process-discovery-Proclets-quick.md]
