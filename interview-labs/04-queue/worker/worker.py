import os, json, time
import psycopg2, pika

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "app")
DB_USER = os.getenv("DB_USER", "app")
DB_PASS = os.getenv("DB_PASS", "app")

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbit")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", "5672"))
RABBIT_USER = os.getenv("RABBIT_USER", "app")
RABBIT_PASS = os.getenv("RABBIT_PASS", "app")
RABBIT_QUEUE = os.getenv("RABBIT_QUEUE", "tasks")

def db():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

creds = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
params = pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT, credentials=creds)

conn = None
for attempt in range(1, 31):
    try:
        conn = pika.BlockingConnection(params)
        break
    except pika.exceptions.AMQPConnectionError:
        time.sleep(1)

if conn is None:
    raise RuntimeError("Failed to connect to RabbitMQ after 30 attempts")
ch = conn.channel()
ch.queue_declare(queue=RABBIT_QUEUE, durable=True)

def on_msg(chx, method, props, body):
    msg = json.loads(body)
    task_id = msg["task_id"]

    time.sleep(2)

    with db() as c, c.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET status=%s, result=%s WHERE id=%s",
            ("DONE", json.dumps({"ok": True}), task_id)
        )

    chx.basic_ack(method.delivery_tag)

ch.basic_consume(queue=RABBIT_QUEUE, on_message_callback=on_msg)
ch.start_consuming()
