import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df = pd.read_csv('startup_funding.csv' , encoding='utf-8')
print(df.head())
df.columns = df.columns.str.strip()
df.drop(columns = ['Remarks'],inplace =True)


st.set_page_config(page_title='StartUp Analysis' ,layout='wide')


df.rename(columns = {
    'Date dd/mm/yyyy' : 'Date',
    'Industry Vertical' : 'Vertical',
    'SubVertical' : 'Sub Vertical',
    'City  Location' : 'Location',
    'Amount in USD' : 'Amount', 
    'InvestmentnType' : 'Round'
    
},inplace =True)


df.set_index('Sr No' ,inplace =True)



df['Amount']  = df['Amount'].fillna('0')
df['Amount']=df['Amount'].str.replace(',','')
df['Amount']=df['Amount'].str.replace('undisclosed','0' , case =False)
df['Amount']=df['Amount'].str.replace('unknown','0')
df['Amount']=df['Amount'].str.replace('+','')
df['Amount']=df['Amount'].str.replace('\\\\xc2\\\\xa0','')
df['Amount'] = df['Amount'].str.replace('N/A', '0', case=False)
temp = pd.to_numeric(df['Amount'], errors='coerce')
temp = (temp*96.25)/10000000
df['Amount']=temp



df['Date'] = df['Date'].str.replace("05/072018","05/07/2018")
df['Date'] = df['Date'].str.replace("01/07/015","01/07/2015")
df['Date'] = df['Date'].str.replace(".","/" ,regex = False)
df['Date'] = df['Date'].str.replace("//","/",regex = False)
df['Date'] = df['Date'].str.replace("\\\\xc2\\\\xa0","")
temp = pd.to_datetime(df['Date'],format = '%d/%m/%Y' , errors = 'coerce')
# df.loc[temp.isna(),'Date']
df['Date'] = temp




df['Investors Name'] = df['Investors Name'].fillna('Undisclosed')
investors = df['Investors Name'].str.split(',').explode().str.strip()
investors = investors.str.replace(r"\\xe2\\x80\\x99", "'", regex=False)
investors = investors.str.replace(r'\\xc2\\xa0','', regex=False)
investors = investors.str.replace(r'\\n','', regex=False)
investors = investors.str.replace(r'\\xc3\\x98','', regex=False)
invest = investors.value_counts()
names = invest.index
lnames = list(names)
unique_investors = sorted(list(set(lnames)))


df['Startup Name'] = df['Startup Name'].str.replace(r'\\xe2\\x80\\x99' ,'')



new_df = df.copy() 
new_df['Investors Name'] = new_df['Investors Name'].str.strip('').str.lower()
new_df['Investors Name'] = new_df['Investors Name'].str.split(',')
new_df= new_df.explode('Investors Name')


df['Round'] = df['Round'].str.strip().str.lower().str.title()
for i in df['Round'].unique():
    repr(i)



df['Round']=df['Round'].str.replace(r'\\N' , ' ')
df['Round']=df['Round'].replace({'Seed Funding':'Seed',                                  
'Seed Round': 'Seed',
'Seed Funding Round': 'Seed',
'Seed / Angel Funding':'Seed/Angel',
'Seed/ Angel Funding':'Seed/Angel',                         
'Seed/Angel Funding':'Seed/Angel',
'Seed / Angle Funding':'Seed/Angel',
'Angel / Seed Funding':'Seed/Angel',                                   
'Private Equity Round': 'Private Equity',
'Privateequity': 'Private Equity',
# 'Private\\Nequity': 'Private Equity',
'Venture Round': 'Venture',
'Single Venture': 'Venture',
'Venture - Series Unknown': 'Venture',
'Debt Funding': 'Debt',
'Debt-Funding': 'Debt',
'Structured Debt': 'Debt',
'Debt And Preference Capital': 'Debt',
'Term Loan': 'Debt',
'Pre Series A': 'Pre-Series A',                                
'Equity Based Funding': 'Equity',
'Series B (Extension)': 'Series B'                                  
})



print(df['Round'].nunique())
df.dropna(subset = 'Startup Name')
print(df['Startup Name'].nunique())
df['Startup Name'] = df['Startup Name'].str.replace(r'\s+', ' ', regex=True)
df['Startup Name'] = df['Startup Name'].str.replace(r'\\n', '', regex=False)
df['Startup Name'] = df['Startup Name'].str.replace(r'\\xc2\\xa0', '', regex=False)
df["Startup Name"] = df['Startup Name'].str.strip().str.lower().str.title()
print(df['Startup Name'].nunique())


# print(df[df['Startup Name'].str.contains(r'\d' , regex=True)]).../     commit
print('add function')


print('image')


print('sides')










def load_investor(investor):
    st.title(investor)
    # recent investments
    st.subheader('Recent Investments')
    details = df[df['Investors Name'].str.contains(investor)][['Date','Startup Name' ,'Vertical','Round','Amount']].sort_values(by = 'Date' ,ascending = False).head(5)  
    st.dataframe(details ,hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="DD-MM-YYYY",
        )
    })

    # biggest investments
    biggest = df[df['Investors Name'].str.contains(investor)].groupby('Startup Name')['Amount'].sum().sort_values(ascending=False).head() 
    st.dataframe(biggest)


    

    col1 ,col2 = st.columns(2)
    with col1:
        st.markdown('''###  Biggest Investments''')
        fig, ax = plt.subplots()
        ax.bar(biggest.index, biggest.values ,color="purple")
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")
        st.pyplot(fig)

    

    # similar = df[df['Investors Name'].str.contains(investor)]['Vertical'].value_counts().head()
    # st.dataframe(similar)

    #  similar type of investments


    intrests = df[df['Investors Name'].str.contains(investor)].groupby('Vertical')['Amount'].sum()
    with col2:
        
        st.markdown('''### Sectors Of Investment''')
        fig1, ax1 = plt.subplots()
        ax1.pie(intrests.values, labels = intrests.index ,autopct='%1.1f%%')
        ax1.set_xlabel("X Axis")
        ax1.set_ylabel("Y Axis")
        st.pyplot(fig1)


    #  Stage of investments

    stages = df[df['Investors Name'].str.contains(investor)]['Round'].value_counts()
    col3 ,col4 = st.columns(2)
    with col3:
        st.markdown('''### Stages Breakdown''')
        fig3, ax3 = plt.subplots()
        ax3.pie(stages.values, labels= stages.index ,autopct='%1.1f%%')
        ax3.set_xlabel("X Axis")
        ax3.set_ylabel("Y Axis")
        st.pyplot(fig3)
    
    cities =  df[df['Investors Name'].str.contains(investor)].groupby('Location')['Amount'].sum()   
    with col4:
        st.markdown('''### Investment Breakdown''')
        fig4, ax4 = plt.subplots()
        ax4.pie(cities.values, labels= cities.index ,autopct='%1.1f%%')
        ax4.set_xlabel("X Axis")
        ax4.set_ylabel("Y Axis")
        st.pyplot(fig4)

    #  year on year investment
    yby = df[df['Investors Name'].str.contains(investor)].groupby(df['Date'].dt.year)['Amount'].sum()
    st.markdown('''### Year On Year Investment Breakdown''')
    fig5, ax5 = plt.subplots()
    ax5.plot(yby.index , yby.values)
    ax5.set_xlabel("X Axis")
    ax5.set_ylabel("Y Axis")
    st.pyplot(fig5)


def load_startup(company):
    st.title(company)
    company_df = df[df['Startup Name'].str.contains(company, case=False, na=False)]

    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric('Total Investment' , round(company_df['Amount'].sum(),2),'4%')
    with col2:
        st.metric('Mean Investment' , round(company_df['Amount'].mean(),2),'4%')
    with col3:
        st.metric('Maximum Investment' , round(company_df['Amount'].max(),2),'4%')
    with col4:
        st.metric('Minimum Investment' , round(company_df['Amount'].min(),2),'4%')


    # Investors
    st.markdown('''### Investing Partners''')
    investors_name = new_df[new_df["Startup Name"].str.contains(company)]['Investors Name'].unique()
    st.dataframe(investors_name)


    #  Investmeny vs year
    st.markdown('''### Yearly Fundings ''')
    st.dataframe(company_df.groupby(company_df['Date'].dt.year)['Amount'].sum())


    # funding by the round

    st.markdown('''### Funding By Rounds''')
    round_df = df[df['Startup Name'].str.contains(company, case=False, na=False)]['Round'].value_counts()
    fig6 ,ax6 = plt.subplots()
    plt.pie(round_df.values , labels = round_df.index , autopct='%1.1f%%', radius=0.9)
    ax6.set_xlabel("X Axis")
    ax6.set_ylabel("Y Axis")
    st.pyplot(fig6)


    # funding frequency
    st.markdown('''### Funding Frequency''')
    company_df['year'] = company_df['Date'].dt.year
    frequency = company_df.groupby('year')['Amount'].count().reset_index()
    frequency.rename(columns={
        "Amount" :'count'
    })
    print(type(frequency))
    st.dataframe(frequency,hide_index=True)


    #  latest fundings
    st.markdown('''### Latest Fundings''')
    st.dataframe(df[df['Startup Name'].str.contains(company)][['Date','Startup Name' , 'Vertical' ,'Investors Name','Location','Round','Amount']].sort_values(by='Date',ascending=False),hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="DD-MM-YYYY",
        )
    })

    # total funding in that city 
    st.markdown('''### Total Funding By City''')
    st.dataframe(df[df['Startup Name'].str.contains(company)].groupby('Location')['Amount'].sum())




def load_overall():
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric('Total Startups' , df['Startup Name'].nunique())
    with col2:
        st.metric('Total Investors' , new_df['Investors Name'].nunique())
    with col3:
        st.metric('Total Funding' , round(df['Amount'].sum(),2))
    with col4:
        st.metric('Maximum Funding' , round(df['Amount'].max(),2))


   #year wise funding trend
    fpy = df.groupby(df['Date'].dt.year)['Amount'].sum()
    fig ,ax = plt.subplots()
    plt.plot(fpy.index ,fpy.values)
    ax.set_xlabel('Years')
    ax.set_ylabel('Fundings')
    st.pyplot(fig)

    # year wise no of funding rounds

    frpy = df.groupby(df['Date'].dt.year)['Round'].size()
    fig2 ,ax2 = plt.subplots()
    ax2.bar(frpy.index , height=frpy.values)
    ax2.set_xlabel('Years')
    ax2.set_ylabel('Funding Rounds')
    st.pyplot(fig2)

    #  top 10 funded startups

    ttf = df.groupby('Startup Name')['Amount'].sum().nlargest(10,keep='all')
    st.dataframe(ttf)
    


    # top industries by funding
    top_funding_industries = df.groupby('Vertical')['Amount'].sum().nlargest(10)
    fig3 , ax3 = plt.subplots()
    ax3.barh(top_funding_industries.index , width=top_funding_industries.values)
    ax3.set_ylabel('Total Funding')
    ax3.set_xlabel('Industries')
    st.pyplot(fig3)



    # top industries by number of startups

    top_industries = df.groupby('Vertical')['Vertical'].count().sort_values(ascending = False).head(10)
    st.dataframe(top_industries)

    # investment typr distribution 

    type_distribution = df['Round'].value_counts()
    fig4 , ax4 = plt.subplots()
    ax4.pie(type_distribution.values , labels=type_distribution.index)
    ax4.set_ylabel('Total Funding')
    ax4.set_xlabel('Industries')
    st.pyplot(fig4)




st.sidebar.title('Indian Startups Analaysis')
choice = st.sidebar.selectbox('Choose Your Analysis Type: ' , ['Overall Analysis' ,'Startup Analysis' ,'Investor Analysis']
                              ,index=None,placeholder='Take An Action:' ,)


if choice is None:
    st.title("Welcome to Indian Startups Analysis")
    st.write("Please select an analysis type from the sidebar to begin.")


elif choice == 'Overall Analysis':
    st.title('Overall Analysis')
    load_overall()

elif choice == 'Startup Analysis':
    startup = st.sidebar.selectbox('Choose Startup For Analysis:',df['Startup Name'].unique(),index=None,placeholder='Choose Startup:')
    btn1 = st.sidebar.button('Search')
    if btn1 and startup:
        load_startup(startup)

elif choice =='Investor Analysis':
    selected = st.sidebar.selectbox('Choose Startup For Analysis:',unique_investors,index=None,placeholder='Choose An Investor:')
    btn2 = st.sidebar.button('Search')
    if btn2 and selected:
        load_investor(selected)
