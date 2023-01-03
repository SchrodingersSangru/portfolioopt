from cvxpy import Minimize
from scipy.optimize import minimize 
import numpy as np


class opt_weights:
    
    def __init__(self,log_returns,opt_bitstring, trading_days):
        self.log_returns = log_returns
        # self.risk_appetite = risk_appetite
        self.assets = log_returns.columns.values.tolist()
        self.opt_bitstring = opt_bitstring
        self.trading_days = trading_days
    
    
    def get_selected_assets(self):
        selected_bitstring = [i for i, e in enumerate(self.opt_bitstring) if e == 1]
        # print(selected_bitstring)
        my_assets = [self.assets[i] for i in selected_bitstring]
        # print("my selected assets before weight alloc is ", my_assets)
        return my_assets
    
        
    def weights_(self):
        weights = np.array(np.random.random(len(self.get_selected_assets())))
        print("weightsss ", weights)
        print('normalised weights :')
        weights = (weights/np.sum(weights))
        print('normalised weights : ', weights)
        return weights
    
        
    def get_ret_vol_sr(self,weights,log_return): 
        weights = np.array(weights)
        ret = np.sum(log_return.mean() * weights) * self.trading_days
        vol = np.sqrt(np.dot(weights.T,np.dot(log_return.cov()*self.trading_days,weights)))
        # sr = ret - self.risk_appetite*vol  # this is absolutely wrong way of making objecive function
        # sr = ret - vol
        sr = ret/vol 
        return np.array(sr)
    

    def neg_sharpe(self,weights): 
        log_returns = self.log_returns[self.get_selected_assets()]
        # print(log_returns)
        return self.get_ret_vol_sr(weights,log_returns)*-1

    def check_sum(self,weights): 
        return np.sum(weights) - 1
    
    def round_w(self):
        round_weights = []
        weights = self.weights_()
        for i in range(len(weights)):
            round_weights.append(round(weights[i],1))
        return round_weights
    
    
     
    def optimize_weights(self):
        
        cons = ({'type':'eq','fun':self.check_sum})
        bounds = tuple((0, 1) for stocks in range(len(self.get_selected_assets()))) 
        init_guess = np.random.dirichlet(np.ones(len(self.get_selected_assets())),size=1)
        
        opt_results = minimize(self.neg_sharpe, self.round_w(), method='SLSQP', bounds=bounds, constraints=cons)
        my_weights = np.array(opt_results.x)
        my_weights = np.round(my_weights, 8)
        my_weights = my_weights.tolist()
        weights_alloc = dict(zip(self.get_selected_assets(), my_weights))
        return weights_alloc


class get_portfolio_sharpe:
    def __init__(self, log_returns, weights_dict, trading_days):
        self.log_returns = log_returns
        self.weights_dict = weights_dict
        self.trading_days = trading_days
        # print(self.log_returns)
        # print(self.weights_dict.values())
    
    def get_sharpe_ratio(self):
        # weights = np.array(weights)
        
        assets = list(self.weights_dict.keys())
        
        log_returns = self.log_returns[assets]
        weights = list(self.weights_dict.values())
        weights = np.array(weights)
        # print("type of weghtss ", type(weights))
        ret = np.sum(log_returns.mean() * weights) * 252
        vol = np.sqrt(np.dot(weights.T,np.dot(log_returns.cov()*252 ,weights)))
        sr = ret/vol 
        annual_sharpe_ratio_dict = {
            'Returns': ret*100, 
            'Risk' : vol*100,
            'Sharpe Ratio' : sr
        }
        
        return annual_sharpe_ratio_dict