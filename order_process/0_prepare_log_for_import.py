# prepare inputfile BPI_Challenge_2017.csv for import into Neo4j 
# by renaming columns into standard values and reformatting timestamps

import pandas as pd
import time, os, csv

#config

inputpath = './input_logs/'
inputfile = 'order_process_event_table_orderhandling.csv'
outputpath = './prepared_logs/'

outputfile = 'order_process_event_table_orderhandling_prepared.csv'


def LoadLog(localFile):
    datasetList = []
    headerCSV = []
    i = 0
    with open(localFile) as f:
        reader = csv.reader(f)
        for row in reader:
            if (i==0):
                headerCSV = list(row)
                i +=1
            else:
               datasetList.append(row)
        
    log = pd.DataFrame(datasetList,columns=headerCSV)
    
    return headerCSV, log

def PrepareOrderHandling(inputpath, outputpath, fileName):
    csvLog = pd.read_csv(os.path.realpath(inputpath+inputfile), keep_default_na=True) #load full log from csv                  
    csvLog.drop_duplicates(keep='first', inplace=True) #remove duplicates from the dataset
    csvLog = csvLog.reset_index(drop=True) #renew the index to close gaps of removed duplicates 
    
    # rename CSV columns to standard value
    # Activity
    # timestamp
    # Actor
    # rename columns with whitepsaces
    csvLog = csvLog.rename(columns={'event': 'Activity','time':'timestamp','User':'Actor','Supplier Order':'SupplierOrder','Order Details':'Order_Details'})

    # create a unique event id from the a combination of event attributes
    # this example data already has a unique event ID per event, 
    # so the step is redundant
    #csvLog['EventIDraw'] = csvLog['EventID']

    # the following loop allows to pre-process individual event records in the data 
    # for the order process, there is nothing to pre-process and we only copy rows from
    # the csv file into a list to fill a dataframe for final formatting
    sampleList = [] #create a list (of lists) for the sample data containing a list of events for each of the selected cases
    for index, row in csvLog.iterrows():
        rowList = list(row)        #add the event data to rowList
        sampleList.append(rowList) #add the extended, single row to the sample dataset
    
    # create dataframe for default timestamp formatting (YYYY-MM-DD HH:MM:SS.ms)
    header =  list(csvLog) #save the updated header data
    logSamples = pd.DataFrame(sampleList,columns=header) #create pandas dataframe and add the samples  

    logSamples['timestamp'] = pd.to_datetime(logSamples['timestamp'], format='%d.%m.%Y %H:%M:%S')
    
    logSamples.fillna(0)
    # sort all events by time, add a second column if data contains events with identical timestamps to ensure canonical ordering
    logSamples['timestamp'] = logSamples['timestamp'].map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S.%f')[0:-3]+'+0100')
    logSamples.sort_values(['timestamp'], inplace=True)

    # and write dataframe to CSV file sorted by time
    if not os.path.isdir(outputpath):
        os.mkdir(outputpath)
    logSamples.to_csv(outputpath+fileName, index=False)
    #logSamples.to_csv(outputpath+fileName, index=True, index_label="idx") # use this line to generate an artificial index column

    
t_start = time.time()
PrepareOrderHandling(inputpath, outputpath, outputfile)
t_end = time.time()
print("Prepared data for import in: "+str((t_end - t_start))+" seconds.") 
