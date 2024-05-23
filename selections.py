from objects import MonthlyNeededExpenses, Debt, Insurance, Investment, EmployerBenefits, FinancialProfile
import numpy as np

## Basic Settings

look_ahead_years = 20

### Taxes and max investments

federal_tax_brackets = [
    (11600, 0.10),
    (47150, 0.12),
    (100525, 0.22),
    (191950, 0.24),
    (243725, 0.32),
    (609350, 0.35),
    (float('inf'), 0.37)
] # Federal tax brackets 

standard_deduction=14600 # applys to both state and federal taxes, as well as FICA

fica_rate=0.0765 # Includes medicare, social security, etc

state_tax_rate=0.0475 # Flat rate in NC

max_401K_legal= 23000 / 12

max_IRA_legal= 7000 / 12

#### Personal Settings

current_age = 24
maximum_monthly_loan_payment = 400.0
prioritize_matching_over_emergency_fund = True

# Define debts

debts = dict({
    "Private Student Loan" : Debt(initial_outstanding_balance=25000, interest_rate=0.11, compounding="daily", type = "Private Student Loan"),
    "Federal Student Loan" : Debt(initial_outstanding_balance=25000, interest_rate=0.04, compounding="annually", type = "Federal Student Loan")
})

# Define insurances

insurances = dict({
    "Health" : Insurance(monthly_premium=100, type = "Health"),
    "Car" : Insurance(monthly_premium=100, type = "Car"),
    "Renters" :  Insurance(monthly_premium=100, type = "renters")
})

# Define investments

short_term_investments = dict({
    "Savings" : Investment(initial_outstanding_balance=10000, interest_rate=0.01, compounding="annually", type = "Savings")
})

employer_matched_investments = dict({
    "401K" : Investment(initial_outstanding_balance=0, interest_rate=0.06, compounding="annually", type = "401K")
})

ira_investments = dict({
    "IRA" : Investment(initial_outstanding_balance=0, interest_rate=0.05, compounding="annually", type = "Traditional IRA")
})

other_investments = dict({
    "HSA" : Investment(initial_outstanding_balance=0, interest_rate=0.05, compounding="annually", type = "HSA")
})

investments = dict({
    "Short Term" : short_term_investments,
    "Employer Matched Retirement" : employer_matched_investments,
    "IRA" : ira_investments,
    "Other" : other_investments
})

# Define job benefits & salary

job_benefits = dict({"Biocore" : EmployerBenefits(salary=60000,
                                                  retirement_matching=dict({"401K" : 0.04}),
                                                  monthly_flat_rate_contributions=dict({"HSA" : 100}),
                                                  company_insurances = ["Health"],
                                                  insurances=insurances)})

# Define needs
needs = dict({
    "Personal Needs" : MonthlyNeededExpenses(rent=1500, food=500, electric=50, internet=35/2, 
                                             personal_insurance=["Car", "Renters"],
                                             minimum_excess_expendature = 700,
                                             insurances=insurances)
})

profile = FinancialProfile(debts = debts, 
                           investments = investments, 
                           monthly_needs = needs, 
                           employer_benefits = job_benefits, 
                           maximum_monthly_loan_payment = maximum_monthly_loan_payment,
                           federal_tax_brackets = federal_tax_brackets, 
                           standard_deduction = standard_deduction, fica_rate = fica_rate, 
                           state_tax_rate = state_tax_rate, 
                           max_401K_legal = max_401K_legal, max_IRA_legal = max_IRA_legal, 
                           prioritize_matching_over_emergency_fund=prioritize_matching_over_emergency_fund)

results = profile.simulate_n_years(years=50, verbose = False)