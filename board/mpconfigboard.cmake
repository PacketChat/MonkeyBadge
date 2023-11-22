set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
set(SDKCONFIG_DEFAULTS
    ${CMAKE_SOURCE_DIR}/boards/sdkconfig.base
#   ${CMAKE_SOURCE_DIR}/boards/sdkconfig.ble
    ${MICROPY_BOARD_DIR}/sdkconfig.board
)

get_cmake_property(_variableNames VARIABLES)
foreach (_variableName ${_variableNames})
    message(STATUS "${_variableName}=${${_variableName}}")
endforeach()
