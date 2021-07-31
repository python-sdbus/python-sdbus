sd_bus_internals_sources = files(
    './sd_bus_internals.c',
    './sd_bus_internals_bus.c',
    './sd_bus_internals_funcs.c',
    './sd_bus_internals_interface.c',
    './sd_bus_internals_message.c',
    './sd_bus_internals.h',
)

python3_dep = dependency('python3', version : '>= 3.7')

c_compiler = meson.get_compiler('c')

lint_args = ['-Wall', '-Wextra', '-Werror']

sd_bus_internals_module = shared_module(
    'sd_bus_internals',
    sd_bus_internals_sources,
    dependencies : python3_dep,
    c_args : lint_args,
)

sd_bus_internals_module_stable = shared_module(
    'sd_bus_internals_stable',
    sd_bus_internals_sources,
    dependencies : python3_dep,
    c_args : lint_args + ['-DPy_LIMITED_API=0x03070000'],
)
