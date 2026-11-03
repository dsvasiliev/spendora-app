from infrastructure.tools.get_user_data_path import get_user_data_path

APP_NAME = "Spendora"
VERSION = "0.0.1"

MONTHS_RU = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]

DB_PATH = get_user_data_path(APP_NAME) / "categories.memory"

EMAIL = 'help@spendora.ru'

# API
# WEBSITE_URL = "https://spendora.ru"
WEBSITE_URL = "http://127.0.0.1:8000"
ACTUAL_INFO_URL = WEBSITE_URL + "/actual_info"
IMPORTANT_INFO_URL = WEBSITE_URL + "/important_info"
UPDATER_URL = f"{WEBSITE_URL}/files/versions/updater"
TABLES_URL = WEBSITE_URL + "/tables"
TERMS_OF_USE_URL = f"{WEBSITE_URL}/legal/app/terms-of-use/{VERSION}"
PRIVACY_POLICY_URL = f"{WEBSITE_URL}/legal/app/privacy-policy/{VERSION}"
STATISTIC_URL = WEBSITE_URL + "/statistic"
SURVEY_URL = f"{WEBSITE_URL}/legal/survey"

