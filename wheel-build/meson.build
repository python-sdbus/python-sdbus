archive_builder = find_program('./build_container_archive.py')
# archive_builder = files('./build_container_archive.py')

build_container_archive = custom_target(
    'container_archive.tar',
    build_by_default : false,
    output : 'container_archive.tar',
    command : [
        archive_builder,
        '--build-dir', '@PRIVATE_DIR@',
        '--output-file', '@OUTPUT@',
        '--source-root', '@SOURCE_ROOT@',
    ]
)
