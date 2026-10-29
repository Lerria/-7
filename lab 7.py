""" Візуалізація даних Світового банку.

Показник: GDP per capita (current US$). Країни: Україна та обрана користувачем.
"""

import requests
import matplotlib.pyplot as plt

# Параметри програми
INDICATOR = "NY.GDP.PCAP.CD"          # GDP per capita (current US$)
INDICATOR_NAME = "GDP per capita (current US$)"
COUNTRIES = "UA;PL"                   # Україна та Польща (для лінійного графіка)
START_YEAR = 2000
END_YEAR = 2023
API_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"


def build_url(countries):
    """Формує URL-адресу API для заданих країн (коди через ';')."""
    return (
        API_URL.format(countries=countries, indicator=INDICATOR)
        + f"?date={START_YEAR}:{END_YEAR}&format=json&per_page=200"
    )


def fetch_data(url):
    """Виконує HTTP-запит і повертає JSON-відповідь (або None при помилці)."""
    try:
        response = requests.get(url, timeout=30)
    except requests.exceptions.RequestException as error:
        print("Помилка виконання HTTP-запиту:", error)
        return None
    if response.status_code != 200:
        print("Помилка отримання даних, код відповіді:", response.status_code)
        return None
    return response.json()


def build_dataset(data):
    """Формує словник {країна: {рік: значення}} (записи без значення пропускаються)."""
    dataset = {}
    for item in data[1]:
        if item["value"] is None:
            continue
        country = item["country"]["value"]
        dataset.setdefault(country, {})[int(item["date"])] = item["value"]
    return dataset


def fetch_country(code):
    """Завантажує дані показника для однієї країни за її кодом (UA, PL, DE ...)."""
    data = fetch_data(build_url(code))
    # при неправильному коді API повертає список з одним елементом (повідомлення про помилку)
    if not data or len(data) < 2 or not data[1]:
        return None
    return build_dataset(data) or None


def plot_dynamics(dataset):
    """Графік динаміки показника для всіх країн набору на одній площині."""
    plt.figure(figsize=(10, 6))
    for country, values in dataset.items():
        years = sorted(values)
        plt.plot(years, [values[y] for y in years], marker="o", label=country)
    plt.title(f"Динаміка показника: {INDICATOR_NAME}, {START_YEAR}–{END_YEAR}")
    plt.xlabel("Рік")
    plt.ylabel("USD на одну особу")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("line_chart.png", dpi=150)
    plt.show()


def plot_bar(dataset):
    """Стовпчаста діаграма зміни показника за роками для однієї країни."""
    country, values = next(iter(dataset.items()))
    years = sorted(values)
    plt.figure(figsize=(10, 6))
    plt.bar(years, [values[y] for y in years], color="steelblue")
    plt.title(f"{INDICATOR_NAME}: {country}, {START_YEAR}–{END_YEAR}")
    plt.xlabel("Рік")
    plt.ylabel("USD на одну особу")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("bar_chart.png", dpi=150)
    plt.show()


def plot_pie(ukraine_values, country_name, country_values, year):
    """Кругова діаграма: частка України та обраної країни за заданий рік."""
    if year not in ukraine_values or year not in country_values:
        print(f"Для {year} року немає даних для обох країн")
        return
    labels = ["Ukraine", country_name]
    values = [ukraine_values[year], country_values[year]]
    plt.figure(figsize=(7, 7))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90,
            colors=["#ff7f0e", "#1f77b4"])
    plt.title(f"{INDICATOR_NAME}: частка країн у сумі за {year} рік")
    plt.tight_layout()
    plt.savefig("pie_chart.png", dpi=150)
    plt.show()


def main():
    data = fetch_data(build_url(COUNTRIES))
    if not data or len(data) < 2:
        print("Дані відсутні")
        return
    dataset = build_dataset(data)
    if "Ukraine" not in dataset:
        print("Дані для України відсутні")
        return

    # 1. Динаміка показника: Україна та Польща
    plot_dynamics(dataset)

    # 2. Стовпчаста діаграма для країни, введеної користувачем
    code = input("Введіть код країни (наприклад, DE, US, FR): ").strip()
    country_data = fetch_country(code)
    if not country_data:
        print("Дані для цієї країни відсутні або код введено неправильно")
        return
    plot_bar(country_data)

    # 3. Кругова діаграма: Україна та обрана країна за вказаний рік
    try:
        year = int(input(f"Введіть рік ({START_YEAR}-{END_YEAR}) для кругової діаграми: "))
    except ValueError:
        print("Рік потрібно ввести числом")
        return
    country_name, country_values = next(iter(country_data.items()))
    plot_pie(dataset["Ukraine"], country_name, country_values, year)


if __name__ == "__main__":
    main()
