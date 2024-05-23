def calculate_net_income(gross_income, standard_deduction, federal_tax_brackets, state_tax_rate, fica_rate,
                         additional_deductions=0):
    """
    Calculate the net income from the gross income considering federal and state taxes.

    :param gross_income: Gross income in dollars.
    :param state_tax_rate: State tax rate as a decimal (e.g., 0.05 for 5%).
    :return: Net income in dollars.
    """

    # Apply the standard deduction
    taxable_income = gross_income - standard_deduction - additional_deductions
    if taxable_income <= 0:
        return gross_income  # If deduction is more than gross income, no tax

    # Calculate federal tax
    federal_tax = 0
    for bracket in federal_tax_brackets:
        if taxable_income > bracket[0]:
            federal_tax += bracket[0] * bracket[1]
            taxable_income -= bracket[0]
        else:
            federal_tax += taxable_income * bracket[1]
            break

    # Calculate state tax
    state_tax = gross_income * state_tax_rate

    # Calculate other mandatory deductions
    fica_tax = gross_income * fica_rate  

    # Calculate net income
    net_income = gross_income - (federal_tax + state_tax + fica_tax)

    return net_income

def flatten_investment_dict(nested_dict):
    """Flatten a nested dictionary to a single level with concatenated keys."""
    all_keys = []
    ret_dict = dict()
    for k1, inner_dict in nested_dict.items():
        for k2, v2 in inner_dict.items():
            if k2 in all_keys:
                raise ValueError("There is more than one investment type with the same name.")
            all_keys.append(k2)
            ret_dict.update({k2 : v2})
    return ret_dict