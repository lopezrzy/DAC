import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from lmfit import Model, Parameters, Minimizer, report_fit
from sklearn.metrics import r2_score


def percent_errorRefvsModel(dataref, datafit):
    reference_adsorption = dataref['Quantity Adsorbed (mmol/g)'] 
    fitModel_adsorption = datafit['Quantity Adsorbed (mmol/g)'] 
    percent_error= np.mean(abs((fitModel_adsorption - reference_adsorption) / reference_adsorption) * 100)
    return percent_error

def import_isotherms4(comp, temp, run_number):
    sample_mass=[]
    data= []
    for i in range(len(temp)):
        df=pd.read_excel(path+'files/000-'+run_number[i]+' Absolute Pressure '+comp+' '+temp[i]+'C.xls')
        
        sample_mass.append(float(df.iloc[13,1].split(' ')[0]))
        df = df.reset_index(drop=True).iloc[26:]
        df.columns=df.iloc[0]
        df = df.reset_index(drop=True).iloc[2:]
        df = df[df['Quantity Adsorbed (mmol/g)'] >= 0]
        df = df.reset_index(drop=True)
        data.append(df)
        
    datafiltered=[]
    for i in range(len(temp)):
        data2=data[i][['Absolute Pressure (kPa)', 'Quantity Adsorbed (mmol/g)']].apply(pd.to_numeric, errors='coerce')
        decrease_index = data2['Absolute Pressure (kPa)'].diff().lt(0).idxmax()
        #data2['Absolute Pressure (kPa)']=data2['Absolute Pressure (kPa)']/100
        data2['Temperature C']= int(temp[i])
        # Filter out the rows after the decrease index
        #data2.rename(columns={'Quantity Adsorbed (mmol/g)': 'Quantity Adsorbed (mmol/g)'+temp[i]}, inplace=True)
        #data2.rename(columns={'Absolute Pressure (kPa)': 'Absolute Pressure (bar)'+temp[i]}, inplace=True)

        datafiltered.append(data2.loc[:decrease_index-1])
        
    return datafiltered

def dsl_T_model_func(x,q1, bo1, H1,q2, bo2, H2):
    #x=np.transpose(x)
    T, P = x
    #R=8.31446261815324 #J⋅K−1⋅mol−1
    # H1, H2 in J/mol
    #T=(T+273.15)
    b1 = bo1 * np.exp(-H1 / (8.31446261815324 * (T + 273.15)))
    b2 = bo2 * np.exp(-H2 / (8.31446261815324 * (T + 273.15)))
    return (q1 * b1 * P / (1 + b1 * P) + q2 * b2 * P / (1 + b2 * P))

def dsl_model_func(x,q1, b1, q2, b2):
    T, P = x
    return (q1 * b1 * P / (1 + b1 * P) + q2 * b2 * P / (1 + b2 * P))

#Van’t Hoff
def vantHoff_model_func(x, bo, H):
    T = x
    return bo * np.exp(-(H) / (8.31446261815324 * (T + 273.15)))

# When th,ese parameters are inserted into the regular Toth
# isotherm as a function of temperature, then the TD Toth
# isotherm (q as a function of c) becomes a correlation with
# a total of seven parameters: bo, (Q/RTo), To, to, α, qso,
# and χ
def toth_model_func(x, bo, Q, To, to, alpha, qso, chi):
    # χ chi
    T, P = x
    R=8.31446261815324 #J⋅K−1⋅mol−1
    T=(T+273.15)
    b=bo*np.exp(Q/(R*To)*(To/T-1))
    qs=qso*np.exp(chi*(1-T/To))
    t=to+alpha*(1-To/T)
    return qs*b*P/((1+((b*P)**t))**(1/t))

def KH_temp_func(x, DH, KHx):
    T, P = x
    R=8.31446261815324 #J⋅K−1⋅mol−1
    T=(T+273.15)
    return KHx*np.exp(DH/(R*T))*P

def linear_T_func(x, m, D):
    T, P = x
    return m*P*np.exp(D/(T+273.15))

def execute_Model(data, modelN, iv):
    #iv initial values
       
    if modelN== 'dsl_T':
        parametersString=['q1', 'bo1', 'H1', 'q2', 'bo2', 'H2']
        q1i, bo1i, H1i, q2i, bo2i, H2i = iv
        T_data = data['Temperature C']
        P_data = data['Absolute Pressure (kPa)'] 
        X_data = np.array([T_data, P_data])
        Y_data = np.array(data['Quantity Adsorbed (mmol/g)'])
        # Create an lmfit Model object
        model = Model(dsl_T_model_func) 
        # Set initial parameter values
        model.set_param_hint('q1', value=q1i, vary=False)
        model.set_param_hint('bo1', value=bo1i)
        model.set_param_hint('H1', value=H1i)
        model.set_param_hint('q2', value=q2i, vary=False)
        model.set_param_hint('bo2', value=bo2i)
        model.set_param_hint('H2', value=H2i)
        # Perform the fitting
        result = model.fit(Y_data, x=X_data)
        
    elif modelN== 'dsl_LP':
        parametersString=['q1', 'b1', 'q2', 'b2']
        q1i, b1i, q2i, b2i = iv      
        T_data = data['Temperature C']
        P_data = data['Absolute Pressure (kPa)'] 
        X_data = np.array([T_data, P_data])
        Y_data = np.array(data['Quantity Adsorbed (mmol/g)'])
        # Create an lmfit Model object
        model = Model(dsl_model_func) 
        # Set initial parameter values
        params = Parameters()         
        params.add('q1', value=q1i, vary= True)    
        params.add('b2', value=b2i, vary=True)
        params.add('delta2', value=0.01, min=0.001, vary=True)
        #params.add('delta2', value=0.00002, min=0.00001, vary=True) #gives bad results
        params.add('b1', expr='delta2+b2')
        params.add('q2', expr='(0.9922-q1*b1)/b2')
        result = model.fit(Y_data, x=X_data, params=params) 
        # force q1>q2 & b1>b2 :
        # params.add('b2', value=b2i, vary=True)
        # params.add('delta2', value=0.01, min=0.001, vary=True)
        # params.add('delta3', value=0.01, min=0.001, vary=True)
        # params.add('b1', expr='delta2+b2')
        # params.add('q1', expr='delta3+ 0.922/(b1+b2)') 
        # params.add('q2', expr='(0.9922-q1*b1)/b2-delta3')
        
        result = model.fit(Y_data, x=X_data, params=params) 
        
    elif modelN== 'dsl_HP':
        parametersString=['q1', 'b1', 'q2', 'b2']
        q1i, b1i, q2i, b2i = iv
        T_data = data['Temperature C']
        P_data = data['Absolute Pressure (kPa)'] 
        X_data = np.array([T_data, P_data])
        Y_data = np.array(data['Quantity Adsorbed (mmol/g)'])
        # Create an lmfit Model object
        model = Model(dsl_model_func) 
        # Set initial parameter values
        params = Parameters()         
        params.add('q1', value=q1i, vary=False)
        params.add('q2', value=q2i, vary=False) 
        #params.add('delta2', value=0.00002, min=0.00001, vary=True) #gives bad results
        params.add('delta2', value=0.01, min=0.001, vary=True)
        params.add('b1', expr='delta2+0.9922/(q1+q2)')
        # to avoid negative values in b2: comment the previus delta2 and b1, and uncomment:
        #params.add('b1', value=b1i, max=0.9921/q1i, vary=True) #expr='0.9921/q1-delta2')
        params.add('b2', expr='(0.9922-q1*b1)/q2')   
        result = model.fit(Y_data, x=X_data, params=params)  

    elif modelN== 'vantHoff':    
        parametersString=['bo', 'H']
        boi, Hi = iv
        T_data, b = data
        # Create an lmfit Model object
        model = Model(vantHoff_model_func) 
        # Set initial parameter values
        params = Parameters()         
        params.add('bo', value=boi, vary=True)
        params.add('H', value=Hi, vary=True)
        result = model.fit(b, x=T_data, params=params)
        
    elif modelN== 'dsl_T_step4':
        parametersString=['q1', 'bo1', 'H1', 'q2', 'bo2', 'H2']
        q1i, bo1i, H1i, q2i, bo2i, H2i = iv
        T_data = data['Temperature C']
        P_data = data['Absolute Pressure (kPa)'] 
        X_data = np.array([T_data, P_data])
        #X_data = np.column_stack([T_data, P_data])
        Y_data = np.array(data['Quantity Adsorbed (mmol/g)'])
        # Create an lmfit Model object
        model = Model(dsl_T_model_func) 
        # Set initial parameter values
        params = Parameters()   
        params.add('q1', value=q1i, vary=False)
        params.add('q2', value=q2i, vary=False)
        # params.add('bo1', value=bo1i)
        params.add('bo2', value=bo2i)
        # params.add('H1', value=H1i)
        # params.add('H2', value=H2i)
        params.add('delta', value=15, min=14.5, vary=True)
        params.add('bo1', expr='delta+bo2')
        params.add('H2', value=H2i, vary=True)
        params.add('deltaH', value=38400, min=38000, vary=True)
        params.add('H1', expr='deltaH+H2')   
        # Perform the fitting
        result = model.fit(Y_data, x=X_data, params=params)#, nan_policy='omit')

    elif modelN== 'toth': #
        parametersString=['bo', 'Q', 'To', 'to', 'alpha', 'qso', 'chi']
        boi, Qi, Toi, toi, alphai, qsoi, chii = iv
        T_data = data['Temperature C']
        P_data = data['Absolute Pressure (kPa)'] 
        X_data = np.array([T_data, P_data])
        #X_data = np.column_stack([T_data, P_data])
        Y_data = np.array(data['Quantity Adsorbed (mmol/g)'])
        # Create an lmfit Model object
        model = Model(toth_model_func) 
        # Set initial parameter values
        params = Parameters()   
        params.add('bo', value=boi)
        params.add('Q', value=Qi)
        params.add('To', value=Toi)
        params.add('to', value=toi)
        params.add('alpha', value=alphai)
        params.add('qso',value=qsoi)
        params.add('chi',value=chii)       
        # Perform the fitting
        result = model.fit(Y_data, x=X_data, params=params)#, nan_policy='omit')     
    elif modelN== 'KH_Temp':    
        parametersString=['DH', 'KHx']
        DHi, KHxi = iv
        T_data = data['Temperature C']
        P_data = data['Absolute Pressure (kPa)'] 
        X_data = np.array([T_data, P_data])
        Y_data = np.array(data['Quantity Adsorbed (mmol/g)'])
        # Create an lmfit Model object
        model = Model(KH_temp_func) 
        # Set initial parameter values
        params = Parameters()         
        params.add('DH', value=DHi, vary=True)
        params.add('KHx', value=KHxi, vary=True)
        result = model.fit(Y_data, x=X_data, params=params)
    elif modelN== 'linear_T':    
        parametersString=['m', 'D']
        mi, Di = iv
        T_data = data['Temperature C']
        P_data = data['Absolute Pressure (kPa)'] 
        X_data = np.array([T_data, P_data])
        Y_data = np.array(data['Quantity Adsorbed (mmol/g)'])
        # Create an lmfit Model object
        model = Model(linear_T_func) 
        # Set initial parameter values
        params = Parameters()         
        params.add('m', value=mi, vary=True)
        params.add('D', value=Di, vary=True)
        result = model.fit(Y_data, x=X_data, params=params)  
    parameters=[]
    paramError=[]
    print('Optimized parameters')
    for i in range(len(iv)):
        parameters.append(result.params[parametersString[i]].value)
        paramError.append(result.params[parametersString[i]].stderr)
    print(f"{parametersString}: {parameters}")
    print(f"Error: +/- {paramError}")

    return parameters, paramError

def get_isoFitDataDataFrame(parameters_opt,datarefDF, modelN):
    pressure=datarefDF['Absolute Pressure (kPa)']
    temp=datarefDF['Temperature C']   
    if modelN=='dsl_T' or modelN=='dsl_T_step4':
        q1_opt, bo1_opt, H1_opt,q2_opt, bo2_opt, H2_opt=parameters_opt
        q=dsl_T_model_func([temp, pressure], q1_opt, bo1_opt, H1_opt,q2_opt, bo2_opt, H2_opt) 
    if modelN=='toth':
        bo, Q, To, to, alpha, qso, chi =parameters_opt
        q=toth_model_func([temp, pressure], bo, Q, To, to, alpha, qso, chi)
    if modelN=='dsl':
        q1, b1, q2, b2 =parameters_opt
        q=dsl_model_func([temp, pressure], q1, b1, q2, b2)
    if modelN=='KH_Temp':
        DH, KHx =parameters_opt
        q=KH_temp_func([temp, pressure], DH, KHx)
    if modelN=='linear_T':
        m, D =parameters_opt
        q=linear_T_func([temp, pressure], m, D)
    isoFitDF=pd.DataFrame({'Absolute Pressure (kPa)':pressure,'Quantity Adsorbed (mmol/g)':q, 'Temperature C':temp })
    return isoFitDF

def get_isoFitDataList(parameters_opt, dataref, tempList ,modelN):
    temp_int = list(map(int, tempList)) 
    z1=[]
    for i in range(len(temp_int)):
        z1.append(get_isoFitDataDataFrame(parameters_opt, dataref[i], modelN))
    return z1

def plotModel(parameters_opt, dataref, temp,pressure_Range, unit, log, colors, modelN):
    Pi, Pf = pressure_Range
    temp_int = list(map(int, temp))
    pressure=np.logspace(np.log10(Pi), np.log10(Pf), 1000)
    z1=[]
    modelN2=modelN.split('_')[0].capitalize()
    if modelN=='dsl_T' or modelN=='dsl_T_step4':
        q1_opt, bo1_opt, H1_opt,q2_opt, bo2_opt, H2_opt=parameters_opt
        for i in range(len(temp_int)):
            z1.append(dsl_T_model_func([np.full(1000, temp_int[i]), pressure], q1_opt, bo1_opt, H1_opt,q2_opt, bo2_opt, H2_opt))
    if modelN=='toth':
        bo, Q, To, to, alpha, qso, chi =parameters_opt
        for i in range(len(temp_int)):
            z1.append(toth_model_func([np.full(1000, temp_int[i]), pressure], bo, Q, To, to, alpha, qso, chi))        
    if modelN=='dsl':
        q1, b1, q2, b2 =parameters_opt
        for i in range(len(temp_int)):
            z1.append(dsl_model_func([np.full(1000, temp_int[i]), pressure], q1, b1, q2, b2))          
    if modelN=='KH_Temp':
        DH, KHx =parameters_opt
        for i in range(len(temp_int)):
            z1.append(KH_temp_func([np.full(1000, temp_int[i]), pressure], DH, KHx))          
    if modelN=='linear_T':
        m, D =parameters_opt
        for i in range(len(temp_int)):
            z1.append(linear_T_func([np.full(1000, temp_int[i]), pressure], m, D)) 
    #filter dataref only in pressure range
    datarefFilt=[]
    for df in dataref:
        datarefFilt.append(df[df['Absolute Pressure (kPa)'].between(Pi, Pf)])
        
    if unit=='bar':
        fig, ax = plt.subplots(1, figsize=(8, 5))
        for i in range(len(temp_int)):
            plt.plot(pressure/100, z1[i], label=temp[i]+' °C, ' +modelN2 +' fit ', color=colors[i], mfc='none')
            plt.plot(datarefFilt[i]['Absolute Pressure (kPa)']/100, datarefFilt[i]['Quantity Adsorbed (mmol/g)'], label=temp[i]+' °C, Experimental ', color=colors[i],  mfc='none', linestyle='dotted', marker='.')
            #plt.plot(dataref[i]['Absolute Pressure (kPa)']/100, dataref[i]['Quantity Adsorbed (mmol/g)'], label=temp[i]+' °C, Experimental ', color=colors[i],  mfc='none', linestyle='dotted', marker='.')
        if log==True:
            plt.xscale('log')
            plt.yscale('log')
        plt.xlabel('Absolute Pressure (bar)')
        plt.ylabel('Quantity Adsorbed (mmol/g)')
        plt.legend()
        plt.show()
    if unit=='ppm':
        x=pressure/100*1000000 
        for i in range(len(temp_int)):
            plt.plot(x, z1[i], label=temp[i]+' °C, ' +modelN2 +' fit ', color=colors[i], mfc='none')
            plt.plot(datarefFilt[i]['Absolute Pressure (kPa)']/100*1000000, datarefFilt[i]['Quantity Adsorbed (mmol/g)'], label=temp[i]+' °C, Experimental ', color=colors[i],  mfc='none', linestyle='dotted', marker='.')
        plt.axvline(x=400, color='black', linestyle='--')
        if log==True:
            plt.xscale('log')
            plt.yscale('log')
        plt.xlabel('CO2 concentration (ppm)')
        plt.ylabel('Quantity Adsorbed (mmol/g)')
        plt.legend()
        plt.show()
    return None

def find_HK(co2datafilteredLowTemp):
    #find KH from the lowest temperature data
    co2data_5=co2datafilteredLowTemp[co2datafilteredLowTemp['Absolute Pressure (kPa)'].between(0, 1)]
    co2data_5['Q/p']=co2data_5['Quantity Adsorbed (mmol/g)']/(co2data_5['Absolute Pressure (kPa)'])
    plt.plot(co2data_5['Absolute Pressure (kPa)'], co2data_5['Q/p'],marker='.')
    plt.xlabel('Loading (mmol/g)')
    plt.ylabel('q/p')
    
    x1=co2data_5['Quantity Adsorbed (mmol/g)'][0]
    x2=co2data_5['Quantity Adsorbed (mmol/g)'][1] 
    y1=co2data_5['Q/p'][0]
    y2=co2data_5['Q/p'][1]
    #KH Henry's constant. KH: 
    slope = (y2 - y1) / (x2 - x1)
    HK = y1 - slope * x1
    return HK

# this is the same as Van't Hoffs eq in execute_model
def find_bo1(bT1, bT2, T1, T2):
    T1= T1 + 273.15
    T2= T2 + 273.15
    return np.exp((T1 * np.log(bT1) - T2 * np.log(bT2)) / (T1 - T2))

def estimateQatLowPressures(co2datafiltered, typeOfFit ):
    co2datafiltered2=[]
    i=0
    # a & b from Fitting Parameters.xlsx - excel interp
    if typeOfFit=='power':
        a =	[0.062309435	, 0.025470532,	0.018945961,	   0.010939802,	 0.009159665]
        b =	[0.404472412	, 0.361801172,	0.253867774,	   0.258667284, 	0.381651783]
        for df in co2datafiltered:
            df2=pd.DataFrame()
            p=np.logspace(np.log10(0.0015), np.log10(df['Absolute Pressure (kPa)'][0]), 50)
            df2['Absolute Pressure (kPa)']=p[:-1]
            df2['Quantity Adsorbed (mmol/g)'] = a[i]*(df2['Absolute Pressure (kPa)'])**b[i]
            df2['Temperature C']=np.full(49, df['Temperature C'][0])
            co2datafiltered2.append(pd.concat([df2, df], ignore_index=True))
            i=i+1
    elif typeOfFit=='linear':
        a = [0.096369,	0.025682	, 0.015692,	0.008044	, 0.002887]
        b = [0.011799,	0.008374	, 0.008924,	0.005399	, 0.005597]
        for df in co2datafiltered:
            df2=pd.DataFrame()
            p=np.logspace(np.log10(0.0015), np.log10(df['Absolute Pressure (kPa)'][0]), 50)
            df2['Absolute Pressure (kPa)']=p[:-1]
            df2['Quantity Adsorbed (mmol/g)'] = a[i]*(df2['Absolute Pressure (kPa)'])+b[i]
            df2['Temperature C']=np.full(49, df['Temperature C'][0])
            co2datafiltered2.append(pd.concat([df2, df], ignore_index=True))
            i=i+1
    elif typeOfFit=='linear2':
        a = [0.120281,	0.029464	, 0.019267,	0.009525	, 0.003558]
        b = [0.011799,	0.007954,	0.008509	, 0.005178,	0.005354]
        for df in co2datafiltered:
            df2=pd.DataFrame()
            p=np.logspace(np.log10(0.0015), np.log10(df['Absolute Pressure (kPa)'][0]), 50)
            df2['Absolute Pressure (kPa)']=p[:-1]
            df2['Quantity Adsorbed (mmol/g)'] = a[i]*(df2['Absolute Pressure (kPa)'])+b[i]
            df2['Temperature C']=np.full(49, df['Temperature C'][0])
            co2datafiltered2.append(pd.concat([df2, df], ignore_index=True))
            i=i+1            
    return co2datafiltered2  

def FoM_fit(dataref, datafit, temperature, pf):
        #FoM figures of merit
    FoM=pd.DataFrame({'Temperature':temperature, 'Percentual Error': temperature, 'R2 Score': temperature})
    for i in range(len(temperature)):
        datarefDF=dataref[i][dataref[i]['Absolute Pressure (kPa)']<=pf]
        datafitDF=datafit[i][datafit[i]['Absolute Pressure (kPa)']<=pf]
        FoM['Percentual Error'][i] =percent_errorRefvsModel(datarefDF, datafitDF )
        FoM['R2 Score'][i] = r2_score(datarefDF['Quantity Adsorbed (mmol/g)'],  datafitDF['Quantity Adsorbed (mmol/g)'])
    return FoM

## DSL TEST with reference data: all pressures, low pressures, and high pressures
# using the DSL equation directly 
path='/Users/lopezrzy/Documents/CEA/CRBNET/Isotherms/'

comp='CO2'
# tempCO2=['-5', '20', '40', '60', '75']
# run_numberCO2= ['782', '785', '785', '786','799']
tempCO2=['-5', '20', '40', '60']
run_numberCO2= ['782', '785', '785', '786']
modelN='toth'

co2datafiltered= import_isotherms4(comp, tempCO2, run_numberCO2) 
co2datacombined = pd.concat(co2datafiltered, ignore_index=True)
co2datacombined=co2datacombined[co2datacombined['Absolute Pressure (kPa)']<101]

co2datacombinedLowP=co2datacombined[co2datacombined['Absolute Pressure (kPa)']<10]
co2datacombinedHighP=co2datacombined[co2datacombined['Absolute Pressure (kPa)']>=10]

iv=[1.169, 0.004, -12, 0.1518, 0.89, 21]
colors=['black','blue','darkmagenta','orangered','red']
print('All pressure range')
parameters_opt, parametersE_opt = execute_Model(co2datacombined, 'dsl_T', iv)
plotModel(parameters_opt, co2datafiltered, ['-5', '20', '40', '60'],[0.02, 100],'ppm', True, colors,'dsl_T')
plotModel(parameters_opt, co2datafiltered, ['-5', '20', '40', '60'],[0.02, 100],'bar', True, colors,'dsl_T')

print('Low pressure parameters')
iv=[0.44, 4, -80, 0.04, 2000, 9.4]
parameters_optLP, parametersE_optLP= execute_Model(co2datacombinedLowP, 'dsl_T', iv)
plotModel(parameters_optLP, co2datafiltered, ['-5', '20', '40', '60'], [0.02,10], 'ppm', True, colors,'dsl_T')

print('High pressure parameters')
iv=[1.855, 0.24, -8, 0.293, 11, 96]
parameters_optHP, parametersE_optHP = execute_Model(co2datacombinedHighP, 'dsl_T', iv)
parameters_optHP=[1.855, 0.24, -8, 0.293, 11, 96]
plotModel(parameters_optHP, co2datafiltered, ['-5', '20', '40', '60'], [10,100], 'ppm', True, colors,'dsl_T')


############################################################################
############################################################################

# DSL MODEL:  fitting Procedure # 3 OF PAPER

path='/Users/lopezrzy/Documents/CEA/CRBNET/Isotherms/'
comp='CO2'
tempCO2=['-5', '20', '40', '60', '75']
run_numberCO2= ['782', '785', '785', '786','799']
colors=['black','blue','darkmagenta','orangered','red']

co2datafiltered= import_isotherms4(comp, tempCO2, run_numberCO2) 

##### ADD ESTIMATED VALUES AT LOW PRESSURES
co2datafiltered=estimateQatLowPressures(co2datafiltered,'power')

co2datacombined = pd.concat(co2datafiltered, ignore_index=True)

# Keep only kpa> 100 (for a test, i added to the '-5 C file' some estimated 
# concentration values for pressures above 100 kPa )
co2datacombined=co2datacombined[co2datacombined['Absolute Pressure (kPa)']<=101]

# # # # # # # # # STEP 1 : 
#HK= find_HK (co2datafiltered[0])
# 🚨 put HK in execute_Model   ->   dsl_LP & dsl_HP

print('Step 1. Initial parameters (-5 C)')
params_5C, paramsE_5C = execute_Model(co2datacombined[co2datacombined['Temperature C']==-5],'dsl_LP',[1.6, 10, 0.6, 0.01])
plotModel(params_5C, [co2datafiltered[0]], ['-5'],[0.03, 100],'bar', True, colors, 'dsl')

# step 1 with high pressure data (kpa >10)
#co2datacombinedHighP=co2datacombined[co2datacombined['Absolute Pressure (kPa)']>=10]
#params_5C, paramsE_5C = execute_Model(co2datacombinedHighP[co2datacombinedHighP['Temperature C']==-5],'dsl_LP',[0.22, 4.3, 1.8, 0.003])

# # # # # # # # # STEP2 
print('Step 2. Parameters for all the temperatures:')
params_dsl=pd.DataFrame(columns=['q1','b1','q2','b2', 'Temperature'])
paramsError=pd.DataFrame(columns=['q1','b1','q2','b2', 'Temperature'])

for temp in tempCO2:
    params, paramsE=execute_Model(co2datacombined[co2datacombined['Temperature C']==int(temp)],'dsl_HP',params_5C)
    params_dsl = params_dsl.append(pd.Series(params, index=params_dsl.columns[:4]), ignore_index=True)
    paramsError = paramsError.append(pd.Series(paramsE, index=paramsError.columns[:4]), ignore_index=True)    
params_dsl['Temperature']=list(map(int, tempCO2)) 
paramsError['Temperature']=list(map(int, tempCO2)) 

#STEP 3
print('Step 3')
print('bo1, H1')
boH1_5, boH1E_5 = execute_Model([[params_dsl['Temperature'][0], params_dsl['Temperature'][1]] , [params_dsl['b1'][0], params_dsl['b1'][1]] ],'vantHoff',[4,130])
print('bo2, H2')
boH2_5, boH2E_5 = execute_Model([[params_dsl['Temperature'][0], params_dsl['Temperature'][1]] , [params_dsl['b2'][0], params_dsl['b2'][1]] ],'vantHoff',[0.1,-39000])

#step 4
#['q1', 'bo1', 'H1', 'q2', 'bo2', 'H2']
iv=[params_dsl['q1'][0],	boH1_5[0],	boH1_5[1],	params_dsl['q2'][0], 	boH2_5[0],	boH2_5[1]]
#plotModel(iv, [co2datafiltered[0]], ['-5'],[0.03, 100],'bar', True, colors, 'dsl_T_step4')

parametersFV_opt, parametersFVE_opt = execute_Model(co2datacombined, 'dsl_T_step4', iv)

plotModel(parametersFV_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 100],'bar', False, colors, 'dsl_T_step4')
plotModel(parametersFV_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 100],'bar', True, colors, 'dsl_T_step4')

plotModel(iv, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 100],'bar', True, colors, 'dsl_T_step4')
plotModel(iv, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0001, 0.3],'ppm', False, colors, 'dsl_T_step4')

isoFitDataDSL=get_isoFitDataList(parametersFV_opt, co2datafiltered, tempCO2 ,'dsl_T')
FoMDSL_05=FoM_fit(co2datafiltered, isoFitDataDSL, tempCO2, 0.5)
FoMDSL_1=FoM_fit(co2datafiltered, isoFitDataDSL, tempCO2, 1)
FoMDSL_100=FoM_fit(co2datafiltered, isoFitDataDSL, tempCO2, 100)

####################################################################################
####################################################################################
####################################################################################
####################################################################################
#TOTH

path='/Users/lopezrzy/Documents/CEA/CRBNET/Isotherms/'

comp='CO2'
tempCO2=['-5', '20', '40', '60', '75']
run_numberCO2= ['782', '785', '785', '786','799']
colors=['black','blue','darkmagenta','orangered','red']

co2datafiltered= import_isotherms4(comp, tempCO2, run_numberCO2) 
co2datacombined = pd.concat(co2datafiltered, ignore_index=True)
co2datacombined2=co2datacombined[co2datacombined['Absolute Pressure (kPa)']<=0.5]
#    bo, Q, To, to, alpha, qso, chi):
#iv=[5, 41, 40, 0.7, 0, 1.5, 0 ]
iv=[0.8, 30.004, -12, 0.03, 0, 21, 0 ]
parametersToth_opt, parametersTothE_opt = execute_Model(co2datacombined2, 'toth', iv)

plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.025, 100],'bar', True, colors, 'toth')
plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.025, 100],'bar', False, colors, 'toth')

plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.025, 100],'ppm', True, colors, 'toth')
plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.025, 100],'ppm', False, colors, 'toth')


plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.025, 0.1],'ppm', True, colors, 'toth')
plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.025, 0.5],'ppm', False, colors, 'toth')


### test pygaps model for each temperature

path='/Users/lopezrzy/Documents/CEA/CRBNET/Isotherms/'

comp='CO2'
tempCO2=['-5', '20', '40', '60', '75']
run_numberCO2= ['782', '785', '785', '786','799']
colors=['black','blue','darkmagenta','orangered','red']

co2datafiltered= import_isotherms4(comp, tempCO2, run_numberCO2) 
#co2datacombined = pd.concat(co2datafiltered, ignore_index=True)
#co2datacombinedHighP=co2datacombined[co2datacombined['Absolute Pressure (kPa)']<=101]

plotModel([1.169,	0.008931	 , 0.1518,	0.5833], [co2datafiltered[0]], ['-5'],[0.01, 100],'bar', True, colors, 'dsl')
plotModel([0.9877,	0.006155	, 0.06471,	0.4419], [co2datafiltered[1]], ['20'],[0.01, 100],'bar', True, colors, 'dsl')
plotModel([0.7617,	0.005342, 0.03006, 1.207] , [co2datafiltered[2]], [ '40'],[0.01, 100],'bar', True, colors, 'dsl')
plotModel( [0.7919,	0.003025,	0.01731, 	1.035], [co2datafiltered[3]], ['60'],[0.01, 100],'bar', True, colors, 'dsl')
plotModel( [0.6833,	0.002454	, 0.007971,	8.007], [co2datafiltered[4]], ['75'],[0.01, 100],'bar', True, colors, 'dsl')

####################################################################################
####################################################################################
## Try estimating the adsorption quantity at low pressures and then apply Toth fit model 
                                   #  TOTH

path='/Users/lopezrzy/Documents/CEA/CRBNET/Isotherms/'
comp='CO2'
tempCO2=['-5', '20', '40', '60', '75']
run_numberCO2= ['782', '785', '785', '786','799']
colors=['black','blue','darkmagenta','orangered','red']

co2datafiltered= import_isotherms4(comp, tempCO2, run_numberCO2) 
co2datafiltered=estimateQatLowPressures(co2datafiltered,'power')

co2datacombined = pd.concat(co2datafiltered, ignore_index=True)
co2datacombined2=co2datacombined[co2datacombined['Absolute Pressure (kPa)']<=0.5]
#    bo, Q, To, to, alpha, qso, chi):
iv=[0.8, 30.004, -12, 0.03, 0, 21, 0 ]

parametersToth_opt, parametersTothE_opt = execute_Model(co2datacombined2, 'toth', iv)

plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 100],'bar', True, colors, 'toth')

plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 100],'bar', False, colors, 'toth')

plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 100],'ppm', True, colors, 'toth')
plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 100],'ppm', False, colors, 'toth')

# Low pressures plot
plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 0.5],'bar', True, colors, 'toth')
plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 0.5],'bar', False, colors, 'toth')

plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 1],'ppm', True, colors, 'toth')
plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 0.5],'ppm', False, colors, 'toth')
plotModel(parametersToth_opt, co2datafiltered, ['-5', '20', '40', '60','75'],[0.0015, 0.12],'ppm', False, colors, 'toth')

# toth gives the best fit case at low pressures ---> pressures for the fitting < 0.5, using 'power'  at estimateQatLowPressures
# find rsme

isoFitDataToth=get_isoFitDataList(parametersToth_opt, co2datafiltered, tempCO2 ,'toth')
FoMToth_05=FoM_fit(co2datafiltered, isoFitDataToth, tempCO2, 0.5)
FoMToth_1=FoM_fit(co2datafiltered, isoFitDataToth, tempCO2, 1)
FoMToth_100=FoM_fit(co2datafiltered, isoFitDataToth, tempCO2, 100)



temp2test=['-5', '15', '20', '35', '40', '60', '75']
TempPress=[]
for i in temp2test:
    TempPress.append(pd.DataFrame({'Absolute Pressure (kPa)': np.logspace(np.log10(0.0015), np.log10(0.5), 100), 'Temperature C': np.full(100, int(i))}))
isoFitDataToth=get_isoFitDataList(parametersToth_opt, TempPress, temp2test ,'toth')

for i in range(len(temp2test)):
    plt.plot(isoFitDataToth[i]['Absolute Pressure (kPa)']/100*1000000, isoFitDataToth[i]['Quantity Adsorbed (mmol/g)'], label=temp2test[i]+' °C, Toth ',  mfc='none', linestyle='dotted', marker='.')
plt.axvline(x=400, color='black', linestyle='--')
plt.xlabel('CO2 concentration (ppm)', fontsize=10)
plt.ylabel('Quantity Adsorbed (mmol/g)', fontsize=10)
plt.legend(fontsize=10)
plt.show()


##### KH_temp Henry's Law temperature dependant

path='/Users/lopezrzy/Documents/CEA/CRBNET/Isotherms/'
comp='CO2'
tempCO2=['-5', '20', '40', '60', '75']
run_numberCO2= ['782', '785', '785', '786','799']
colors=['black','blue','darkmagenta','orangered','red']

co2datafiltered= import_isotherms4(comp, tempCO2, run_numberCO2) 
co2datafiltered2=[]
for i in range(len(co2datafiltered)):
    #use only the two lowest pressures
    co2datafiltered2.append( co2datafiltered[i].head(2))

co2datacombined = pd.concat(co2datafiltered2, ignore_index=True)
#    linear attempt
# iv=[2 , 3000]
# parametersKHTemp_opt, parametersKHTempE_opt = execute_Model(co2datacombined, 'linear_T', iv)

#    DH, KHx
iv=[27000 , 0.1 ]
parametersKHTemp_opt, parametersKHTempE_opt = execute_Model(co2datacombined, 'KH_Temp', iv)
plt.plot(iv)
plotModel(parametersKHTemp_opt, co2datafiltered2, tempCO2,[0.0015, 1],'ppm', True, colors, 'KH_Temp')

co2datacombined = pd.concat(co2datafiltered, ignore_index=True)
co2datacombined2=co2datacombined[co2datacombined['Absolute Pressure (kPa)']<=0.5]
plotModel(parametersKHTemp_opt, co2datafiltered, tempCO2,[0.0015, 1],'bar', True, colors, 'KH_Temp')
plotModel(parametersKHTemp_opt, co2datafiltered, tempCO2,[0.0015, 1],'bar', False, colors, 'KH_Temp')


