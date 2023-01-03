import yfinance as yf
import numpy as np
import pandas as pd


class Data_load:
    
    def __init__(self, index, assets, start_date, end_date, risk_factor, budget ) -> None:
        self.assets = assets
        self.start_date = start_date
        self.end_date = end_date
        self.risk_factor = risk_factor
        self.budget = budget
        self.index = index
        
    def get_data(self):

        stocks_data = yf.download(self.assets, start = self.start_date, end = self.end_date)['Adj Close']

        ###          filtering stocks based on the max returns and minimum risk              ###
        # annual_return = stocks_data.pct_change().mean()*252
        # annual_volatility = stocks_data.pct_change().std()*np.sqrt(252)
        
        annual_return = (np.log(stocks_data/stocks_data.shift(1))).mean()*252
        annual_volatility = (np.log(stocks_data/stocks_data.shift(1))).std()*np.sqrt(252)
        filter_df = pd.DataFrame(data={"returns":annual_return,"volatility":annual_volatility})
        
        filter_df["retvol"] = filter_df.returns / filter_df.volatility
        filter_df = filter_df.sort_values(by = ["retvol"], ascending = False)
        
        #risk factor is low, so it means a user wants to get top less risky or high returns stocks. risk factor is alos called as risk bearing capacity.
        # if self.risk_factor < 0.5 :
        #     filter_df = filter_df.sort_values(by = ["returns"], ascending = False)
        #     filter_df = filter_df["returns"]
            
        # elif self.risk_factor >= 0.5: 
        #     filter_df = filter_df.sort_values(by = ["volatility"], ascending = True)
        #     filter_df = filter_df["volatility"]
            
        filter_df = pd.DataFrame(filter_df)
        # filter_df
        
        sorted_assets = list(filter_df.T.columns)
        
        print(" filtered stocks on max returns n min risk \n ", filter_df)
        sorted_assets = sorted_assets[:self.budget *2]
        
            
        selected_stocks_data = stocks_data[sorted_assets]
        # selected_stocks_data.head()
        print("selected stocks after filtering are ", sorted_assets)
        log_return = np.log(selected_stocks_data/selected_stocks_data.shift(1))
        
        
        if self.index == 'Dow 30':
            sorted_assets.append('^DJI') # adding index data to the datafrae to remove redundancy. 
        
        selected_stocks_data = stocks_data[sorted_assets] # keep this line below log_retuns to remove index to present in every place. 
        
        # return stocks_data, num_assets, mu, sigma
        return selected_stocks_data, log_return
    
    
