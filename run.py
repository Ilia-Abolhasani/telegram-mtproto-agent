import src
from src.server import Server
from src.Telegram import Telegram
from src.cron import manager
from src.config import Config


if __name__ == '__main__':
    server = Server()
    telegram_api = Telegram(
        Config.telegram_app_id,
        Config.telegram_app_hash,
        Config.telegram_phone,
        Config.database_encryption_key,
        Config.tdlib_directory,
        Config.start_mtproto_address,
        Config.start_mtproto_port,
        Config.start_mtproto_secret
    )
    result = telegram_api.remove_all_proxies()
    manager.start_jobs(server, telegram_api)
    telegram_api.idle()