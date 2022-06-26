# 組み込み
#import asyncio.windows_events
#from asyncio.windows_events import NULL

import asyncio
import os
import json
import re
import datetime

# 追加インストール
import discord

# bot関連
import messages
import common
import reserve
import fin
import la
import cancel
import ms
import manage
import view
import start                # コマンド 20210831 start 追加
import help                 # コマンド 20210907 help 追加
import game
import tl

# icon追加
import cancel_icon
import start_icon
import help_icon
import word

client = discord.Client()

BOT_TOKEN = os.getenv('BOT_TOKEN')

OK_HAND = '\N{OK HAND SIGN}'

async def shutdown(message , data, command_args, mention_ids):
    await message.add_reaction(OK_HAND)
    await client.logout()
    return (True,'')

# コマンド 20210831 start 追加
COMMAND_LIST = [
    (['.reserve', '.re', '.予約'], reserve.reserve, True),
    (['.finish', '.fin', '.完了'], fin.fin, True),
    (['.lastattack', '.la', '.討伐','.〆'], la.la, True),
    (['.cancel', '.cl', '.取消'], cancel.cancel, True),
    (['.modifystatus', '.ms', '.ステータス変更'], ms.ms, True),
    (['.start', '.st', '.開始'], start.start, True),
    (['.help', '.he', '.救援'], help.help, True),
    (['.word', './', '.名言'], word.word, True),
    (['.tl'], tl.time_line, True),
    (['.word_cl', './!', './cl','.名言削除'], word.remove, True),
    (['.omikuzi', '.omi', '.おみくじ'], game.omikuzi, True),
    (['.dice', '.さいころ', '.サイコロ'], game.dice, True),
    (['.add', '.追加'], manage.add, False),
    (['.remove', '.削除'], manage.remove, False),
    (['.allremove', '.バルス！'], manage.allremove, False),
    (['.modifyboss', '.mb', '.ボス変更'], manage.mb, False),
    (['.shutdown'], shutdown, False),
    (['.kickbot'], manage.kickbot, False)
    ]

# icon用コマンドを追加
ICON_COMMAND_LIST = [
    (['.cancel', '.cl_icon', '.取消'], cancel_icon.cancel, True),
    (['.start', '.st_icon', '.開始'], start_icon.start, True),
    (['.help', '.he_icon', '.救援'], help_icon.help, True)
    ]

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    return

# 発言時に実行されるイベントハンドラを定義
@client.event
async def on_message(message):    
    # .で始まらない場合はコマンドではないので無視する
    if not message.content.startswith('.') :
        return

    try:
        common.create_lock()
    except:
        await common.reply_author(message, messages.error_lock)
        return
    
    try:
        await command_main(message)
    finally:
        common.delete_lock()
    
    return

# 20211212  アイコンでのコマンド呼び出し対応 
@client.event
async def on_raw_reaction_add(payload):

    if payload.member.bot:
        return

    cha = client.get_channel(payload.channel_id)
    message = await cha.fetch_message(payload.message_id)

    # 他チャンネルでアイコンは押された時の対応
    data = dict()
    #サーバー設定ファイルの有無を検索 →　見つからなければチャンネル作成
    await recreate_channels_if_not_exist(data, message.guild)
    #サーバー情報読み出し
    data[common.DATA_SERVER_KEY] = common.load_server_settings()
    
    # コマンド入力チャンネルではない場合は無視する
    if not message.channel.id in [data[common.DATA_SERVER_KEY][common.SERVER_COMMAND_CHANNEL_KEY], data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY], data[common.DATA_SERVER_KEY][common.SERVER_RESERVATION_CHANNEL_KEY]]:
        return
    
    try:
        common.create_lock()
    except:
        await common.reply_author(message, messages.error_lock)
        return
    
    try:
        await icon_command_main(payload, payload.emoji, 0)

        # caccelのみアイコンを戻す
        #if payload.emoji.name == common.OK_CANCEL:
        await message.remove_reaction(payload.emoji.name, payload.member)
        
    finally:
        common.delete_lock()
    
    return

# 20211212  アイコンでのコマンド呼び出し対応 
"""@client.event
async def on_raw_reaction_remove(payload):

    if(payload.emoji.name == common.OK_CANCEL):
        return

    cha = client.get_channel(payload.channel_id)
    message = await cha.fetch_message(payload.message_id)

    try:
        common.create_lock()
    except:
        await common.reply_author(message, messages.error_lock)
        return
    
    try:
        await icon_command_main(payload, payload.emoji, 1)
         # アイコンを戻す
        #await message.remove_reaction(payload.emoji.name, payload.member)

    finally:
        common.delete_lock()
    
    return"""


#@client.event
#async def on_reaction_add(reaction, author):
#    if reaction.message.author.bot:
#        print("botのメッセージ？")
#        return

#    await reaction.message.channel.send("{0}によって「{1}」に「{2}」が押されました。".format(author, reaction.message.content, reaction.emoji))
#    return

# 20211212  アイコンでのコマンド呼び出し対応 


async def icon_command_main(payload, emoji, call):

    # dataを受け取る箱を作成
    data = dict()

    #サーバー情報読み出し
    data[common.DATA_SERVER_KEY] = common.load_server_settings()

    cha = client.get_channel(payload.channel_id)
    message = await cha.fetch_message(payload.message_id)
   
    # 凸開始の場合のエラー判定
    if not message.content.startswith('.') and message.channel.id != data[common.DATA_SERVER_KEY][common.SERVER_RESERVATION_CHANNEL_KEY]:
            return

    # 特定のアイコンじゃない場合
    if  not (emoji.name in [common.OK_START, common.OK_HELP, common.OK_CANCEL]):
        await common.reply_mension(message,payload.user_id, messages.error_icon_dif_icon)
        return

    #configをjson形式で読み出し
    data[common.DATA_CONFIG_KEY] = common.load_config()

    # メンバ情報を取得　ファイル読み込み　ファイル見つからなければメッセージ表示で終了
    try:
        data[common.DATA_MEMBER_KEY] = common.load_members()
    except FileNotFoundError:
        await common.reply_author(message, messages.error_icon_not_file)
        return

    # ボス情報を取得　ファイル見つからなければエラーメッセージ表示で終了
    try:
        data[common.DATA_BOSS_KEY] = common.load_boss()
    except FileNotFoundError:
       await common.reply_author(message, messages.error_icon_not_file)
       return

    try:
        data[common.DATA_DAILY_KEY] = common.load_daily()

        # 5時をまたいだ場合は初期化する　
        if datetime.date.fromisoformat(data[common.DATA_DAILY_KEY][common.DAILY_DATE_KEY]) < common.get_date(datetime.datetime.now()):
            await common.reply_author(message, messages.error_icon_dif_day)
            return

    except FileNotFoundError:
       await common.reply_author(message, messages.error_icon_not_file)
       return

    # コマンドの要素数が2以上だったら削除

    if  emoji.name == common.OK_START:
        command = '.st_icon'
        
    elif emoji.name == common.OK_HELP:
        command = '.he_icon'
    
    elif emoji.name == common.OK_CANCEL:
        command = '.cl_icon'

    try:
        flg = True
        for c in ICON_COMMAND_LIST :
            if command in c[0] :
                if (not c[2]) and (message.channel.id != data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]):
                    raise common.CommandError(messages.error_command_limited)

                ref = await c[1](payload, message , data, call)

                flg = False
                break

        if flg:
            await common.reply_mension(message, payload.user_id, messages.error_cmd_none)
            return

    except common.CommandError as ce : 
        await common.reply_mension(message, payload.user_id,ce.args[0])
        # アイコン戻す
        await message.remove_reaction(payload.emoji.name, payload.member)
        return
    
    if ref[0]:
        reservation_message = await fetch_reservation_message(data, message.guild)
        rest_detail_message = await fetch_rest_detail_message(data, message.guild)

    if ref[1] != '':
        #msgがある
        await common.reply_mension(message, payload.user_id,ref[1])

    await view.display_reservation(data, reservation_message)
    await view.display_rest_detail(data, rest_detail_message)

    # 正常終了のため　cansel押下した場合のみhelp と cancel icon戻す
    #if(payload.emoji.name == common.OK_CANCEL):
    #    await message.remove_reaction(common.OK_HELP, payload.member)
    #    await message.remove_reaction(common.OK_CANCEL, payload.member)

    return
# 20211212  アイコンでのコマンド呼び出し対応 ここまで

async def command_main(message):
    data = dict()
    #サーバー設定ファイルの有無を検索 →　見つからなければチャンネル作成
    await recreate_channels_if_not_exist(data, message.guild)
    #configをjson形式で読み出し
    data[common.DATA_CONFIG_KEY] = common.load_config()
    #サーバー情報読み出し
    data[common.DATA_SERVER_KEY] = common.load_server_settings()

    # コマンド入力チャンネルではない場合は無視する
    if not message.channel.id in [data[common.DATA_SERVER_KEY][common.SERVER_COMMAND_CHANNEL_KEY], data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]]:
        return

    # メンバ情報を取得　ファイル読み込み　ファイル見つからなければ空のファイル作成
    try:
        data[common.DATA_MEMBER_KEY] = common.load_members()
    except FileNotFoundError:
        await common.reply_author(message, messages.error_init_member)
        data[common.DATA_MEMBER_KEY] = []
        common.save_members(data[common.DATA_MEMBER_KEY])

    # ボス情報を取得　ファイル見つからなければconfigから再生成
    try:
        data[common.DATA_BOSS_KEY] = common.load_boss()
    except FileNotFoundError:
        common.init_boss(data)

    # 日次予約情報を取得
    try:
        data[common.DATA_DAILY_KEY] = common.load_daily()
        
        # 5時をまたいだ場合は初期化する　daily.txtの日付は5時を過ぎるか過ぎないかで当日/翌日の判断をしている
        if datetime.date.fromisoformat(data[common.DATA_DAILY_KEY][common.DAILY_DATE_KEY]) < common.get_date(datetime.datetime.now()):
            #20210827　ログ出力　 追加
            common.get_dont_three_attacks(data)
            #20210827 ここまで 
            common.init_daily(data)
            # 20210912 ロール処理追加 ここまで
            await common.reply_author(message, messages.msg_new_daily)

    except FileNotFoundError:
        common.init_daily(data)

   # メンションの全IDを取得    正規表現パターンをオブジェクトとして生成　→　検索　.addって入力したID？
    mention_re = re.compile('<@!\d+>')  
    mention_ids = [int(s[3: len(s)-1]) for s in mention_re.findall(message.content)]
    
    #可能であればロールでのメンション対応したいが　個人IDとロールIDは表示方法が違う　いろいろ面倒なので後回し　20210827
    if len(mention_ids) > 0 and (message.channel.id != data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]) and data[common.DATA_CONFIG_KEY][common.CONFIG_DEPUTY_LIMITED_KEY]:
        await common.reply_author(message, messages.error_mention_limited)
        return 

    #コマンドを取り出し　メンションの無いコマンドの場合はメッセージ全文取り出し
    mention_match = mention_re.search(message.content)
    if mention_match:
        command_str = message.content[:mention_match.start(0)]
    else :
        command_str = message.content

    # メンションを文字列から削除したのち、空白でコマンドを分割
    command_args = re.split('\s+', command_str.replace('　',' ').strip() )

    # コマンド部分は英字大文字を小文字に置き換える
    command_args[0] = str.lower(command_args[0])

     # IDが0個の場合はメッセージ送信者のIDを追加する
    if len(mention_ids)==0 :
        mention_ids.append(message.author.id)
   
    ref = (False,'')
    #入力されたコマンドが何のコマンドなのかをコマンドリストの上から読む
    try:
        flg = True
        for c in COMMAND_LIST :
            if command_args[0] in c[0] :
                if (not c[2]) and (message.channel.id != data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]):
                    raise common.CommandError(messages.error_command_limited)

                ref = await c[1](message, data, command_args, mention_ids)
                # reコマンドのみリアクションを複数追加
                if common.RESERVE_COMMAND in c[0]:
                    # リアクションを複数返す
                    for reaction in [OK_HAND, common.OK_START]:
                        await message.add_reaction(reaction)

                else :
                    await message.add_reaction(OK_HAND)

                flg = False
                break
        
        if flg:
            await common.reply_author(message, messages.error_cmd_none)
            return
        
    except common.CommandError as ce :
        await common.reply_author(message, ce.args[0])
        return
    
    # バルスコマンド処理
    if common.ALL_REMOVE_COMMAND in c[0]:
        #チャンネル削除して終了
        await delete_bot_channels(data, message.guild)
        return

    reservation_message = await fetch_reservation_message(data, message.guild)

    rest_detail_message = await fetch_rest_detail_message(data, message.guild)

    await set_help_message(data, message.guild)

    if ref[0]:
        await view.display_reservation(data, reservation_message)
        await view.display_rest_detail(data, rest_detail_message)

    if ref[1] != '':
        await common.reply_author(message, ref[1])

    # 20210912 ロール処理追加   ここで呼ぶかは要検討　毎回atk判定処理が走ってしまう
    await common.add_remove_role(data, message.guild, False)
    # 20210912 ロール処理追加 ここまで
    return

@client.event
async def on_guild_join(guild):
    data = dict()
    await create_bot_channels(data, guild) 
    return

#async def get_mention(message):
    # メンションの全IDを取得    正規表現パターンをオブジェクトとして生成　→　検索　.addって入力したID？
    mention_re = re.compile('<@!\d+>')  
    mention_ids = [int(s[3: len(s)-1]) for s in mention_re.findall(message.content)]

     #コマンドを取り出し　メンションの無いコマンドの場合はメッセージ全文取り出し
    mention_match = mention_re.search(message.content)
    
    # IDが0個の場合はメッセージ送信者のIDを追加する
    if len(mention_ids)==0 :
        mention_ids.append(message.author.id)



    return mention_ids, mention_match

# bot用のチャンネルを生成
async def create_bot_channels(data, guild):
    category_channel      = await guild.create_category_channel('ちぇるBOT')
    command_channel       = await guild.create_text_channel('コマンド入力',category = category_channel )
    admin_command_channel = await guild.create_text_channel('管理コマンド入力',category = category_channel )
    reservation_channel   = await guild.create_text_channel('予約状況表示',category = category_channel )
    rest_detail_channel   = await guild.create_text_channel('残凸状況表示',category = category_channel )
    help_channel          = await guild.create_text_channel('コマンドヘルプ',category = category_channel )

    server_setting = {
        common.SERVER_GUILD_ID_KEY : guild.id,
        common.SERVER_CATEGORY_CHANNEL_KEY : category_channel.id,
        common.SERVER_COMMAND_CHANNEL_KEY : command_channel.id,
        common.SERVER_ADMIN_COMMAND_CHANNEL_KEY : admin_command_channel.id,
        common.SERVER_RESERVATION_CHANNEL_KEY : reservation_channel.id,
        common.SERVER_REST_DETAIL_CHANNEL_KEY : rest_detail_channel.id,
        common.SERVER_HELP_CHANNEL_KEY : help_channel.id
    }

    data[common.DATA_SERVER_KEY] = server_setting
    #サーバー設定の書き込み
    common.save_server_settings(data[common.DATA_SERVER_KEY])

    return

# bot用チャンネル削除
async def delete_bot_channels(data, guild):
    category_channel      = client.get_channel(data[common.DATA_SERVER_KEY][common.SERVER_CATEGORY_CHANNEL_KEY])
    command_channel       = client.get_channel(data[common.DATA_SERVER_KEY][common.SERVER_COMMAND_CHANNEL_KEY])
    admin_command_channel = client.get_channel(data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY])
    reservation_channel   = client.get_channel(data[common.DATA_SERVER_KEY][common.SERVER_RESERVATION_CHANNEL_KEY])
    rest_detail_channel   = client.get_channel(data[common.DATA_SERVER_KEY][common.SERVER_REST_DETAIL_CHANNEL_KEY])
    help_channel          = client.get_channel(data[common.DATA_SERVER_KEY][common.SERVER_HELP_CHANNEL_KEY])

    # channel削除
    await command_channel.delete()
    await admin_command_channel.delete()
    await reservation_channel.delete()
    await rest_detail_channel.delete()
    await help_channel.delete()

    # カテゴリー削除
    await category_channel.delete()
    
    # serverファイル削除
    common.delete_file(common.DATA_SERVER_PATH)

    return

# 設定ファイルが無い場合は、チャンネルを新たに生成
async def recreate_channels_if_not_exist(data, guild):
    if(not os.path.exists(common.DATA_SERVER_PATH)) :
        await create_bot_channels(data, guild)

    return

# 予約表示用メッセージを取得
async def fetch_reservation_message(data, guild):
    server = data[common.DATA_SERVER_KEY]
    #予約状況表示チャンネルの情報GET
    channel = guild.get_channel(server[common.SERVER_RESERVATION_CHANNEL_KEY])

    #表示用チャンネルのメッセージID（どのメッセージを編集するかの情報）　がなかったら　よやく　メッセージを送信して　そこを編集用keyとする
    if (not common.SERVER_RESERVATION_MESSAGE_KEY in server):
        message = await channel.send('よやく')
        message_id = message.id
        server[common.SERVER_RESERVATION_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    message_id = server[common.SERVER_RESERVATION_MESSAGE_KEY]
    message = channel.get_partial_message(message_id)

    try:
        message = await message.fetch()
    except discord.NotFound:
        message = await channel.send('よやく')
        message_id = message.id
        server[common.SERVER_RESERVATION_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    return message

# 残凸表示用メッセージを取得
async def fetch_rest_detail_message(data, guild):
    server = data[common.DATA_SERVER_KEY]

    channel = guild.get_channel(server[common.SERVER_REST_DETAIL_CHANNEL_KEY])

    if (not common.SERVER_REST_DETAIL_MESSAGE_KEY in server):
        message = await channel.send('ざんとつ')
        message_id = message.id
        server[common.SERVER_REST_DETAIL_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    message_id = server[common.SERVER_REST_DETAIL_MESSAGE_KEY]
    message = channel.get_partial_message(message_id)

    try:
        message = await message.fetch()
    except discord.NotFound:
        message = await channel.send('ざんとつ')
        message_id = message.id
        server[common.SERVER_REST_DETAIL_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    return message

# ヘルプメッセージを取得
async def set_help_message(data, guild):
    server = data[common.DATA_SERVER_KEY]

    channel = guild.get_channel(server[common.SERVER_HELP_CHANNEL_KEY])
    # ヘルプメッセージIDをserver.txtに保持
    if (not common.SERVER_HELP_MESSAGE_KEY in server):
        message = await channel.send(common.load_help())
        message_id = message.id
        server[common.SERVER_HELP_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    message_id = server[common.SERVER_HELP_MESSAGE_KEY]
    message = channel.get_partial_message(message_id)

    try:
        message = await message.fetch()
    except discord.NotFound:
        message = await channel.send(common.load_help())
        message_id = message.id
        server[common.SERVER_HELP_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    return message

# Botの起動とDiscordサーバーへの接続
client.run(BOT_TOKEN)