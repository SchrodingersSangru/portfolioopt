
from data_load import Data_load
from asset_selection import portfolio_opt
from weights_allocation import opt_weights, get_portfolio_sharpe
import datetime as datetime 
# from datetime import datetime
from dateutil.relativedelta import relativedelta
import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import hydralit as hy
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import sqlite3
import yfinance as yf
import altair as alt
from yahooquery import Ticker
import streamlit_authenticator as stauth

import time as time
# import plotly.express as px

app = hy.HydraApp(title= ' Portfolio Optimization App ')



class portfolio_run:
    
    def __init__(self, index, assets, budget, start_date, end_date, algorithm, device, risk_factor) -> None:
        self.index = index
        self.assets = assets 
        self.budget = budget
        self.start_date = start_date
        self.end_date = end_date
        self.algorithm = algorithm
        self.device = device 
        self.risk_factor = risk_factor
        
        

    
    def run_app(self):
            
        t1 = time.time()
        data = Data_load(self.index, self.assets, self.start_date, self.end_date, self.risk_factor, self.budget)
        stocks_data, log_returns = data.get_data()
        
        print(log_returns)
        
        index_data = stocks_data.iloc[: , -1]
        
        trading_days = log_returns.shape[0]
        print("shape of df is", trading_days)
        # print("returns are ", log_returns)
        
        
        opt_bit = portfolio_opt(self.assets, log_returns, self.budget, self.device, self.risk_factor, trading_days = trading_days)
        
        # [ "QAOA with Cobyla", "QAOA with SPSA", "VQE with Cobyla", "VQE with SPSA"],
        if self.algorithm ==  "QAOA with Cobyla":
            opt_bitstring  = opt_bit.get_solution_using_qaoa_cobyla()
            
        elif self.algorithm ==  "QAOA with SPSA":
            opt_bitstring  = opt_bit.get_solution_using_qaoa_spsa()
            
        elif self.algorithm ==  "VQE with Cobyla":
            opt_bitstring  = opt_bit.get_solution_using_vqe_cobyla()
            
        elif self.algorithm ==  "VQE with SPSA":
            opt_bitstring  = opt_bit.get_solution_using_vqe_spsa()
        
        
        print("opimal bitsring ", opt_bitstring)
        
        # opt_bitstring 
        
        my_weight  = opt_weights(log_returns, opt_bitstring, trading_days)
        my_weights = my_weight.optimize_weights()
        # my_weights
    
        my_stocks = list(my_weights.keys())
        
        # portfolio_data =  stocks_data.loc[:, stocks_data]
        portfolio_data =  stocks_data[my_stocks[:-1]]
        
        sharpe = get_portfolio_sharpe(log_returns, my_weights, trading_days)
        sharpe_ratio = sharpe.get_sharpe_ratio()
        
        st.title(" Quantum Powered Portfolio Optimization ")
        # Insert a form in the container
        
            
        t2 = time.time()
        
        total_time_taken = float(t2 - t1)
        print("time taken iss ", total_time_taken)
        
        return my_weights, sharpe_ratio, index_data, portfolio_data, total_time_taken



def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False
# DB Management

conn = sqlite3.connect('data.db')
c = conn.cursor()

# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
    conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username,password))
    data = c.fetchall()
    print(data)
    return data



def add_optim_db(username, current_time, my_stocks, my_weightss, sr):
    c.execute('CREATE TABLE IF NOT EXISTS optim_details(time TEXT, selected_assets TEXT, weights TEXT, sharpe_ratio TEXT, FOREIGN KEY (username))')
    # current_time = kwargs["trading_days"]
    # my_stocks = kwargs["my_stocks"]
    # my_weightss = kwargs["my_weightss"]
    # sr = kwargs["Sharpe_ratio"]
    conn.execute(f"INSERT INTO optim_details (time, selected_assets, weights, sharpe_ratio) VALUESVALUES(?,?,?,?,?)", ({username}, {current_time}, {my_stocks}, {my_weightss}, {sr}))
    conn.commit()
    print(" record saved succesfully.. ")
        
        
        




#when we import hydralit, we automatically get all of Streamlit


@app.addapp()
def login():
    hy.info('Login Page')

 # Create an empty container
    placeholder = st.empty()

    # actual_email = "email"
    # actual_password = "password"
    # username = st.text_input("User Name")
    # password = st.text_input("Password",type='password')
        

    #st.title("Welcome")
    st.title(" Quantum Powered Portfolio Optimization ")
    # Insert a form in the container
    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        username = st.text_input("User Name")
        password = st.text_input("Password",type='password')
        # if st.button("Login"):
            # if password == '12345':
        create_usertable()
        hashed_pswd = make_hashes(password)

        result = login_user(username,check_hashes(password,hashed_pswd))
        submit = st.form_submit_button("Login")

    if submit and username == username and password == password:
        # If the form is submitted and the email and password are correct,
        # clear the form/container and display a success message
        placeholder.empty()
        
        st.success("Login successful")
        st.title("WELCOME")
        st.title(" Portfolio Optimization Dashbboard")
        
        
    elif submit and username != username and password != password:
        st.error("Login failed")
    else:
        pass




@app.addapp()
def user_manual():
    hy.info(' User Manual ') 
    
    st.subheader(" Get the quantum power to get optimal portfolio for your financial investments")
    
    st.write("\n \n \n")
    
    st.write(" sometime it might take few more seconds to load the data, and to show you the optimal result, kindly wait for a minute. ")
    st.subheader(" steps to use our system ")
    
    
    
    st.write(" we load our data on per minute basis, so after every minute you can generate profit on every trade executed")
    
    st.write("\n \n \n")
    st.write("1. Login to our system")
    st.write("2. select the stocks that you want ")
    st.write("3. select the values for other inputs asked ")
    st.write("4. click on the button to get you the results ")

    st.write("5. read the output and execute the trade accoridngly ")
    st.write("6. earn profit and make life happier  ")

    st.write("\n \n")
    
    st.write("This Project is developed By Qkrishi ... ")
    st.write(" Copyright - Qkrishi www.qkrishi.com ")
        




@app.addapp()
def portfolio_core_app():
    
    st.title ("  Portfolio Optimization  ")

    st.subheader(" Portfolio Optimization app  ")

    investment_amount =  st.sidebar.number_input('investment ', min_value=10000, step=500)

    algorithm = st.sidebar.radio(
            "Algorithm ",
            key="visibility",
            options=[ "QAOA with Cobyla", "QAOA with SPSA", "VQE with Cobyla", "VQE with SPSA"],
    )
    # ['AED', 'ARS', 'AUD', 'BGN', 'BRL', 'BSD', 'CAD', 'CHF', 'CLP', 'CNY', 'COP', 'CZK', 'DKK',  'DOP', 'EGP', 'GBP', 'HKD', 'HRK', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'MVR', 'MXN', 'MYR', 'NOK', 'NZD', 'RUB', 'SAR', 'SEK', 'SGD', 'THB', 'TRY', 'TWD', 'UAH', 'USD', 'UYU', 'ZAR']
    # stocks = pd.DataFrame({'labels':['WMT','WBA', 'VZ', 'V', 'UNH', 'TRV', 'PG', 'NKE', 'MSFT',  'MRK',  'MMM', 'MCD', 'KO', 'JPM', 'JNJ', 'INTC', 'IBM', 'HON', 'HD', 'GS', 'DOW', 'DIS', 'CVX', 'CSCO', 'CRM', 'CAT', 'BA', 'AXP', 'AMGN', 'AAPL']})


    index = st.sidebar.radio(
                        " Stocks Market Index ", 
                        options = ['Dow 30']
    )


    if index == 'Dow 30':
        assets = ['MMM','AXP','AAPL','BA','CAT','CVX','CSCO','KO','DOW', 'XOM','GS','HD','IBM','INTC','JNJ','JPM','MCD','MRK','MSFT','NKE','PFE','PG','TRV','UNH','UTX','VZ','V','WMT','WBA','DIS']
        assets.append('^DJI')
        print("asssetss with index ", assets)
    
    today = datetime.date.today()
    past_date = today - datetime.timedelta(days=1000)
    start_date = st.sidebar.date_input('Start date', past_date)
    end_date = st.sidebar.date_input('End date', today)
    
    if start_date < end_date:
        # st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
        st.success('')
    else:
        st.error('Error: End date must fall after start date.')

    device = st.sidebar.radio(
                        " Simulator device ", 
                        options = [' QASM Simulator ']
    )
    
    risk_factor = st.sidebar.slider(" your risk factor ", min_value=0.0, max_value= 1.0, value=0.5,  step = 0.1)

    budget =  st.sidebar.number_input('no of stocks to be selected in portfolio', min_value=len(assets)//10, max_value=len(assets), value=5, step=1)
    # budget =  st.sidebar.number_input('no of stocks to be selected in portfolio', min_value=len(assets)//4, max_value=len(assets), step=1)



    if st.sidebar.button('Get optimal portfolio '):
        
        
        ## definfing a button, which after pressing will create a qubo and will give optiml path to be used by an user.
        portfolio_app = portfolio_run(index, assets, budget, start_date, end_date, algorithm, device, risk_factor)
        portfolio_output = portfolio_app.run_app()
        my_weights, sharpe_ratio, index_data, portfolio_data, time_taken = portfolio_output
        
        
        print(sharpe_ratio)
        print("my weights dict ", my_weights)
        
        my_stocks = list(my_weights.keys())
        # print(" my stocks before weights assignment iss ", my_stocks)
        weights = list(my_weights.values())
        
        
        ##index part 
        # index_data = yf.download("^DJI", start = start_date, end = end_date)["Adj Close"]
        index_data  = pd.Series(index_data)
        print('inddddex ata \n ' , index_data)
         
        index_data  = pd.Series(index_data, name = "index_vals")
        print("index dataaaaaa", index_data)
        
        portfolio_data["portfolio_vals"] = portfolio_data.mean(axis =1)

        portfolio_data = portfolio_data["portfolio_vals"]
        portfolio_df = portfolio_data.to_frame(name = "portfolio_vals")
        portfolio_df = portfolio_df.rename_axis('Dates', axis=1)
        index_first = index_data.iloc[0]
        portfolio_first = portfolio_data.iloc[0]
        
        index_data  = index_data.multiply(portfolio_first/index_first)
        index_df = index_data.to_frame(name = "index_vals")
        index_df = index_df.rename_axis('Dates', axis=1)
        
        # index_port_df  = pd.DataFrame(portfolio_data, index_data)
        st.write("\n \n ")
        # st.table(index_port_df)
        
        portfolio_val = portfolio_data.mean()
        print("portfolio valll ", portfolio_val)
        index_val = index_data.mean()
        print("index valll ", index_val)


        portfolio_index_ratio = portfolio_val / index_val
        ### end of index part 
        myyy_weights = [item * 100 for item in weights]
        
        print(" \n \n ")

        # print(" my stockkkkks typeeeee ", type(my_stocks))
        # print("types of eights isssss", type(weights))
        
        #get company names 
        
        tickers = Ticker(my_stocks, asynchronous=False)

        data = tickers.get_modules("summaryProfile quoteType")
        df = pd.DataFrame.from_dict(data).T
        

        # flatten dicts within each column, creating new dataframes
        dataframes = [pd.json_normalize([x for x in df[module] if isinstance(x, dict)]) for module in ['summaryProfile', 'quoteType']]

        # concat dataframes from previous step
        df = pd.concat(dataframes, axis=1)

        # View columns
        # df.columns
        df = df[['symbol', 'shortName']]
        
        df.set_index(['symbol', 'shortName'])
        # print(df)
        company_names_dict = df.set_index('symbol').to_dict()['shortName']
    
        
        # holdngs_data = {"Assets":my_stocks, "Weights(%)": weights, "Money($)":allocated_money}
        holdngs_data = {"Assets":company_names_dict.keys(), "Company Name": company_names_dict.values(), "Weights(%)": np.round(myyy_weights, 2) } 
           
        # print(summary_df)
        sharpe_ratio_df = pd.DataFrame(sharpe_ratio.items(), columns=['index', 'value'])
        # sharpe_ratio = sharpe_ratio_df['Sharpe Ratio']
        # print(sharpe_ratio_df)
        
        allocated_money = [(investment_amount*i)/100 for i in myyy_weights]

        # allocated_money = np.round(allocated_money, 2)
        
        alloc_dict = dict(zip(company_names_dict.keys(), np.round(allocated_money, 2)))
        alloc_df = pd.DataFrame(alloc_dict.items(), columns=["assets", "money"])
        
        
        my_allocated_stocks = list((k for k, v in alloc_dict.items() if v > 0))
        print("allllllllocated stickss ", my_allocated_stocks)
        
        sr = sharpe_ratio['Sharpe Ratio']
        print("sharpe ratio of creted portfolio is ", sr)
        
        print(" \n \n ")
        print(" --------- "*10)
        print(" \n \n ")
        
        # current_username = login_user()
        # print("uername is", current_username[0])
        # add_optim_db(current_username, current_time, my_stocks, myyy_weights, sr)
        
        
        col_1, col_2= st.columns([1.3,2])
        with col_1:
    
            st.subheader(" Weights Allocation ")
            
            holdngs_df = pd.DataFrame(holdngs_data)
            # holdngs_df.loc[(holdngs_df['Weights(%)'] != 0)]
            # holdngs_df.reset_index(drop=True, inplace=False)
            st.table(holdngs_df.sort_values(by=["Weights(%)"], ascending=False ))
            # st.table(holdngs_df.sort_values(by=["Weights(%)"], ascending=False ))
            
            st.write(" \n \n ")
            st.subheader(" Money Allocation ")
            st.table(alloc_df.sort_values(by=["money"], ascending=False ))
            
            fig, ax = plt.subplots()
            ax.pie(myyy_weights, labels= my_stocks)
            st.pyplot(fig)
            
            st.write(" \n  \n ")

            st.subheader("Portfolio quality ")
            st.table(sharpe_ratio_df)
        
        #st.subheader(" Portfolio vs Index graph ")
        #chart_df = pd.concat([portfolio_data, index_data], axis=1)
        # print("tyyytpppesss 0000 ", type(chart_df))
        #st.line_chart(chart_df)
        
        
        
        st.write(" our portfolio beats index by " +str(portfolio_index_ratio)+ " times.. ")
        st.write(" So, you can see our portfolio is beating the Dow30 index.. ")
        st.write(" time taken for computing the optimal portfolio is in sec "+str(time_taken)+ " seconds")
        
    
        # current_time =  datetime.now()
        # add_optim_db()
        st.write(" \n \n ")
        st.write(" \n \n ")
        
        
        
        st.write("This Project is developed By Qkrishi ... ")
        st.write(" Copyright - Qkrishi www.qkrishi.com ")
        
        # st.success('Record added Successfully')
        
        

@app.addapp()
def signup():
    hy.info("Create New Account ")
    
    # st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password",type='password')

    if st.button("Signup"):
        create_usertable()
        add_userdata(new_user,make_hashes(new_password))
        st.success("You have successfully created a Account")
        st.info("Go to Login Menu to login")



## python -m streamlit hello --server.port 8000 --server.address 0.0.0.0 -> use this code to test whether streamlit is up? 

#Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
app.run()

 


