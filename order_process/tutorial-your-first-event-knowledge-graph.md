# Tutorial 1: Building Your First Event Knowledge Graph with Neo4j and Cypher

This first tutorial introduces you to the basics of building event knowledge graphs from event tables, using the database system Neo4j and the Cypher query language. Below you find instructions for downloading and setting up the necessary software.

The tutorial then covers step by step the Cypher queries needed to build event knowledge graphs.

## Download and Install

To follow this tutorial you need
* an instance of the Neo4j database
* the tutorial files
* Python3 (tested on Python 3.7.9) with the following packages
   * `neo4j`
   * `graphviz`


### Neo4j

You need a clean instance of Neo4j running for this tutorial.
1. Download and install Neo4j, e.g., Neo4j Desktop from [https://neo4j.com/download/]
2. Create a new Neo4j instance, see [https://neo4j.com/docs/desktop-manual/current/operations/create-dbms/]  
   This example assumes the default user '**neo4j**' with password '**1234**', which you can set when creating a new neo4j instance.

#### How to configure Neo4j for local file import

This example imports the event data from a local file. By default Neo4j does not allow importing data from arbitrary local URLs. To allow Neo4j importing a file from a local directoy, take the following steps:

1. Find the `neo4j.conf` file for your Neo4j installation, see [https://neo4j.com/docs/operations-manual/current/configuration/file-locations/].  
   If you are using Neo4j Desktop, the neo4j.conf file is located under _&lt;yourGraph&gt; > Manage > Settings_ (you have to stop the DB instance first)
2. Comment out this line (by adding `#` at the start of the line):  
   `dbms.directories.import=import`
3. Uncomment this line to allow CSV import from file URL:  
   `#dbms.security.allow_csv_import_from_file_urls=true`

#### How to start and connect to Neo4j

Start the configured Neo4j instance. You can connect to the Neo4j instance via
* the [Neo4j browser](https://neo4j.com/docs/browser-manual/current/) to enter [Cypher queries](https://neo4j.com/docs/cypher-manual/current/introduction/) directly
* via Python with package `neo4j` and the following code
```
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234")) 
```

### Tutorial files

Download all files of this repository/unzip the file into a directory _&lt;tutorial&gt;_ with no dash character '-' in the entire directory path. Otherwise data import into Neo4j will not succeed.


## Preparing Event Data for Import

The input data for this tutorial is a single event table in `.csv` format: [./input_logs/order_process_event_table_orderhandling.csv](./input_logs/order_process_event_table_orderhandling.csv) which contains multiple records, each describing one event that has been executed with the following attributes:
* a timestamp attribute `time`
* an attribute `event` describing the activity that has been executed
* several other attributes describing entity identifiers, e.g., `Order` and `Supplier Order`, or properties of these entities, e.g., `Order Details`

The input data is not yet in shape to be imported into Neo4j and we need to pre-process it
* the `time` attribute format has to be converted to a full UTC timestamp `YYYY-MM-DD hh:mm:ss.fff+timezone` and renamed to a standard attribute name `timestamp`
* the attribute name `event` is ambiguous, our subsequent queries assume a standard attribute name `Activity`
* column names cannot contain spaces, e.g., we have to rename `Supplier Order` to `SupplierOrder`

The python script [./0_prepare_log_for_import.py](./0_prepare_log_for_import.py) does that for us. The script itself has provisions for more preprocessing options, e.g., preprocessing specific to individual records, deriving unique event identifiers from other attributes, etc.

Running the script will read the file [./input_logs/order_process_event_table_orderhandling.csv](./input_logs/order_process_event_table_orderhandling.csv), preprocess it, and output [./prepared_logs/order_process_event_table_orderhandling_prepared.csv](./prepared_logs/order_process_event_table_orderhandling_prepared.csv) which is ready for Neo4j import.

## Building Event Knowledge Graphs

We now start from the prepared event table [./prepared_logs/order_process_event_table_orderhandling_prepared.csv](./prepared_logs/order_process_event_table_orderhandling_prepared.csv). Building an event knowledge graph takes the following steps.

1. Importing all event records from [./prepared_logs/order_process_event_table_orderhandling_prepared.csv](./prepared_logs/order_process_event_table_orderhandling_prepared.csv) into Neo4j as `:Event` nodes
2. Identify entity types in the event attributes and derive `:Entity` nodes for each entity type
3. Create `:CORR` (correlation) relationships between `:Event` and `:Entity` nodes to model which events have been observed for which entity
4. Infer `:DF` (directly-follows) relationships from between `:Event` nodes correlated to the same `:Entity` node

For each step, we first show and explain the `Cypher` query that can be executed directly in the Neo4j browswer and then point to the Python scripts that automate the steps, and finally the entire procedure.

### Import event records as event nodes

Open Neo4j browser (or any other Neo4j console) and enter the following Cypher query to import events from  [./prepared_logs/order_process_event_table_orderhandling_prepared.csv](./prepared_logs/order_process_event_table_orderhandling_prepared.csv) into Neo4j. Make sure to replace the placeholder _&lt;tutorial&gt;_ with the full OS directory path to where you unzipped the tutorial files, e.g., `D:/data/eventgraph_tutorial/` or `/home/myUsername/eventgraph_tutorial/`.

```
LOAD CSV WITH HEADERS FROM "file:///<tutorial>/order_process/prepared_logs/order_process_event_table_orderhandling_prepared.csv" as line CREATE (e:Event {Log: "order_process",EventID: line.EventID, Activity: line.Activity, timestamp: datetime(line.timestamp), User: line.User, Order: line.Order, SupplierOrder: line.SupplierOrder, Order_Details: line.Order_Details, Item: line.Item, Invoice: line.Invoice, Payment: line.Payment, Tray: line.Tray })
```

The `LOAD CSV ..  as line` command loads each row of the input `.csv` file separately into the variable `line` and then executes the `CREATE (...)` query for each `line`. The `CREATE` query creates per `line` one `(:Event {...})` node with several properties specified between `{ ... }`. The property values are set according to the values in variable `line`, for example property `Activity` is set from the value `line.Activity`.

Executing the query should yield the following response
```
Added 34 labels, created 34 nodes, set 242 properties, completed after 10 ms.
```


Note: the above query is not scalable to large input files of 1000s of event records. Below we embed the query into a transaction that will improve performance, but for now we focus on the essence.

### Query the event nodes imported

In the Neo4j browser, we can query for the event nodes we just imported and inspect them. Enter
```
MATCH (e:Event) RETURN e
```
to retrieve all `:Event` nodes that were created. Neo4j will visualize the nodes. You can inspect the details of a node by hovering over it.

!["Image of event nodes after importing event table"](./tutorial_images/event_nodes_graph.png "Event nodes after importing event table")

We can query for a specific subset of events by their properties
```
MATCH (e:Event {Order:"O1"}) RETURN e
```
which returns only the subset of nodes that have the specified property
!["Image of event nodes for Order O1 after importing event table"](./tutorial_images/event_nodes_graph_orderO1.png "Event nodes of Order O1 after importing event table")

We can also query for just properties instead of entire nodes
```
MATCH (e:Event) RETURN e.Order,e.Order_Details,e.SupplierOrder,e.Item,e.Invoice,e.Payment,e.Actor
```
which returns a table with the queried properties
!["Image of some event properties"](./tutorial_images/event_nodes_property_table.png "Some event properties")

See the [Cypher documentation on MATCH](https://neo4j.com/docs/cypher-manual/current/clauses/match/) for further details on querying nodes.

### Identify entity types and create entity nodes (from singleton values)

If we inspect the event node properties, for example with the previous query, we can see that some properties hold identifiers for entities of a specific type. For example, property _Order_ holds identifies _O1_ and _O2_ referring to two different orders. By exploring and querying the data - combined with some domain knowledge or common sense - we can pick out which properties describe entity types. In the tutorial data, these are
* data objects
   * _Order_
   * _SupplierOrder_
   * _Item_
   * _Invoice_
   * _Payment_
* humans/users
   * _Actor_

Property *Order_Details* with values such as _X,X,Y_ does not identify an entity.

To confirm and understand which concrete entities identifers are in the data, we can query all unique values per entity property. For example,
```
MATCH (e:Event) WHERE e.Order <> "null" RETURN distinct e.Order
```
returns
| e.Order |
|---------|
| "O1"  |
| "O2"  |

This means, attribute _Order_ directly holds _O1_ and _O2_ as entity identifiers. 

With the following query, we create for each identifier value of _Order_ a new unique `:Entity` node of type _Order_ with a specific `ID`. In other words, we materialize the entity we saw as attribute as a new node (that we later can refer to).

```
MATCH (e:Event) WHERE e.Order <> "null" 
WITH DISTINCT e.Order AS id_val
CREATE (:Entity {ID:id_val, EntityType:"Order"})
```

We can query for the two new `:Entity` nodes with `MATCH (n:Entity {EntityType:"Order"}) RETURN n`. Note that executing the above query a second time will again create two `:Entity` nodes, resulting in two entities with _ID="O1"_ and two entities with _ID="O2"_. First, two clean up such mistakes, you can use the query `MATCH (n:Entity {EntityType:"Order"}) DELETE n` which will delete all `:Entity` nodes where `EntityType="Order"`. Second, we can use `MERGE` instead of `CREATE`. `MERGE` will not create a new node if there already exists a node with the same label and properties:

```
MATCH (e:Event) WHERE e.Order <> "null" 
WITH DISTINCT e.Order AS id_val
MERGE (:Entity {ID:id_val, EntityType:"Order"})
```

From the above query, we can define a generic template of creating `:Entity` nodes for entities referenced from a property always only holding a single value:

```
MATCH (e:Event) WHERE e.$EntityName <> "null" 
WITH DISTINCT e.$EntityName AS id_val
MERGE (:Entity {ID:id_val, EntityType:"$EntityName"})
```

### Identify entity types and create entity nodes (from list values)

The above query for entity creation does not work if an attribute holds a list of entity identifier values. For example, the query

```
MATCH (e:Event) WHERE e.Item <> "null" RETURN distinct e.Item
```

returns
| e.Item  |
|---------|
| "X1,X2,X3" |
| "X3"       |
| "X1"       |
| "X2"       |
| "Y1,Y2"    |
| "Y1"       |
| "Y2"       |
| "X1,X2,Y1" |
| "X3,Y2"    |

The _Item_ property holds a _string_ and each string represents a list of identifier values. Now, that is because Neo4j imports each `.csv` column that it cannot match to a native datatype as a string. We first have to turn propert _Item_ from a string (representing a list) into an actual list (of identifiers, which are strings).
```
MATCH (e:Event) WHERE e.Item <> "null"
WITH e,split(e.Item, ',') AS items
SET e.Item=items
```
The query splits the the string `e.Item` on the delimiter `','` into a list of strings and stores them in the variable `items`. We then update property `e.Item` to be this list. Running again the query `MATCH (e:Event) WHERE e.Item <> "null" RETURN distinct e.Item` now gives us.
| e.Item  |
|---------|
| ["X1","X2","X3"] |
| ["X3"] |
| ["X1"] |
| ["X2"] |
| ["Y1","Y2"] |
| ["Y1"] |
| ["Y2"] |
| ["X1","X2","Y1"] |
| ["X3","Y2"] |
Each value for _Item_ now is a list of identifiers. We can use `UNWIND` on `e.Item` to iterate over the list and create one entity node per identifier in the list, as we did for the singleton value case. 
```
MATCH (e:Event) WHERE e.Item <> "null" 
UNWIND e.Item AS id_val
WITH DISTINCT id_val
MERGE (:Entity {ID:id_val, EntityType:"Item"})
```
This results in the creation of 5 `:Entity` nodes of type _Item_ for _X1,X2,X3,Y1,Y2_. The clause `WITH DISTINCT id_val`, which ensures that we do not pass dupicate values to `MERGE` is not strictly necessary, as `MERGE` already prevents creating duplicate nodes. 

Luckily, we can apply the above query with `UNWIND` also on properties with just singleton values. Cypher will gracefully treat the singleton value as a singleton list. This means our generic query template for creating entity nodes from property `$EntityName` is
```
MATCH (e:Event) WHERE e.$EntityName <> "null" 
UNWIND e.$EntityName AS id_val
WITH DISTINCT id_val
MERGE (:Entity {ID:id_val, EntityType:"$EntityName"})
```