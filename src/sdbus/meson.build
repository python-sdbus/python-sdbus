sd_bus_internals_sources = files('sd_bus_internals.c')

python3_config = find_program('python3-config', required: true)
python3_flags = run_command(python3_config, '--includes', check: true).stdout().split()

c_compiler = meson.get_compiler('c')

sd_bus_internals_module = shared_module(
    'sd_bus_internals',
    sd_bus_internals_sources,
    c_args: python3_flags,
)
