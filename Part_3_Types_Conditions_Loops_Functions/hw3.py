#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_LEN = 10
STATS_QUERY_LEN = 2
NORMILISED_QUERY_LEN = 4

TUPLE_TRIPLE_INT = tuple[int, int, int]
GET_QUERY_RETURN_TYPE = tuple[str, str | None, float, str | None]


EXPENSE_CATEGORIES = {  # noqa: RUF100, WPS407
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}


capital: float = float(0)
date_stats_capital: dict[str, list[float]] = {}
date_stats_categories: dict[str, dict[str, float]] = {}
financial_transactions_storage: list[dict[str, Any]] = []


def check_category(category: str) -> str | None:
    if "::" not in category:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    main_cat, loc_cat = map(str, category.split("::"))
    if main_cat not in EXPENSE_CATEGORIES or loc_cat not in EXPENSE_CATEGORIES[main_cat]:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    return None


def check_date_main(date: str | None) -> str | None:
    if not date or not check_date(extract_date(date)):
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    return None


def check_number(number: str) -> str | None:
    number_fl: float = float(number.replace(",", "."))
    if number_fl <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    return None


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def extract_date(maybe_dt: str) -> TUPLE_TRIPLE_INT | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if len(maybe_dt) != DATE_LEN:
        return None
    if maybe_dt[2] != "-" or maybe_dt[5] != "-":
        return None
    day = maybe_dt[:2]
    month = maybe_dt[3:5]
    year = maybe_dt[6:]
    if not (day.isdigit() and year.isdigit()):
        return None
    if not month.isdigit():
        return None
    return (int(day), int(month), int(year))


def check_date(date: TUPLE_TRIPLE_INT | None) -> bool:
    if not date:
        return False
    february = 29 if is_leap_year(date[2]) else 28
    month_capacity = [31, february, 31, 30, 31, 30]
    month_capacity += [31, 31, 30, 31, 30, 31]
    return bool(date[0] <= month_capacity[date[1] - 1])


def get_query(
    inpt_list: list[str],
    inpt_len: int,
    category: str | None,
    date: str | None,
    query_type: str,
) -> GET_QUERY_RETURN_TYPE | None:
    if check_date_main(date):
        print(INCORRECT_DATE_MSG)
        return None
    if inpt_len > STATS_QUERY_LEN:
        number = float(inpt_list[-2].replace(",", "."))
        if check_number(inpt_list[-2]):
            print(NONPOSITIVE_VALUE_MSG)
            return None
    else:
        number = 0
    return (query_type, category, number, date)


def check_args(query_type: str, additional_args: int) -> bool:
    match query_type:
        case "income":
            return additional_args == 1
        case "cost":
            return additional_args in (0, STATS_QUERY_LEN)
        case "stats":
            return additional_args == STATS_QUERY_LEN
        case _:
            return False


def split_query(inpt: str) -> tuple[str, str | None, float, str | None] | None:
    inpt_list = list(inpt.split())
    additional_args = 0
    while len(inpt_list) < NORMILISED_QUERY_LEN:
        additional_args += 1
        inpt_list.insert(1, "")
    query_type = inpt_list[0]
    if not check_args(query_type, additional_args):
        print(UNKNOWN_COMMAND_MSG)
        return None
    match query_type:
        case "income":
            return get_query(inpt_list, 3, None, inpt_list[-1], query_type)
        case "cost":
            needed_args = 4 - additional_args
            return get_query(inpt_list, needed_args, inpt_list[1], inpt_list[-1], query_type)
        case "stats":
            return get_query(inpt_list, 2, None, inpt_list[-1], query_type)
        case _:
            print(UNKNOWN_COMMAND_MSG)
            return None


def get_category_string(categories: list[tuple[str, float]], i: int) -> str:
    category = categories[i][0]
    value = categories[i][1]
    index = i + 1
    return f"{index}. {category}: {value}"


def print_month_capital(month_income: float) -> None:
    month_income_abs = abs(month_income)
    print_message = "loss amounted to" if month_income < 0 else "profit amounted to"
    print(
        f"This month, the {print_message} {month_income_abs} rubles"
    )


def print_categories_list(categories_numed_list: list[str]) -> None:
    categories_numed_list_str = "\n".join(categories_numed_list)
    print(f"{categories_numed_list_str}")


def print_stats(date_str: str) -> None:
    income = date_stats_capital[date_str][0]
    cost = date_stats_capital[date_str][1]
    month_income = income - cost
    categories = [(key, value) for key, value in date_stats_categories[date_str].items()]
    categories = sorted(categories, key=lambda x: x[0])
    categories_numed_list = [get_category_string(categories, i) for i in range(len(categories))]
    print(f"Your statistics as of {date_str}:")
    print(f"Total capital: {capital} rubles")
    print_month_capital(month_income)
    print(f"Income: {income} rubles")
    print(f"Expenses: {cost} rubles")
    print()
    print("Details (category: amount):")
    print_categories_list(categories_numed_list)


def income_handler(amount: float, income_date: str) -> str:
    global capital  # noqa: PLW0603
    if check_number(str(amount)):
        return NONPOSITIVE_VALUE_MSG
    if check_date_main(income_date):
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({"amount": amount, "date": extract_date(income_date)})
    capital += amount
    if income_date not in date_stats_capital:
        date_stats_capital[income_date] = [float(0), float(0)]
        date_stats_categories[income_date] = {}
    date_stats_capital[income_date][0] += amount
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    global capital  # noqa: PLW0603
    if check_category(category_name):
        return NOT_EXISTS_CATEGORY
    if check_number(str(amount)):
        return NONPOSITIVE_VALUE_MSG
    if check_date_main(income_date):
        return INCORRECT_DATE_MSG
    loc_cat = category_name.split("::")[1]
    financial_transactions_storage.append({"category": category_name,
                                           "amount": amount, "date": extract_date(income_date)})
    capital -= amount
    if income_date not in date_stats_categories:
        date_stats_capital[income_date] = [float(0), float(0)]
        date_stats_categories[income_date] = {}
    date_stats_capital[income_date][1] += amount
    if loc_cat not in date_stats_categories[income_date]:
        date_stats_categories[income_date][loc_cat] = float(0)
    date_stats_categories[income_date][loc_cat] += amount
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categors = [f"{k}::{v}" for k, kv in EXPENSE_CATEGORIES.items() for v in kv]
    return "\n".join(categors)


def stats_handler(report_date: str) -> str:
    print_stats(report_date)
    return f"Statistic for {report_date}"


def proccess_new_query() -> bool:
    inpt = input()
    if not inpt:
        return False
    query = split_query(inpt)
    if not query:
        return True
    match query[0]:
        case "income":
            if not query[3]:
                print(UNKNOWN_COMMAND_MSG)
                return True
            print(income_handler(query[2], query[3]))
        case "cost":
            if not query[2]:
                print(cost_categories_handler())
            else:
                if not query[3] or not query[1]:
                    print(UNKNOWN_COMMAND_MSG)
                    return True
                print(cost_handler(query[1], query[2], query[3]))
        case "stats":
            if not query[3]:
                print(UNKNOWN_COMMAND_MSG)
                return True
            print(stats_handler(query[3]))
    return True


def main() -> None:
    while True:
        if not proccess_new_query():
            break


if __name__ == "__main__":
    main()
