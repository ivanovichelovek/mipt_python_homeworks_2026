#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

DATE_LEN = 10
STATS_QUERY_LEN = 2


class DateStatistics:
    def __init__(self):
        self.income = 0.0
        self.outcome = 0.0
        self.categories = {}

    def new_income(self, income: float) -> None:
        self.income += income

    def new_outcome(self, category: str, outcome: float) -> None:
        self.outcome += outcome
        if category not in self.categories:
            self.categories[category] = 0
        self.categories[category] += outcome


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return bool((year % 4 == 0 and year % 100 != 0) or (year % 100 == 0 and year % 400 == 0))


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if len(maybe_dt) != DATE_LEN or maybe_dt[2] != "-" or maybe_dt[5] != "-":
        return None
    if not maybe_dt[0:2].isdigit() or not maybe_dt[3:5].isdigit() or not maybe_dt[6:].isdigit():
        return None
    return (int(maybe_dt[0:2]), int(maybe_dt[3:5]), int(maybe_dt[6:]))


def check_date(date: tuple[int, int, int]) -> bool:
    month_capacity = [31, 29 if is_leap_year(date[2]) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return bool(date[0] <= month_capacity[date[1] - 1])  # Change this


def get_query(inpt_list: list, inpt_len: int, category: str | None, date: list, query_type: str) -> list | None:
    if len(inpt_len) > STATS_QUERY_LEN:
        number = float(inpt_list[-2].replace(",", "."))
        if number <= 0:
            print(INCORRECT_DATE_MSG)
            return None
    if len(inpt_list) != inpt_len or not date or not check_date(date):
        print(INCORRECT_DATE_MSG)
        return None
    print(OP_SUCCESS_MSG)
    return [query_type, category, number, date]


def split_query(inpt: str) -> list | None:
    inpt_list = list(inpt.split())
    query_type = inpt_list[0]
    date = extract_date(inpt_list[-1])
    match query_type:
        case "income":
            return get_query(inpt_list, 3, None, date, query_type)
        case "cost":
            return get_query(inpt_list, 4, inpt_list[1], date, query_type)
        case "stats":
            return get_query(inpt_list, 2, None, date, query_type)
        case _:
            print(UNKNOWN_COMMAND_MSG)
            return None


def print_stats(date_stats: DateStatistics, date: tuple, capital: float) -> None:
    month_income = date_stats.income - date_stats.outcome
    categories = sorted([[key, value] for key, value in date_stats.categories.items()], key=lambda x: x[0])
    print(f"""Your statistics as of {"-".join(str(i) for i in date)}:
    Total capital: {capital} rubles
    This month, the {"loss amounted to" if month_income < 0 else "profit amounted to"} {abs(month_income)} rubles
    Income: {date_stats.income} rubles
    Expenses: {date_stats.outcome} rubles

    Details (category: amount):
    {"\n".join([f"{i + 1}. {categories[i][0]}: {categories[i][1]}" for i in range(len(categories))])}""")


def income_handler(amount: float, income_date: str) -> str:
    return f"{OP_SUCCESS_MSG} {amount=} {income_date=}"


def main() -> None:
    capital = 0
    date_stats = {}

    query = ""
    while True:
        query = split_query(input())
        match query[0]:
            case None:
                continue
            case "income":
                if query[2] not in date_stats:
                    date_stats[query[2]] = DateStatistics()
                date_stats[query[2]].new_income(query[1])
                capital += query[1]
            case "cost":
                if query[3] not in date_stats:
                    date_stats[query[3]] = DateStatistics()
                date_stats[query[3]].new_outcome(query[1], query[2])
                capital -= query[2]
            case "stats":
                if query[1] not in date_stats:
                    date_stats[query[1]] = DateStatistics()
                print_stats(date_stats[query[1]], query[1], capital)


if __name__ == "__main__":
    main()
