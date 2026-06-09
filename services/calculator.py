def calculate_markup_amount(total_rub, markup):
    return total_rub * (markup / 100)


def calculate_net_rub(total_rub, markup):
    markup_amount = calculate_markup_amount(total_rub, markup)
    return total_rub - markup_amount


def calculate_usdt(net_rub, rate):
    if rate <= 0:
        return 0
    return net_rub / rate