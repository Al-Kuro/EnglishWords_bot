def get_call_data_form():
    form = 'form'
    form_first_lst = ['3', '4', '5']
    form_second_lst = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    form_third_lst = ['yes_rates', 'no_rates']

    form_separately = form, form_first_lst, form_second_lst, form_third_lst
    form_all = form, *form_first_lst, *form_second_lst, *form_third_lst

    return form_separately, form_all
