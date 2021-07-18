from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
)

from config import (
    BOT_TOKEN,
    SELECTION_GOODS, SELECTION_REGION, SELECTION_PAYMENT, SUBMIT_PAYMENT,
    REJECT_ORDER, END, ORDER_MENU, SELECTION_FIELDS, CHANGE_FIELD,
    INPUT, CH_INDEX, CH_NAME, CH_REGION, CH_PRICE, CH_PHOTO, CH_SUBMIT
)
from handlers import (
    start,
    select_goods,
    select_region,
    reject_order,
    select_payment,
    waiting_payment,
    submit_payment,
    end,
    stop, 
    cancel,
    myorder,
    add_goods,
    selection_fields,
    change_index,
    change_name,
    change_price,
    change_region,
    change_photo,
    change_submit,
    save_input,
    save_photo,
    kuna
)

def main():
    """An entry point."""
    updater = Updater(token=BOT_TOKEN,
                      use_context=True)


    order_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTION_GOODS: [
                CallbackQueryHandler(select_goods),
            ],
            SELECTION_REGION: [
                CallbackQueryHandler(select_region),
            ],
            SELECTION_PAYMENT: [
                CallbackQueryHandler(reject_order,
                                     pattern='^' + str(REJECT_ORDER) + '$'),
                CallbackQueryHandler(select_payment)
            ],
            SUBMIT_PAYMENT: [
                CallbackQueryHandler(reject_order,
                                     pattern='^' + str(REJECT_ORDER) + '$'),
                CallbackQueryHandler(waiting_payment,
                                     pattern='^' + str(END) + '$'),
                CallbackQueryHandler(submit_payment),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
            CommandHandler("stop", stop)
        ]
    )
    
    myorder_conv = ConversationHandler(
        entry_points=[CommandHandler("myorder", myorder)],
        states={
            ORDER_MENU: [
                CallbackQueryHandler(reject_order,
                                     pattern='^' + str(REJECT_ORDER) + '$'),
                CallbackQueryHandler(waiting_payment,
                                     pattern='^' + str(END) + '$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
            CommandHandler("stop", stop)
        ]
    )
    
    add_conv  = ConversationHandler(
        entry_points=[CommandHandler("add", add_goods)],
        states={
            SELECTION_FIELDS: [
                CallbackQueryHandler(selection_fields)
            ],
            CHANGE_FIELD: [
                CallbackQueryHandler(change_index,
                                     pattern="^" + str(CH_INDEX) + "$"),
                CallbackQueryHandler(change_name,
                                     pattern="^" + str(CH_NAME) + "$"),
                CallbackQueryHandler(change_region,
                                     pattern="^" + str(CH_REGION) + "$"),
                CallbackQueryHandler(change_price,
                                     pattern="^" + str(CH_PRICE) + "$"),
                CallbackQueryHandler(change_photo,
                                     pattern="^" + str(CH_PHOTO) + "$"),
                CallbackQueryHandler(change_submit,
                                     pattern="^" + str(CH_SUBMIT) + "$")
            ],
            INPUT: [
                MessageHandler(Filters.text, save_input),
                MessageHandler(Filters.photo, save_photo)
            ]
        },
        fallbacks=[
            CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
            CommandHandler("cancel", cancel)
        ]
    )

    updater.dispatcher.add_handler(order_conv)
    updater.dispatcher.add_handler(myorder_conv)
    updater.dispatcher.add_handler(add_conv)
    updater.dispatcher.add_handler(CommandHandler("kuna", kuna))
    
    #Start the bot
    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()
