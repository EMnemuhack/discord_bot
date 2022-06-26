import datetime

import re
import messages
import common

async def start(payload, message, data, call):
    msg = ''

    try :
        # 予約者とicon押下者が違う場合の判定
        if(payload.user_id != message.author.id):
                raise common.CommandError(messages.error_icon_dif_user)
                #await common.reply_mension(message,payload.user_id, "せんぱ～い　せんぱ…　あれ？　あなた誰ですか？")
        
        #　アイコンを押下したメッセージを抜き出す
        command_str = message.content
        command_args = re.split('\s+', command_str.replace('　',' ').strip() )

        attack_index = common.convert_damage_with_attack_no(command_args[2])
        
        if attack_index[1] != common.ATTACK_MAIN:
            target_branch = 1
        else:
            target_branch = 0

        #ID作成
        mention_re = re.compile('<@!\d+>')  
        mention_ids = [int(s[3: len(s)-1]) for s in mention_re.findall(message.content)]

        if len(mention_ids) == 0:
            mention_ids.append(message.author.id)


        # bossIDを取得
        boss_id = common.convert_boss_no(command_args[1])
        # mensionIDを取得
        target_id = common.get_target_id(mention_ids)

        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        # boss情報取得
        boss = data[common.DATA_BOSS_KEY]

        # 既存の予約情報を取得
        daily = data[common.DATA_DAILY_KEY]

        # IDをkeyとして取得
        target_key = str(target_id)

        # 予約情報があるかの判定
        if not target_key in daily[common.DAILY_MEMBER_KEY]:
            raise common.CommandError(messages.error_start_not_reserve)


        # メンションIDから情報取得
        member = daily[common.DAILY_MEMBER_KEY][target_key]
        
        # 予約情報取得
        res = member[common.DAILY_MEMBER_RESERVATION_KEY]
        res_len = len(res)-1

        
        for i in range(len(res)):
            for j in range(len(res[i])):

                if res[i][j][common.RESERVATION_STATUS_KEY] == common.RESERVE_STATUS_START :
                    
                    # 戻す処理
                    if call == 1:
                        res[i][j][common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_RESERVED
                        # メッセージ用
                        msg_atk_index =  i
                        msg_atk_branch = j
                        common.save_daily(daily)
                        msg = str(msg_atk_index +1) + messages.word_atk_index + messages.word_atk_branch[msg_atk_branch] + 'の凸開始をキャンセルしました'
                        return (True, msg)
                
                if res[i][j][common.RESERVATION_STATUS_KEY] in [common.RESERVE_STATUS_START, common.RESERVE_STATUS_HELP]:
                    raise common.CommandError(messages.error_icon_already)

        # 凸状況取得
        atk = member[common.DAILY_MEMBER_ATTACK_KEY]
        
        # コマンドで指定されたbossの現在の周状態を取得
        current_lap_no = data[common.DATA_BOSS_KEY][boss_id][common.BOSS_LAP_NO_KEY]
        current_lap_key = str(current_lap_no)

        # なぜ並べ替える？　現在の周のボス凸予約情報をソートする　dic　= 現在の凸予約情報
        dic = common.generate_reservation_dict(data)

        # 入力された周のboss情報を抜き出す → メンションID一致かつブランチ = 0(本凸予約)
        # 本凸予約があるかどうかをチェック
        flg = True
        if current_lap_key in dic:
            # 指定した凸情報を抜き出す dic lapley 週目　の　boss_idのボス情報
            rs = dic[current_lap_key][boss_id]

            for i in range(0, len(rs)):
                # 予約があった場合は予約情報を保存 ブランチ = 0以外 は持ち越し凸ということ
                if rs[i][common.RESERVATION_ID_KEY] == target_id :
                 
                    if rs[i][common.RESERVATION_BRANCH_KEY] == target_branch:
                        target_res = rs[i]
                        flg = False
                        break
        
        # 予約が無い場合エラー
        if flg:
           raise common.CommandError(messages.error_start_not_reserve)

        # 予約した凸順
        org_attack_index = target_res[common.RESERVATION_SEQ_KEY]
        #org_attack_index = target_attack_index
        
        # 持ち越しか本凸か
        org_branch_index = target_res[common.RESERVATION_BRANCH_KEY]                  

        # 予約情報のstatusを変更 ここは複数に対応させるため繰り返し処理と判定処理を入れる必要がある
        #if (res[org_attack_index][org_branch_index][common.RESERVATION_STATUS_KEY] == common.RESERVE_STATUS_START):
            #raise common.CommandError(messages.error_start_already)
        
        # 予約情報のstatus変更する
        res[org_attack_index][org_branch_index][common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_START

        # メッセージ用
        msg_atk_index =  org_attack_index
        msg_atk_branch = org_branch_index

        common.save_daily(daily)

        msg = str(msg_atk_index +1) + messages.word_atk_index + messages.word_atk_branch[msg_atk_branch] + messages.msg_start_success

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0])

    return (True,msg)




