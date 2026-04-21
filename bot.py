def button(update, context):
    query = update.callback_query
    query.answer()

    chat_id = str(query.message.chat.id)
    user_id = str(query.from_user.id)
    name = query.from_user.first_name

    # ================= START =================
    if query.data == "start":

        if chat_id in user_data and user_data[chat_id].get("active"):
            query.answer("Game masih berjalan!", show_alert=True)
            return

        try:
            query.edit_message_reply_markup(reply_markup=None)
        except:
            pass

        user_data[chat_id] = {
            "active": True,
            "current_q": None,
            "last_q_msg": None,
            "answered": False  # 🔥 penting
        }

        query.message.reply_text("🔥 Quiz dimulai!")
        send_question(context.bot, chat_id)
        return

    # ================= CEK GAME =================
    if chat_id not in user_data or not user_data[chat_id].get("active"):
        return

    user = user_data[chat_id]

    if not query.data.startswith("ans_"):
        return

    # 🔥 kalau sudah ada yang jawab
    if user.get("answered"):
        query.answer("❌ Sudah ada yang jawab!", show_alert=True)
        return

    ans = int(query.data.split("_")[1])
    q = user["current_q"]

    # 🔒 kunci soal
    user["answered"] = True

    # 🔥 matikan tombol
    try:
        query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    # 🔥 hapus soal lama
    try:
        context.bot.delete_message(chat_id=int(chat_id), message_id=user["last_q_msg"])
    except:
        pass

    # ================= JAWABAN =================
    if ans == q["answer"]:
        user["score"] = user.get("score", 0) + 10

        query.message.reply_text(
            f"⚡ {name} tercepat!\n\n+10 poin\nTotal 👉 {user['score']}"
        )

    # ⏳ delay 3 detik
    import time
    time.sleep(3)

    # 🔄 reset untuk soal berikutnya
    user["answered"] = False

    # lanjut soal
    send_question(context.bot, chat_id)
