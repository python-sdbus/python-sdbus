archive_builder = find_program('./build_container_archive.py')
podman_runner = find_program('./run_podman.py')
container_script = files('run_inside_container.py')

build_container_archive = custom_target(
    'container_archive.tar',
    build_by_default : false,
    output : 'container_archive.tar',
    input : container_script,  # Force archive rebuilt on script changes
    command : [
        archive_builder,
        '--build-dir', '@PRIVATE_DIR@',
        '--output-file', '@OUTPUT@',
        '--source-root', '@SOURCE_ROOT@',
    ],
)

run_podman = run_target(
    'run_podman',
    command : [
        podman_runner,
        '--archive', build_container_archive,
        '--source-root', '@SOURCE_ROOT@',
    ],
)
