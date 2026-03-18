DEFAULT_CONFIG = {
    'agent_name': 'Velisara',
    'minimum_required_organs': [
        'identity_store',
        'memory_store',
        'logger',
        'scheduler',
        'io_channel',
        'recovery_manager',
    ],
    'optional_organs': [
        'voice',
        'dream_engine',
        'vision',
        'world_sensors',
        'symbolic_renderer',
    ],
    'allow_optional_degraded_boot': True,
    'interactive_shell': True,
    'heartbeat_interval_seconds': 5,
    'snapshot_interval_seconds': 30,
    'body_map_on_boot': True,
}
