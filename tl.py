from ast import arg
import discord

import messages
import common
import re

async def time_line(message, data, command_args, mention_ids):
    msg = ''
   
    words = dict()

    try :

        target_id = common.get_target_id(mention_ids)

         # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        if(command_args[1] > '90' or command_args[1] < '0'):
            raise common.CommandError("時間の指定は0 ~ 90 秒で指定してください\n")

        # 対象となる時刻の取得
        tl_time = int(command_args[1])

        text = ''

        (text, target_List) = argsList(command_args)

        """
        #単語の抽出
        repatter = r'[0-1]:[0-9][0-9]\s[^0-1]*'
        text = message.content.translate( str.maketrans({chr(0xFF10 + i) : chr(0x30 + i) for i in range(0, 10)}) )
        text = text.translate( str.maketrans({"：":":"}) )

        #説明文の抽出
        #free_str = ''
        #freepta = r'^(?![0-1]:[0-9][0-9]).*$'
        #free_str = re.findall(freepta, text, flags=re.DOTALL)


        target_List = re.findall(repatter, text, flags=re.DOTALL)
        if (len(target_List) in [0]):
            raise common.CommandError("TLが見つかりません\n")
        """

        #リストの時間と文字を分割
        target_str = []
        for i in range(len(target_List)):
            #全角スペースを半角スペースに置き換える
            target_List[i] = target_List[i].replace("　"," ")

            repatter = (' +')
            target_str.append( re.split(repatter, target_List[i], maxsplit = 1) )

            #TLの時間を秒に直してリストを更新
            target_str[i][0] = (90 - get_second(target_str[i][0])) * -1

            #TL開始時間を足す
            target_str[i][0] += tl_time

            #秒を分:秒の形に戻す
            target_str[i][0] = get_min_sec(target_str[i][0])
        
        #埋め込みを作成
        embed = discord.Embed(title=" ", color=0x00ff00)
         
        #表示用のメッセージ作成
        value_msg = ''
        #表示するメッセージを作成
        target_str = sort_tl_list(target_str)
        value_msg += createTlList(target_str)
        embed.add_field(name = 'TL'+ str(tl_time) +'秒の持ち越しですよ～☆', value = '```prolog\n' + text + value_msg + '```', inline=False) # フィールドを追加。
        #埋め込みを送信
        new_message = await message.channel.send(embed=embed)
        #await new_message.delete(delay = common.REPLY_DISPLAY_TIME)

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_tl_arg)

    return (True,msg)

#分:秒 の文字列を 整数型の秒数で返す
def get_min_sec(sec_str):
    rt = ''
    if(sec_str >= 70):
        rt += ' 1:'+ str(sec_str % 60)
    elif(sec_str >= 60):
        rt += ' 1:0'+ str(sec_str % 60)
    elif(sec_str >= 10):
        rt += ' 0:' + str(sec_str)
    elif(sec_str >= 0):
        rt += ' 0:0' + str(sec_str)
    elif(sec_str > -10):
        rt += '-0:0' + str(sec_str * -1)
    elif(sec_str > -60):
        rt += '-0:' + str(sec_str * -1)
    elif(sec_str > -70):
        rt += '-1:0' + str((sec_str * -1)% 60)
    elif(sec_str >= -90):
        rt += '-1:' + str((sec_str * -1)% 60)
    else:
        print('err')

    return rt

#command argsからリストを生成
def argsList(args):
    index = 0
    pettern = r'[0-1]:[0-9][0-9]'
    creList = []
    msg = ''
    flg = True
    text = ''
    for i in range(2, len(args)):
        #全角対応
        text = args[i].translate( str.maketrans({chr(0xFF10 + i) : chr(0x30 + i) for i in range(0, 10)}) )
        text = text.translate( str.maketrans({"：":":"}) )
        
          #TL時間だったら
        if re.fullmatch(pettern, text):
            flg = False

        #TL前のコメント取得
        if flg:
            msg += args[i] + '\n'

        #TL時間とコメントを取得
        else:
            if re.fullmatch(pettern, text):
                creList.append(text)

                if index != 0:
                    creList[index - 1] += '\n'

                #creList[index] =  text   #時間
                index += 1

            else:
                creList[index - 1] += ' ' + text
        
    return (msg, creList)


#分:秒 の文字列を 整数型の秒数で返す
def get_second(min_str):

    #文字列を数値に変換、そこからtl_timeを引く
    target_time = []
    repatter = ':'
    target_time.append( re.split(repatter, str(min_str)) )
    
    #if( re.search(r'\W', target_time[0]) ):
    #    raise common.CommandError("TLと分:秒とキャラ名の間に半角スペースがありません\n")

    min = int(target_time[0][0]) #分
    sec = int(target_time[0][1]) #秒
    
    #入力された時間
    rt = min * 60 + sec
    return rt 

#リストを時間でまとめる
def sort_tl_list(tl_list):

    rt_list = []
    match_cnt = 0
    flg = True
    for index in range(0, len(tl_list)):
        
        if flg:

            rt_list.append([[],[]])
            rt_list[index][0] = tl_list[index + match_cnt][0] #時間を追加

             #メッセージがUBだったら
            if checkUB( tl_list[index + match_cnt][1].upper() ):
                rt_list[index][1] = '=====' + tl_list[index + match_cnt][1].rstrip() + '=====\n' #メッセージを追加
            else:
                rt_list[index][1] = tl_list[index + match_cnt][1] #メッセージを追加

            if (index + match_cnt + 1) >= len(tl_list):
                flg = False
                break

            #次のTLと時間が一致
            while( get_second(tl_list[index + match_cnt][0]) == get_second(tl_list[index + match_cnt + 1][0]) ):

                #次のメッセージがUBだったら
                if checkUB(tl_list[index + match_cnt + 1][1].upper() ):
                    rt_list[index][1] += tl_list[index + match_cnt + 1][0] + ' =====' + tl_list[index + match_cnt + 1][1].rstrip() + '=====\n'
                else:
                    #追加する空白数を調べる
                    blank = ' '
                    for j in range(0, len(tl_list[index + match_cnt][0])):
                        blank += ' '

                    rt_list[index][1] += blank + tl_list[index + match_cnt + 1][1]  #単語を追加
                match_cnt += 1

                if (index + match_cnt + 1) >= len(tl_list):
                    flg = False
                    break

    return rt_list

def checkUB(tl_string):
    flg = False
    state = -1
    
    #コメントのUB
    if re.compile('敵UB\S').search(tl_string):
        flg = False
    #TL最後のUB
    elif re.compile('敵UB').search(tl_string):
        flg = True
    #TLのUB
    elif re.compile('敵UB\s').search(tl_string):
        flg = True

    return flg

def createTlList(tl_list):
    msg = ''

    for i in range(0, len(tl_list)):
        msg += tl_list[i][0] + ' ' +tl_list[i][1]
    return msg
