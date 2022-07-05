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

## Looking for more?

* [https://github.com/multi-dimensional-process-mining/graphdb-eventlogs] provides Python scripts implementing parameterized Cypher query templates for building event knowledge graphs of 5 real-life event logs, see also [https://zenodo.org/record/4708117] for a fully packaged `.zip` with queries and datasets
* [https://github.com/multi-dimensional-process-mining/event-graph-task-pattern-detection] a Python library for detecting task execution patterns in event knowledge graphs