# backend/core/db_init.py
try:
    import sqlite3
except Exception:
    import pysqlite3 as sqlite3

from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "backend" / "data" / "procurement.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

schema = """
CREATE TABLE IF NOT EXISTS vendors(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  approved INTEGER DEFAULT 1,
  ext_score REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS items(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  sku TEXT,
  unit TEXT,
  unit_price REAL DEFAULT 0,
  default_vendor_id INTEGER,
  FOREIGN KEY(default_vendor_id) REFERENCES vendors(id)
);
CREATE TABLE IF NOT EXISTS inventory(
  item_id INTEGER PRIMARY KEY,
  qty_on_hand INTEGER DEFAULT 0,
  max_capacity INTEGER DEFAULT 0,
  min_qty INTEGER DEFAULT 0,
  FOREIGN KEY(item_id) REFERENCES items(id)
);
CREATE TABLE IF NOT EXISTS budgets(
  dept TEXT,
  period TEXT,
  limit_amount REAL,
  used_amount REAL DEFAULT 0,
  PRIMARY KEY(dept, period)
);
CREATE TABLE IF NOT EXISTS policies(
  key TEXT PRIMARY KEY,
  value TEXT
);
CREATE TABLE IF NOT EXISTS orders(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INTEGER,
  qty INTEGER,
  vendor_id INTEGER,
  amount REAL,
  status TEXT DEFAULT 'DRAFT',
  pdf_path TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(item_id) REFERENCES items(id),
  FOREIGN KEY(vendor_id) REFERENCES vendors(id)
);

CREATE TABLE IF NOT EXISTS emails (
    id TEXT PRIMARY KEY,
    subject TEXT,
    sender TEXT,
    date TEXT,
    body TEXT,
    folder TEXT,
    is_read BOOLEAN DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS email_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id TEXT NOT NULL,
    priority TEXT,
    summary TEXT,
    item_id INTEGER,
    item_name TEXT,
    item_unit_price REAL,
    item_quantity INTEGER,
    vendor_id INTEGER,
    vendor_name TEXT,
    vendor_email TEXT,
    vendor_phone TEXT,
    total_cost REAL,
    compliance_status TEXT DEFAULT 'Pending',
    compliance_explanation TEXT,
    order_id INTEGER,
    FOREIGN KEY(email_id) REFERENCES emails(id),
    FOREIGN KEY(order_id) REFERENCES orders(id)
);

"""

conn = sqlite3.connect(str(DB_PATH))
conn.executescript(schema)

# seed a couple of rows
#conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,approved,ext_score) VALUES (1,'Acme Corp','sales@acme.example',1,82)")
#conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (1,'M4 Stainless Screws','M4-SS-100','box',12.50,1)")
#conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Operations','2025-Q3',50000,0)")
#conn.execute("INSERT OR IGNORE INTO policies(key,value) VALUES ('max_single_order_amount','50000')")
#conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (1, 0, 1000, 50)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (1,'Tesla Energy','sales@teslaenergy.com','555-0199',1,90)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (2,'LG Chem','contact@lgchem.com','555-0288',1,88)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (3,'Panasonic','supply@panasonic.com','555-0377',1,85)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (4,'Bosch Mobility','orders@bosch.com','555-0466',1,87)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (5,'CATL','info@catl.com','555-0555',1,92)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (6,'BYD Components','orders@byd.com','555-0644',1,89)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (7,'Continental AG','sales@continental.com','555-0733',1,84)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (8,'Valeo','orders@valeo.com','555-0822',1,83)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (9,'Nippon Glass','supply@nippon-glass.jp','555-0911',1,86)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (10,'ZF Friedrichshafen','sales@zf.com','555-1000',1,82)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (11,'Delphi Tech','orders@delphi.com','555-1199',1,80)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (12,'Magna EV Systems','supply@magna.com','555-1288',1,81)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (13,'Samsung SDI','orders@samsung-sdi.com','555-1377',1,91)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (14,'Hitachi Automotive','sales@hitachi-auto.com','555-1466',1,85)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (15,'Infineon Tech','orders@infineon.com','555-1555',1,87)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (16,'Texas Instruments','supply@ti.com','555-1644',1,86)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (17,'Aptiv','contact@aptiv.com','555-1733',1,84)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (18,'Lear Corp','sales@lear.com','555-1822',1,83)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (19,'Harman Automotive','orders@harman.com','555-1911',1,82)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (20,'Acme Corp','sales@acme.example','555-2000',1,82)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (21,'NVIDIA Auto','sales@nvidia-auto.com','555-2100',1,95)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (22,'Intel Mobileye','orders@mobileye.com','555-2200',1,93)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (23,'Qualcomm Auto','supply@qualcomm.com','555-2300',1,90)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (24,'Brembo S.p.A.','sales@brembo.com','555-2400',1,89)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (25,'Ohlins Racing','orders@ohlins.com','555-2500',1,88)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (26,'Recaro Automotive','supply@recaro.com','555-2600',1,87)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (27,'Sparco','sales@sparco.com','555-2700',1,85)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (28,'Hella GmbH','orders@hella.com','555-2800',1,86)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (29,'Denso Corp','sales@denso.com','555-2900',1,88)")
conn.execute("INSERT OR IGNORE INTO vendors(id,name,email,phone,approved,ext_score) VALUES (30,'Aisin Seiki','supply@aisin.com','555-3000',1,84)")

# ---------------- Items ----------------
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (1,'Lithium-ion Battery Pack 75kWh Model X','BAT-75KWH-X','unit',7500,1)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (2,'Lithium-ion Battery Pack 100kWh Model Y','BAT-100KWH-Y','unit',9500,2)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (3,'EV Motor 250kW Model X','MOTOR-250KW-X','unit',12000,4)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (4,'EV Motor 150kW Model Y','MOTOR-150KW-Y','unit',9000,4)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (5,'Onboard Charger 11kW Standard','CHGR-11KW-ST','unit',900,5)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (6,'Onboard Charger 22kW Fast','CHGR-22KW-FAST','unit',1400,5)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (7,'Inverter 400V Model X','INV-400V-X','unit',3000,6)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (8,'Inverter 800V Model Y','INV-800V-Y','unit',4500,6)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (9,'DC-DC Converter 12V for Model X','DC-DC-12V-X','unit',600,7)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (10,'High Voltage Cable 10m','CABLE-HV-10M','meter',50,7)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (11,'Thermal Management Pump Standard','PUMP-COOL-STD','unit',250,8)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (12,'Radiator for EV Model X','RAD-EV-X','unit',800,8)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (13,'Windshield Glass Model S Front','GLASS-MS-F','unit',500,9)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (14,'Windshield Glass Model X Front','GLASS-MX-F','unit',600,9)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (15,'Side Mirror Assembly Model S','MIRROR-SIDE-MS','unit',120,10)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (16,'Rear Camera Model X','CAM-REAR-X','unit',200,10)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (17,'Radar Sensor Front Model X','SENSOR-RADAR-F','unit',400,11)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (18,'LiDAR Sensor Roof Model Y','SENSOR-LIDAR-R','unit',1500,11)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (19,'Ultrasonic Sensor Side Model X','SENSOR-ULTRA-S','unit',80,12)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (20,'Steering Wheel Model X Sport','STEER-EV-SP','unit',250,12)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (21,'Driver Seat Assembly Model X','SEAT-DRV-X','unit',800,13)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (22,'Passenger Seat Assembly Model X','SEAT-PASS-X','unit',750,13)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (23,'Infotainment Display 15in Model X','DISP-INFO-15X','unit',1200,14)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (24,'Headlight LED Low Beam Model X','LIGHT-LED-LB-X','unit',300,14)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (25,'Taillight LED Model X','LIGHT-TAIL-X','unit',200,14)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (26,'Alloy Wheel 18in Model X','WHEEL-18-X','unit',400,15)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (27,'Alloy Wheel 20in Model Y','WHEEL-20-Y','unit',500,15)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (28,'Tire 18in Model X','TIRE-18-X','unit',150,16)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (29,'Tire 20in Model Y','TIRE-20-Y','unit',180,16)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (30,'Brake Pad Set Model X Front','BRAKE-PAD-FX','set',200,17)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (31,'Brake Disc Model X Rear','BRAKE-DISC-RX','unit',300,17)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (32,'Suspension Strut Model X Front','SUSP-STRUT-FX','unit',350,18)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (33,'Shock Absorber Model X Rear','SHOCK-ABS-RX','unit',320,18)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (34,'Wiring Harness Model X Front','WIRE-HARN-FX','set',500,19)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (35,'Software License ECU Model X','ECU-SW-LIC-X','unit',200,19)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (36,'Battery Management System 100kWh Model Y','BMS-CTRL-Y','unit',1500,2)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (37,'Charging Port CCS Model X','PORT-CCS-X','unit',600,3)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (38,'Charging Port CHAdeMO Model Y','PORT-CHD-Y','unit',550,3)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (39,'Heater Assembly Model X','HEATER-EV-X','unit',400,20)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (40,'Air Conditioning Unit Model X','AC-EV-X','unit',900,20)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (41,'Fuse High Voltage Model X','FUSE-HV-X','unit',40,6)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (42,'Relay High Voltage Model X','RELAY-HV-X','unit',60,6)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (43,'Washer Fluid Pump Model X','PUMP-WASH-X','unit',30,8)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (44,'Wiper Blade Set Model X Front','WIPER-BLD-FX','set',50,9)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (45,'Battery Cooling Plate Model X','BAT-COOL-X','unit',700,5)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (46,'Motor Cooling Jacket Model Y','MOTOR-COOL-Y','unit',800,5)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (47,'Seat Belt Assembly Model X','BELT-SEAT-X','unit',120,12)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (48,'Airbag Module Front Model X','AIRBAG-FR-X','unit',500,13)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (49,'Central Control Unit Model X','CCU-MAIN-X','unit',2200,19)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (50,'Telematics Control Unit Model X','TCU-CON-X','unit',1800,19)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (51,'GPU Module Drive Orin','GPU-ORIN-X','unit',1500,21)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (52,'Vision Processor EyeQ5','VIS-EYEQ5','unit',800,22)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (53,'Snapdragon Ride SoC','SOC-SD-RIDE','unit',1200,23)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (54,'Carbon Ceramic Brake Disc Front','BRAKE-CC-F','unit',2000,24)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (55,'Carbon Ceramic Brake Disc Rear','BRAKE-CC-R','unit',1800,24)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (56,'Performance Coilover Set','SUSP-COIL-perf','set',3500,25)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (57,'Sport Bucket Seat Alcantara','SEAT-SP-ALC','unit',1500,26)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (58,'Racing Harness 5-Point','BELT-RACE-5','unit',300,27)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (59,'Matrix LED Headlight Assembly','LIGHT-MTX-LED','unit',1200,28)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (60,'Alternator High Output','ALT-HO-12V','unit',400,29)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (61,'Transmission 8-Speed Auto','TRANS-8SP-AT','unit',4500,30)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (62,'Hybrid Power Control Unit','PCU-HYBRID','unit',2500,29)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (63,'Fuel Injection Pump High Pressure','PUMP-FUEL-HP','unit',600,29)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (64,'Turbocharger Electric Assist','TURBO-E-AST','unit',1800,10)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (65,'Exhaust Manifold Sport','EXH-MAN-SP','unit',450,18)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (66,'Catalytic Converter Euro 7','CAT-CONV-E7','unit',900,18)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (67,'Steering Rack Electric','STEER-RACK-E','unit',750,12)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (68,'Air Suspension Compressor','SUSP-COMP-AIR','unit',500,11)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (69,'Door Module Controller','MOD-DOOR-CTRL','unit',150,19)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (70,'Window Regulator Motor','MOTOR-WIN-REG','unit',80,19)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (71,'Sunroof Motor Assembly','MOTOR-SUN-ASM','unit',120,8)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (72,'Rain Sensor Module','SENSOR-RAIN','unit',40,11)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (73,'TPMS Sensor Set','SENSOR-TPMS-4','set',100,7)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (74,'Keyless Entry Fob','KEY-FOB-ENTRY','unit',80,7)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (75,'Ambient Lighting Kit','LIGHT-AMB-KIT','kit',200,14)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (76,'Floor Mat Set Premium','MAT-FLOOR-PREM','set',150,13)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (77,'Roof Rack Crossbars','RACK-ROOF-BAR','set',250,13)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (78,'Tow Hitch Assembly','HITCH-TOW-ASM','unit',400,15)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (79,'Mud Flap Set','FLAP-MUD-SET','set',60,15)")
conn.execute("INSERT OR IGNORE INTO items(id,name,sku,unit,unit_price,default_vendor_id) VALUES (80,'Car Cover Weatherproof','COVER-CAR-WP','unit',120,20)")
# ---------------- Budgets (Expanded) ----------------
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Battery Dept','2025-Q3',5000000,500000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Motor Assembly','2025-Q3',4000000,250000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Glass & Interiors','2025-Q3',2000000,100000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Electronics','2025-Q3',3000000,200000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Chassis & Wheels','2025-Q3',2000000,150000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('R&D','2025-Q3',5000000,800000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Procurement','2025-Q3',1000000,100000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Engineering','2025-Q3',5000000,200000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('IT','2025-Q3',3000000,150000)")
conn.execute("INSERT OR IGNORE INTO budgets(dept,period,limit_amount,used_amount) VALUES ('Operations','2025-Q3',4000000,500000)")

# ---------------- Policies ----------------
conn.execute("INSERT OR IGNORE INTO policies(key,value) VALUES ('max_single_order_amount','100000')")
conn.execute("INSERT OR IGNORE INTO policies(key,value) VALUES ('min_vendor_score','80')")
conn.execute("INSERT OR IGNORE INTO policies(key,value) VALUES ('max_open_orders','500')")

# ---------------- Inventory (Expanded Capacity) ----------------
# Existing items expanded
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (1,500,10000,1000)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (2,400,8000,800)")
# ... (Assuming existing inserts are handled by IGNORE, but we want to UPDATE capacity if exists? IGNORE skips. So I should probably DELETE and re-insert or assume clean slate. The script does CREATE TABLE IF NOT EXISTS. If DB exists, these INSERT OR IGNOREs do nothing for existing IDs.
# To ensure expansion, I will assume the user might delete the DB or I should use REPLACE or update the values.)
# Since this is an init script, I will just add *new* items.
# But user said "expand compliance limits in order to support more storage". If DB exists, I might need to run an UPDATE.
# I'll add an UPDATE at the end for existing items to boost capacity.

# Removed New Vendors block (moved to top with phone data)




# New Inventory (51-80)
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (51,50,500,100)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (52,60,600,120)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (53,40,400,80)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (54,20,200,40)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (55,20,200,40)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (56,10,100,20)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (57,15,150,30)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (58,50,500,100)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (59,30,300,60)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (60,40,400,80)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (61,10,100,20)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (62,15,150,30)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (63,25,250,50)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (64,20,200,40)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (65,30,300,60)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (66,25,250,50)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (67,20,200,40)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (68,15,150,30)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (69,100,1000,200)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (70,80,800,160)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (71,40,400,80)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (72,120,1200,240)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (73,200,2000,400)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (74,300,3000,600)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (75,50,500,100)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (76,100,1000,200)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (77,20,200,40)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (78,10,100,20)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (79,80,800,160)")
conn.execute("INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES (80,40,400,80)")

# Update existing inventory limits to support more storage
conn.execute("UPDATE inventory SET max_capacity = max_capacity * 2 WHERE item_id <= 50")
conn.execute("UPDATE budgets SET limit_amount = limit_amount * 2")
conn.execute("UPDATE policies SET value = '100000' WHERE key = 'max_single_order_amount'")


#orders

conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (1,1,5,1,37500,'DRAFT','orders/order_1.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (2,2,3,2,28500,'APPROVED','orders/order_2.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (3,3,2,4,24000,'PENDING','orders/order_3.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (4,4,4,4,36000,'DRAFT','orders/order_4.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (5,5,10,5,9000,'APPROVED','orders/order_5.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (6,6,6,5,8400,'PENDING','orders/order_6.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (7,7,3,6,9000,'DRAFT','orders/order_7.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (8,8,2,6,9000,'APPROVED','orders/order_8.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (9,9,20,7,12000,'PENDING','orders/order_9.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (10,10,15,7,750,'DRAFT','orders/order_10.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (11,11,5,8,1250,'APPROVED','orders/order_11.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (12,12,3,8,2400,'PENDING','orders/order_12.pdf')")
conn.execute("INSERT OR IGNORE INTO orders(id,item_id,qty,vendor_id,amount,status,pdf_path) VALUES (13,13,7,9,3500,'DRAFT','orders/order_13.pdf')")




conn.commit()
conn.close()
print(f"Initialized DB at {DB_PATH}")

