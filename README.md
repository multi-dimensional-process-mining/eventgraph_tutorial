# eventgraph_tutorial
A collection of tutorials for using Cypher and Neo4j for creating, querying, analyzing, and doing process mining with event knowledge graphs. 

All tutorials require a clean instance of the Neo4j graph database system running for this tutorial.
1. You can download and install Neo4j from [https://neo4j.com/download/]
2. See [https://neo4j.com/docs/desktop-manual/current/operations/create-dbms/] for how to create a new Neo4j instance.
   All tutorials assumes the default user '**neo4j**' with password '**1234**', which you can set when creating a new neo4j instance.

## Tutorial 1: [./order_process](./order_process)

This is the very first tutorial you should follow. In this tutorial, you learn
1. How to set up and configure Neo4j for working with event data
2. How to import event data into Neo4j from a `.csv` file
3. How to use Cypher to
  * identify entity types and entity identifiers
  * construct entity nodes and correlate events to entity nodes
  * infer directly-follows relationships over events in a graph
  * query the graph for directly-follows paths

The tutorial comes with
1. step by step instructions in [./order_process/tutorial-your-first-event-knowledge-graph.md](./order_process/tutorial-your-first-event-knowledge-graph.md)
2. a small example dataset that on which you can learn all the design ideas and modeling power of event knowledge graphs while still knowing every event by its name

## Looking for more?

* [https://github.com/multi-dimensional-process-mining/graphdb-eventlogs] provides Python scripts implementing parameterized Cypher query templates for building event knowledge graphs of 5 real-life event logs, see also [https://zenodo.org/record/4708117] for a fully packaged `.zip` with queries and datasets
* [https://github.com/multi-dimensional-process-mining/event-graph-task-pattern-detection] a Python library for detecting task execution patterns in event knowledge graphs