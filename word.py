import datetime
import discord
import random

import messages
import common
import re

async def word(message, data, command_args, mention_ids):
    msg = ''
    # メンションでの予約ではなくて単語での予約とする
    # 改行やスペースにも対応するため　./ 登録コマンド #単語 　としてコマンドを呼び出す形式とする
    # 呼び出すコマンドにはダブルコーテーションをつけてもらう
    # 
    words = dict()
    # 単語情報取り出し
    try:
        words = common.load_word()

    # 取り出せなければ新規作成
    except FileNotFoundError:
        words = []
        common.save_word(words)

    try : 
        # 引数チェック 呼び出しキーワードがなかったら
        if  (len(command_args) in [1]) :
            raise common.CommandError(messages.error_args)
        
        #単語の抽出
        repatter = r'\"(.*)'
        r = re.findall(repatter, message.content, flags=re.DOTALL)
        target_str = ''
        if not (len(r) in [0]):
            target_str = r[0]


        # 対象となる呼び出しキーワードの取得
        target_keyword = command_args[1]

        flg = True
        # キーワードが既に登録済みかを検索
        for i in range(len(words)):
            if target_keyword == words[i][common.MEMBER_NAME_KEY]:
                target_index = i
                flg = False
                break

        # 単語登録
        if not (len(command_args) in [2]):
            # 新たに単語を登録
            if target_str == '':
                raise common.CommandError(messages.error_word_nothing)

            if flg:
                # 配列の作成
                word_array = []
                word_array.append(target_str)

                # 単語を新規に登録
                e = dict()
                e[common.WORD_NAME_KEY] = target_keyword
                e[common.WORD_WORD_KEY] = word_array
                words.append(e)
            
            #既存の登録者の更新
            else:
                # 配列を取得
                word_array = words[target_index][common.WORD_WORD_KEY]
                if len(word_array) >= common.MAX_WORD:
                    raise common.CommandError(messages.error_word_over)

                word_array.append(target_str)

                # 単語を更新
                words[target_index][common.WORD_WORD_KEY] = word_array

            common.save_word(words)
            msg = messages.msg_word_success
       
        # 単語呼び出し
        else:
            # 登録キーワードを全て表示する
            if target_keyword in ['all', 'ALL']:
                msg += '\n登録されているキーワード一覧\n'
                cnt = 1
                for jsonkey in words:
                    msg += str(cnt) +': '+ jsonkey[common.WORD_NAME_KEY] + '\n'
                    cnt += 1
            else:
                if flg:
                    raise common.CommandError(messages.error_word_keyword_nothing)
                else:
                    # 配列を取得
                    word_array = words[target_index][common.WORD_WORD_KEY]
                if len(word_array) in [0]:
                    raise common.CommandError(messages.error_word_word_nothing)
                # 配列からランダムに要素を取り出す
                msg = '\n'+ random.choice(word_array) + '\n by ' + target_keyword

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_word_arg)

    return (True,msg)



async def remove(message, data, command_args, mention_ids):

    # 単語削除コマンドの呼び出しは ./cl キーワード 何番目の単語か(0だったら単語を全て表示する)
    msg = ''

    words = dict()
    # 単語情報取り出し
    try:
        words = common.load_word()
    # 取り出せなければエラー
    except FileNotFoundError:
        raise common.CommandError(messages.error_delword_not_load)

    try: 
         # 引数チェック
        if not (len(command_args) in [2,3]) :
            raise common.CommandError(messages.error_args)

        if len(command_args) == 3:
            target_word_index = int(command_args[2])
            if not ((target_word_index >= -1) and (target_word_index <= 5)):
                raise common.CommandError(messages.error_delword_not_number)
        else:
            target_word_index = 0

        # キーワードを取得
        target_keyword = command_args[1]
        flg = True

        # キーワードが既に登録済みかを検索
        for i in range(len(words)):
            if target_keyword == words[i][common.MEMBER_NAME_KEY]:
                target_index = i
                flg = False
                break

        if flg:
            raise common.CommandError(messages.error_word_keyword_nothing)
       
        #登録されている単語を表示する
        if target_word_index == 0 :
            array = words[target_index][common.WORD_WORD_KEY]

            if len(array) != 0:
                msg = target_keyword + "に登録されている単語は\n"
                cnt = 1

                for s in array:
                    msg += str(cnt) + ' : ' + s + '\n'
                    cnt += 1
            else:
                msg = target_keyword + "に登録されている単語はありませんよ"


        #登録されている単語の削除
        else:
            if target_word_index == -1:
                #登録されているキーワードを削除
                #array = []
                #words[target_index][common.WORD_WORD_KEY] = array
                #words[target_index] = array
                del words[target_index]
                msg = 'キーワード: ' + target_keyword + ' を削除しましたよ'

            else:
                # 指定した単語のみを削除
                array = words[target_index][common.WORD_WORD_KEY]

                #if len(array) < target_word_index:
                    #raise common.CommandError('登録されている単語を超えた番号が指定されています')
                del_word = array[target_word_index -1]
                del array[target_word_index -1]
                words[target_index][common.WORD_WORD_KEY] = array
                msg = '単語: ' + del_word + ' を削除しましたよ'

            common.save_word(words)
            
        

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_delword_arg)

    return (True,msg)




