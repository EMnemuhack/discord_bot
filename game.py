import discord
import random

import messages
import common

import re


async def omikuzi(message, data, command_args, mention_ids):
    try:
        if len(command_args) != 1:
            raise common.CommandError(messages.error_args)

        #確率乱数発生
        num = random.randint(1,100)
        # ちぇる吉 4%
        if num <= 4:
            choices = 0
        # 大吉 10%
        elif 4 < num <= 14:
            choices = 1
        # 中吉 25%
        elif 14 < num <= 39:
            choices = 2
        # 小吉 25%
        elif 39 < num <= 64:
            choices = 3
        # 凶 20%
        elif 64 < num <= 84:
            choices = 4
        # 大凶 15%
        elif 84 < num <= 99:
            choices = 5
        # りゅうちぇる 1%
        elif num == 100:
            num = random.randint(1,10)
            if num == 1:
                choices = 7
            else:
                choices = 6

        # 結果表示

        await common.reply_author(message,messages.omikuzi_message)
        await common.sleep_late(2.5)

        if (choices == 7):
            image = discord.File(common.CHELL_IMAGE_HIGECHELL)
        elif (choices == 6):
            image = discord.File(common.CHELL_IMAGE_RYUUCHELL)        
        elif (choices == 0):
            image = discord.File(common.CHELL_IMAGE_CHELLKITI)
       
        if 'image' in locals():     
            new_message = await message.channel.send(file=image)
            await new_message.delete(delay = common.REPLY_DISPLAY_TIME)

        await common.reply_author(message, messages.omikuzi_anser[choices])
        
        return (True,'')

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_omi_arg)        


async def dice(message, data, command_args, mention_ids):
    try:
        if not (len(command_args) in [1,2]) :
            raise common.CommandError(messages.error_args)

        if len(command_args) == 1:
            search_text = '1d6'
        else:
            search_text = command_args[1]

        pattern = '\d{1,2}d\d{1,3}|\d{1,2}D\d{1,3}'
        split_pattern = 'd|D'
        
        # パターンにマッチしているかの判定
        if judge_nDn(search_text, pattern):
            result,sum_dice,is1dice = role_nDn(search_text, split_pattern)
            if is1dice:
                response_string = '結果は～　**`' + str(sum_dice) + '`**　ですよ☆'
                
            else:
                response_string = '結果は～ ｼﾞｬﾗｼﾞｬﾗｼﾞｬﾗ　**`' + str(result) + '`** = **`' + str(sum_dice) + '`**　ですよ☆'

            return (True, response_string)    
        else:
            raise common.CommandError(messages.error_dice_arg)

    except common.CommandError as ce: 
        raise common.CommandError(ce.args[0] + '\n' + messages.cmd_dice_arg)        

# ダイスを振る
def role_nDn(src, split_pattern):
    result = []
    sum_dice = 0
    role_index = split_nDn(src, split_pattern)
    role_count = int(role_index[0])
    nDice = int(role_index[1])

    for i in range(role_count):
        tmp = random.randint(1,nDice)
        result.append(tmp)
        sum_dice = sum_dice + tmp

    is1dice = True if role_count == 1 else False

    return result,sum_dice,is1dice

# パターン判定
def judge_nDn(src, pattern):
    repatter = re.compile(pattern)
    result = repatter.fullmatch(src)
    if result is not None:
        return True
    else:
        return False

# 何面ダイスを何回振るか
def split_nDn(src, split_pattern):
    return re.split(split_pattern,src)

