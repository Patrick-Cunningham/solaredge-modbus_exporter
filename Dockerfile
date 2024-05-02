FROM python:3.12.3-alpine3.18

COPY solaredge-modbus-exporter.py solaredge-modbus-exporter.py

RUN pip install solaredge-modbus prometheus-client

EXPOSE 2112

CMD ["python", "solaredgeModbusExporter.py"]