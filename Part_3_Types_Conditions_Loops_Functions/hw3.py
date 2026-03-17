#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

DATE_LEN = 10
STATS_QUERY_LEN = 2
NORMILISED_QUERY_LEN = 4

TUPLE_TRIPLE_INT = tuple[int, int, int]
GET_QUERY_RETURN_TYPE = tuple[str, str | None, float, TUPLE_TRIPLE_INT]


class DateStatistics:
    def __init__(self) -> None:
        self.income = float(0)
        self.outcome = float(0)
        self.categories: dict[str, float] = {}

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
    if not (day.isdigit() or year.isdigit()):
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
    date: TUPLE_TRIPLE_INT | None,
    query_type: str,
) -> GET_QUERY_RETURN_TYPE | None:
    if not date or not check_date(date):
        print(INCORRECT_DATE_MSG)  # noqa: T201
        return None
    print(OP_SUCCESS_MSG)  # noqa: T201
    if inpt_len > STATS_QUERY_LEN:
        number = float(inpt_list[-2].replace(",", "."))
        if number <= 0:
            print(INCORRECT_DATE_MSG)  # noqa: T201
            return None
    else:
        number = 0
    return (query_type, category, number, date)


def check_args(query_type: str, additional_args: int) -> bool:
    match query_type:
        case "income":
            return additional_args == 1
        case "cost":
            return additional_args == 0
        case "stats":
            return additional_args == STATS_QUERY_LEN
        case _:
            return False


def split_query(inpt: str) -> tuple[str, str | None, float, TUPLE_TRIPLE_INT] | None:
    inpt_list = list(inpt.split())
    additional_args = 0
    while len(inpt_list) < NORMILISED_QUERY_LEN:
        additional_args += 1
        inpt_list.insert(1, "")
    query_type = inpt_list[0]
    date = extract_date(inpt_list[-1])
    check_answer = check_args(query_type, additional_args)
    if not check_answer:
        print(UNKNOWN_COMMAND_MSG)  # noqa: T201
        return None
    match query_type:
        case "income":
            return get_query(inpt_list, 3, None, date, query_type)
        case "cost":
            return get_query(inpt_list, 4, inpt_list[1], date, query_type)
        case "stats":
            return get_query(inpt_list, 2, None, date, query_type)
        case _:
            print(UNKNOWN_COMMAND_MSG)  # noqa: T201
            return None


def get_category_string(categories: list[tuple[str, float]], i: int) -> str:
    return f"{i + 1}. {categories[i][0]}: {categories[i][1]}"


def print_stats(date_stats: DateStatistics, date: TUPLE_TRIPLE_INT, capital: float) -> None:
    month_income = date_stats.income - date_stats.outcome
    categories = [(key, value) for key, value in date_stats.categories.items()]
    categories = sorted(categories, key=lambda x: x[0])
    categories_numed_list = [get_category_string(categories, i) for i in range(len(categories))]
    print(f"Your statistics as of {"-".join(str(i) for i in date)}:")  # noqa: T201
    print(f"Total capital: {capital} rubles")  # noqa: T201
    print(  # noqa: T201
        f"This month, the {"loss amounted to" if month_income < 0 else "profit amounted to"} {abs(month_income)} rubles"
    )
    print(f"Income: {date_stats.income} rubles")  # noqa: T201
    print(f"Expenses: {date_stats.outcome} rubles")  # noqa: T201
    print()  # noqa: T201
    print("Details (category: amount):")  # noqa: T201
    print(f"{"\n".join(categories_numed_list)}")  # noqa: T201


def income_handler(amount: float, income_date: str) -> str:
    return f"{OP_SUCCESS_MSG} {amount=} {income_date=}"


def main() -> None:
    capital = float(0)
    date_stats = {}

    while True:
        query = split_query(input())
        if not query:
            continue
        query_type, category, number, date = query
        if date not in date_stats:
            date_stats[date] = DateStatistics()
        match query_type:
            case "income":
                date_stats[date].new_income(income=number)
                capital += number
            case "cost":
                if not category:
                    continue
                date_stats[date].new_outcome(category=category, outcome=number)
                capital -= number
            case "stats":
                print_stats(date_stats[date], date, capital)


if __name__ == "__main__":
    main()
