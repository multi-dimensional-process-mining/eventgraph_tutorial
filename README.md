# eventgraph_tutorial
A collection of tutorials for using Cypher and Neo4j for creating, querying, analyzing, and doing process mining with event knowledge graphs. 

All tutorials require a clean instance of the Neo4j graph database system running for this tutorial.
1. You can download and install Neo4j from [https://neo4j.com/download/]
2. See [https://neo4j.com/docs/desktop-manual/current/operations/create-dbms/] for how to create a new Neo4j instance.
   All tutorials assumes the default user '**neo4j**' with password '**1234**', which you can set when creating a new neo4j instance.

## Tutorials 1-3: [./order_process](./order_process)

This is the very first set of tutorials you should follow. This set of tutorials comes with
1. a small example dataset that on which you can learn all the design ideas and modeling power of event knowledge graphs while still knowing every event by its name
2. step by step instructions for using Cypher and Neo4j to construct and analyze event knowledge graphs
3. quick versions of the tutorials for the impatient ones

[Tutorial 1: Building Your First Event Knowledge Graph with Neo4j and Cypher](./order_process/tutorial-your-first-event-knowledge-graph.md) ([quick version](./order_process/tutorial-your-first-event-knowledge-graph-quick.md)). In this tutorial you learn
  * How to set up and configure Neo4j for working with event data
  * How to import event data into Neo4j from a `.csv` file
  * How to use Cypher to
     * identify entity types and entity identifiers
     * construct entity nodes and correlate events to entity nodes
     * infer directly-follows relationships over events in a graph
     * query the graph for directly-follows paths

[Tutorial 2: Basic Process Discovery in Event Knowledge Graphs](./order_process/tutorial-basic-process-discovery-DFG-quick.md). In this tutorial you learn how to use Cypher to
  * aggregate events to activity nodes (and other types of event classes)
  * aggregate directly-follows relations to construct multi-entity directly-follows graphs
  * use filtering on events during aggregation to create specific directly-follows graphs
Currently only the quick version of the tutorial is available; the full version is under development.

[Tutorial 3: Discovering Proclet Models in Event Knowledge Graphs](./order_process/tutorial-basic-process-discovery-Proclets-quick.md). In this tutorial you learn how to use Cypher to construct an advanced type of process model called "proclets" by:
  * creating more advanced event classes to distinguish activities in different entities
  * aggregate directly-follows relations per entity and add synchronization edges between activities in different entities
Currently only the quick version of the tutorial is available; the full version is under development.

## Tutorials for Object-Centric Process Mining

### on the [./order_process](./order_process)

[Tutorial OCPM 1: Building and Analyzing Object Relations](./order_process/tutorial-ocpm-relations.md). In this tutorial you learn 
  * how to identify relations between objects,
  * how to assign directions to relations, and
  * how to create a simple but powerful object-centric process mining summary based on object relations.

[Tutorial OCPM 2: Analyzing and Summarzing Object Traces](./order_process/tutorial-ocpm-object-traces.md). In this tutorial you learn 
  * how to query for and visualize object-centric behavior in terms of **object-traces**, and
  * how to summarize the behavior of all objects of the same type as **object trace variants**

[Tutorial OCPM 3.1: Defining and Querying Object-Centric Process Executions](./order_process/tutorial-ocpm-object-centric-process-executions.md). In this tutorial you learn 
  * how we can transfer the notion of the classical "case" concept to an object-centric setting and define **object-centric start-to-end executions** in different forms
  * how to query and materialize knowledge about object-centric start-to-end executions by extending the EKG
  * how to **visualize, understand, and compare** object-centric start-to-end executions of the same kind

[Tutorial OCPM 3.2: Summarizing and Analyzing Object-Centric Process Executions](./order_process/tutorial-ocpm-object-centric-process-executions-summarizing.md). In this tutorial you learn 
  * how to summarize object-centric process executions in terms of activities resulting in **object-centric process variants**
  * how to model object-centric process executions in terms of involved objects and which insights can be gained
  * how to generete a global behavioral summary of an EKG

[Tutorial OCPM 3.3: Generalized Object-Centric Start-to-End Executions](./order_process/tutorial-ocpm-object-centric-process-executions-generalized.md). In this tutorial you learn 
  * how to generalize the notion object-centric start-to-end executions by
    * using **start/end activities** instead of start/end objects
    * allowing **multiple start/end events** instead of single start/end events
    * **filtering** which objects to include/exclude in the execution
  * how to apply all of the above to define a form of **object-centric cases** based on a **leading object type**  

## Looking for more?

* [https://github.com/multi-dimensional-process-mining/graphdb-eventlogs] provides Python scripts implementing parameterized Cypher query templates for building event knowledge graphs of 5 real-life event logs, see also [https://zenodo.org/record/4708117] for a fully packaged `.zip` with queries and datasets
* [https://github.com/multi-dimensional-process-mining/event-graph-task-pattern-detection] a Python library for detecting task execution patterns in event knowledge graphs