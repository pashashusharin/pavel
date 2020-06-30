# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 14:46:47 2019

@author: pshusharin
"""
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import os 
import xlsxwriter

def get_data(filename):  
    '''This function gets the data from a single file and returns formatted data for visualization'''
    df = pd.read_csv(filename, skiprows = 5,sep = '\s+')
    plt.ion() # turns on interactive mode so that I can analyze Profile timing if I wanted to 

    max_lh = []
    wire_num = [] 
    span_ht = []
    for j in df.Index.unique():       # for loop for DEVICE ID 
        a = df[df.Index == j]
        for i in a.Wire.unique():     # for loop for WIRE ID 
            b = a[a.Wire == i]        # this is a 4 by 25 data frame  
            wire_num.append(i)                          # this is wire number column 
            max_lh.append(max(b['LoopHtFromRefBond']))                           # fill in the Max LH in the list 
            span_ht.append(b['EdgeHeight'][b.EdgeHeight.notnull()].values[0])    # fill in the Span HT values for non-zero instances non-zero instances 
    
    #Define 5 lists for each wire group 
    g1 = list(range(17,25)) + list(range(41,51)) + list(range(71,79)) + list(range(95,105))
    g2 = list(range(25,33)) + list(range(51,61)) + list(range(79,87)) + list(range(105,115)) 
    g4 = list(range(33,41)) + list(range(61,71)) + list(range(87,95)) + list(range(115,125))
    g3 = list(range(125,161))
    g5 = list(range(161,197))
    
    new_data = []   #empty list to be converted into a data frame 
    group_num = []  #empty list as a placeholder for group number 
    for i,x in enumerate(wire_num): 
        if x in g1:
            group_num.append(1)
        elif x in g2: 
            group_num.append(2)
        elif x in g4: 
            group_num.append(4)
        elif x in g3: 
            group_num.append(3)
        elif x in g5: 
            group_num.append(5)
        #combine all the useful data into a dictionary     
        new_data.append({'Wire': x, 
                        'max_lh': max_lh[i],
                        'span_ht': span_ht[i],
                        'group_num': group_num[i]}) 
    
    good_data = pd.DataFrame(new_data) #Changed from new_data
    #filter the negative and very high positive values from both rows in a new database 
    #good_data = new_data[(new_data['max_lh'] < 500) & (new_data['max_lh'] > 50) \
    #                     & (new_data['span_ht'] < 450) & (new_data['span_ht'] > 0)]
    return os.path.split(filename)[1], good_data

def cumulative_graph(good_data):
    '''This function returns 2 Whiskers plots of Max LH and Span HT for each 5 groups '''
    plt.rcParams['figure.figsize'] = (15, 7)
    plt.rcParams['xtick.labelsize'] = (15.0)
    plt.rcParams['ytick.labelsize'] = (15.0)
    plt.rcParams['axes.titlesize'] = (20.0)
    plt.rcParams['axes.labelsize'] = (20.0)
    
    lh_by_group = []                                 #Define empty list for plotting loop heights 
    sp_by_group = []                                 #Define empty list for plotting span heights
    lh_sum = []                                      #Define empty list for summary statistics for loop heights 
    sp_sum = []                                      #Define empty list for summary statistics for loop heights 
    #Combine all the Wires in same Groups together and create summary tables 
    for count, i in enumerate(good_data.group_num.unique()): 
        data_by_group = good_data[good_data.group_num == i]
        lh_by_group.append(data_by_group.max_lh)              
        sp_by_group.append(data_by_group.span_ht)
        lh_sum.append(data_by_group.max_lh.describe())
        sp_sum.append(data_by_group.span_ht.describe())
    
    #Format the Summary Tables 
    lh_sum = pd.DataFrame(lh_sum).T
    sp_sum = pd.DataFrame(sp_sum).T
    lh_sum.columns = ['G1-76.2(um)','G2-127(um)','G4-304.8(um)','G3-203.2(um)','G5-406.4(um)' ]
    sp_sum.columns = ['G1-76.2(um)','G2-127(um)','G4-304.8(um)','G3-203.2(um)','G5-406.4(um)' ]
    #lh_sum.drop(['25%','50%', '75%'],inplace=True)
    #sp_sum.drop(['25%','50%', '75%'],inplace=True)
    lh_sum = lh_sum.round(2)
    sp_sum = sp_sum.round(2)
    
    # PLOT The data 
    # Another way to define fig1,(ax1,ax2) = plt.subplots(1,2)
    # the_list = plt.subplots(1,2)
    # fig = the_list[0]
    # ax1 = the_list[1][0]
    # ax2 = the_list[1][1]   
    
    fig1,(ax1,ax2) = plt.subplots(1,2)
    ax1.set_title('Max Loop Height', loc ='Center')
    ax1.boxplot(lh_by_group, whis = 'range')
    ax1.set_ylabel('Loop Height (um)')
    ax1.set_xlabel('Group Number')
    
    ax2.set_title('Span Height', loc ='Center')
    ax2.boxplot(sp_by_group, whis = 'range')
    ax2.set_ylabel('Loop Height (um)')
    ax2.set_xlabel('Group Number')
    plt.show()
    
    return lh_sum, sp_sum

gr_names ={1: 'Group 1 - 76.2(um)',
           2: 'Group 2 - 127(um)', 
           3: 'Group 3 - 203.2(um)',
           4: 'Group 4 - 304.8(um)',
           5: 'Group 5 - 406.4(um)'}

def comp_graph(lis):
    plt.rcParams['figure.figsize'] = (15, 7)
    plt.rcParams['figure.titlesize'] = (15.0)
    plt.rcParams['xtick.labelsize'] = (10.0)
    plt.rcParams['ytick.labelsize'] = (10.0)
    plt.rcParams['axes.titlesize'] = (12.0)
    plt.rcParams['axes.labelsize'] = (12.0)
    
    df_lh_sum = []
    df_sp_sum = []
    data_lis = [] 
    name_lis = []
    #First, split the list of tuples - 'lis' into two different lists 
    for count, i in enumerate(lis):
        name_lis.append(lis[count][0])
        data_lis.append(lis[count][1])
    #Split the list of data frames by group and instantiate the plots for each of the groups 
    #j is a group number - 1,2,3,4,5    
    for j in data_lis[0].group_num.unique():
        fig1,(ax1,ax2) = plt.subplots(1,2) 
        fig1.suptitle(gr_names[j]) 
        
        mlh = {}
        sph = {}
        lh_by_dataset = []
        sp_by_dataset = []
        #split the data by files
        #k is a data from a particular file
        for count, k in enumerate(data_lis):
            f = k
            dataset = k
            #split loop height and span height information and asign it to mlh and sph dictionarties
            mlh[name_lis[count]] = f[f['group_num'] == j]['max_lh']
            sph[name_lis[count]] = f[f['group_num'] == j]['span_ht']
            #convert the dictionary into dataframes
            mlh = pd.DataFrame(mlh)
            sph = pd.DataFrame(sph) 
            #append data sets for loop height and span height
            lh_by_dataset.append(dataset[dataset.group_num == j].max_lh.values.T)
            sp_by_dataset.append(dataset[dataset.group_num == j].span_ht.values.T)
            
        df_by_group_lh = pd.DataFrame(lh_by_dataset, index=name_lis).T
        df_by_group_sp = pd.DataFrame(sp_by_dataset, index=name_lis).T
        df_by_group_lh_sum = df_by_group_lh.describe()
        df_by_group_sp_sum = df_by_group_sp.describe()
        df_by_group_lh_sum.drop(['25%','50%', '75%'],inplace=True)
        df_by_group_sp_sum.drop(['25%','50%', '75%'],inplace=True)
        df_lh_sum.append(df_by_group_lh_sum)
        df_sp_sum.append(df_by_group_sp_sum)
        
        #Use Average of a baseline as a Y axis center point
        '''y_lh_cen = df_lh_sum[-1].iloc[:,0].mean
        y_sp_cen = df_sp_sum[-1].iloc[:,0].mean
        y_lh_low = y_lh_cen - 50
        y_lh_high = y_lh_cen + 50
        y_sp_low = y_sp_cen - 70
        y_sp_high = y_sp_cen + 70'''
        
        #Plotting
        mlh.boxplot(ax = ax1, grid = False)
        ax1.set_title('Max Loop Height', loc ='Center')
        ax1.set_ylabel('Loop Height (um)')
        ax1.set_xlabel('Data Set')
        #ax1.set_ylim(y_lh_low, y_lh_high)
        
        sph.boxplot(ax = ax2, grid = False)
        ax2.set_title('Span Height', loc ='Center')
        ax2.set_ylabel('Loop Height (um)')
        ax2.set_xlabel('Data Set')     
        #ax2.set_ylim(y_sp_low, y_sp_high)
        
        #Create pictures of each subplot
        fig1.savefig('{}.png'.format(gr_names[j]))    
        
    #Create a summary Excel file with the Two sheets, one for Loop Heights, one for Span Heights     
    with pd.ExcelWriter('Summary_By_Group4.xlsx') as writer:
        t = 0                   #Counters for rows 
        r = 0
        for i in df_lh_sum:
            i.to_excel(writer, sheet_name ='Loop_Heights', startrow = t)
            t = t + 6
        for j in df_sp_sum:
            j.to_excel(writer, sheet_name ='Span_Heights', startrow = r)
            r = r + 6
    return df_lh_sum, df_sp_sum

#m = get_data(r'L:\_Looping Development-2013\Pavel\ProAu\Run 6 Arc 2nd Approach\R6ARC.DAT')
#p = get_data(r'L:\_Looping Development-2013\Pavel\ProAu\Run 4 LF0\LF0.DAT')
b = get_data(r'L:\_Looping Development-2013\Pavel\ProAu\Run 6 Arc 2nd Approach\Data Analysis\6_1_LH3.DAT')



lis2 = [b]
          
comp_graph(lis2)

#cumulative_graph(b[1])










