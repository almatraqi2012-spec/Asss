import telebot, threading, time, asyncio, requests, random, os, sqlite3
from telebot import types
from telethon import TelegramClient, functions, types as tl_types, errors
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest

# ================= [ ⚙️ الإعدادات المركزية ] ================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MY_API_ID = 21349867
MY_API_HASH = '7ced3ee4c80117bd5138410811b91f9f'
ADMIN_ID = 6016547718

OXAPAY_KEY = "CE8H0F-ISXBD2-RXHALY-KZXUZU"
MY_WALLET = "TLtLuhkU2kkkR1Wz1TtrBTpoNRTNviYpsA"
PRICE_PER_MEMBER = 0.04
REFERRAL_GIFT = 0.05

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
user_states = {}

# ================= [ 💾 إدارة البيانات ] ================
    conn.execute('PRAGMA journal_mode=WAL;')      # يحسن بالعمليات والكتابة في نفس الوقت بالهجوم
    conn.execute('PRAGMA synchronous=NORMAL;')    # يسرع عملية حفظ البيانات بشكل كبير
    conn.execute('PRAGMA cache_size=10000;')      # يختزن ذاكرة مؤقتة لتسريع الاستجابة
    # -------------------------------------------

    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, balance REAL DEFAULT 0, joined_date TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS accounts (session_name TEXT PRIMARY KEY, status TEXT DEFAULT "active")')
    conn.execute('CREATE TABLE IF NOT EXISTS memory (target_id TEXT PRIMARY KEY)')
    conn.commit()
    return conn

def get_db():
    conn = sqlite3.connect('dragon_final_v73.db', timeout=30)
    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, balance REAL DEFAULT 0.0)')
    return conn

def get_balance(uid):
    conn = get_db(); res = conn.execute("SELECT balance FROM users WHERE uid=?", (uid,)).fetchone()
    conn.close(); return res[0] if res else 0.0

def update_balance(uid, amt):
    conn = get_db(); curr = get_balance(uid)
    conn.execute("INSERT OR REPLACE INTO users VALUES (?, ?)", (uid, round(curr + amt, 2)))
    conn.commit(); conn.close()

def save_user_memory(user_id):
    with open('memory.txt', 'a') as f: f.write(str(user_id) + '\n')

def get_memory():
    if not os.path.exists('memory.txt'): return []
    with open('memory.txt', 'r') as f: return f.read().splitlines()

# ================= [ ⚔️ محرك سهم V73 - القفز التلقائي ] ================
async def run_sahm_v73(army, src, trg, total, uid):
    success = 0
    bot.send_message(uid, "🚀 **تفعيل رادار سهم... جاري اختراق المصدر.**")

    for session_file in army:
        if success >= total or get_balance(uid) < PRICE_PER_MEMBER: break
        added_list = get_memory()
        client = TelegramClient(session_file.replace('.session',''), MY_API_ID, MY_API_HASH)
        try:
            await client.connect()
            if not await client.is_user_authorized(): continue
            targets = []
            async for m in client.iter_messages(src, limit=5000):
                if len(targets) >= 100: break
                if m.sender_id and str(m.sender_id) not in added_list:
                    u = await m.get_sender()
                    if isinstance(u, tl_types.User) and not u.bot:
                        if u.id not in [x.id for x in targets]: targets.append(u)
            count = 0
            for t in targets:
                if success >= total or count >= 40 or get_balance(uid) < PRICE_PER_MEMBER: break
                try:
                    await client(InviteToChannelRequest(trg, [t]))
                    save_user_memory(t.id)
                    update_balance(uid, -PRICE_PER_MEMBER)
                    success += 1; count += 1
                    bot.send_message(uid, f"➕ [{session_file}] أضاف: `{t.first_name}`")
                    await asyncio.sleep(random.randint(20, 40))
                except errors.FloodWaitError:
                    break # القفز الفوري للحساب التالي عند الحظر
                except:
                    continue
            await client.disconnect()
        except: continue

    bot.send_message(uid, f"🏁 **اكتملت المهمة!**\n✅ الإضافة: `{success}`\n💰 الرصيد المتبقي: `{get_balance(uid)}$` ")

# ================= [ 📱 الواجهة ونظام الإحالة ] ================
@bot.message_handler(commands=['start'])
def start_main(m):
    uid = m.chat.id
    conn = get_db()
    res = conn.execute("SELECT uid FROM users WHERE uid=?", (uid,)).fetchone()
    conn.close()

    if res is None:
        params = m.text.split()
        if len(params) > 1:
            referrer_id = params[1]
            if referrer_id.isdigit():
                ref_id = int(referrer_id)
                if ref_id != uid:
                    update_balance(ref_id, REFERRAL_GIFT)
                    try: bot.send_message(ref_id, f"🎊 **بشارة!** دخل صديق برابطك، حصلت على `{REFERRAL_GIFT}$`.")
                    except: pass

        conn = get_db()
        conn.execute("INSERT INTO users (uid, balance) VALUES (?, ?)", (uid, 0.0))
        conn.commit(); conn.close()

    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("⚔️ بدء الأضافه", "➕ إضافة حساب للجيش")
    mk.add("💰 شحن الرصيد", "👤 حسابي")
    mk.add("📊 الإحصائيات", "🗑️ حذف حساب", "🎁 كسب رصيد مجاني")
    if uid == ADMIN_ID: mk.add("💎 لوحة المالك")
    bot.send_message(uid, "🐲 **مرحباً بك في دراجون المطور!**\nأسرع نظام لسحب الأعضاء.", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == "🎁 كسب رصيد مجاني")
def referral_menu(m):
    ref_link = f"https://t.me/{bot.get_me().username}?start={m.chat.id}"
    bot.send_message(m.chat.id, f"🎁 **نظام الإحالات:**\n\nرابطك لربح `{REFERRAL_GIFT}$`:\n`{ref_link}`")

# ================= [ 💳 الشحن والمحفظة ] ================
@bot.message_handler(func=lambda m: m.text == "💰 شحن الرصيد")
def payment_menu(m):
    user_states[m.chat.id] = None
    mk = types.InlineKeyboardMarkup(row_width=1)
    mk.add(types.InlineKeyboardButton("⚡ شحن Oxapay (آلي)", callback_data="pay_oxa"),
           types.InlineKeyboardButton("💳 شحن محفظة (يدوي)", callback_data="pay_man"))
    bot.send_message(m.chat.id, f"💰 رصيدك: `{get_balance(m.chat.id)}$` ", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data == "pay_oxa")
def oxa_call(c):
    msg = bot.send_message(c.message.chat.id, "💵 **أدخل المبلغ ($):**")
    bot.register_next_step_handler(msg, process_oxa)

def process_oxa(m):
    try:
        amt = float(m.text)
        res = requests.post("https://api.oxapay.com/merchants/request", json={'merchant': OXAPAY_KEY, 'amount': amt, 'currency': 'USD'}).json()
        if res.get('payLink'):
            mk = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("دفع 🔗", url=res['payLink']))
            bot.send_message(m.chat.id, f"✅ فاتورة {amt}$:", reply_markup=mk)
    except: bot.send_message(m.chat.id, "⚠️ رقم غير صحيح.")

@bot.callback_query_handler(func=lambda c: c.data == "pay_man")
def man_call(c):
    user_states[c.message.chat.id] = "waiting_receipt"
    bot.send_message(c.message.chat.id, f"💳 المحفظة:\n`{MY_WALLET}`\n📸 أرسل الإيصال.")

@bot.message_handler(content_types=['photo'])
def handle_receipt(m):
    if user_states.get(m.chat.id) == "waiting_receipt":
        mk = types.InlineKeyboardMarkup(row_width=3)
        mk.add(types.InlineKeyboardButton("✅ 5$", callback_data=f"set_5_{m.chat.id}"),
               types.InlineKeyboardButton("✅ 10$", callback_data=f"set_10_{m.chat.id}"),
               types.InlineKeyboardButton("✅ 50$", callback_data=f"set_50_{m.chat.id}"))
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=f"📩 إيصال من `{m.chat.id}`", reply_markup=mk)
        bot.reply_to(m, "⏳ جارٍ المراجعة...")
        user_states[m.chat.id] = None

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_"))
def admin_confirm(c):
    _, amt, uid = c.data.split('_')
    update_balance(int(uid), float(amt))
    bot.send_message(int(uid), f"🎉 تم شحن {amt}$!")
    bot.edit_message_caption(f"✅ تم تفعيل {amt}$ للحساب {uid}", c.message.chat.id, c.message.message_id)

# ================= [ 📱 نظام إضافة الحسابات المطور ] ================
@bot.message_handler(func=lambda m: m.text == "➕ إضافة حساب للجيش")
def add_acc_start(m):
    msg = bot.send_message(m.chat.id, "📱 **أرسل الرقم مع المفتاح الدولي:**")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(m):
    ph = m.text.strip().replace('+', '').replace(' ', '')
    if not ph.isdigit(): return bot.send_message(m.chat.id, "⚠️ أرقام فقط.")
    sess = f"sess_{m.chat.id}_{ph}"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    cl = TelegramClient(sess, MY_API_ID, MY_API_HASH, loop=loop)
    async def get_c():
        await cl.connect()
        try:
            res = await cl.send_code_request(ph)
            return res.phone_code_hash, "OK"
        except Exception as e: return str(e), "ERR"
        finally: await cl.disconnect()
    try:
        h, status = loop.run_until_complete(get_c())
        if status == "OK":
            msg = bot.send_message(m.chat.id, "📩 **أرسل الكود:**")
            bot.register_next_step_handler(msg, process_code, ph, h, sess)
        else: bot.send_message(m.chat.id, f"❌ {h}")
    except Exception as e: bot.send_message(m.chat.id, f"⚠️ عطل: {str(e)}")
    finally: loop.close()

def process_code(m, ph, h, sess):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    cl = TelegramClient(sess, MY_API_ID, MY_API_HASH, loop=loop)
    async def sign():
        await cl.connect()
        try:
            await cl.sign_in(ph, m.text, phone_code_hash=h)
            return "OK"
        except errors.SessionPasswordNeededError: return "2FA"
        except Exception as e: return str(e)
        finally: await cl.disconnect()
    try:
        res = loop.run_until_complete(sign())
        if res == "OK": bot.send_message(m.chat.id, "✅ **تم الربط!**")
        elif res == "2FA":
            msg = bot.send_message(m.chat.id, "🔐 **أرسل 2FA:**")
            bot.register_next_step_handler(msg, process_password, sess)
        else: bot.send_message(m.chat.id, f"❌ {res}")
    finally: loop.close()

def process_password(m, sess):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    cl = TelegramClient(sess, MY_API_ID, MY_API_HASH, loop=loop)
    async def sign_p():
        await cl.connect()
        try: await cl.sign_in(password=m.text); return "OK"
        except Exception as e: return str(e)
        finally: await cl.disconnect()
    try:
        if loop.run_until_complete(sign_p()) == "OK": bot.send_message(m.chat.id, "✅ **تم الربط!**")
        else: bot.send_message(m.chat.id, "❌ خطأ في كلمة السر.")
    finally: loop.close()

# ================= [ ⚙️ الإدارة والتشغيل ] ================
@bot.message_handler(func=lambda m: m.text == "📊 الإحصائيات")
def stats_all(m):
    a = len([f for f in os.listdir('.') if f.startswith(f"sess_{m.chat.id}_") and f.endswith('.session')])
    bot.send_message(m.chat.id, f"📊 **إحصائياتك:**\n📱 الجيش: `{a}`\n💰 الرصيد: `{get_balance(m.chat.id)}$` ")

@bot.message_handler(func=lambda m: m.text == "⚔️ بدء الأضافه")
def start_attack_cmd(m):
    if get_balance(m.chat.id) < PRICE_PER_MEMBER: return bot.send_message(m.chat.id, "❌ رصيد منخفض.")
    army = [f for f in os.listdir('.') if f.startswith(f"sess_{m.chat.id}_") and f.endswith('.session')]
    if not army: return bot.send_message(m.chat.id, "❌ أضف حسابات أولاً.")
    msg = bot.send_message(m.chat.id, "📡 **يوزر المصدر:**")
    bot.register_next_step_handler(msg, lambda s: bot.register_next_step_handler(bot.send_message(m.chat.id, "🎯 **يوزر مجموعتك:**"), lambda t: bot.register_next_step_handler(bot.send_message(m.chat.id, "🔢 **العدد المطلوب:**"), lambda n: threading.Thread(target=lambda: asyncio.run(run_sahm_v73(army, s.text, t.text, int(n.text), m.chat.id))).start())))

@bot.message_handler(func=lambda m: m.text == "👤 حسابي")
def info(m):
    a = len([f for f in os.listdir('.') if f.startswith(f"sess_{m.chat.id}_")])
    bot.send_message(m.chat.id, f"👤 **حسابك:**\n💰 الرصيد: `{get_balance(m.chat.id)}$` \n📱 الجيش: `{a}`")

if __name__ == '__main__':
    print("🐲 دراجون V73 ينطلق الآن...")
    bot.infinity_polling()
