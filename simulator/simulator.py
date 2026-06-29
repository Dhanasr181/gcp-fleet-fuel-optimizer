import time
import random
import datetime
import os
from google.cloud import pubsub_v1
import schema_pb2

PROJECT_ID = os.getenv("GCP_PROJECT") # Automatically picks up Cloud Shell project
TOPIC_ID = "telemetry-raw"

# Initialize Publisher with strict batch parameters
publisher = pubsub_v1.PublisherClient(
    batch_settings=pubsub_v1.types.BatchSettings(
        max_messages=50, 
        max_bytes=1024 * 50, 
        max_latency=0.5
    )
)
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def generate_telemetry_event(vehicle_id):
    now = datetime.datetime.utcnow().isoformat() + "Z"
    is_braking = random.choices([True, False], weights=[0.15, 0.85])[0]
    
    # Simulating behavioral divergence (Efficient vs Inefficient Drivers)
    if random.random() > 0.7:  # Aggressive Driver Profile
        brake_force = random.uniform(65.0, 98.0) if is_braking else 0.0
        fuel_flow = random.uniform(35.0, 60.0)
        rpm = random.randint(2800, 4000)
    else:                      # Fuel Efficient Driver Profile
        brake_force = random.uniform(10.0, 40.0) if is_braking else 0.0
        fuel_flow = random.uniform(12.0, 28.0)
        rpm = random.randint(1100, 2200)

    return schema_pb2.VehicleTelemetry(
        vehicle_id=vehicle_id,
        timestamp=now,
        latitude=random.uniform(37.7749, 37.8049),
        longitude=random.uniform(-122.4194, -122.4494),
        speed_kmh=random.uniform(40.0, 85.0),
        rpm=rpm,
        throttle_pct=random.uniform(15.0, 90.0),
        fuel_flow_lph=fuel_flow,
        brake_event=is_braking,
        brake_force_pct=brake_force,
        braking_distance_m=random.uniform(4.0, 35.0) if is_braking else 0.0,
        acceleration_ms2=random.uniform(-3.5, 3.5),
        load_weight_kg=random.uniform(12000, 26000),
        engine_temp_c=random.uniform(88.0, 102.0),
        idle_duration_secs=random.choice([0, 0, 0, 30, 120]),
        gear_position=str(random.randint(5, 10)),
        road_grade_pct=random.uniform(-2.0, 5.0)
    )

def main():
    vehicles = [f"TRUCK-{i:03d}" for i in range(1, 11)] # 10 Trucks
    print(f"Executing simulator against Pub/Sub target: {topic_path}")
    
    try:
        while True:
            for v_id in vehicles:
                event = generate_telemetry_event(v_id)
                serialized = event.SerializeToString()
                future = publisher.publish(topic_path, serialized)
                future.add_done_callback(lambda f: f.result())
            time.sleep(2.0) # Send updates every 2 seconds
    except KeyboardInterrupt:
        print("\nSimulation suspended safely.")

if __name__ == "__main__":
    main()
