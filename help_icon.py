import datetime

import messages
import common

async def help(payload, message, data, call):
    msg = ''

    try : 

        mention_ids = [payload.user_id]

    	# 対象となるIDの取得
        target_id = common.get_target_id(mention_ids)

        # bossIDの判定で1～5を超えていないかどうか　配列の添え字として使うため戻り値は引数-1を行う
        #boss_id = common.convert_boss_no()
        
        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        # boss情報取得
        boss = data[common.DATA_BOSS_KEY]

        # 既存の予約情報を取得
        daily = data[common.DATA_DAILY_KEY]

        target_key = str(target_id)

        if not target_key in daily[common.DAILY_MEMBER_KEY]:
            raise common.CommandError(messages.error_help_not_reserve)

        # メンションIDから情報取得
        member = daily[common.DAILY_MEMBER_KEY][target_key]
        
        # 予約情報取得
        res = member[common.DAILY_MEMBER_RESERVATION_KEY]
        res_len = len(res)-1

        # bossIDの取得 = .stがついている場所

        # 予約数分回す
        flg = True
        for i in range(len(res)):
            for j in range(len(res[i])):

                if call == 1:
                    if res[i][j][common.RESERVATION_STATUS_KEY] == common.RESERVE_STATUS_HELP:
                        # 戻す処理
                        res[i][j][common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_START
                        # メッセージ用
                        msg_atk_index =  i
                        msg_atk_branch = j
                        common.save_daily(daily)
                        msg = str(msg_atk_index +1) + messages.word_atk_index + messages.word_atk_branch[msg_atk_branch] + 'の凸救援をキャンセルしました'
                        return (True, msg)

                if res[i][j][common.RESERVATION_STATUS_KEY] == common.RESERVE_STATUS_START:
                    res[i][j][common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_HELP
                    msg_atk_index = i
                    msg_atk_branch = j
                    flg = False
                    break
            # 複数.stがあった場合一番早い凸に対応するため 追加   
            if not flg:
                break    
        
        if flg:
            raise common.CommandError(messages.error_icon_not_st)

        common.save_daily(daily)

        msg = str(msg_atk_index +1) + messages.word_atk_index + messages.word_atk_branch[msg_atk_branch] + messages.msg_help_success

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0])
    
    return (True,msg)




