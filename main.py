import wxpy
from wx_controller import wx_controller as WX_C
import os

class MainProcess:
    def __init__(self):
        is_save_bot = './bot_saver/'
        bot_temp_name = input('请问你登陆微信的备注是(输入0不缓存)：')
        if bot_temp_name == '0':
            is_save_bot = False
        else:
            is_save_bot += bot_temp_name + '.pkl'
        bot = wxpy.Bot(cache_path=is_save_bot, console_qr=False)  # 如果你是linux用户，请把console_qr设置为True或者2
        wx_c = WX_C(bot)
        wx_c.login_callback()
        bot.join()


if __name__ == '__main__':
    if os.path.exists('./bot_saver') is False:
        os.mkdir('./bot_saver')
    main = MainProcess()
