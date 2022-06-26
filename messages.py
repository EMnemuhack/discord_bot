# 単語
word_atk_branch = ['本凸','持越']
word_atk_index = '凸目'
word_atk_status = ['未凸','持越','凸済']
word_atk_status_mark = ['\N{LARGE BLUE CIRCLE}','\N{LARGE GREEN CIRCLE}','\N{LARGE ORANGE CIRCLE}','\N{LARGE RED CIRCLE}'] #赤サークル追加
word_name_unknown = '(不明)'
word_three_attack =['未完了','3凸済み']

# お知らせ文言
msg_new_daily = 'ちぇるーん朝ですよ先輩！'
msg_reserve_success = 'として予約しました！いや～出来る後輩！'
msg_fin_success = 'として完了登録しときましたよ☆　え、もう凸終わっちゃったんです？'
msg_la_success = ' として討伐登録しときましたよ☆　あれ？先輩もう倒しちゃったんです？'
msg_ms_success = 'に変更しましたよ？（イニシャライズ！！）'
msg_start_success = 'に凸っちゃって下さい！'
msg_help_success = 'に救援を依頼しました！は？何度目です？' 
msg_shutdown_success = 'ちぇるちぇぽぱっぴ？'
msg_notice_boss_change = 'ちぇるーん'
msg_delete_success = '予約を削除しときましたよ'
msg_word_success = '単語登録しときましたよ☆ キーワード忘れないでくださいね'

# エラー文言
error_not_admin = '残念でした～、滅びの呪文は実行できませんよ☆'
error_lock = '休憩時間でーす☆もう一度入力してね♪'
error_role_get = 'ロールの取得に失敗しましたよ'
error_args = '先輩！正しい引数を入力されてないですよ？'
error_boss_no = 'ボス番号は1~5を入力してっていったじゃないですか！'
error_lap_no = '周の指定は1~180を入力ですよ☆'
error_attack_no = '「何凸目か」は1~3をちぇるして下さい！'
error_carry_attack_no = '「m何凸目か」はm1~m3をちぇるして下さい！'
error_damage = 'ダメージは数値0～99999をちぇるして下さい！'
error_carry_over = '持ち越し秒数は21~90の範囲でちぇるしてください'
error_cmd_none = '正しいコマンドをちぇるしてください'
error_multi_mention = '複数のメンション付けられてます'
error_init_member = '初回起動もしくは設定読込の失敗のため、クラメン情報が初期化されましたよ'
error_not_member = 'クラメンとして登録されてないメンバですよ'
error_status = 'ステータスは000～222の中から選んでください 0:未凸 1:持越 2:凸済'
error_mention_limited = '代行入力は管理コマンド入力チャンネルからのみ入力可能'
error_command_limited = '管理コマンド入力チャンネルから実行！'

error_boss_no_with_lap_no = 'ボス番号は ボス番号(1～5) もしくは ボス番号+ もしくは ボス番号@周(1～180) で指定しちゃってください'
error_damage_with_attack_no = 'ダメージは ダメージ もしくは ダメージm もしくは ダメージm1～3 で指定しちゃってください'
error_carry_over_with_attack_no = '持ち越しは 持ち越し秒数 もしくは m もしくは m1～3 で指定しちゃってください'
error_cancel_attack_no = '対象は 1～3 もしくは m1～3 で指定しちゃってください'
error_lap_no_with_status = '周番号は 周番号(1～180) もしくは 周番号+ で指定しちゃってください'

error_reserve_limit_lap_no = '予約可能な範囲を超えてます'
error_reserve_full = 'これ以上予約できませんよ'
error_reserve_done = '該当の凸はすでに終わってますよ'
error_reserve_impossible = '該当の持越し凸の予約はできませんよ'
error_reserve_defeated = '既に討伐されてます'

# 20210831 start追加開始
error_start_impossible = 'すでに凸開始済み、または凸予約が見つかりませんよ'
error_start_not_reserve = '凸予約がありませんよ'
error_start_main_full = '凸開始できる本凸予約がありませんよ'
error_start_carry_full = '凸開始できる持ち越し予約がありませんよ'
error_start_already = 'すでに凸開始済みです'
# 20210831 start追加終了

# 20210907 help追加開始
error_help_impossible = 'すでに救援希望に設定済み、または凸予約が見つかりませんよ'
error_help_not_reserve = '凸予約がありませんよ'
error_help_main_full= '救援希望できる本凸予約がありませんよ'
error_help_carry_full = '救援希望できる持ち越し予約がありませんよ'
error_help_already = 'すでに救援希望済みです'
# 20210907 help追加終了

error_fin_defeated = '既に討伐されてます'
error_fin_full = 'これ以上凸できしませんよ'
error_fin_damage_over = '実績ダメージが残りHP以上となってます　討伐登録をする場合は討伐コマンドで登録！登録！！'
error_fin_impossible = '該当の持越し凸の登録はできませんよ'

error_la_defeated = '既に討伐されてます'
error_la_full = 'これ以上凸できませんよ'
error_la_impossible = '該当の持越し凸の登録はできませんよ'

error_add_impossible = 'これ以上クラメンの追加はできませんよ'

# 20211215　アイコン押下対応
error_icon_not_file = '緊急事態！緊急事態！TTRに連絡してください！！'
error_icon_dif_icon = '先輩そこじゃ無いですよ！'
error_icon_dif_user = 'はァァァーーー！無理こいつまじ無理！本当無理だし視界に入ンのすら無理！サイアク、気分悪い、吐きそう、もう帰る！'
error_icon_dif_day = '昨日の凸漏れはしゃーないですよ！今日頑張りましょ！'
error_icon_already = 'すでに凸開始か凸救援になってるみたいですよ'
error_icon_not_st = '凸開始が見つかりませんよ'
error_icon_not_sthe = '削除する予約がありませんよ'

# 20220103 単語登録機能追加
error_word_nothing = '単語がみつかりませんよ'
error_word_over = '登録できる単語は5つまでですよ'
error_word_keyword_nothing = 'キーワードが見つかりませんよ'
error_word_word_nothing = 'このキーワードには単語が登録されていませんよ'

error_delword_not_load = 'おきのどくですが たんごのしょ は きえてしまいました'
error_delword_not_number = '削除対象は -1~5 で指定してください'

# 用例
cmd_re_arg = '.re ボス番号[@周 or +] 予定ダメージ(万単位)[m[何凸目か]] [コメント]\n(例: .re 3+ 700m 討伐予定)'
cmd_fin_arg = '.fin ボス番号 実績ダメージ(万単位)[m[何凸目か]]\n(例: .fin 2 700m1)'
cmd_la_arg = '.la ボス番号 持ち越し秒数 or m[何凸目か]\n(例: .la 5 m)'
cmd_cancel_arg = '.cl \n(例: .cl)'
cmd_st_arg = '.st ボス番号 [m[何凸目か]] \n(例: .st 3 m)'
cmd_he_arg = '.he ボス番号 \n(例: .he 1)'
cmd_add_arg = '.add (追加したいメンバをメンション) \n(例: .add @ちぇる )'
cmd_remove_arg = '.remove (追加したいメンバをメンション) \n(例: .remove @ちぇる )'
cmd_ms_arg = '.ms 000～222 \n(例: .ms 000 )'
cmd_mb_arg = '.mb ボス番号 周[+] [HP] \n(例: .mb 3 10+ )'
cmd_dice_arg ='.dice [回数]d[何面か] \n(例: .dice 3d6)'
cmd_omi_arg = '.おみくじ \n(例: .おみくじ)'

cmd_word_arg = './ キーワード ["単語] \n(例: ./ ちぇる "ちぇるちぇぽぱっぴ)'
cmd_delword_arg = './cl キーワード 対象の番号 \n(例: ./cl ちぇる 1)'
cmd_tl_arg = '.tl 秒数 \n(例: .tl 60)'

# ラピュタ(Castle in the Sky)
Castle_in_the_Sky =['ムスカ\nっはっはっはっは、どこへゆこうというのかね？',
                    'シータ\n早くこれを！！・・・ムスカが・・・急いでぇ！！',
                    'ムスカ\nその石を大事に持ってろ！小娘の命と引き替えだ！！',
                    'ムスカ\n・・・終点が、玉座の間だとは、上出来じゃないか。ここへ来い！',
                    'シータ\nこれが玉座ですって？！！ここはお墓よ。あなたとあたしの。',
                    'シータ\n・・・国が滅びたのに、王だけ生きてるなんてこっけいだわ。あなたに石は渡さない・・・あなたはここから出ることもできずに、私と死ぬの！！',
                    'シータ\n・・・いまは、・・ラピュタがなぜ滅びたのかあたしよく分かる。',#ゴンドアの谷の歌にあるもの・・・『土に根をおろし、風と共に生きよう。種と共に冬を越え、鳥と共に春をうたおう。』・・・どんなに恐ろしい武器を持っても、・・・たくさんのかわいそうなロボットを操っても・・・土から離れては生きられないのよ！！！',
                    'ムスカ\nラピュタは滅びぬ。何度でも甦るさ！ラピュタの力こそ、人類の夢だからだ！！',
                    'パズー\n待てーーーっっ！！石は隠した！シータを撃ってみろ、石は戻らないぞ',
                    'シータ\nパズー来ちゃだめ、この人はどうせあたし達を殺す気よ！！',
                    'ムスカ\n小僧。娘の命と引き替えだ！石のありかを言え！！・・・それとも、その大砲で、私と勝負するかね？',
                    'パズー\n・・・シータと、二人っきりで話がしたい。',
                    'シータ\n来ちゃだめぇ！！石を捨てて逃げてぇ！！',
                    'ムスカ\n３分間待ってやる。',
                    'パズー\n・・シータ。落ち着いてよく聞くんだ。・・・あの言葉を教えて。・・・ぼくも一緒に言う。ぼくの左手に、手を乗せて・・・',
                    'パズー\n・・・おばさん達の縄は、切ったよ。',
                    'ムスカ\n時間だ！答えを聞こう！！',
                    'パズー　シータ\nバルス！！'
                    ]

error_file_remove = 'ちぇるりれれろりろりろ'
my_eyes_cant_see = 'あぁぁ、目がぁ、目がぁ〜〜〜あああああああ〜〜〜〜'
wait_3min ='3秒間待ってやる'

# おみくじメッセージ
omikuzi_message = '今回の凸の運勢は～'
omikuzi_anser = [
                '☆ちぇる吉！ちぇる～ん♪　ちぇる　ちぇぱら　ちぇらるれろ　ちぇるちぇぽっぱっぴ？なーんて、嘘ですよー、えへっ☆',
                '☆大吉！ウェーイ！おめでとパイセン行け行け！ヒューヒュー！',
                '☆中吉！大抵のTLはうまくいくんじゃないですか？とりま模擬っときますぅ？',
                '☆小吉！そこそこ・・まあ先輩らしいのでチエルはいいと思いますよ？',
                '☆凶！先輩マジっすか・・最後のUB打てませんよ？',
                '☆大凶！先輩サイテー、絶対幽閉されます！',
                '☆りゅうちぇる！てかTLとかどうでもよくな～い？運勢なんて気にしな～い',
                '☆ひげちぇる！てか今日ひげ剃ってな～い、さげぽよ～↓↓ でも気分はあげぽよ～↑↑'
                ]

error_dice_arg = 'さいころを回す回数は99回以下、面数は999面以下で指定してください'