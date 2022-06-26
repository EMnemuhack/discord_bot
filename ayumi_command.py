# 組み込み
#import asyncio.windows_events
#from asyncio.windows_events import NULL

import asyncio
import os
import json
import re
import datetime
import pytz

# 追加インストール
import discord

# bot関連
import messages
import common
import ms
import manage
import view

# icon追加
import cancel_icon
import help_icon
import fin_icon
import la_icon
import reserve_icon

client = discord.Client()

BOT_TOKEN = os.getenv('BOT_TOKEN')

OK_HAND = '\N{OK HAND SIGN}'

async def shutdown(message , data, command_args, mention_ids):
    await message.add_reaction(OK_HAND)
    await client.logout()
    return (True,'')

# メインコマンド
ICON_COMMAND_LIST = [
    ('.re_icon', reserve_icon.reserve, True),
    ('.cl_icon', cancel_icon.cancel, True),
    ('.he_icon', help_icon.help, True),
    ('.fin_icon', fin_icon.fin, True),
    ('.la_icon', la_icon.la, True),
    ('.add_icon', manage.add_icon, True),
    ('.remove_icon', manage.remove_icon, True)
    ]

# 管理コマンド用
COMMAND_LIST = [
    (['.modifystatus', '.ms', '.ステータス変更'], ms.ms, False),
    (['.add', '.追加'], manage.add, False),
    (['.shutdown'], shutdown, False),
    (['.import', '.im', '.取込'], manage.im, False),
    (['.remove', '.削除'], manage.remove, False),
    (['.kickbot'], manage.kickbot, False)
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
    # 管理コマンドと　チャンネルを最初に作るときに試用する
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
    if not message.channel.id in [data[common.DATA_SERVER_KEY][common.SERVER_RESULT_CHANNEL_KEY], data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY], data[common.DATA_SERVER_KEY][common.SERVER_RESERVATION_CHANNEL_KEY], data[common.DATA_SERVER_KEY][common.SERVER_REST_DETAIL_CHANNEL_KEY]]:
        return
    
    try:
        common.create_lock()
    except:
        await common.reply_author(message, messages.error_lock)
        return
    
    try:
        await icon_command_main(payload, message, payload.emoji)

        # caccelのみアイコンを戻す
        #if payload.emoji.name == common.OK_CANCEL:
        await message.remove_reaction(payload.emoji.name, payload.member)
        
    finally:
        common.delete_lock()
    
    return

# =====================================コマンド入力用メイン=====================================
async def icon_command_main(payload, message, emoji):

    # dataを受け取る箱を作成
    data = dict()

    #サーバー情報読み出し
    data[common.DATA_SERVER_KEY] = common.load_server_settings()

    #configをjson形式で読み出し　ボスの名前だけの情報
    data[common.DATA_CONFIG_KEY] = common.load_config()

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
        if datetime.date.fromisoformat(data[common.DATA_DAILY_KEY][common.DAILY_DATE_KEY]) < common.get_date(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))):
            #20210827　ログ出力　 追加
            #common.get_dont_three_attacks(data)
            #20210827 ここまで 
            common.init_daily(data)
            # 20210912 ロール処理追加 ここまで
            await common.reply_author(message, messages.msg_new_daily)
    except FileNotFoundError:
        common.init_daily(data)

    # アイコンの判定処理
    command = common.icon_celecter(emoji.name)

    # 編集用埋め込みメッセージオブジェクト送信
    embed_message = await fetch_reservation_embed(data, message.guild)
    #アイコン用メッセージとアイコンを送信
    await fetch_reservation_message(data, message.guild)
    await fetch_fin_message(data, message.guild)
    #編集用凸管理状況のメッセージ送信
    rest_detail_message = await fetch_rest_detail_message(data, message.guild)
    
    ref = (False,'')
    # モジュールの呼び出し
    try:
        flg = True
        for c in ICON_COMMAND_LIST :
            if command in c[0] :
                ref = await c[1](payload, message , data)
                flg = False
                break

        if flg:
            await common.reply_mension(message, payload.user_id, messages.error_icon_cmd_none)
            return
    except common.CommandError as ce : 
        await common.reply_mension(message, payload.user_id,ce.args[0])
        await message.remove_reaction(payload.emoji.name, payload.member)
        return

    if ref[0]:
        await view.display_reservation(data, embed_message)
        await view.display_rest_detail(data, rest_detail_message)

    if ref[1] != '':
        await common.reply_author(message, ref[1])

    return
# =====================================コマンド入力用メイン=====================================

@client.event
async def on_guild_join(guild):
    data = dict()
    await create_bot_channels(data, guild) 
    return

# =====================================テキスト入力用メイン=====================================
async def command_main(message):
    data = dict()
    #サーバー設定ファイルの有無を検索 →　見つからなければチャンネル作成
    await recreate_channels_if_not_exist(data, message.guild)
    #configをjson形式で読み出し
    data[common.DATA_CONFIG_KEY] = common.load_config()
    #サーバー情報読み出し
    data[common.DATA_SERVER_KEY] = common.load_server_settings()

    # コマンド入力チャンネルではない場合は無視する
    if not message.channel.id == data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]:
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
        if datetime.date.fromisoformat(data[common.DATA_DAILY_KEY][common.DAILY_DATE_KEY]) < common.get_date(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))):
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
   

    # 編集用埋め込みメッセージオブジェクト送信
    embed_message = await fetch_reservation_embed(data, message.guild)
    # アイコン用メッセージとアイコンを送信
    await fetch_reservation_message(data, message.guild)
    await fetch_fin_message(data, message.guild)
    # 編集用凸管理状況のメッセージ送信
    rest_detail_message = await fetch_rest_detail_message(data, message.guild)

    ref = (False,'')
    # 入力されたコマンドが何のコマンドなのかをコマンドリストの上から読む
    try:
        flg = True
        for c in COMMAND_LIST :
            if command_args[0] in c[0] :
                if (not c[2]) and (message.channel.id != data[common.DATA_SERVER_KEY][common.SERVER_ADMIN_COMMAND_CHANNEL_KEY]):
                    raise common.CommandError(messages.error_command_limited)

                ref = await c[1](message, data, command_args, mention_ids)
                await message.add_reaction(OK_HAND)
                flg = False
                break
        
        if flg:
            await common.reply_author(message, messages.error_cmd_none)
            return
        
    except common.CommandError as ce :
        await common.reply_author(message, ce.args[0])
        return

    if ref[0]:
        await view.display_rest_detail(data, rest_detail_message)

    if ref[1] != '':
        await common.reply_author(message, ref[1])

    # 20210912 ロール処理追加   ここで呼ぶかは要検討　毎回atk判定処理が走ってしまう
    #await common.add_remove_role(data, message.guild, False)
    # 20210912 ロール処理追加 ここまで
    return
# =====================================テキスト入力用メイン=====================================


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
    category_channel      = await guild.create_category_channel('あゆみBOT')
    reservation_channel   = await guild.create_text_channel('凸宣言',category = category_channel )
    result_channel        = await guild.create_text_channel('凸報告',category = category_channel )
    rest_detail_channel   = await guild.create_text_channel('残凸状況表示',category = category_channel )
    admin_command_channel = await guild.create_text_channel('管理コマンド入力',category = category_channel )

    server_setting = {
        common.SERVER_GUILD_ID_KEY : guild.id,
        common.SERVER_CATEGORY_CHANNEL_KEY : category_channel.id,
        common.SERVER_RESERVATION_CHANNEL_KEY : reservation_channel.id,
        common.SERVER_RESULT_CHANNEL_KEY : result_channel.id,
        common.SERVER_REST_DETAIL_CHANNEL_KEY : rest_detail_channel.id,
        common.SERVER_ADMIN_COMMAND_CHANNEL_KEY : admin_command_channel.id
    }

    data[common.DATA_SERVER_KEY] = server_setting
    #サーバー設定の書き込み
    common.save_server_settings(data[common.DATA_SERVER_KEY])

    return

# 設定ファイルが無い場合は、チャンネルを新たに生成
async def recreate_channels_if_not_exist(data, guild):
    if(not os.path.exists(common.DATA_SERVER_PATH)) :
        await create_bot_channels(data, guild)

    return

# 埋め込み表示用メッセージを取得
async def fetch_reservation_embed(data, guild):
    server = data[common.DATA_SERVER_KEY]
    #予約状況表示チャンネルの情報GET
    channel = guild.get_channel(server[common.SERVER_RESERVATION_CHANNEL_KEY])
    #　編集用embedを作成し　IDを保持
    if (not common.SERVER_RESERVATION_MESSAGE_KEY in server):
        embed = discord.Embed(title="予約",description="ここには予約が表示されます")
        message = await channel.send(embed=embed)
        for reaction in [common.OK_HELP, common.OK_CANCEL]:
            await message.add_reaction(reaction)

        message_id = message.id
        server[common.SERVER_RESERVATION_MESSAGE_KEY] = message_id
        common.save_server_settings(server)
    message_id = server[common.SERVER_RESERVATION_MESSAGE_KEY]
    
    # embedを取得
    try:
        embed_message = await channel.fetch_message(message_id)
    except discord.NotFound:
        embed = discord.Embed(title="予約",description="ここには予約が表示されます")
        message = await channel.send(embed=embed)
        for reaction in [common.OK_HELP, common.OK_CANCEL]:
            await message.add_reaction(reaction)
        message_id = message.id
        server[common.SERVER_RESERVATION_MESSAGE_KEY] = message_id
        common.save_server_settings(server)
        # 埋め込みを持ってるmessageオブジェクトを返す
        embed_message = await channel.fetch_message(message_id)

    return embed_message

# アイコン用メッセージを取得 
async def fetch_reservation_message(data, guild):

    server = data[common.DATA_SERVER_KEY]
    #予約状況表示チャンネルの情報GET
    channel = guild.get_channel(server[common.SERVER_RESERVATION_CHANNEL_KEY])

    #表示用チャンネルのメッセージID（どのメッセージを編集するかの情報）　がなかったら　よやく　メッセージを送信して　そこを編集用keyとする
    if (not common.SERVER_ATTACK_MESSAGE_KEY in server):
        message = await channel.send('**本凸**')
        for reaction in [common.ONE, common.TWO, common.THREE, common.FOUR, common.FIVE]:
            await message.add_reaction(reaction)

        message_id = message.id
        server[common.SERVER_ATTACK_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    #表示用チャンネルのメッセージID（どのメッセージを編集するかの情報）　がなかったら　よやく　メッセージを送信して　そこを編集用keyとする
    if (not common.SERVER_CARRYOVER_ATTACK_MESSAGE_KEY in server):
        message = await channel.send('**持ち越し凸**')
        for reaction in [common.ONE, common.TWO, common.THREE, common.FOUR, common.FIVE]:
            await message.add_reaction(reaction)

        message_id = message.id
        server[common.SERVER_CARRYOVER_ATTACK_MESSAGE_KEY] = message_id
        common.save_server_settings(server)
    
    #ここから下のメッセージがきちんと取得できたかどうかは省略してもいいかも
    message_id = server[common.SERVER_ATTACK_MESSAGE_KEY]
    message1 = channel.get_partial_message(message_id)

    message_id = server[common.SERVER_CARRYOVER_ATTACK_MESSAGE_KEY]
    message2 = channel.get_partial_message(message_id)


    # 作成されているメッセージを取得できなかったら　再度作成する メッセージが削除されていた場合の処理
    try:
        message = await message1.fetch()
    except discord.NotFound:
        message = await channel.send('**本凸**')
        for reaction in [common.ONE, common.TWO, common.THREE, common.FOUR, common.FIVE]:
            await message.add_reaction(reaction)
        message_id = message.id
        server[common.SERVER_ATTACK_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    try:
        message = await message2.fetch()
    except discord.NotFound:
        message = await channel.send('**持ち越し凸**')
        for reaction in [common.ONE, common.TWO, common.THREE, common.FOUR, common.FIVE]:
            await message.add_reaction(reaction)
        message_id = message.id
        server[common.SERVER_CARRYOVER_ATTACK_MESSAGE_KEY] = message_id
        common.save_server_settings(server)
        
    return 

# 凸完了用アイコン送信
async def fetch_fin_message(data, guild):
    # Embedを定義する
    """embed = discord.Embed(
                          title = "凸報告",# タイトル
                          color = 0x00ff00,
                          description = '**凸完了**'+ common.OK_FIN +' \n **ボス討伐** '+ common.OK_LA
                         )"""
    server = data[common.DATA_SERVER_KEY]
    channel = guild.get_channel(server[common.SERVER_RESULT_CHANNEL_KEY])

    if (not common.SERVER_RESULT_MESSAGE_KEY in server):
        message = await channel.send('**凸完了**'+ common.OK_FIN +' \n **ボス討伐** '+ common.OK_LA)
        for reaction in [common.OK_FIN, common.OK_LA]:
            await message.add_reaction(reaction)
        message_id = message.id
        server[common.SERVER_RESULT_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    message_id = server[common.SERVER_RESULT_MESSAGE_KEY]
    message = channel.get_partial_message(message_id)

    try:
        message = await message.fetch()
    except discord.NotFound:
        message = await channel.send('**凸完了**'+ common.OK_FIN +' \n **ボス討伐** '+ common.OK_LA)
        for reaction in [common.OK_FIN, common.OK_LA]:
            await message.add_reaction(reaction)
        message_id = message.id
        server[common.SERVER_RESULT_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    return message

# 残凸表示用メッセージを取得
async def fetch_rest_detail_message(data, guild):
    server = data[common.DATA_SERVER_KEY]

    channel = guild.get_channel(server[common.SERVER_REST_DETAIL_CHANNEL_KEY])

    if (not common.SERVER_REST_DETAIL_MESSAGE_KEY in server):
        message = await channel.send('ざんとつ')
        for reaction in [common.OK_ADD, common.OK_X]:
            await message.add_reaction(reaction)
        message_id = message.id
        server[common.SERVER_REST_DETAIL_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    message_id = server[common.SERVER_REST_DETAIL_MESSAGE_KEY]
    message = channel.get_partial_message(message_id)

    try:
        message = await message.fetch()
    except discord.NotFound:
        message = await channel.send('ざんとつ')
        for reaction in [common.OK_ADD, common.OK_X]:
            await message.add_reaction(reaction)
        message_id = message.id
        server[common.SERVER_REST_DETAIL_MESSAGE_KEY] = message_id
        common.save_server_settings(server)

    return message

"""# ヘルプメッセージを取得
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

    return message"""

# Botの起動とDiscordサーバーへの接続
client.run(BOT_TOKEN)