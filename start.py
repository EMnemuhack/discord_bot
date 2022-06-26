import datetime

import messages
import common

async def start(message, data, command_args, mention_ids):
    msg = ''

    try : 
        # 引数チェック
        if not (len(command_args) in [2,3]) :
            raise common.CommandError(messages.error_args)

    	# 対象となるIDの取得
        target_id = common.get_target_id(mention_ids)
        # bossIDの判定で1～5を超えていないかどうか　配列の添え字として使うため戻り値は引数-1を行う
        boss_id = common.convert_boss_no(command_args[1])
        
        if len(command_args) == 3:
            # 持ち越し時の凸番号
            attack_index = common.convert_attack_type_with_attack_no(command_args[2])
        else:
            # 通常凸周指定無しの場合
            attack_index = (common.ATTACK_MAIN,common.NO_ATTACK_NUMBER)
        
        # クラメンとして登録済みかをチェック
        common.check_registered_member(data, target_id)

        # boss情報取得
        boss = data[common.DATA_BOSS_KEY]

        # 既存の予約情報を取得
        daily = data[common.DATA_DAILY_KEY]

        target_key = str(target_id)

        if not target_key in daily[common.DAILY_MEMBER_KEY]:
            raise common.CommandError(messages.error_start_not_reserve)

        # メンションIDから情報取得
        member = daily[common.DAILY_MEMBER_KEY][target_key]
        
        # 予約情報取得
        res = member[common.DAILY_MEMBER_RESERVATION_KEY]
        res_len = len(res)-1
        # 凸状況取得
        atk = member[common.DAILY_MEMBER_ATTACK_KEY]
        # コマンドで指定されたbossの現在の周状態を取得
        current_lap_no = data[common.DATA_BOSS_KEY][boss_id][common.BOSS_LAP_NO_KEY]
        current_lap_key = str(current_lap_no)

        # なぜ並べ替える？　現在の周のボス凸予約情報をソートする　dic　= 現在の凸予約情報
        dic = common.generate_reservation_dict(data)

        # コマンドから本凸か持越しかを判定
        if attack_index[0] == common.ATTACK_MAIN:
            # 凸を指定しない本凸の場合
            if attack_index[1] == common.NO_ATTACK_NUMBER:
                # 消費対象の凸を判定 消費対象の凸がない場合はエラー
                for i in range(0, common.ATTACK_MAX + 1):
                    # 3凸の中に0が無かったらエラー  # 予約情報が検索範囲を超えないかの判定
                    if i == common.ATTACK_MAX or res_len < i:
                        raise common.CommandError(messages.error_start_main_full)
                    # 未凸の凸情報を取得
                    if atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] == common.DAILY_ATTACK_STATUS_NONE: 
                        if res[i][0][common.RESERVATION_STATUS_KEY] != common.RESERVE_STATUS_START :
                            target_attack_index = i
                            break
            
            # 凸指定本凸の場合 該当のステータスが未凸でない場合はエラー
            else:
                if atk[attack_index[1]][common.DAILY_MEMBER_ATTACK_STATUS_KEY] != common.DAILY_ATTACK_STATUS_NONE:
                    raise common.CommandError(messages.error_start_main_full)
                
                target_attack_index = attack_index[1]

            # 入力された周のboss情報を抜き出す → メンションID一致かつブランチ = 0(本凸予約)
            # 本凸予約があるかどうかをチェック
            flg = True

            if current_lap_key in dic:
                # 指定した凸情報を抜き出す dic lapley 週目　の　boss_idのボス情報
                rs = dic[current_lap_key][boss_id]

                for i in range(0, len(rs)):
                    # 予約があった場合は予約情報を保存 ブランチ = 0以外 は持ち越し凸ということ
                    if rs[i][common.RESERVATION_ID_KEY] == target_id and rs[i][common.RESERVATION_BRANCH_KEY] == 0 and rs[i][common.RESERVATION_STATUS_KEY] != common.RESERVE_STATUS_START:
                        target_res = rs[i]
                        flg = False
                        break
            
            # 本凸予約が無い場合エラー
            if flg:
               raise common.CommandError(messages.error_start_impossible)


        # 持ち越しの場合  
        else:
            # 凸を指定しない持越しの場合
            if attack_index[1] == common.NO_ATTACK_NUMBER:
                # 対象の凸を判定 消費対象の凸がない場合はエラー
                #raise common.CommandError(messages.error_start_not_attack)
                for i in range(0, common.ATTACK_MAX + 1):
                    if i == common.ATTACK_MAX or res_len < i:
                        raise common.CommandError(messages.error_start_carry_full)

                    if atk[i][common.DAILY_MEMBER_ATTACK_STATUS_KEY] == common.DAILY_ATTACK_STATUS_CARRY_OVER :
                        if res[i][1][common.RESERVATION_STATUS_KEY] != common.RESERVE_STATUS_START :
                            target_attack_index = i
                            break

            # 凸指定持ち越しの場合 該当のステータスが持越しでない場合はエラー
            else:
                if atk[attack_index[1]][common.DAILY_MEMBER_ATTACK_STATUS_KEY] != common.DAILY_ATTACK_STATUS_CARRY_OVER:
                    raise common.CommandError(messages.error_start_carry_full)
                
                target_attack_index = attack_index[1]

            # 持越予約があるかどうかをチェック
            flg = True

            if current_lap_key in dic:
                #現在の周のボスを抜き出し
                rs = dic[current_lap_key][boss_id]

                for i in range(0, len(rs)):
                    # 予約があった場合は予約情報を保存
                    if rs[i][common.RESERVATION_ID_KEY] == target_id and rs[i][common.RESERVATION_BRANCH_KEY] == 1 and rs[i][common.RESERVATION_STATUS_KEY] != common.RESERVE_STATUS_START:
                        target_res = rs[i]
                        flg = False
                        break

            # 予約なし
            if flg:
                raise common.CommandError(messages.error_start_impossible)


        # 予約した凸順
        #org_attack_index = target_res[common.RESERVATION_SEQ_KEY]
        org_attack_index = target_attack_index
        
        # 持ち越しか本凸か
        org_branch_index = target_res[common.RESERVATION_BRANCH_KEY]                  

        # 予約情報のstatusを変更 ここは複数に対応させるため繰り返し処理と判定処理を入れる必要がある
        if (res[org_attack_index][org_branch_index][common.RESERVATION_STATUS_KEY] == common.RESERVE_STATUS_START):
            raise common.CommandError(messages.error_start_already)
        
        # 予約情報のstatus変更する
        res[org_attack_index][org_branch_index][common.RESERVATION_STATUS_KEY] = common.RESERVE_STATUS_START
        
        # 凸状態変更はいったん保留
        # atk[org_attack_index][common.DAILY_MEMBER_ATTACK_STATUS_KEY]  = common.DAILY_ATTACK_STATUS_START

        # メッセージ用
        msg_atk_index =  org_attack_index
        msg_atk_branch = org_branch_index

        common.save_daily(daily)

        msg = str(msg_atk_index +1) + messages.word_atk_index + messages.word_atk_branch[msg_atk_branch] + messages.msg_start_success

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_st_arg)

    return (True,msg)




