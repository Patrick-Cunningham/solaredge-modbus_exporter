"""
    Solaredge-modbus Prometheus Exporter
    Copyright (C) 2024 Patrick Cunningham

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
#!/usr/bin/env python3

import time
import os

import solaredge_modbus
from prometheus_client import start_http_server, Gauge, Info

class SolarEdgeMetrics:
    """Metrics Class"""
    def __init__(self, se_host, se_port, se_timeout, se_unit, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds

        print("Solaredge-modbus Prometheus Exporter")
        print("------------------------------------")
        print(f"Solaredge Host: {se_host}")
        print(f"Solaredge Port: {se_port}")
        print(f"Solaredge Timeout: {se_timeout}")
        print(f"Solaredge Unit: {se_unit}")

        self.inverter = solaredge_modbus.Inverter(
            host=se_host,
            port=se_port,
            timeout=se_timeout,
            unit=se_unit
        )

        values = {}
        values = self.inverter.read_all()

        self.info = Info("solaredge_info", "SolarEdge Info")

        self.temperature = Gauge("solaredge_temperature", "SolarEdge Temperature")

        self.current = Gauge("solaredge_current", "Current")

        if values['c_sunspec_did'] is solaredge_modbus.sunspecDID.THREE_PHASE_INVERTER.value:
            self.l1_current = Gauge("solaredge_phase1_current", "Phase 1 Current")
            self.l2_current = Gauge("solaredge_phase2_current", "Phase 2 Current")
            self.l3_current = Gauge("solaredge_phase3_current", "Phase 3 Current")

            self.l1_voltage = Gauge("solaredge_phase1_voltage", "Phase 1 Voltage")
            self.l2_voltage = Gauge("solaredge_phase2_voltage", "Phase 2 Voltage")
            self.l3_voltage = Gauge("solaredge_phase3_voltage", "Phase 3 Voltage")

            self.l1_n_voltage = Gauge("solaredge_phase1-n_voltage", "Phase 1-N Voltage")
            self.l2_n_voltage = Gauge("solaredge_phase2-n_voltage", "Phase 2-N Voltage")
            self.l3_n_voltage = Gauge("solaredge_phase3-n_voltage", "Phase 3-N Voltage")
        else:
            self.l1_voltage = Gauge("solaredge_phase1_voltage", "Phase 1 Voltage")

        self.frequency = Gauge("solaredge_frequency", "Frequency")
        self.power_ac = Gauge("solaredge_power_ac", "AC Power")
        self.power_apparent = Gauge("solaredge_power_apparent", "Apparent Power")
        self.power_reactive = Gauge("solaredge_power_reactive", "Reactive Power")
        self.power_factor = Gauge("solaredge_power_factor", "Power Factor")
        self.energy_total = Gauge("solaredge_energy_total", "Total Energy")

        self.current_dc = Gauge("solaredge_dc_current", "DC Current")
        self.voltage_dc = Gauge("solaredge_dc_voltage", "DC Voltage")
        self.power_dc = Gauge("solaredge_dc_power", "DC Power")

    def run_metrics_loop(self):
        """Main metrics loop"""
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """Fetch new solaredge values"""
        values = {}
        values = self.inverter.read_all()
        self.info.info({
            "c_manufacturer": values['c_manufacturer'],
            "c_model": values['c_model'],
            "c_sunspec_did": solaredge_modbus.C_SUNSPEC_DID_MAP[str(values['c_sunspec_did'])],
            "c_version": values['c_version'],
            "c_serialnumber": values['c_serialnumber'],
            "status": solaredge_modbus.INVERTER_STATUS_MAP[values['status']]
        })

        self.temperature.set(float(values['temperature'] * (10 ** values['temperature_scale'])))
        self.current.set(float(values['current'] * (10 ** values['current_scale'])))

        if values['c_sunspec_did'] is solaredge_modbus.sunspecDID.THREE_PHASE_INVERTER.value:
            self.l1_current.set(float(values['l1_current'] * (10 ** values['current_scale'])))
            self.l2_current.set(float(values['l2_current'] * (10 ** values['current_scale'])))
            self.l3_current.set(float(values['l3_current'] * (10 ** values['current_scale'])))
            self.l1_voltage.set(float(values['l1_voltage'] * (10 ** values['voltage_scale'])))
            self.l2_voltage.set(float(values['l2_voltage'] * (10 ** values['voltage_scale'])))
            self.l3_voltage.set(float(values['l3_voltage'] * (10 ** values['voltage_scale'])))
            self.l1_n_voltage.set(float(values['l1n_voltage'] * (10 ** values['voltage_scale'])))
            self.l2_n_voltage.set(float(values['l2n_voltage'] * (10 ** values['voltage_scale'])))
            self.l3_n_voltage.set(float(values['l3n_voltage'] * (10 ** values['voltage_scale'])))
        else:
            self.l1_voltage.set(float(values['l1_voltage'] * (10 ** values['voltage_scale'])))

        self.frequency.set(float(values['frequency'] * (10 ** values['frequency_scale'])))
        self.power_ac.set(float(values['power_ac'] * (10 ** values['power_ac_scale'])))
        self.power_apparent.set(float(values['power_apparent'] * (10 ** values['power_apparent_scale'])))
        self.power_reactive.set(float(values['power_reactive'] * (10 ** values['power_reactive_scale'])))
        self.power_factor.set(float(values['power_factor'] * (10 ** values['power_factor_scale'])))
        self.energy_total.set(float(values['energy_total'] * (10 ** values['energy_total_scale'])))

        self.current_dc.set(float(values['current_dc'] * (10 ** values['current_dc_scale'])))
        self.voltage_dc.set(float(values['voltage_dc'] * (10 ** values['voltage_dc_scale'])))
        self.power_dc.set(float(values['power_dc'] * (10 ** values['power_dc_scale'])))

def main():
    """Main Function"""
    solar_edge_metrics = SolarEdgeMetrics(
        se_host=os.environ.get('SOLAREDGE_HOST','192.168.1.152'),
        se_port=os.environ.get('SOLAREDGE_PORT', 1502),
        se_timeout=os.environ.get('SOLAREDGE_TIMEOUT',5),
        se_unit=os.environ.get('SOLAREDGE_UNIT', 0x1),
    )

    start_http_server(2112)
    solar_edge_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
