cmake_minimum_required(VERSION 3.17)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_VERSION 1)

# Must be before project() to skip linking test
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

project({{PROJECT_NAME}} C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# CPU-specific flags
add_compile_options(
    -mcpu={{MCPU}}
    -mthumb
    -mthumb-interwork
    {{FPU_FLAGS}}
    -ffunction-sections
    -fdata-sections
    -fno-common
    -fmessage-length=0
    -Wall
    -Wno-unused-function
)

if("${CMAKE_BUILD_TYPE}" STREQUAL "Release")
    add_compile_options(-Ofast)
elseif("${CMAKE_BUILD_TYPE}" STREQUAL "RelWithDebInfo")
    add_compile_options(-Ofast -g)
elseif("${CMAKE_BUILD_TYPE}" STREQUAL "MinSizeRel")
    add_compile_options(-Os)
else()
    add_compile_options(-Og -g)
endif()

add_compile_definitions(
    USE_STDPERIPH_DRIVER
    {{DEVICE_DEFINE}}
    {{HXTAL_DEFINES}}
)

# Linker script
set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/{{LINKER_SCRIPT}})

# GCC startup file — set assembler-with-cpp for .S/.s files
set_source_files_properties(
    STARTUP/{{STARTUP_FILE}}
    PROPERTIES COMPILE_FLAGS "-x assembler-with-cpp"
)
enable_language(ASM)

# SDK sources (CMSIS + FIRMWARE — suppress all SDK warnings)
set(SDK_SOURCES
    STARTUP/{{STARTUP_FILE}}
    {{SDK_SOURCES}}
    {{FREERTOS_CMAKE_SOURCES}}
    {{RTT_CMAKE_SOURCES}}
)

# User sources (app + driver + system — keep warnings)
set(USER_SOURCES
    {{USER_SOURCES}}
)

add_executable(${PROJECT_NAME} ${SDK_SOURCES} ${USER_SOURCES})
set_source_files_properties(${SDK_SOURCES} PROPERTIES COMPILE_FLAGS "-w")

# Include directories
# System includes (suppress SDK warnings)
target_include_directories(${PROJECT_NAME} SYSTEM PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/CMSIS
    ${CMAKE_CURRENT_SOURCE_DIR}/CMSIS/{{DEVICE_INC_REL}}/Include
    ${CMAKE_CURRENT_SOURCE_DIR}/FIRMWARE/Include
    {{FREERTOS_CMAKE_INCLUDES}}
    {{RTT_CMAKE_INCLUDES}}
)

# User includes (keep warnings for user code)
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/APP
    ${CMAKE_CURRENT_SOURCE_DIR}/DRIVER
    ${CMAKE_CURRENT_SOURCE_DIR}/HARDWARE
    ${CMAKE_CURRENT_SOURCE_DIR}/SYSTEM/delay
    ${CMAKE_CURRENT_SOURCE_DIR}/SYSTEM/sys
    ${CMAKE_CURRENT_SOURCE_DIR}/USER
)

# Link options
target_link_options(${PROJECT_NAME} PRIVATE
    -mcpu={{MCPU}}
    -mthumb
    -mthumb-interwork
    {{FPU_FLAGS}}
    -T${LINKER_SCRIPT}
    -Wl,-gc-sections
    -Wl,--print-memory-usage
    -Wl,-Map=${PROJECT_BINARY_DIR}/${PROJECT_NAME}.map
    --specs=nosys.specs
)

# Generate hex and bin
set(HEX_FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.hex)
set(BIN_FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.bin)

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -Oihex $<TARGET_FILE:${PROJECT_NAME}> ${HEX_FILE}
    COMMAND ${CMAKE_OBJCOPY} -Obinary --gap-fill=0xFF $<TARGET_FILE:${PROJECT_NAME}> ${BIN_FILE}
    COMMENT "Building ${HEX_FILE} and ${BIN_FILE}"
)
