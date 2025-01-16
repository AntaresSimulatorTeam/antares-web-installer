import hashlib
from pathlib import Path

import pytest

from antares_web_installer.app import App, EXCLUDED_ROOT_RESOURCES


class TestApp:
    def test_run(self) -> None:
        pass

    def test_kill_running_server(self) -> None:
        # 1. Lancer un serveur
        # 2. Appeler la méthode kill_running_server
        # 3. Vérifier que le serveur a bien été tué
        pass

    def test_install_files__from_scratch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Case where the target directory does not exist.
        """
        # Prepare the test resources
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        target_dir = tmp_path / "target"
        monkeypatch.setattr("antares_web_installer.app.App.check_version", lambda _: "2.17.0")

        # Say we have dummy files in the source directory
        expected_files = ["dummy.txt", "folder/dummy2.txt"]
        for name in expected_files:
            dummy_file = source_dir / name
            dummy_file.parent.mkdir(parents=True, exist_ok=True)
            dummy_file.touch()

        # Run the test
        app = App(source_dir=source_dir, target_dir=target_dir)
        app.install_files()

        # Check the results
        for name in expected_files:
            assert (target_dir / name).exists(), f"File {name} must be copied"

    def test_copy_files__nominal_case(self, datadir: Path) -> None:
        # Prepare the test resources
        source_dir = datadir.joinpath("copy_files/source_files")
        target_dir = datadir.joinpath("copy_files/target_files")

        # collect the checksum of all files in the target directory
        old_checksum_by_name = {}
        for file in target_dir.rglob("*.*"):
            content = file.read_bytes()
            old_checksum_by_name[file.relative_to(target_dir)] = hashlib.md5(content).hexdigest()

        # Run the test
        app = App(source_dir=source_dir, target_dir=target_dir)
        app.copy_files()

        # Check the results
        for file in target_dir.rglob("*.*"):
            relative_path = file.relative_to(target_dir)
            content = file.read_bytes()
            old_checksum = old_checksum_by_name[relative_path]
            new_checksum = hashlib.md5(content).hexdigest()
            root_name = Path(relative_path.parts[0])
            if root_name in EXCLUDED_ROOT_RESOURCES:
                assert old_checksum == new_checksum, f"File {file} must not have been modified"
            else:
                assert old_checksum != new_checksum, f"File {file} must have been updated"

    def test_check_version(self, tmp_path: Path) -> None:
        # 3 cas à tester :
        # 1. Le programme exécutable n'existe pas => InstallError
        # 2. Le programme exécutable existe, mais le programme plante => InstallError
        # 3. Le programme exécutable existe et fonctionne => pas d'erreur
        pass
