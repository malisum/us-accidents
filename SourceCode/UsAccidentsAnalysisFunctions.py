####################################################################################################################################################################################
# Import Dependencies:
####################################################################################################################################################################################

# Import Python Dependencies
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

# Import configurations & global data
from Configs import inputFileName
from Configs import inputFilePath
from Configs import outputFilePath
from Configs import numOfYears
from Configs import timezonePopulationDict
from Configs import statesPopulationDict
from Configs import statesLandSqMilesDict

####################################################################################################################################################################################
# Function(s) Definitions:
####################################################################################################################################################################################


# These functions ae used in the main script file(s)


####################################################################################################################################################################################
# Function: Get input file 
####################################################################################################################################################################################
def getInputFile():
    inputFile = inputFilePath + inputFileName
    print("Input file is: " + inputFile)
    return inputFile

####################################################################################################################################################################################
# Function: Get initial data from input file as dataframe  
####################################################################################################################################################################################
def getInputData(inputFile: str) -> pd.DataFrame:
    inputDF = pd.read_csv(inputFile)
    print("Dataframe created")
    return inputDF

####################################################################################################################################################################################
# Function: Cleanup initial data from input file  
####################################################################################################################################################################################
def cleanInputData(inputDF: pd.DataFrame) -> pd.DataFrame:
    
    
    # Save counts for later analysis
    columnCountBeforeCleanup = len(inputDF.columns)
    rowCountBeforeCleanup = inputDF['ID'].count()
    
    # Remove columns not being used for analysis
    inputDF.drop(columns=['End_Lat', 'End_Lng', 'End_Time', 'Distance(mi)', 'Number', 'Street', \
                          'Side', 'Wind_Chill(F)', 'Wind_Direction', 'Civil_Twilight', \
                          'Nautical_Twilight', 'Astronomical_Twilight', 'Temperature(F)', \
                          'Humidity(%)', 'Pressure(in)', 'Visibility(mi)'], inplace=True)

    # Remove any rows with all columns na/null
    inputDF.dropna(how = 'all', inplace=True)
    
    # For columns being analysed - remove any rows that have na/null value as it cannot be aggregated
    # These columns are: ID, State, Start_Time, Start_Lat, Start_Lng, Timezone, Weather_Condition, Sunrise_Sunset 
    inputDF.dropna(subset=['ID', 'State', 'Start_Time', 'Start_Lat', 'Start_Lng', 'Timezone', 'Weather_Condition', 'Sunrise_Sunset'], inplace=True)


    # Keep only rows that are for year 2017 & 2018 (data for other years is not consistent):
    # Drop data less than 2017
    indexDatesDrop = inputDF[ inputDF['Start_Time'] < '2017-01-00 00:00:00' ].index
    inputDF.drop(indexDatesDrop , inplace=True)
    # Drop data more that 2018
    indexDatesDrop = inputDF[ inputDF['Start_Time'] > '2018-12-31 23:59:59' ].index
    inputDF.drop(indexDatesDrop , inplace=True)

    # Save counts for later analysis (if needed)
    columnCountAfterCleanup = len(inputDF.columns)
    rowCountAfterCleanup = inputDF['ID'].count()

    columnsDeleted = columnCountBeforeCleanup-columnCountAfterCleanup 
    rowsDeleted = rowCountBeforeCleanup-rowCountAfterCleanup
    # Print counts of cleanup
    print("Clean up done, Number of columns deleted: {}, Number of rows deleted: {}".format(columnsDeleted, rowsDeleted))

    return inputDF

####################################################################################################################################################################################
# Function: Add date columns to the dataframe  
####################################################################################################################################################################################
def addDateColumns(inputDF: pd.DataFrame) -> pd.DataFrame:

    # Add columns for Month, Hour & Weekday
    inputDF['Year']=pd.to_datetime(inputDF['Start_Time']).dt.year
    inputDF['Month']=pd.to_datetime(inputDF['Start_Time']).dt.month
    inputDF['Hour']=pd.to_datetime(inputDF['Start_Time']).dt.hour
    inputDF['Year-Month']=pd.to_datetime(inputDF['Start_Time']).dt.to_period('M')
    inputDF['Weekday']=pd.to_datetime(inputDF['Start_Time']).dt.weekday_name

    # Print columns added
    print("Added required date columns to the dataframe")

    return inputDF


####################################################################################################################################################################################
# Function: Analyze by Timezone  
####################################################################################################################################################################################
def accidentsByTimezone(inputDF: pd.DataFrame):
    
    outputFileSubPath = 'ByTimezone/'

    # Get unique timezones & counts
    timezonesCounts = inputDF['Timezone'].value_counts().sort_index().tolist()
    timezonesLabels = inputDF['Timezone'].value_counts().sort_index().index.tolist()

    # Unique list all Severity values in the dataset
    uniqueSevList = inputDF['Severity'].value_counts(dropna=False).sort_index().index.tolist()
 
    # Set colors for timezones
    timezonesGraphColors = ['royalblue', 'darkorange', 'gold', 'darkolivegreen']
    # Set colors for severity 
    severityGraphColors = ['royalblue', 'lightgreen', 'gold', 'darkorange', 'red']
    

    # 1. Pie Chart (Count(s) of Accidents by timezone)
    # Set the plot attributes & Plot the Pie chart
    pieExplode = (0, 0, 0, 0)    
    plt.figure(figsize=(12, 8))
    plt.axis("equal")
    plt.pie(timezonesCounts, explode=pieExplode, colors=timezonesGraphColors, labels=timezonesLabels,
        autopct="%1.1f%%", shadow=True, startangle=135)
    plt.title("Accidents in Different Timezone")
    
    # Save output file
    outputFile = outputFilePath + outputFileSubPath + 'Timezone_Accidents_1_Counts_Pie.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



    # 2. Bar Chart (Counts by timezone)
    # Set the plot attributes & Plot the Bar chart
    plt.figure(figsize=(12, 8))
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(timezonesLabels)-0.25)
    plt.xlabel("Timezone")
    xlocs, xlabs = plt.xticks()
    # xlocs=[i+1 for i in range(0,len(timezonesLabels))]
    # xlabs=[i/2 for i in range(0,len(timezonesLabels))]
    xlocs=[i for i in range(0,len(timezonesLabels))]
    xlabs=timezonesLabels
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(timezonesCounts)+200000)
    plt.ylabel("Count of Accident(s)")
    # Plot the chart
    plt.bar(timezonesLabels, timezonesCounts, color=timezonesGraphColors, alpha=0.5, align="center")
    plt.title("Accidents in Different Timezone")
    # put value labes for Y-Axis 
    for i, v in enumerate(timezonesCounts):
        # Tip: Adjust -0.10 & +0.01 for positioning the lable text in the bar column
        plt.text(xlocs[i] -0.10, v + 0.01, str(v))
    
    # Save output file 
    outputFile = outputFilePath + outputFileSubPath + 'Timezone_Accidents_2_Counts_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



    # 3. Average severity pf accident by Timezone

    # Empty lists for bar chart to be plotted
    timezonesAvgSev = []
    
    # Extract mean (avg) sev for each timezone:
    for tz in timezonesLabels:
        meanSev = inputDF[inputDF['Timezone'] == tz]['Severity'].mean()
        timezonesAvgSev.append(round(meanSev,3))

    # Set the plot attributes & Plot the Bar chart
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(timezonesLabels)-0.25)
    plt.xlabel("Timezone")
    xlocs, xlabs = plt.xticks()
    xlocs=[i+1 for i in range(0,len(timezonesAvgSev))]
    xlabs=[i/2 for i in range(0,len(timezonesAvgSev))]
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(timezonesAvgSev)+0.500)
    plt.ylabel("Avergare Severity of Accident")
    # Plot the chart:
    plt.figure(figsize=(12, 8))
    plt.bar(timezonesLabels, timezonesAvgSev, color=timezonesGraphColors, alpha=0.5, align="center")
    plt.title("Average Accidents Severity in Different Timezone")
    # put value labes for Y-Axis 
    for i, v in enumerate(timezonesAvgSev):
        # Tip: Adjust -1.10 & +0.01 for positioning the lable text in the bar column
        plt.text(xlocs[i] -1.10, v + 0.01, str(v))
    
    # Define & Save: Output file - Pie chart
    outputFile = outputFilePath + outputFileSubPath + 'Timezone_Accidents_3_AvgSev_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)

    

    # 4. Weighted Severity Index per 1000 accidents by Timezone
    # Severity = 0, 1, 2, 3, 4
    # Severity Weights = 10, 20, 40, 80, 160 (Total Weight = 310)
    # Total Weighted Severity = ((Count of 0 Sev * 10) + (Count of 1 Sev * 10) + (Count of 2 Sev * 20) + (Count of 3 Sev * 30) + (Count of 4 Sev * 40))/(Total Weight = 310)
    # Weighted Severity Index = Total Weighted Severity / Total Count of Accidents (in  Timezone)
    # Weighted Severity Index per 1000 accidents =  Weighted Severity Index * 1000

    # Empty lists for bar chart to be plotted
    timezonesWeigthedSevIndex = []

    # Severity weights 
    sevWeight = [10, 20, 40, 80, 160]
    # Extract mean (avg) sev for each timezone:
    for tz in timezonesLabels:
        sevList = inputDF[inputDF['Timezone'] == tz]['Severity'].value_counts(dropna=False).sort_index().index.tolist()
        sevCounts = inputDF[inputDF['Timezone'] == tz]['Severity'].value_counts(dropna=False).sort_index().tolist()
                
        # Initialize calculated variables to 0 before calulcation per timezone
        # Weighted Severity Index per 1000 Accidents 
        weightedSevIndex = 0
        # Calculated Weighted Severity Index per Accident
        totalWeightedSevIndex = 0
        # Calculated Weighted Severity 
        weightedSev = 0
        # Calculated Total Weighted Severity 
        totalWeightedSev = 0
        # Count of Accidents by Timezone
        countByTimezone = 0        
        
        # for each severity found in timezone
        for i, sev in enumerate(sevList):
            # Note: sev is used as index for sevWeight (instead of i) to be sure that the correct count of severity - 
            # - is used with the matching severity weight as all sev may not be present i a tz
            totalWeightedSev = totalWeightedSev + (sevCounts[i] * sevWeight[sev])
            countByTimezone = countByTimezone + sevCounts[i]

        # Now have data per severity - calculate the final value for timezone
        weightedSev = totalWeightedSev/sum(sevWeight)
        totalWeightedSevIndex = weightedSev/countByTimezone 
        weightedSevIndex = round((totalWeightedSevIndex * 1000),2)
        timezonesWeigthedSevIndex.append(weightedSevIndex)
    
    # Done for all timezones

    # Set the plot attributes & Plot the Bar chart
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(timezonesLabels)-0.25)
    plt.xlabel("Timezone")
    xlocs, xlabs = plt.xticks()
    xlocs=[i+1 for i in range(0,len(timezonesAvgSev))]
    xlabs=[i/2 for i in range(0,len(timezonesAvgSev))]
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(timezonesWeigthedSevIndex)+10.00)
    plt.ylabel("Weighted Severity Index per 1000 Accidents")
    # Plot the chart:
    plt.figure(figsize=(12, 8))
    plt.bar(timezonesLabels, timezonesWeigthedSevIndex, color=timezonesGraphColors, alpha=0.5, align="center")
    plt.title("Weighted Severity of Accidents in Different Timezone (per 1000 Accidents)")
    # put value labes for Y-Axis 
    for i, v in enumerate(timezonesWeigthedSevIndex):
        # Tip: Adjust -1.10 & +0.01 for positioning the lable text in the bar column
        plt.text(xlocs[i] -1.10, v + 0.01, str(v))

    # Define & Save: Output file - Pie chart
    outputFile = outputFilePath + outputFileSubPath + 'Timezone_Accidents_4_WeightedSevIndex_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



    # 5. Bar Chart: Number of accidents by timezone per year per 1000 people
    # Count of Accidents by Timezone = Number of accidents per timezone in data analyzed
    # Count of Accidents by Timezone per year = Count of Accidents by Timezone / num of years of data being analyzed
    # Count of Accidents by Timezone per year per person = Count of Accidents by Timezone per year / population of timezone
    # Count of Accidents by Timezone per year per 1000 people = Count of Accidents by Timezone per year per person * 1000
    
    # Initialize variables used for calcuations:
    # List of Number of accidents per timezone per year per 1000 people
    timezoneCountsPerYearPer1000PopulationList = []
    
    # Get Accident per population * 1000 by Timezone in order as present in timezonesLabels
    for i, tz in enumerate(timezonesLabels):
 
        # Initialize variables used for calcuations:
        # Number of accidents per timezone per year 
        timezoneCountsPerYear = 0 
        # Number of accidents per timezone per year per person
        timezoneCountsPerYearPerPopulation = 0  
        # Number of accidents per timezone per year per 1000 people
        timezoneCountsPerYearPer1000Population = 0 

        # Perform the calulation 
        timezoneCountsPerYear = timezonesCounts[i]/numOfYears
        timezoneCountsPerYearPerPopulation = timezoneCountsPerYear / timezonePopulationDict[tz]
        timezoneCountsPerYearPer1000Population = round((timezoneCountsPerYearPerPopulation * 1000),3)

        # Add the calculated value to the list for the graph
        timezoneCountsPerYearPer1000PopulationList.append(timezoneCountsPerYearPer1000Population)


    # Calculations done - have the data now plot the bar chart  

    # Set the plot attributes & Plot the Bar chart
    plt.figure(figsize=(12, 8))
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(timezonesLabels)-0.25)
    plt.xlabel("Timezone")
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in range(0,len(timezonesLabels))]
    xlabs=timezonesLabels
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(timezoneCountsPerYearPer1000PopulationList)+0.250)
    plt.ylabel("Accident(s) per 1000 People")
    # Plot the chart
    plt.bar(timezonesLabels, timezoneCountsPerYearPer1000PopulationList, color=timezonesGraphColors, alpha=0.5, align="center")
    plt.title("Accidents in Different Timezone per Population of 1000")
    # put value labes for Y-Axis 
    for i, v in enumerate(timezoneCountsPerYearPer1000PopulationList):
        # Tip: Adjust -0.10 & +0.01 for positioning the lable text in the bar column
        plt.text(xlocs[i] -0.10, v + 0.01, str(v))
    
    # Save output file 
    outputFile = outputFilePath + outputFileSubPath + 'Timezone_Accidents_5_Counts_1000_People_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



    # 6. Pie Chart (Percentage Severity of Accidents by timezone)

    # Plot all 4 timezones in 1 figure : 2 rows 2 cols
    plt.figure(figsize=(12, 8))
    
    # Severity lables:
    uniqueSevLables = []
    for sv in uniqueSevList:
        uniqueSevLables.append("Severity " + str(sv))

    for cnt, tz in enumerate(timezonesLabels):
        sevList = inputDF[inputDF['Timezone'] == tz]['Severity'].value_counts(dropna=False).sort_index().index.tolist()
        sevCounts = inputDF[inputDF['Timezone'] == tz]['Severity'].value_counts(dropna=False).sort_index().tolist()
        
        # Define new lists to hold all severity values  
        sevListPct = []
        sevCountsPct = []

        # offset missing rows for comparison 
        matchIndex = 0
        # Not all timeozone may have an accident for each severity type - check & add a 0 count if needed:
        for i, s in enumerate(uniqueSevList):
            if uniqueSevList[i] == sevList[i-matchIndex]:
                # exists - add to new list for that Severity 
                sevListPct.append(uniqueSevList[i])
                sevCountsPct.append(sevCounts[i-matchIndex])
            else:
                # does not exists - add a 0 count entry for that Severity 
                sevListPct.append(uniqueSevList[i])
                sevCountsPct.append(0)
                matchIndex = matchIndex + 1

        if cnt == 0:
            # 1st Timezone : first row, first col
            ax1 = plt.subplot2grid((2,2),(0,0))
        if cnt == 1:
            # 2nd Timezone: first row, second col
            ax1 = plt.subplot2grid((2,2), (0, 1))
        if cnt == 2:
            # 3rd Timezone: second row, first column
            ax1 = plt.subplot2grid((2,2), (1, 0))
        if cnt == 3:
            # 4th Timezone: second row, second column
            ax1 = plt.subplot2grid((2,2), (1, 1))
        
        piePctExplode = (0.25, 0.25, 0, 0, 0.10)    
        plt.axis("equal")
        plt.pie(sevCountsPct, explode=piePctExplode, colors=severityGraphColors, labels=uniqueSevLables,
            autopct="%1.1f%%", shadow=True, startangle=135)
        plt.title("% Severity in Timezone: " + tz)

    # End of all timezones    
    # Save output file
    outputFile = outputFilePath + outputFileSubPath + 'Timezone_Accidents_6_Severity_Pie.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)


####################################################################################################################################################################################
# Function: Analyze by Hour  
####################################################################################################################################################################################
def accidentsByHour(inputDF: pd.DataFrame):

    outputFileSubPath = 'ByHour/'


    # Get unique hours & counts
    hourCounts = inputDF['Hour'].value_counts(dropna=False).sort_index().tolist()
    hourLabels = inputDF['Hour'].value_counts(dropna=False).sort_index().index.tolist()

    hourIndex = ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10', '10-11', '11-12', '12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24']
    # Plot the bar grapgh
    plt.figure(figsize=(12, 8))
  
    # Set the bar chart attributes such as X-Axis, Y-Axis, colors etc.
    # colors
    barColors = ['royalblue']
 
    # X-Axis limits & label: 
    plt.xlim(-0.75, len(hourLabels)-0.25)
    plt.xlabel("Hour")
    xlocs, xlabs = plt.xticks()
    xlocs=[i+0 for i in range(0,len(hourCounts))]
    xlabs=[i for i in hourIndex]
    plt.xticks(xlocs, xlabs, rotation = 45)
    # Y-Axis limits & label: 
    plt.ylim(0, max(hourCounts)+10000)
    plt.ylabel("Count of Accidents")
    # Plot 
    plt.bar(hourLabels, hourCounts, alpha=0.5, align="center", color=barColors)
    plt.title("Accidents by Hours of the Day")
    ### Commented - Lack of space to put tick labels for each hour
    # # put value labes for Y-Axis 
    # for i, v in enumerate(hourCounts):
    #     # Tip: Adjust -0.10 & +0.01 for positioning the lable text in the bar column
    #     plt.text(xlocs[i] -0.125, v + 0.01, str(v))
    
    # Define & Save: Output file - Bar chart
    outputFile = outputFilePath + outputFileSubPath + 'HourOfDay_Accidents_Counts.jpg'
    plt.savefig(outputFile)
    plt.close()


####################################################################################################################################################################################
# Function: Analyze by Day  
####################################################################################################################################################################################
def accidentsByDay(inputDF: pd.DataFrame):

    outputFileSubPath = 'ByDay/'

    # Chart by day of the week

    # Get unique hours & counts
    weekdayCounts = inputDF['Weekday'].value_counts(dropna=False).tolist()
    weekdayLabels = inputDF['Weekday'].value_counts(dropna=False).index.tolist()

    # Plot the bar grapgh
    plt.figure(figsize=(12, 8))
  
    # Set the bar chart attributes such as X-Axis, Y-Axis, colors etc.
    # colors
    barColors = ['royalblue']
 
    # X-Axis limits & label: 
    plt.xlim(-0.75, len(weekdayLabels)-0.25)
    plt.xlabel("Weekday")
    xlocs, xlabs = plt.xticks()
    xlocs=[i+0 for i in range(0,len(weekdayCounts))]
    xlabs=[i for i in weekdayLabels]
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label: 
    plt.ylim(0, max(weekdayCounts)+25000)
    plt.ylabel("Count of Accidents")
    # Plot 
    plt.bar(weekdayLabels, weekdayCounts, alpha=0.5, align="center", color=barColors)
    plt.title("Accidents by Day of the Week")
    # put value labes for Y-Axis 
    for i, v in enumerate(weekdayCounts):
        # Tip: Adjust -0.10 & +0.01 for positioning the lable text in the bar column
        plt.text(xlocs[i] -0.30, v + 0.01, str(v))
    
    # Define & Save: Output file - Bar chart
    outputFile = outputFilePath + outputFileSubPath + 'DayOfWeek_Accidents_Counts.jpg'
    plt.savefig(outputFile)
    plt.close()

    
####################################################################################################################################################################################
# Function: by Month of Year  
####################################################################################################################################################################################
def accidentsByMonth(inputDF: pd.DataFrame):

    outputFileSubPath = 'ByMonth/'

    # Get unique hours & counts
    monthCounts = inputDF['Month'].value_counts(dropna=False).sort_index().tolist()
    monthLabels = inputDF['Month'].value_counts(dropna=False).sort_index().index.tolist()
    
    # Get counts by YYYY-MM
    yyyymmCounts = inputDF['Year-Month'].value_counts(dropna=False).sort_index().tolist()
    yyyymmLabels = inputDF['Year-Month'].value_counts(dropna=False).sort_index().index.tolist()
    yyyymmCounts2017 = inputDF[inputDF['Year'] == 2017]['Year-Month'].value_counts(dropna=False).sort_index().tolist()
    yyyymmLabels2017 = inputDF[inputDF['Year'] == 2017]['Year-Month'].value_counts(dropna=False).sort_index().index.tolist()
    yyyymmCounts2018 = inputDF[inputDF['Year'] == 2018]['Year-Month'].value_counts(dropna=False).sort_index().tolist()
    yyyymmLabels2018 = inputDF[inputDF['Year'] == 2018]['Year-Month'].value_counts(dropna=False).sort_index().index.tolist()

    monthIndex = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # colors
    barColors = ['royalblue']

    # 1. Plot the bar grapgh
    plt.figure(figsize=(12, 8))
    # plt.bar(monthLabels, monthCounts, alpha=0.5, align="center")
    plt.bar(monthLabels, monthCounts, alpha=0.5, align="center", color=barColors)

    # Set the bar chart attributes such as X-Axis, Y-Axis, colors etc.
    # title
    plt.title("Accidents by Month of the Year")

    # X-Axix limits & label: 
    plt.xlim(-0, len(monthLabels)+.5)
    plt.xlabel("Month")
    xlocs, xlabs = plt.xticks()
    xlocs=[i+1 for i in range(0,len(monthCounts))]
    # xlabs=[i+1 for i in range(0,len(monthCounts))]
    xlabs=[i for i in monthIndex]
    plt.xticks(xlocs, xlabs)
    plt.ylim(0, max(monthCounts)+5000)
    plt.ylabel("Count of Accidents")

    # put value labes for Y-Axis 
    for i, v in enumerate(monthCounts):
        # Tip: Adjust -0.10 & +0.01 for positioning the lable text in the bar column
        plt.text(xlocs[i] -0.30, v + 0.01, str(v))

   # Define & Save: Output file - Bar chart
    outputFile = outputFilePath  + outputFileSubPath + 'MonthOfYear_Accidents_Counts.jpg'
    plt.savefig(outputFile)
    plt.close()

    print("Graph plotted: " + outputFile)



    # 2. Plot a line graph comparing monthly progression by year 
    plt.figure(figsize=(12, 8))

    # Set the bar chart attributes such as X-Axis, Y-Axis, colors etc.
    # colors
    lineColors = ['royalblue', 'darkorange' ]
    # title
    plt.title("Accidents per Month for Year 2017 & 2018")
    plt.plot(monthIndex, yyyymmCounts2017, marker = ' ', color = 'royalblue', label = '2017', linewidth=3)
    plt.plot(monthIndex, yyyymmCounts2018, marker = ' ', color = 'darkorange', label = '2018', linewidth=3, )
    plt.legend()


   # Define & Save: Output file - Bar chart
    outputFile = outputFilePath  + outputFileSubPath + 'MonthOfYear_2_Compare_Accidents_Counts.jpg'
    plt.savefig(outputFile)
    plt.close()

    print("Graph plotted: " + outputFile)



####################################################################################################################################################################################
# Function: by Weather  
####################################################################################################################################################################################
def accidentsByWeather(inputDF: pd.DataFrame):

    outputFileSubPath = 'ByWeather/'

    weatherCounts = inputDF['Weather_Condition'].value_counts(ascending = False)
    weatherLabels = inputDF['Weather_Condition'].value_counts(ascending = False).index.tolist()

    barColors = ['royalblue']


    # Count of Accidents by Weather Condition:

    # Plot the bar grapgh
    plt.figure(figsize=(16, 12))
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(weatherLabels[:10])-0.25)
    plt.xlabel("Weather Condition")
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in range(0,len(weatherLabels[:10]))]
    xlabs=weatherLabels[:10]
    plt.xticks(xlocs, xlabs, rotation = 45)
    # Y-Axis limits & label
    plt.ylim(0, max(weatherCounts[:10])+25000)
    plt.ylabel("Count of Accident(s)")
    # Plot the chart
    plt.bar(weatherLabels[:10], weatherCounts[:10], color=barColors, alpha=0.5, align="center")
    plt.title("Accidents by Top 10 Weather Conditions")
    
    # Save output file 
    outputFile = outputFilePath + outputFileSubPath + 'Weather_Accidents_Counts_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



####################################################################################################################################################################################
# Function: by State  
####################################################################################################################################################################################
def accidentsByState(inputDF: pd.DataFrame):

    outputFileSubPath = 'ByState/'

    stateCounts = inputDF['State'].value_counts(ascending = False)
    stateLabels = inputDF['State'].value_counts(ascending = False).index.tolist()

    barColors = ['royalblue']


    # 1. Count of Accidents by State:

    # Plot the bar grapgh
    plt.figure(figsize=(16, 12))
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(stateLabels)-0.25)
    plt.xlabel("State")
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in range(0,len(stateLabels))]
    xlabs=stateLabels
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(stateCounts)+25000)
    plt.ylabel("Count of Accident(s)")
    # Plot the chart
    plt.bar(stateLabels, stateCounts, color=barColors, alpha=0.5, align="center")
    plt.title("Accidents by State(s)")
    ### Commented to not put the Y-Axis tick labels as there are 50 bars (US States)
    # # put value labes for Y-Axis 
    # for i, v in enumerate(stateCounts):
    #     # Tip: Adjust -0.10 & +0.01 for positioning the lable text in the bar column
    #     plt.text(xlocs[i] -0.10, v + 0.01, str(v))
    
    # Save output file 
    outputFile = outputFilePath + outputFileSubPath + 'State_Accidents_1_Counts_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



    # 2. Average severity of accident by State

    # Empty lists for bar chart to be plotted
    stateAvgSev = []
    
    # Extract mean (avg) sev for each state:
    for st in stateLabels:
        meanSev = inputDF[inputDF['State'] == st]['Severity'].mean()
        stateAvgSev.append(round(meanSev,3))

    # Sort the list descending before plotting
    stateLabels2 = stateLabels
    stateAvgSev2 = stateAvgSev
    stateAvgSev2, stateLabels2 = zip(*sorted(zip(stateAvgSev2, stateLabels2), reverse=True))
 

    # Set the plot attributes & Plot the Bar chart
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(stateLabels2)-0.25)
    plt.xlabel("State")
    xlocs, xlabs = plt.xticks()
    xlocs=[i+1 for i in range(0,len(stateAvgSev2))]
    xlabs=[i/2 for i in range(0,len(stateAvgSev2))]
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(stateAvgSev2)+0.500)
    plt.ylabel("Avergare Severity of Accident")
    # Plot the chart:
    plt.figure(figsize=(16, 12))
    plt.bar(stateLabels2, stateAvgSev2, color=barColors, alpha=0.5, align="center")
    plt.title("Average Accidents Severity per State(s)")
    ### Commented to not put the Y-Axis tick labels as there are 50 bars (US States)
    # # put value labes for Y-Axis 
    # for i, v in enumerate(stateAvgSev2):
    #     # Tip: Adjust -1.10 & +0.01 for positioning the lable text in the bar column
    #     plt.text(xlocs[i] -1.10, v + 0.01, str(v))
    
    # Define & Save: Output file - Pie chart
    outputFile = outputFilePath + outputFileSubPath + 'State_Accidents_2_AvgSev_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)

    

    # 3. Weighted Severity Index per 1000 accidents by State
    # Severity = 0, 1, 2, 3, 4
    # Severity Weights = 10, 20, 40, 80, 160 (Total Weight = 310)
    # Total Weighted Severity = ((Count of 0 Sev * 10) + (Count of 1 Sev * 10) + (Count of 2 Sev * 20) + (Count of 3 Sev * 30) + (Count of 4 Sev * 40))/(Total Weight = 310)
    # Weighted Severity Index = Total Weighted Severity / Total Count of Accidents (in  State)
    # Weighted Severity Index per 1000 accidents =  Weighted Severity Index * 1000

    # Empty lists for bar chart to be plotted
    stateWeigthedSevIndex = []

    # Severity weights 
    sevWeight = [10, 20, 40, 80, 160]
    # Extract mean (avg) sev for each state:
    for st in stateLabels:
        sevList = inputDF[inputDF['State'] == st]['Severity'].value_counts(dropna=False).sort_index().index.tolist()
        sevCounts = inputDF[inputDF['State'] == st]['Severity'].value_counts(dropna=False).sort_index().tolist()
                
        # Initialize calculated variables to 0 before calulcation per state
        # Weighted Severity Index per 1000 Accidents 
        weightedSevIndex = 0
        # Calculated Weighted Severity Index per Accident
        totalWeightedSevIndex = 0
        # Calculated Weighted Severity 
        weightedSev = 0
        # Calculated Total Weighted Severity 
        totalWeightedSev = 0
        # Count of Accidents by state
        countByState = 0        
        
        # for each severity found in state
        for i, sev in enumerate(sevList):
            # Note: sev is used as index for sevWeight (instead of i) to be sure that the correct count of severity - 
            # - is used with the matching severity weight as all sev may not be present i a tz
            totalWeightedSev = totalWeightedSev + (sevCounts[i] * sevWeight[sev])
            countByState = countByState + sevCounts[i]

        # Now have data per severity - calculate the final value for state
        weightedSev = totalWeightedSev/sum(sevWeight)
        totalWeightedSevIndex = weightedSev/countByState 
        weightedSevIndex = round((totalWeightedSevIndex * 1000),2)
        stateWeigthedSevIndex.append(weightedSevIndex)
    
    # Done for all states

    # Sort the list descending before plotting
    stateLabels2 = stateLabels
    stateWeigthedSevIndex2 = stateWeigthedSevIndex
    stateWeigthedSevIndex2, stateLabels2 = zip(*sorted(zip(stateWeigthedSevIndex2, stateLabels2), reverse=True))


    # Set the plot attributes & Plot the Bar chart
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(stateLabels2)-0.25)
    plt.xlabel("State")
    xlocs, xlabs = plt.xticks()
    xlocs=[i+1 for i in range(0,len(stateWeigthedSevIndex2))]
    xlabs=[i/2 for i in range(0,len(stateWeigthedSevIndex2))]
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(stateWeigthedSevIndex2)+10.00)
    plt.ylabel("Weighted Severity Index per 1000 Accidents")
    # Plot the chart:
    plt.figure(figsize=(16, 12))
    plt.bar(stateLabels2, stateWeigthedSevIndex2, color=barColors, alpha=0.5, align="center")
    plt.title("Weighted Severity of Accidents in Different State(s) (per 1000 Accidents)")
    ### Commented to not put the Y-Axis tick labels as there are 50 bars (US States)
    # # put value labes for Y-Axis 
    # for i, v in enumerate(stateWeigthedSevIndex2):
    #     # Tip: Adjust -1.10 & +0.01 for positioning the lable text in the bar column
    #     plt.text(xlocs[i] -1.10, v + 0.01, str(v))

    # Define & Save: Output file - Pie chart
    outputFile = outputFilePath + outputFileSubPath + 'State_Accidents_3_WeightedSevIndex_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



    # 4. Bar Chart: Number of accidents by state per year per 1000 people
    # Count of Accidents by state = Number of accidents per state in data analyzed
    # Count of Accidents by state per year = Count of Accidents by state / num of years of data being analyzed
    # Count of Accidents by state per year per person = Count of Accidents by state per year / population of state
    # Count of Accidents by state per year per 1000 people = Count of Accidents by state per year per person * 1000
    
    # Initialize variables used for calcuations:
    # List of Number of accidents per state per year per 1000 people
    stateCountsPerYearPer1000PopulationList = []
    
    # Get Accident per population * 1000 by state in order as present in stateLabels
    for i, st in enumerate(stateLabels):
 
        # Initialize variables used for calcuations:
        # Number of accidents per state per year 
        stateCountsPerYear = 0 
        # Number of accidents per state per year per person
        stateCountsPerYearPerPopulation = 0  
        # Number of accidents per state per year per 1000 people
        stateCountsPerYearPer1000Population = 0 

        # Perform the calulation 
        stateCountsPerYear = stateCounts[i]/numOfYears
        stateCountsPerYearPerPopulation = stateCountsPerYear / statesPopulationDict[st]
        stateCountsPerYearPer1000Population = round((stateCountsPerYearPerPopulation * 1000),3)

        # Add the calculated value to the list for the graph
        stateCountsPerYearPer1000PopulationList.append(stateCountsPerYearPer1000Population)


    # Calculations done - have the data now plot the bar chart  

    # Sort the list descending before plotting
    stateLabels2 = stateLabels
    stateCountsPerYearPer1000PopulationList2 = stateCountsPerYearPer1000PopulationList
    stateCountsPerYearPer1000PopulationList2, stateLabels2 = zip(*sorted(zip(stateCountsPerYearPer1000PopulationList2, stateLabels2), reverse=True))

    # Set the plot attributes & Plot the Bar chart
    plt.figure(figsize=(16, 12))
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(stateLabels2)-0.25)
    plt.xlabel("State")
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in range(0,len(stateLabels2))]
    xlabs=stateLabels2
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(stateCountsPerYearPer1000PopulationList2)+0.250)
    plt.ylabel("Accident(s) per 1000 People")
    # Plot the chart
    plt.bar(stateLabels2, stateCountsPerYearPer1000PopulationList2, color=barColors, alpha=0.5, align="center")
    plt.title("Accidents in Different State(s) per Population of 1000")
    ### Commented to not put the Y-Axis tick labels as there are 50 bars (US States)
    # # put value labes for Y-Axis 
    # for i, v in enumerate(stateCountsPerYearPer1000PopulationList2):
    #     # Tip: Adjust -0.10 & +0.01 for positioning the lable text in the bar column
    #     plt.text(xlocs[i] -0.10, v + 0.01, str(v))
    
    # Save output file 
    outputFile = outputFilePath + outputFileSubPath + 'State_Accidents_4_Counts_1000_People_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



    # 5. Bar Chart: Number of accidents by state per year per 1000 sq miles
    # Count of Accidents by state = Number of accidents per state in data analyzed
    # Count of Accidents by state per year = Count of Accidents by state / num of years of data being analyzed
    # Count of Accidents by state per year per sq miles = Count of Accidents by state per year / land sq miles of state
    # Count of Accidents by state per year per 1000 sq miles = Count of Accidents by state per year per sq miles * 1000
    
    # Initialize variables used for calcuations:
    # List of Number of accidents per state per year per 1000 sql miles
    stateCountsPerYearPer1000SqMilesList = []
    
    # Get Accident per SqMiles * 1000 by state in order as present in stateLabels
    for i, st in enumerate(stateLabels):
 
        # Initialize variables used for calcuations:
        # Number of accidents per state per year 
        stateCountsPerYear = 0 
        # Number of accidents per state per year per person
        stateCountsPerYearPerSqMiles = 0  
        # Number of accidents per state per year per 1000 SqMiles
        stateCountsPerYearPer1000SqMiles = 0 

        # Perform the calulation 
        stateCountsPerYear = stateCounts[i]/numOfYears
        stateCountsPerYearPerSqMiles = stateCountsPerYear / statesLandSqMilesDict[st]
        stateCountsPerYearPer1000SqMiles = round((stateCountsPerYearPerSqMiles * 1000),3)

        # Add the calculated value to the list for the graph
        stateCountsPerYearPer1000SqMilesList.append(stateCountsPerYearPer1000SqMiles)


    # Calculations done - have the data now plot the bar chart  

    # Sort the list descending before plotting
    stateLabels2 = stateLabels
    stateCountsPerYearPer1000SqMilesList2 = stateCountsPerYearPer1000SqMilesList
    stateCountsPerYearPer1000SqMilesList2, stateLabels2 = zip(*sorted(zip(stateCountsPerYearPer1000SqMilesList2, stateLabels2), reverse=True))

    # Set the plot attributes & Plot the Bar chart
    plt.figure(figsize=(16, 12))
    # X-Axix limits & label: 
    plt.xlim(-0.75, len(stateLabels2)-0.25)
    plt.xlabel("State")
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in range(0,len(stateLabels2))]
    xlabs=stateLabels2
    plt.xticks(xlocs, xlabs)
    # Y-Axis limits & label
    plt.ylim(0, max(stateCountsPerYearPer1000SqMilesList2)+500)
    plt.ylabel("Accident(s) per 1000 Sq Miles")
    # Plot the chart
    plt.bar(stateLabels2, stateCountsPerYearPer1000SqMilesList2, color=barColors, alpha=0.5, align="center")
    plt.title("Accidents in Different State(s) per 1000 Sq Miles of Land Area")
    ### Commented to not put the Y-Axis tick labels as there are 50 bars (US States)
    # # put value labes for Y-Axis 
    # for i, v in enumerate(stateCountsPerYearPer1000SqMilesList2):
    #     # Tip: Adjust -0.10 & +0.01 for positioning the lable text in the bar column
    #     plt.text(xlocs[i] -0.10, v + 0.01, str(v))
    
    # Save output file 
    outputFile = outputFilePath + outputFileSubPath + 'State_Accidents_5_Counts_1000_SqMiles_Bar.jpg'
    plt.savefig(outputFile)
    plt.close()
    print("Graph plotted: " + outputFile)



####################################################################################################################################################################################
# Function: by Hourss of the Day per Month of Year  
####################################################################################################################################################################################
def accidentsByMonthByHours(inputDF: pd.DataFrame):

    outputFileSubPath = 'ByMonth/ByHour/'

    # Get unique months
    monthCounts = inputDF['Year-Month'].value_counts(dropna=False).sort_index().tolist()
    monthLabels = inputDF['Year-Month'].value_counts(dropna=False).sort_index().index.tolist()

    # Hours Index for labels
    hourIndex = ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10', '10-11', '11-12', '12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24']

    # Plot attributes 
    plt.figure(figsize=(16, 12))
    plt.title("Accidents per Hour by Month of Year")

    # Repeat for each month:
    for m in monthLabels:
        # Get unique hours & counts
        hourCounts = inputDF[inputDF['Year-Month'] == m]['Hour'].value_counts(dropna=False).sort_index().tolist()
        # hourLabels = inputDF[inputDF['Month'] == m]['Hour'].value_counts(dropna=False).sort_index().index.tolist()
        plt.plot(hourIndex, hourCounts, marker = ' ', label = str(m), linewidth=2)

    # Done all months 
    plt.legend()

   # Define & Save: Output file - Bar chart
    outputFile = outputFilePath  + outputFileSubPath + 'Accidents_Hour_MonthOfYear_1_Compare_Accidents_Counts.jpg'
    plt.savefig(outputFile)
    plt.close()

    print("Graph plotted: " + outputFile)



####################################################################################################################################################################################
