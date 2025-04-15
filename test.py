
#?pip freeze > requirements.txt    // 기존 가상환경의 모듈 목록을 requirements.txt 파일로 내보냅니다
#! pip install -r requirements.txt  // 새 가상환경에 모듈 설치
# python -m venv myenv
# source myenv/bin/activate  # Linux/Mac
# myenv\Scripts\activate  # Windows

#source .myenv/bin/activate  # Linux/WSL
#.myenv\Scripts\activate     # Windows


#deactivate

# https://github.com/serhmarch/ModbusTools/releases  -modbus-tools

#https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian/    -grafana
#https://grafana.com/grafana/download?pg=get&plcmt=selfmanaged-box1-cta1&platform=windows
#http://127.0.0.1:3000/
#http://localhost:3000/



# raspberrypi.local:5900  -vnc 접속
# ssh pi@raspberrypi.local - ssh 접속
# ping -4 raspberrypi.local


from pymodbus.client import ModbusTcpClient
import sqlite3
from datetime import datetime
import os
from datetime import datetime, timedelta


from apscheduler.schedulers.background import BackgroundScheduler
import time
import random



print("Hello, World!123")

print("Current working directory:", os.getcwd())  #현재 폴더

# Modbus 서버 설정
#MODBUS_SERVER_IP = '127.0.0.1'  # Modbus 서버 IP 주소
#MODBUS_SERVER_IP = '172.20.208.1'  # Modbus 서버 IP 주소
MODBUS_SERVER_IP = '192.168.0.4'  # Modbus 서버 IP 주소
MODBUS_SERVER_PORT = 502        # Modbus 서버 포트
MODBUS_UNIT_ID = 1              # Modbus 장치 ID

# SQLite 데이터베이스 설정
# DATABASE_NAME = '/etc/modbus_data.db'
#DATABASE_NAME = "/home/pesco/Test/database.db"
DATABASE_NAME = "/opt/ystest/ystest1/database.db"
#DATABASE_NAME = 'modbus_data.db'

# Modbus 클라이언트 생성
client = ModbusTcpClient(MODBUS_SERVER_IP, port=MODBUS_SERVER_PORT)
# client.unit_id = MODBUS_UNIT_ID  # unit_id를 설정
# SQLite 데이터베이스 연결
conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
cursor = conn.cursor()

# 테이블 생성 (이미 존재하지 않는 경우)
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS modbus_data (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     timestamp DATETIME,
#     unix_timestamp INTEGER,
#     register_address INTEGER,
#     register_value INTEGER
# )
# ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS raw_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    unix_timestamp INTEGER,
    register_address INTEGER,
    value INTEGER
)
''')



# Modbus 레지스터에서 데이터 읽기
def read_modbus_data(register_address, num_registers=1):
    if client.connect():
        value = random.randint(0, 100)               
        response = client.write_register(address=register_address, value=value)
        
        # response = client.read_holding_registers(address=register_address, count=num_registers)
        response = client.read_holding_registers(address=register_address, count=num_registers,slave=MODBUS_UNIT_ID)
        if not response.isError():
            return response.registers
        else:
            print(f"Error reading Modbus register: {response}")
    else:
        print("Failed to connect to Modbus server")
    return None

# 데이터를 SQLite에 저장
def save_to_sqlite(register_address, register_value):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 현재 UTC 시간 가져오기
    dt_offset = datetime.utcnow()+ timedelta(hours=9)
    # Unix 시간 (초)으로 변환
    unix_time_seconds = int(dt_offset.timestamp())
    print(unix_time_seconds)
    
    # cursor.execute('''
    # INSERT INTO modbus_data (timestamp,unix_timestamp,register_address, register_value)
    # VALUES (?, ?, ?,?)
    # ''', (timestamp,unix_time_seconds, register_address, register_value))
    # conn.commit()
    
    cursor.execute('''
    INSERT INTO raw_table (timestamp,unix_timestamp,register_address, value)
    VALUES (?, ?, ?,?)
    ''', (timestamp,unix_time_seconds, register_address, register_value))
    conn.commit()
    
    



# 메인 로직
def scheduler_logic():
    print(f"Read data from Modbus2222=======")
    register_address = 0  # 읽을 레지스터 주소
    data = read_modbus_data(register_address)
    if data:
        print(f"Read data from Modbus: {data}")
        save_to_sqlite(register_address, data[0])
    else:
        print("No data received from Modbus")   
    
    
    # 스케줄러 설정
scheduler = BackgroundScheduler()
scheduler.add_job(scheduler_logic, 'interval', seconds=2)  # 1초마다 실행


# 메인 로직
def main():    
    # 스케줄러 시작
    scheduler.start()
    # scheduler_logic()
    try:
        # 프로그램이 종료되지 않도록 유지
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # 종료 시 클라이언트와 데이터베이스 연결 종료
        print("종료 시 클라이언트와 데이터베이스 연결 종료========================================") 
        client.close()
        conn.close()
        scheduler.shutdown()    

if __name__ == "__main__":
    main()