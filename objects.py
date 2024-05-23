import polars as pl
import numpy as np
from helper_functions import calculate_net_income, flatten_investment_dict

class Debt:
    """Class for any type of dept profile."""
    def __init__(self, initial_outstanding_balance : float, 
                 interest_rate : float, compounding : str, type : str):
        if compounding not in ['daily', 'monthly', 'semi-annually','annually']:
            raise ValueError("Invalid compounding frequency. Choose from 'daily', 'monthly', 'semi-annually', or 'annually'.")
        self.compounding = compounding
        self.compounding_frequency = {
            'daily': 365,
            'monthly': 12,
            'semi-annually': 2,
            'annually': 1
        }
        self.n = self.compounding_frequency[self.compounding]
        self.rate_per_period = interest_rate / self.n
        self.initial_outstanding_balance = initial_outstanding_balance
        self.outstanding_balance = initial_outstanding_balance
        self.months_since_start = 0
        self.type = type
        self.interest_rate=interest_rate
        
    def make_payment(self, amount):
        """Makes payment and updates loan."""
        self.outstanding_balance = self.outstanding_balance-amount
        
    def estimate_payment_time(self, time_in_years):
        total_periods = self.n * time_in_years
        amount = self.outstanding_balance * (1 + self.rate_per_period) ** total_periods
        return amount

    def mature_one_month(self, verbose = False):
        self.months_since_start+=1
        periods_in_month = (self.n / 12)
        old_balance = self.outstanding_balance
        self.outstanding_balance = self.outstanding_balance * (1 + self.interest_rate / self.n) ** (periods_in_month)
        if verbose:
            print(f"Debt {self.type} increases from ${old_balance} to {self.outstanding_balance}.")
            
    
class Insurance:
    """Insurance policy (employer or personal)."""
    
    def __init__(self, monthly_premium : float, type : str):
        self.monthly_premium=monthly_premium
        self.type = type
    
class MonthlyNeededExpenses:
    """Non-employer related expenses needed (i.e. pre-tax premiums not included)."""
    
    def __init__(self, rent : float, food : float, electric : float, 
                 internet : float, personal_insurance : list, 
                 minimum_excess_expendature : float, insurances : dict):
        self.rent=rent
        self.food=food
        self.electric=electric
        self.internet=internet
        self.personal_insurance=personal_insurance
        self.minimum_excess_expendature = minimum_excess_expendature
        self.insurances = insurances
        
    @property
    def monthly_necessity_costs_dict(self):
        base_dict = dict({"Minimum Leisure" : self.minimum_excess_expendature,
                          "Rent" : self.rent,
                          "Food" : self.food,
                          "Electric" : self.electric,
                          "Internet" : self.internet})
        personal_insurance_dict = dict({insurance : self.insurances[insurance].monthly_premium for insurance in self.personal_insurance})
        base_dict.update(personal_insurance_dict)
        return base_dict
        
    @property
    def monthly_necessity_costs(self):
        return np.sum(list(self.monthly_necessity_costs_dict.values()))

class Investment:
    """All investment funds including 401K, HSA, etc. 
    
    in_tax: whetheror not money is taxed on the way in."""
    
    def __init__(self, initial_outstanding_balance : float, interest_rate : float, compounding : str, type : str):
        if compounding not in ['daily', 'monthly', 'semi-annually','annually']:
            raise ValueError("Invalid compounding frequency. Choose from 'daily', 'monthly', 'semi-annually', or 'annually'.")
        self.compounding = compounding
        self.compounding_frequency = {
            'daily': 365,
            'monthly': 12,
            'semi-annually': 2,
            'annually': 1
        }
        self.n = self.compounding_frequency[compounding]
        self.rate_per_period = interest_rate / self.n
        self.initial_outstanding_balance = np.float64(initial_outstanding_balance)
        self.outstanding_balance = np.float64(initial_outstanding_balance)
        self.months_since_start = 0
        self.interest_rate=interest_rate
        self.type=type
        
    def contribute_funds(self, amount):
        self.outstanding_balance+=amount
        
    def mature_one_month(self, verbose = False):
        self.months_since_start+=1
        periods_in_month = (self.n / 365) * 30.5
        old_balance = self.outstanding_balance
        self.outstanding_balance = self.outstanding_balance * (1 + self.interest_rate / self.n) ** (self.n * periods_in_month)
        if verbose:
            print(f"Investment {self.type} increases from ${old_balance} to {self.outstanding_balance}.")
    
class EmployerBenefits:
    """Defines, stores, and calculates expendature into employer matched funds."""
    
    def __init__(self, salary : float, retirement_matching : dict, 
                 monthly_flat_rate_contributions : dict, company_insurances : list, insurances : dict):
        self.retirement_matching=retirement_matching
        self.monthly_flat_rate_contributions=monthly_flat_rate_contributions
        self.salary=np.float64(salary)
        self.company_insurances=company_insurances
        self.monthly_gross=self.salary/12
        self.insurances = insurances
    
    @property
    def monthly_contributions_to_investments(self):
        """Pre-tax-contribution of gross income for retirement fund matching"""
        funds_cont = dict({fund_type : self.monthly_gross*self.retirement_matching[fund_type] for fund_type in self.retirement_matching.keys()})
        funds_cont.update(self.monthly_flat_rate_contributions)
        return funds_cont
    
class FinancialProfile:
    
    def __init__(self, debts : dict[Debt], investments : dict[dict[Investment]], 
                 monthly_needs : dict[MonthlyNeededExpenses], employer_benefits : dict[EmployerBenefits],
                 maximum_monthly_loan_payment : float, federal_tax_brackets : list[tuple], 
                 standard_deduction : float, fica_rate : float, state_tax_rate : float, 
                 max_401K_legal : float, max_IRA_legal : float, prioritize_matching_over_emergency_fund : bool):
        self.debts=sorted(debts.values(), key=lambda x: x.interest_rate, reverse=True) # Sort objects by interest_rate in decreasing order
        self.short_term_investments=sorted(investments["Short Term"].values(), key=lambda x: x.interest_rate, reverse=True)
        self.employer_matched_investments=sorted(investments["Employer Matched Retirement"].values(), key=lambda x: x.interest_rate, reverse=True)
        self.other_ira_investments=sorted(investments["IRA"].values(), key=lambda x: x.interest_rate, reverse=True)
        self.other_investments=sorted(investments["Other"].values(), key=lambda x: x.interest_rate, reverse=True)
        self.employer_flat_rate_investments=sorted(investments["Employer Flat Rate Retirement"].values(), key=lambda x: x.interest_rate, reverse=True)
        self.monthly_needs=monthly_needs
        self.employer_benefits=employer_benefits
        self.current_month_leftover_net_income = 0
        self.spent_df_list = []
        self.records_df_list = []
        self.years_past = 0.0
        self.investments=investments
        self.flattened_investment_dict = flatten_investment_dict(self.investments)
        self.maximum_monthly_loan_payment=maximum_monthly_loan_payment
        self.matching_amounts_left = self.monthly_pre_net_income_investment_contributions.copy()
        self.spent_401=0
        self.spent_IRA=0
        self.federal_tax_brackets=federal_tax_brackets
        self.standard_deduction=standard_deduction
        self.fica_rate=fica_rate
        self.state_tax_rate=state_tax_rate
        self.max_401K_legal=max_401K_legal
        self.max_IRA_legal=max_IRA_legal
        self.paycheck_only_spending_df_list=[]
        self.simplified_df_list=[]
        self.prioritize_matching_over_emergency_fund=prioritize_matching_over_emergency_fund
        
    def monthly_net_income(self, additional_deductions):
        """Monthly income post-pre-tax-investment contribution, insurance premiums, and taxes."""
        return calculate_net_income(gross_income = np.sum([job.salary for job in self.employer_benefits.values()]), 
                                    standard_deduction = self.standard_deduction, 
                                    federal_tax_brackets = self.federal_tax_brackets, 
                                    state_tax_rate = self.state_tax_rate, 
                                    fica_rate = self.fica_rate,
                                    additional_deductions = additional_deductions)/12
        
    @property
    def monthly_pre_net_income_investment_contributions(self) -> dict:
        combined_dict=dict()
        for job in self.employer_benefits.values():
            combined_dict.update(job.monthly_contributions_to_investments)
        return combined_dict
    
    @property
    def short_term_savings_total(self):
        return np.sum([invest.outstanding_balance for invest in self.short_term_investments])
    
    @property
    def monthly_need_expendature(self):
        need_non_savings = 0
        for need_onject in self.monthly_needs.values():
            need_non_savings+=np.sum([need_value for need_name, need_value\
                in need_onject.monthly_necessity_costs_dict.items() if need_name != "Mandatory Savings"])
        return need_non_savings
    
    @property
    def highest_interest_debt(self):
        return np.max([this_dept.interest_rate for this_dept in self.debts])
    
    ### Complete Monthly Step Check Functions
    
    def get_non_decision_determined_updates(self, verbose=False):
        """Step -1: Do things that occur regardless of decisions."""
        # Mature Depts and Investments
        for dept in self.debts:
            dept.mature_one_month(verbose=verbose)
        for investment_type, investment_type_dict in self.investments.items():
            for investment_type, investment_object in investment_type_dict.items():
                investment_object.mature_one_month(verbose=verbose)   
        # Make money
        self.current_month_leftover_net_income+=self.monthly_net_income(additional_deductions=0)
        if verbose:
            print(f"Make net income of ${self.monthly_net_income(additional_deductions=0)} (Without pre-tax deduction recalculation)")
        # Mature time
        self.years_past+=1/12
        # Reset matching amounts
        self.matching_amounts_left = self.monthly_pre_net_income_investment_contributions.copy()
        self.spent_401=0
        self.spent_IRA=0
        # Contribnute employer flat rate amounts
        for investment_object in self.employer_flat_rate_investments:
            contribution_amount=self.matching_amounts_left[investment_object.type]
            investment_object.contribute_funds(contribution_amount)
            

    def get_monthly_spend_on_needs(self, verbose = False):
        """Step 0: Spend money on determined needs."""
        total_need_spend=0
        spent_dict = dict()
        for need_name, need_object in self.monthly_needs.items():
            spend = need_object.monthly_necessity_costs
            if verbose:
                print(f"Spend ${spend} on {need_name}.")
            total_need_spend+=spend
            spent_dict.update(need_object.monthly_necessity_costs_dict)
        self.current_month_leftover_net_income-=total_need_spend
        return pl.DataFrame(spent_dict)
        
    def get_monthly_emergency_fund_expendature(self,verbose=False):
        """Step 1: Build Emergency Fund of 6 months."""
        # Usual Case
        if (self.short_term_savings_total >= self.monthly_need_expendature*6):
            needed_to_complete_emergency_funds = 0.0
        else:
            needed_to_complete_emergency_funds = min(self.current_month_leftover_net_income, self.monthly_need_expendature*6-self.short_term_savings_total)
        # High Interest Dept Exception Case
        if (self.highest_interest_debt >= 0.15) and (self.short_term_savings_total >= self.monthly_need_expendature):
            needed_to_complete_emergency_funds=0.0
        if (self.short_term_savings_total < self.monthly_need_expendature) and (self.highest_interest_debt > 0.15):
            needed_to_complete_emergency_funds = min(self.current_month_leftover_net_income, self.monthly_need_expendature-self.short_term_savings_total)
        self.current_month_leftover_net_income-=needed_to_complete_emergency_funds
        # Allocate equally accross short term savings accounts
        for bank_account in self.short_term_investments:
            bank_account.contribute_funds(needed_to_complete_emergency_funds/len(self.short_term_investments))
        if verbose:
            print(f"Spend ${needed_to_complete_emergency_funds} on emergency fund.")
        return pl.DataFrame({"Emergency Fund" : needed_to_complete_emergency_funds})
        
    def get_monthly_contribution_to_employer_matching(self,verbose=False):
        """Step 2: Contribute to employer matching funds."""
        true_contribution_amounts=dict()
        for investment_object in self.employer_matched_investments:
            leftover_contribution_amount=self.matching_amounts_left[investment_object.type]
            feasible_contribution_amount = min(self.current_month_leftover_net_income, leftover_contribution_amount) 
            investment_object.contribute_funds(feasible_contribution_amount*2) # Multiply by two for matching
            self.current_month_leftover_net_income-=feasible_contribution_amount
            self.matching_amounts_left[investment_object.type]-=feasible_contribution_amount
            if verbose:
                print(f"Spend ${feasible_contribution_amount} on {investment_object.type} to complete employee match.")
            if self.matching_amounts_left[investment_object.type]!=0:
                print(f"WARNING: Did not complete matching for {investment_object.type} due to insufficient funds.")
            true_contribution_amounts.update({investment_object.type : feasible_contribution_amount})
            self.spent_401+=feasible_contribution_amount
        return pl.DataFrame(true_contribution_amounts)
    
    def pay_off_high_interest_debt(self,verbose=False):
        """Step 3: Pay off high interest debt."""
        debt_contribution_dict = dict()
        possible_contributed = min(self.maximum_monthly_loan_payment, self.current_month_leftover_net_income)
        for debt in self.debts:
            debt_balance = debt.outstanding_balance
            feasible_contribution_amount = min(possible_contributed, debt_balance)
            possible_contributed-=feasible_contribution_amount
            debt.make_payment(feasible_contribution_amount)
            self.current_month_leftover_net_income -= feasible_contribution_amount
            debt_contribution_dict.update({debt.type : feasible_contribution_amount})
            if verbose:
                print(f"Spend ${feasible_contribution_amount} on {debt.type} for dept payoff.")
        return pl.DataFrame(debt_contribution_dict)
            
    def get_IRA_contribution(self,verbose=False):
        """Step 4: Contribute to IRA. Does so evenly across IRAs if you have multiple (still dont understand why you would)."""
        ira_contribution_dict = dict()
        num_iras = len(self.other_ira_investments)
        max_yearly_contribution = 7000 # as of 2024
        per_account = max_yearly_contribution / num_iras / 12
        for investment_object in self.other_ira_investments:
            feasible_contribution_amount = min(self.current_month_leftover_net_income, per_account)
            investment_object.contribute_funds(feasible_contribution_amount)
            if verbose:
                print(f"Spend ${feasible_contribution_amount} on {investment_object.type} for IRA contribution.")
            self.current_month_leftover_net_income -= feasible_contribution_amount
            ira_contribution_dict[investment_object.type]=feasible_contribution_amount
            self.spent_IRA+=feasible_contribution_amount
        return pl.DataFrame(ira_contribution_dict)
    
    def allocate_savings_and_leisure_funds(self,
                                           savings_leftover_percent = 0.5, leisure_leftover_percent = 0.5, verbose=False):
        """Step 5: Excess Savings (i.e. to savings account, round out 401K beyond matching, other investments) and leisure money."""
        leftover = self.current_month_leftover_net_income
        self.current_month_leftover_net_income=0
        leftover_401_possible = self.max_401K_legal-self.spent_401
        leftover_IRA_possible = self.max_IRA_legal-self.spent_IRA
        # Contribute excess 401K
        if leftover >= leftover_401_possible:
            self.investments["Employer Matched Retirement"]["401K"].contribute_funds(leftover_401_possible)
            leftover-=leftover_401_possible
            excess_401 =leftover_401_possible
        else:
            self.investments["Employer Matched Retirement"]["401K"].contribute_funds(leftover)
            excess_401 =leftover
            leftover = 0.0
        if verbose:
            print(f"Excess 401K Contribution: ${excess_401}")
        # Contribute excess IRA
        if leftover >= leftover_IRA_possible:
            self.investments["IRA"]["IRA"].contribute_funds(leftover_IRA_possible)
            excess_IRA =leftover_IRA_possible
            leftover-=leftover_IRA_possible
        else:
            self.investments["IRA"]["IRA"].contribute_funds(leftover)
            excess_IRA =leftover
            leftover = 0.0
        if verbose:
            print(f"Excess IRA Contribution: ${excess_IRA}")
        # Leftover split savings and leisure
        for bank_account in self.short_term_investments:
            amount = (leftover*savings_leftover_percent)/len(self.short_term_investments)
            if verbose:
                print(f"Spend ${amount} on {bank_account.type} for savings.")
            bank_account.contribute_funds(amount)
        if verbose:
            print(f"Spend ${leftover*leisure_leftover_percent} on leftover leisure.")
        return pl.DataFrame({"Excess 401K" : excess_401,
                             "Excess IRA" : excess_IRA,
                             "Excess Savings" : leftover*savings_leftover_percent,
                             "Excess Leisure" : leftover*leisure_leftover_percent})
        
    def advance_one_month(self, verbose = False):
        """Tasks that happen irregardless of above steps (i.e. employer autocontribution to HSA due to HDHP health plan)."""
        # Go through steps
        base_df = pl.DataFrame({"Years" : self.years_past})
        self.get_non_decision_determined_updates(verbose=verbose)
        step_0 = self.get_monthly_spend_on_needs(verbose=verbose)
        if self.prioritize_matching_over_emergency_fund:
            step_2 = self.get_monthly_contribution_to_employer_matching(verbose=verbose)
        step_1 = self.get_monthly_emergency_fund_expendature(verbose=verbose)
        if not self.prioritize_matching_over_emergency_fund:
            step_2 = self.get_monthly_contribution_to_employer_matching(verbose=verbose)
        step_3 = self.pay_off_high_interest_debt(verbose=verbose)
        step_4 = self.get_IRA_contribution(verbose=verbose)
        step_5 = self.allocate_savings_and_leisure_funds(verbose=verbose)
        # return deductions spent
        deductions_spent_df = pl.concat([step_2, step_4, step_5[["Excess 401K", "Excess IRA"]]], how = "horizontal")
        deductions_spent_total = deductions_spent_df.sum_horizontal()[0]
        # return non deduction spent
        general_spending = pl.concat([step_0, step_1, step_3, step_5[["Excess Savings", "Excess Leisure"]]], how = "horizontal")
        general_spending_total = general_spending.sum_horizontal()[0]
        # Sum up deductions and recalculate with pre-tax benefits properly distributed
        month_net_income_post_deductions = self.monthly_net_income(additional_deductions=deductions_spent_total*12) # NOTE: THIS ASSUMES CONSTANT CONTRIBUTION TO DEDUCTION FUNDS
        # Find leftover to distribute after recalculating net income with deductions
        month_net_income_pre_deductions = self.monthly_net_income(additional_deductions=0)
        leftover_to_distribute = month_net_income_post_deductions-month_net_income_pre_deductions
        if verbose:
            print(f"After recalculating with deductions for ${deductions_spent_total} of spending distribute extra ${leftover_to_distribute} to savings and leisure equally.")
        # Distribute leftover to savings and leisure at 50% split
        general_spending = general_spending.with_columns([
            (pl.lit(leftover_to_distribute)/2).alias("Post-Deduction Savings"),
            (pl.lit(leftover_to_distribute)/2).alias("Post-Deduction Leisure")
        ])
        for bank_account in self.short_term_investments:
            amount = (leftover_to_distribute*0.5)/len(self.short_term_investments)
            bank_account.contribute_funds(amount)
        
        # Return final df
        this_month_df = pl.concat([base_df, deductions_spent_df, general_spending], how = "horizontal")
        self.paycheck_only_spending_df_list.append(pl.concat([base_df, general_spending], how = "horizontal"))
        self.spent_df_list.append(this_month_df)
        all_balances_dict = dict({"Years" : self.years_past})
        simplified_df_this_month = pl.DataFrame({"Savings" : step_1.sum_horizontal()[0] + step_5["Excess Savings"][0] + general_spending["Post-Deduction Savings"][0],
                                                 "Retirement/Health" : step_2.sum_horizontal()[0] + step_4.sum_horizontal()[0] + step_5[["Excess 401K", "Excess IRA"]].sum_horizontal()[0],
                                                 "Loans" : step_3.sum_horizontal()[0],
                                                 "Leisure" : step_0["Minimum Leisure"][0] + step_5["Excess Leisure"][0] + general_spending["Post-Deduction Leisure"][0],
                                                 "Need" : step_0.drop("Minimum Leisure").sum_horizontal()[0]})
        self.simplified_df_list.append(pl.concat([base_df, simplified_df_this_month], how = "horizontal"))
        for account_types in [self.short_term_investments, self.debts, self.employer_matched_investments, 
                              self.employer_flat_rate_investments, self.other_ira_investments, self.other_investments]:
            for account in account_types:
                all_balances_dict.update({account.type : account.outstanding_balance})
        self.records_df_list.append(pl.DataFrame(all_balances_dict))
        if verbose:
            print(this_month_df)
        return this_month_df
    
    def simulate_n_years(self, years, verbose = False):
        months = years*12
        for month in range(months):
            self.advance_one_month(verbose=verbose)
        return dict({"Spent" : pl.concat(self.spent_df_list, how = "vertical"), 
                     "Accounts" : pl.concat(self.records_df_list, how = "vertical"),
                     "Paycheck Only Spending" : pl.concat(self.paycheck_only_spending_df_list, how = "vertical"),
                     "Simplified Spending" : pl.concat(self.simplified_df_list, how = "vertical"),})
    
    def reset_profile(self):
        pass
    
    