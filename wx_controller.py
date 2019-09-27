import re
import time
import os
import langid
import requests


class wx_controller:
    def __init__(self, bot):
        self.bot = bot

    def login_callback(self):
        # work after login
        print(self.bot, 'login!')
        # main_worker
        chat_object = self.bot.self
        ReceiveMessage(chat_object, self.bot)


def ReceiveMessage(chat_object, bot):
    global MSGLIST
    MSGLIST = []
    global super_look_group
    super_look_group = list(bot.groups())  # 此处可设置特别关注的群，默认是所有群

    @bot.register()
    def receive_msg_process(msg):
        global MSGLIST, super_look_group
        message = msg.raw
        content = message['Content']
        pattern = r'<sysmsg type="revokemsg"><revokemsg>.+?<msgid>([0-9]+)</msgid>'
        msgid = re.findall(pattern, content)
        if msgid != []:
            oldMsgId = msgid[0]
            for temp_msg in MSGLIST:
                temp_msg_id = temp_msg.raw['MsgId']
                if temp_msg_id == oldMsgId:
                    if temp_msg.type == 'Text':
                        if temp_msg.receiver == bot.self:
                            if temp_msg.member is not None:
                                temp_msg.sender.send(
                                    '【' + temp_msg.raw['ActualNickName'] + '】刚撤回了: ' + temp_msg.text)
                            else:
                                temp_msg.sender.send('你刚撤回了: ' + temp_msg.text)
                        else:
                            temp_msg.receiver.send(temp_msg.sender + '刚撤回了: ' + temp_msg.text)
                    else:
                        if temp_msg.member is not None:
                            temp_msg.sender.send(
                                '【' + temp_msg.raw['ActualNickName'] + '】刚撤回了: 一个文件【' + temp_msg.file_name + '】')
                        else:
                            temp_msg.sender.send('你刚撤回了: 一个文件【' + temp_msg.file_name + '】')

                        filename = './temp/' + temp_msg.file_name
                        temp_msg.get_file(filename)
                        temp_msg.sender.send_file(filename)
                        os.remove(filename)
        else:
            temp_list = []
            for i in MSGLIST:
                if i.raw['CreateTime'] > int(time.time()) - 180:
                    temp_list.append(i)
            MSGLIST = temp_list
            if msg.member is not None and msg.sender in super_look_group:
                MSGLIST.append(msg)
            else:
                MSGLIST.append(msg)

    bot.registered.disable()
    # 检验机器人是否在线
    chat_object.send('若你不确定机器人是否在线，可发送【小白】，本尊会马上跳出来，看不见本尊那就断线了')
    send_number = len(bot.messages.search(sender=bot.self))
    IS_TRANSLATE = False
    while True:
        try:
            sent_msgs = bot.messages.search(sender=bot.self)
            if len(sent_msgs) > send_number:
                SELF_SEND_NUMBER = 0
                for i in sent_msgs[send_number:]:
                    if i.receiver != chat_object:
                        continue
                    if IS_TRANSLATE is False:
                        if i.text == '小白':
                            chat_object.send('本尊还在哦！')
                            SELF_SEND_NUMBER += 1
                        elif i.text == '防撤回':
                            bot.registered.enable(receive_msg_process)
                            chat_object.send('防撤回已启动')
                            SELF_SEND_NUMBER += 1
                        elif i.text == '取消防撤回':
                            bot.registered.disable(receive_msg_process)
                            MSGLIST = []
                            chat_object.send('防撤回已关闭')
                            SELF_SEND_NUMBER += 1
                        elif i.text == '翻译':
                            IS_TRANSLATE = True
                            chat_object.send('打开翻译')
                            SELF_SEND_NUMBER += 1
                    else:
                        if i.text == '取消翻译':
                            IS_TRANSLATE = False
                            chat_object.send('翻译已关闭')
                            SELF_SEND_NUMBER += 1
                            continue
                        lang_type = langid.classify(i.text)[0]
                        # print(i.text)
                        if lang_type == 'zh':
                            # 中译英
                            type = 'ZH_CN2EN'
                        elif lang_type == 'en':
                            # 英译中
                            type = 'EN2ZH_CN'
                        else:
                            type = 'AUTO'
                        try:
                            result_response = requests.get(
                                'http://fanyi.youdao.com/translate?&doctype=json&type=' + type + '&i=' + i.text)
                            result_json = result_response.json()
                            target = result_json['translateResult'][0][0]['tgt']
                        except:
                            target = '网络出现了故障'
                        finally:
                            chat_object.send('【' + type + '翻译结果】:' + target)
                            SELF_SEND_NUMBER += 1
                send_number = len(sent_msgs) + SELF_SEND_NUMBER
        except:
            print(bot.self, '接收信息报错')
            break
