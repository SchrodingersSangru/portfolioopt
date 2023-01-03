#importing the required stuff
from pickletools import optimize
from qiskit import Aer
from qiskit.algorithms import VQE, QAOA, NumPyMinimumEigensolver
from qiskit.algorithms.optimizers import COBYLA, SPSA
from qiskit.circuit.library import TwoLocal
from qiskit.utils import QuantumInstance
from qiskit_finance.applications.optimization import PortfolioOptimization
from qiskit_finance.data_providers import *
from qiskit_finance import QiskitFinanceError
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import OptimizationApplication
from qiskit_optimization.converters import QuadraticProgramToQubo
import numpy as np
import matplotlib.pyplot as plt

import datetime
import pandas as pd
from pandas.plotting import register_matplotlib_converters
# register_matplotlib_converters()
import csv
import yfinance as yf
import pandas_datareader.data as web
from qiskit_finance.applications.optimization import PortfolioDiversification

from qiskit.utils import algorithm_globals


class portfolio_opt:
    
    def __init__(self, selected_assets, log_returns, budget, device, risk_appetite, **kwargs) -> None:
        self.selected_assets = selected_assets
        self.log_returns = log_returns 
        self.budget = budget 
        self.risk_appetite = risk_appetite
        self.device = device
        self.no_trading_days = kwargs["trading_days"]
    
    
    def get_data_params(self):
        
        
        mu = self.log_returns.mean()*self.no_trading_days
        sigma = self.log_returns.cov()*self.no_trading_days
        
        mu = np.array(mu)
        sigma = np.array(sigma)
        return mu, sigma         
    
    
        
    def formulate(self):
        q = self.risk_appetite  # set risk factor
        num_assets = len(self.selected_assets)
        budget = num_assets // 2  # set budget
        penalty = num_assets  # set parameter to scale the budget penalty term
        returns, vol = self.get_data_params()
        portfolio = PortfolioOptimization(
            expected_returns=returns, covariances=vol, risk_factor=q, budget=budget,
        )
        qp = portfolio.to_quadratic_program()
        return qp
    
    
    
    
    
    def get_solution_using_exact_solver(self):
        
        exact = MinimumEigenOptimizer(NumPyMinimumEigensolver())
        model = self.formulate()
        result = exact.solve(model)
        best_result = result.x
        return best_result
    
    
    


    def get_solution_using_vqe_cobyla(self):
        
        # if self.device =="QASM":
        backend = Aer.get_backend("qasm_simulator")
        
        num_assets = len(self.selected_assets)
        optimizer = COBYLA()
        optimizer.set_options(maxiter=50)
        
        ry = TwoLocal(num_assets, "ry", "cz", reps=3, entanglement="full")
        quantum_instance = QuantumInstance(backend=backend, shots=8192) #, seed_simulator=self.seed, seed_transpiler=self.seed)
        vqe_mes = VQE(ry, optimizer=optimizer, quantum_instance=quantum_instance)
        vqe = MinimumEigenOptimizer(vqe_mes)
        
        model = self.formulate()
        result = vqe.solve(model)
        best_result = result.x
        return best_result
        
        
    
    

    def get_solution_using_vqe_spsa(self):
                
        backend = Aer.get_backend("qasm_simulator")
        
        num_assets = len(self.selected_assets)
        optimizer = SPSA()
        optimizer.set_options(maxiter=100)
        
        ry = TwoLocal(num_assets, "ry", "cz", reps=3, entanglement="full")
        quantum_instance = QuantumInstance(backend=backend, shots=8192) 
        vqe_mes = VQE(ry, optimizer=optimizer, quantum_instance=quantum_instance)
        vqe = MinimumEigenOptimizer(vqe_mes)
        
        model = self.formulate()
        result = vqe.solve(model)
        best_result = result.x
        return best_result
    
    
    
    def get_solution_using_qaoa_cobyla(self):
                
        backend = Aer.get_backend("qasm_simulator")
        
        optimizer = COBYLA()
        optimizer.set_options(maxiter=100)
        quantum_instance = QuantumInstance(backend=backend, shots=8192) 
        qaoa_mes = QAOA(optimizer=optimizer, reps=3, quantum_instance=quantum_instance)
        qaoa = MinimumEigenOptimizer(qaoa_mes)

        model = self.formulate()
        result = qaoa.solve(model)
        best_result = result.x
        return best_result
    
    
    
    
    def get_solution_using_qaoa_spsa(self):
                
        backend = Aer.get_backend("qasm_simulator")
        
        optimizer = SPSA()
        optimizer.set_options(maxiter=100)
        quantum_instance = QuantumInstance(backend=backend, shots=8192)
        qaoa_mes = QAOA(optimizer=optimizer, reps=3, quantum_instance=quantum_instance)
        qaoa = MinimumEigenOptimizer(qaoa_mes)

        model = self.formulate()
        result = qaoa.solve(model)
        best_result = result.x
        return best_result
    
    


