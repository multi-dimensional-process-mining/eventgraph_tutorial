
class OcelImportQueryLibrary:

    @staticmethod
    # create index on nodes with label 'node_label', for a specific attribute 'id'
    def q_create_index(nodel_label, id):
        index_query = f'CREATE INDEX {nodel_label}_{id} FOR (n:{nodel_label}) ON (n.{id})'
        print(index_query)
        return index_query

    @staticmethod
    # Use Neo4j's bulk import from CSV to create on :event node per record in CSV file
    # - 'fileName' is the system file path to the CSV file from which Neo4j will load
    # - 'logHeader' the list of attribute names of the CSV file
    # - an optional `LogID` to distinguish events coming from different event logs
    def q_load_csv_as_nodes(fileName, csvHeader, nodeLabel):

        # import each row of the CSV one by one, as variable 'line' 
        query_str = f'LOAD CSV WITH HEADERS FROM \"file:///{fileName}\" as line\n'
        query_str += 'CALL {\n'
        query_str += ' WITH line\n'

        # per line create a node
        query_str = query_str + f' CREATE (e:{nodeLabel} {{ '
        # subsequent lines specify how the attribute of event e are set (from "line')

        # for each colum in the header, set attribute 'column' of event e to the value line.column
        for col in csvHeader:
            # allow type conversion by Neo4j during import
            if col in ['time','timestamp','start','end']:
                # tell Neo4j to typecast timestamp attributes to dateTime during import
                colValue = f'datetime(line.{col})'
            else:
                # every other attribute is just the value stored in the column in that line
                colValue = 'line.'+col

            # distinguish final event to close the CREATE query properly
            if (csvHeader.index(col) < len(csvHeader)-1):
                query_str = query_str + f' {col}: {colValue},'
            else:
                query_str = query_str + f' {col}: {colValue} }})'

        query_str += '\n'    
        query_str += '} IN TRANSACTIONS OF 1000 ROWS;'

        print(query_str)

        return query_str
    
    @staticmethod
    def q_link_node_to_node(sourceNode, sourceAttribute, relationship, targetNode, targetAttribute):
        query_str = f'''
            MATCH (t:{targetNode}) WITH t
            MATCH (s:{sourceNode} {{ {sourceAttribute}: t.{targetAttribute} }}) WITH s,t
            MERGE (s)-[:{relationship}]->(t)'''
        print(query_str)
        return query_str
    
    @staticmethod
    def q_load_csv_as_relation(fileName, csvFrom, sourceNode, sourceAttr, csvType, relationship, csvTo, targetNode, targetAttribute):
        # import each row of the CSV one by one, as variable 'line' 
        query_str = f'''
            LOAD CSV WITH HEADERS FROM \"file:///{fileName}\" as line
            CALL {{
             WITH line
              MATCH (s:{sourceNode} {{ {sourceAttr}:line.{csvFrom} }} )
              MATCH (n:{targetNode} {{ {targetAttribute}:line.{csvTo} }} )
              MERGE (s) -[r:{relationship}]-> (n) ON CREATE SET r.type=line.{csvType}
            }} IN TRANSACTIONS OF 1000 ROWS;'''

        print(query_str)

        return query_str

    @staticmethod
    def q_load_csv_as_e2o_relation(fileName):
        return OcelImportQueryLibrary.q_load_csv_as_relation(fileName, "eventId", "Event", "id", "qualifier", "CORR", "objectId", "Entity", "id")


    @staticmethod
    def q_ocel2_materialize_last_object_state():

        query_str = '''
            MATCH (n:Entity) -[:HAS_ATTRIBUTE]-> (a) WITH DISTINCT n,a.name AS aName 
            MATCH (n) -[:HAS_ATTRIBUTE]-> (a {name:aName}) WITH n, a ORDER BY a.time DESC
            WITH n, a.name AS aName, collect(a.value)[0] AS aValue
            call apoc.create.setProperty(n, aName, aValue)
            YIELD node
            RETURN COUNT(*)
            '''
        print(query_str)

        return query_str