"""Telemetry ingestion from Assetto Corsa shared memory.

Modules:
  - reader: Low-level shared memory interface
  - ac_structs: Binary struct definitions for AC data
  - pipeline: Async pipeline (read → normalize → buffer)
"""
