import messages
import common

async def cancel(payload, message, data, call):
    msg = ''

    try : 
        # if len(command_args) != 3 :
        #     raise common.CommandError(messages.error_args)
        mention_ids = [payload.user_id]
        target_id = common.get_target_id(mention_ids)

        # lb = common.convert_boss_no_with_lap_no(command_args[1])

        # boss_id = lb[0]

        # lap_no = lb[1]

        # ca = common.convert_cancel_attack_no(command_args[2])

        # attack_index = ca[0]

        # cancel_flag = ca[1]
   
        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        daily = data[common.DATA_DAILY_KEY]

        target_key = str(target_id)
        if not target_key in daily[common.DAILY_MEMBER_KEY]:
            daily[common.DAILY_MEMBER_KEY][target_key] = common.create_daily_member()

        # メンションIDから情報取得
        member = daily[common.DAILY_MEMBER_KEY][target_key]
        
        # 予約情報取得
        res = member[common.DAILY_MEMBER_RESERVATION_KEY]

        # 予約数分回す
        flg = True
        for i in range(len(res)):
            for j in range(len(res[i])):
                if res[i][j][common.RESERVATION_STATUS_KEY] in [common.RESERVE_STATUS_START,common.RESERVE_STATUS_HELP] :
                    #予約を消す
                    res[i][j][common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_NONE
                    flg = False
                    break

        if flg:
            raise common.CommandError(messages.error_icon_not_sthe)

        common.save_daily(daily)

        msg = messages.msg_delete_success

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0])

    return (True,msg)
