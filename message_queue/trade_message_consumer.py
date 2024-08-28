from message_queue.base import conn, TradeMessageConsumer, trade_message_queue

if __name__ == '__main__':
    worker = TradeMessageConsumer(conn, trade_message_queue.routing_key)
    worker.run()