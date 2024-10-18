from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
import requests
import time


def read_user_ids():
    # читаем список user_id из файла
    with open('id.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]


def close_browser(user_id):
    # функция для закрытия браузера по user_id
    try:
        close_url = f"http://local.adspower.net:50325/api/v1/browser/stop?user_id={user_id}"
        requests.get(close_url).json()
    except Exception as e:
        print(f"Error while closing browser for {user_id}: {str(e)}")


def run_for_user(user_id, numbers):
    driver = None
    start_time = datetime.now()

    try:
        # открываем браузер для текущего user_id
        open_url = f"http://local.adspower.net:50325/api/v1/browser/start?user_id={user_id}"
        response = requests.get(open_url).json()

        # настройка ChromeDriver для удалённого подключения
        chrome_driver = response["data"]["webdriver"]
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", response["data"]["ws"]["selenium"])

        service = Service(executable_path=chrome_driver)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(1200, 720)

        # заходим на сайт
        driver.get("https://mission.swanchain.io/")

        # нажимаем на кнопку ежедневного бокса
        time.sleep(2)
        reward_button = driver.find_element(By.CSS_SELECTOR, ".reward-card-btn")
        reward_button.click()

        # вводим числа дня
        for number in numbers:
            button_selector = f".random-image{number}"
            button = driver.find_element(By.CSS_SELECTOR, button_selector)
            button.click()
            time.sleep(1)

        # подтверждаем действие нажатием на кнопку
        confirm_button = driver.find_element(By.CSS_SELECTOR, ".confirm-btn")
        confirm_button.click()

        # еще раз подтверждаем
        time.sleep(1)
        confirm_button = driver.find_element(By.CSS_SELECTOR, ".confirm-btn")
        confirm_button.click()

        # задержка, чтобы увидеть результат
        time.sleep(3)

        end_time = datetime.now()
        print(
            f"Completed work: {user_id} from {start_time.strftime('%Y-%m-%d %H:%M:%S')} to"
            f" {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"Error while working with {user_id}: {str(e)}")
        with open('error.txt', 'a') as error_file:
            error_file.write(f"{user_id}: {str(e)}\n")

    finally:
        # закрытие браузера в любом случае
        close_browser(user_id)
        if 'driver' in locals():
            driver.quit()


def main():
    user_ids = read_user_ids()

    # ввод трех чисел от 1 до 12 включительно
    try:
        numbers = [int(input(f"Введите число {i+1} (от 1 до 12 включительно): ")) for i in range(3)]
        if not all(1 <= num <= 12 for num in numbers):
            raise ValueError("Числа должны быть в диапазоне от 1 до 12 включительно.")
    except ValueError as e:
        print(f"Ошибка: {e}")
        return

    # основной цикл по каждому user_id
    for user_id in user_ids:
        if user_id.lower() == 'stop':
            break
        run_for_user(user_id, numbers)


if __name__ == "__main__":
    main()
