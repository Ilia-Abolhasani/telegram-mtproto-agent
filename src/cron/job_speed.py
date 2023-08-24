from src.util import DotDict
from src.config import Config
from src.util import create_packs
from src.cron import job_lock, queue

import tqdm


def download_spped(telegram_api):
    result = telegram_api.get_message(
        Config.download_chat_id,
        Config.download_message_id)
    content = result.update["content"]
    document = content['document']
    document = document['document']
    file_id = document['id']
    return telegram_api.speed_test(file_id)


def _start(server, telegram_api, proxies):
    result = telegram_api.remove_all_proxies()
    batch = Config.batch_size_speed_test
    pack_proxies = create_packs(proxies, batch)
    for pack in tqdm.tqdm(pack_proxies):
        report_list = []
        for proxy in pack:
            proxy = DotDict(proxy)
            report = {"proxy_id": proxy.id}
            result = telegram_api.add_proxy(
                proxy.server,
                proxy.port,
                proxy.secret)
            td_proxy_id = result.update['id']
            result = telegram_api.enable_proxy(td_proxy_id)
            result = telegram_api.ping_proxy(td_proxy_id)
            seconds = -1
            speed = 0
            if (not result.error):
                seconds = result.update['seconds'] * 1000
                speed = download_spped(telegram_api)
            result = telegram_api.remove_proxy(td_proxy_id)
            report['speed'] = speed
            report['ping'] = seconds
            report_list.append(report)
        server.send_speed_report({"reports": report_list})


def _start_speed(server, telegram_api):
    result = telegram_api.remove_all_proxies()
    try:
        result = server.get_speed_test_proxies()
    except:
        return
    if not result:
        return
    proxies = result['result']
    if (len(proxies) == 0):
        queue.speed_test = False
        return

    _start(server,
           telegram_api,
           proxies
           )


def start_safe(server, telegram_api):
    global queue
    if (queue.speed_test):
        return
    queue.speed_test = True
    _start_speed(server, telegram_api)
    queue.speed_test = False