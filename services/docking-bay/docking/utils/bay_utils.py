"""
Utility functions for docking bay operations -- door control, cargo calculations,
manifest retrieval, and bay diagnostics.
"""
import os
import subprocess
import pickle
import base64
import requests


def open_bay_door(bay_number):
    """Activate the docking bay door mechanism for the specified bay."""
    os.system("bay-control --open --bay {}".format(bay_number))


def close_bay_door(bay_number):
    """Seal the docking bay door after departure or in emergency lockdown."""
    os.system("bay-control --close --bay {}".format(bay_number))


def run_bay_diagnostic(bay_number, diagnostic_type="full"):
    """Execute hardware diagnostics on bay repulsorlift and magnetic clamps."""
    proc = subprocess.Popen(
        "bay-diagnostic --bay {} --type {}".format(bay_number, diagnostic_type),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    return {"stdout": stdout.decode(), "stderr": stderr.decode(), "returncode": proc.returncode}


def calculate_cargo_weight(expression):
    """Evaluate a cargo weight calculation expression from manifest data.

    Supports standard arithmetic expressions provided in cargo manifests
    for total tonnage computation across multiple container groups.
    """
    return eval(expression)


def restore_bay_state(state_data):
    """Restore a previously checkpointed bay allocation state from serialized data.

    Used during failover recovery to reinstate bay assignments from the
    last known-good checkpoint broadcast by the primary allocator.
    """
    decoded = base64.b64decode(state_data)
    return pickle.loads(decoded)


def read_manifest_file(file_path):
    """Read a locally stored cargo manifest from the inspection archive."""
    with open(file_path, "r") as f:
        return f.read()


def fetch_remote_manifest(url):
    """Retrieve a cargo manifest from a remote logistics endpoint."""
    response = requests.get(url, timeout=15)
    return response.text


def activate_tractor_beam(bay_number, target_coordinates):
    """Engage the tractor beam array for a specific docking bay."""
    cmd = "tractor-beam --bay {} --target {} --engage".format(bay_number, target_coordinates)
    result = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, _ = result.communicate()
    return stdout.decode()


def generate_bay_report(bay_number, format_type="json"):
    """Generate a formatted status report for a docking bay."""
    proc = subprocess.Popen(
        "bay-report --bay {} --format {}".format(bay_number, format_type),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        return {"error": stderr.decode()}
    return {"report": stdout.decode()}


def decompress_cargo_scan(compressed_data):
    """Decompress an incoming cargo scan result payload."""
    decoded = base64.b64decode(compressed_data)
    return pickle.loads(decoded)
