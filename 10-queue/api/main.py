import os, json, uuid
import psycopg2, pika
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "app")
DB_USER = os.getenv("DB_USER", "app")
DB_PASS = os.getenv("DB_PASS", "app")

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbit")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", "5672"))
RABBIT_USER = os.getenv("RABBIT_USER", "app")
RABBIT_PASS = os.getenv("RABBIT_PASS", "app")
RABBIT_QUEUE = os.getenv("RABBIT_QUEUE", "tasks")

class CreateTask(BaseModel):
    payload: dict

def db():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

@app.on_event("startup")
def init():
    with db() as c, c.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
          id TEXT PRIMARY KEY,
          status TEXT,
          payload JSONB,
          result JSONB
        )
        """)

@app.post("/tasks")
def create_task(req: CreateTask):
    task_id = str(uuid.uuid4())
    with db() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks VALUES (%s,%s,%s,%s)",
            (task_id, "PENDING", json.dumps(req.payload), None)
        )

    creds = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT, credentials=creds)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.queue_declare(queue=RABBIT_QUEUE, durable=True)
    ch.basic_publish("", RABBIT_QUEUE, json.dumps({"task_id": task_id, "payload": req.payload}))
    conn.close()

    return {"task_id": task_id}

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    with db() as c, c.cursor() as cur:
        cur.execute("SELECT id,status,result FROM tasks WHERE id=%s", (task_id,))
        r = cur.fetchone()
    if not r:
        raise HTTPException(404)
    return {"id": r[0], "status": r[1], "result": r[2]}
