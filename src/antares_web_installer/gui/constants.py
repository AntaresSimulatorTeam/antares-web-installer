import os

filetypes = {
    "COMMON_EXCLUDED_FILES": {"config.prod.yaml", "config.yaml", "examples", "logs", "matrices", "tmp"},
}

filetypes.update({
    "POSIX_EXCLUDED_FILES": filetypes["COMMON_EXCLUDED_FILES"] | {"AntaresWebWorker"},
    "WINDOWS_EXCLUDED_FILES": filetypes["COMMON_EXCLUDED_FILES"] | {"AntaresWebWorker.exe"},
    "SERVER_NAMES": {"posix": "AntaresWebServer", "nt": "AntaresWebServer.exe"},
    "SHORTCUT_NAMES": {"posix": "AntaresWebServer.desktop", "nt": "AntaresWebServer.lnk"},
})

filetypes.update({
    "EXCLUDED_FILES": filetypes["POSIX_EXCLUDED_FILES"] if os.name == "posix" else filetypes["WINDOWS_EXCLUDED_FILES"],
})

