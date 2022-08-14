def number_rounder(number:float) -> str:
    # if the number is not 1, 2, 3 ...
    if int(number) != number:
        # separate the number into two parts (integer part and decimal part)
        # rstrip method does not delete the zero before the point (.) sign
        integer, decimal = f"{number:.20f}".rstrip("0").split(".")
        # get the number of zeros at the beginning of the deciaml part 
        zeros = len(decimal) - len(decimal.strip("0"))
        # add rstrip method for handling numbers like this -> 1.300002 to not convert to this -> 1.300 
        return (integer+"."+decimal[:zeros+3]).rstrip("0")
    else: return str(number)


def percentage_difference(list_of_numbers:list) -> float:
    row = list_of_numbers
    while True:
        min_value, max_value = min(row), max(row)
        try:
            result = (max_value-min_value)*100/min_value
        except ZeroDivisionError:
            row.remove(min_value)
            continue
        # correct result
        if result < 200:
            break
        # delete the maximum number and try again
        else:
            row.remove(max_value)
    # return rounded result with 2 decimal place
    return round(result,2)