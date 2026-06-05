from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import paho.mqtt.client as mqtt
import os
import uuid
from datetime import datetime

from app.api.v1 import inspections_router, parts_router, detection_router
from app.core.database import engine, SessionLocal
from app.models import Part, Inspection, User
from app.core.database import Base
from app.services.sensor_fusion import determine_status
from app.models.inspection import Inspection as InspectionModel
from app.models.part import Part as PartModel

MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.emqx.io")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "capstone/A4/4")

DEFAULT_PART_ID = int(os.getenv("DEFAULT_PART_ID", 1))
DEFAULT_OPERATOR = os.getenv("DEFAULT_OPERATOR", "mqtt_default")

def process_mqtt_payload(payload: dict):
    """
    Memproses payload MQTT dengan format:
    {
        "part_id": int,
        "user": str,
        "jumlah_objek": int,
        "berat_g": float,
        "timestamp": float (opsional)
    }
    """
    db = SessionLocal()
    try:
        part_id = payload.get("part_id")
        operator_username = payload.get("user")
        n_cv = payload.get("jumlah_objek")
        weight_gram = payload.get("berat_g")

        if n_cv is None or weight_gram is None:
            print("Payload MQTT tidak memiliki 'jumlah_objek' atau 'berat_g'")
            return

        if part_id is None:
            part_id = DEFAULT_PART_ID
            print(f"part_id tidak ada, menggunakan default {part_id}")

        if operator_username is None:
            operator_username = DEFAULT_OPERATOR
            print(f"user tidak ada, menggunakan default '{operator_username}'")

        part = db.query(PartModel).filter(PartModel.id == part_id).first()
        if not part:
            print(f"Part dengan id {part_id} tidak ditemukan")
            return
        
        n_weight = int(round(weight_gram / float(part.weight_per_unit)))
        difference = abs(n_cv - n_weight)
        status = determine_status(difference, part.threshold)

        inspection_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        new_inspection = InspectionModel(
            inspection_id=inspection_id,
            part_id=part.id,
           user=operator_username,
            qty_label=part.target_qty,
            n_cv=n_cv,
            n_weight=n_weight,
            difference=difference,
            status=status,
            threshold_used=part.threshold
        )
        db.add(new_inspection)
        db.commit()
        db.refresh(new_inspection)
        print(f"Data MQTT tersimpan: {inspection_id} | Status: {status.value}")

    except Exception as e:
        print(f"Error memproses data MQTT: {e}")
    finally:
        db.close()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"MQTT terhubung ke {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribe topik: {MQTT_TOPIC}")
    else:
        print(f"Gagal konek MQTT, kode {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"MQTT dari {msg.topic}: {payload}")
        process_mqtt_payload(payload)
    except json.JSONDecodeError:
        print(f"Payload bukan JSON: {msg.payload}")
    except Exception as e:
        print(f"Error handling MQTT: {e}")

def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    return client

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Memulai MQTT subscriber...")
    mqtt_client = start_mqtt_client()
    app.state.mqtt_client = mqtt_client
    yield
    if hasattr(app.state, 'mqtt_client'):
        app.state.mqtt_client.loop_stop()
        app.state.mqtt_client.disconnect()
        print("MQTT subscriber dihentikan.")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Part Counting Station API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inspections_router, prefix="/api/v1")
app.include_router(parts_router, prefix="/api/v1")
app.include_router(detection_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Part Counting Station API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}